from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import ProviderSubscriptionPlan, ProviderSubscription, SubscriptionUsage
from .serializers import ProviderSubscriptionPlanSerializer, ProviderSubscriptionSerializer, SubscriptionUsageSerializer


class SubscriptionPlanListView(generics.ListAPIView):
    """List all available subscription plans"""
    queryset = ProviderSubscriptionPlan.objects.filter(is_active=True)
    serializer_class = ProviderSubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """Get details of a specific subscription plan"""
    queryset = ProviderSubscriptionPlan.objects.filter(is_active=True)
    serializer_class = ProviderSubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionListView(generics.ListAPIView):
    """List user's subscriptions"""
    serializer_class = ProviderSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProviderSubscription.objects.filter(user=self.request.user)


class UserSubscriptionDetailView(generics.RetrieveAPIView):
    """Get details of a specific user subscription"""
    serializer_class = ProviderSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProviderSubscription.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_status(request):
    """Get current subscription status for the user"""
    try:
        subscription = ProviderSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).latest('created_at')
        
        return Response({
            'has_subscription': True,
            'subscription': ProviderSubscriptionSerializer(subscription).data
        })
    except ProviderSubscription.DoesNotExist:
        return Response({
            'has_subscription': False,
            'message': 'No active subscription found'
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_subscription(request):
    """Create a new subscription (called after successful payment)"""
    plan_id = request.data.get('plan_id')
    
    try:
        plan = ProviderSubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except ProviderSubscriptionPlan.DoesNotExist:
        return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Deactivate any existing active subscriptions
    ProviderSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).update(is_active=False, status='cancelled')
    
    # Create new subscription
    subscription = ProviderSubscription.objects.create(
        user=request.user,
        plan=plan,
        status='active'
    )
    
    # Create usage tracking
    SubscriptionUsage.objects.create(subscription=subscription)
    
    return Response(ProviderSubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request, subscription_id):
    """Cancel a subscription"""
    try:
        subscription = ProviderSubscription.objects.get(
            id=subscription_id,
            user=request.user
        )
        subscription.status = 'cancelled'
        subscription.is_active = False
        subscription.save()
        
        return Response({
            'message': 'Subscription cancelled successfully',
            'subscription': ProviderSubscriptionSerializer(subscription).data
        })
    except ProviderSubscription.DoesNotExist:
        return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_usage(request):
    """Get subscription usage information"""
    try:
        subscription = ProviderSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).latest('created_at')
        
        try:
            usage = SubscriptionUsage.objects.get(subscription=subscription)
            return Response(SubscriptionUsageSerializer(usage).data)
        except SubscriptionUsage.DoesNotExist:
            return Response({'message': 'No usage data available'})
    except ProviderSubscription.DoesNotExist:
        return Response({'error': 'No active subscription'}, status=status.HTTP_404_NOT_FOUND)