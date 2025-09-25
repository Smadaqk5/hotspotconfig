from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import SubscriptionPlan, Subscription, SubscriptionUsage
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionUsageSerializer


class SubscriptionPlanListView(generics.ListAPIView):
    """List all available subscription plans"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionView(generics.RetrieveAPIView):
    """Get current user's subscription"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return Subscription.objects.filter(
                user=self.request.user,
                is_active=True
            ).latest('created_at')
        except Subscription.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        subscription = self.get_object()
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        return Response({'message': 'No active subscription found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_status(request):
    """Get subscription status and details"""
    try:
        subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True
        ).latest('created_at')
        
        return Response({
            'has_subscription': True,
            'subscription': SubscriptionSerializer(subscription).data,
            'is_active': subscription.status == 'active' and not subscription.is_expired(),
            'days_remaining': subscription.days_remaining(),
        })
    except Subscription.DoesNotExist:
        return Response({
            'has_subscription': False,
            'message': 'No active subscription'
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_subscription(request):
    """Create a new subscription (called after successful payment)"""
    plan_id = request.data.get('plan_id')
    
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Deactivate any existing active subscriptions
    Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).update(is_active=False, status='cancelled')
    
    # Create new subscription
    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan,
        status='active'
    )
    
    # Create usage tracking
    SubscriptionUsage.objects.create(subscription=subscription)
    
    return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)
