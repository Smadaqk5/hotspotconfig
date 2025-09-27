from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Payment, PaymentItem
from .serializers import PaymentSerializer, CreatePaymentSerializer
from .pesapal import PesapalAPI
from subscriptions.models import ProviderSubscriptionPlan, ProviderSubscription
import json


class PaymentCreateView(generics.CreateAPIView):
    """Create a new payment"""
    serializer_class = CreatePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Initialize Pesapal API
            pesapal = PesapalAPI()
            
            # Get access token
            token_response = pesapal.get_access_token()
            if not token_response or 'token' not in token_response:
                return Response(
                    {'error': 'Failed to get Pesapal access token'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            access_token = token_response['token']
            
            # Register IPN
            ipn_response = pesapal.register_ipn(access_token)
            if not ipn_response:
                return Response(
                    {'error': 'Failed to register IPN'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create order data
            order_data = {
                'id': str(payment.id),
                'currency': payment.currency,
                'amount': float(payment.amount),
                'description': payment.description,
                'callback_url': settings.PESAPAL_CALLBACK_URL,
                'cancellation_url': f"{settings.PESAPAL_CALLBACK_URL}?status=cancelled",
                'notification_id': ipn_response.get('ipn_id'),
                'billing_address': {
                    'phone_number': request.user.phone_number or '',
                    'email_address': request.user.email,
                    'country_code': 'KE',
                    'first_name': request.user.first_name or '',
                    'middle_name': '',
                    'last_name': request.user.last_name or '',
                    'line_1': '',
                    'line_2': '',
                    'city': '',
                    'state': '',
                    'postal_code': '',
                    'zip_code': ''
                }
            }
            
            # Create Pesapal order
            order_response = pesapal.create_order(order_data, access_token)
            if not order_response:
                return Response(
                    {'error': 'Failed to create Pesapal order'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Update payment with Pesapal details
            payment.pesapal_order_tracking_id = order_response.get('order_tracking_id')
            payment.pesapal_merchant_reference = order_response.get('merchant_reference')
            payment.save()
            
            return Response({
                'payment': PaymentSerializer(payment).data,
                'checkout_url': order_response.get('redirect_url'),
                'order_tracking_id': order_response.get('order_tracking_id')
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(generics.ListAPIView):
    """List user's payments"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, payment_id):
    """Get payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return Response(PaymentSerializer(payment).data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def pesapal_callback(request):
    """Handle Pesapal payment callback"""
    order_tracking_id = request.GET.get('OrderTrackingId')
    merchant_reference = request.GET.get('OrderMerchantReference')
    payment_reference = request.GET.get('OrderNotificationType')
    
    if not all([order_tracking_id, merchant_reference]):
        return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(
            pesapal_order_tracking_id=order_tracking_id,
            pesapal_merchant_reference=merchant_reference
        )
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Initialize Pesapal API to verify payment
    pesapal = PesapalAPI()
    token_response = pesapal.get_access_token()
    
    if token_response and 'token' in token_response:
        access_token = token_response['token']
        status_response = pesapal.get_order_status(order_tracking_id, access_token)
        
        if status_response and status_response.get('payment_status') == 'COMPLETED':
            # Update payment status
            payment.status = 'completed'
            payment.pesapal_payment_reference = payment_reference
            payment.completed_at = timezone.now()
            payment.save()
            
            # Create or update subscription
            from subscriptions.views import create_subscription
            subscription_data = {
                'plan_id': payment.items.first().name  # This should be the plan ID
            }
            
            # You might want to call the subscription creation logic here
            # For now, we'll just return success
            
            return Response({'status': 'success', 'message': 'Payment completed'})
    
    return Response({'status': 'pending', 'message': 'Payment still processing'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def pesapal_ipn(request):
    """Handle Pesapal IPN (Instant Payment Notification)"""
    # This is where Pesapal sends server-to-server notifications
    # You should verify the signature and update payment status accordingly
    
    data = request.data
    order_tracking_id = data.get('OrderTrackingId')
    merchant_reference = data.get('OrderMerchantReference')
    payment_status = data.get('PaymentStatus')
    
    if not all([order_tracking_id, merchant_reference, payment_status]):
        return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(
            pesapal_order_tracking_id=order_tracking_id,
            pesapal_merchant_reference=merchant_reference
        )
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update payment status based on Pesapal notification
    if payment_status == 'COMPLETED':
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Create subscription
        # You'll need to implement this logic based on your requirements
        
    elif payment_status == 'FAILED':
        payment.status = 'failed'
        payment.save()
    
    return Response({'status': 'success'})
