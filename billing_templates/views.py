"""
Views for Billing Templates
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Min, Max
from django.utils import timezone
from datetime import timedelta

from .models import BillingTemplate, BillingTemplateUsage, BillingTemplateCategory
from .serializers import (
    BillingTemplateSerializer, BillingTemplateListSerializer,
    BillingTemplateUsageSerializer, BillingTemplateCategorySerializer,
    BillingTemplateWithCategoriesSerializer, BillingTemplateStatsSerializer,
    BillingTemplateConfigDataSerializer
)


class BillingTemplateListView(generics.ListAPIView):
    """List all active billing templates"""
    queryset = BillingTemplate.objects.filter(is_active=True).order_by('sort_order', 'price')
    serializer_class = BillingTemplateListSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint


class BillingTemplateDetailView(generics.RetrieveAPIView):
    """Get details of a specific billing template"""
    queryset = BillingTemplate.objects.filter(is_active=True)
    serializer_class = BillingTemplateSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint


class BillingTemplateWithCategoriesView(generics.RetrieveAPIView):
    """Get billing template with category information"""
    queryset = BillingTemplate.objects.filter(is_active=True)
    serializer_class = BillingTemplateWithCategoriesSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint


class PopularBillingTemplatesView(generics.ListAPIView):
    """Get popular billing templates"""
    queryset = BillingTemplate.objects.filter(is_active=True, is_popular=True).order_by('sort_order', 'price')
    serializer_class = BillingTemplateListSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint


class BillingTemplateCategoriesView(generics.ListAPIView):
    """List all billing template categories"""
    queryset = BillingTemplateCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = BillingTemplateCategorySerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint


class BillingTemplateByCategoryView(generics.ListAPIView):
    """Get billing templates by category"""
    serializer_class = BillingTemplateListSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return BillingTemplate.objects.filter(
            is_active=True,
            category_assignments__category_id=category_id
        ).order_by('sort_order', 'price')


class BillingTemplateStatsView(APIView):
    """Get billing template statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive billing template statistics"""
        
        # Basic counts
        total_templates = BillingTemplate.objects.count()
        active_templates = BillingTemplate.objects.filter(is_active=True).count()
        popular_templates = BillingTemplate.objects.filter(is_active=True, is_popular=True).count()
        
        # Usage statistics
        total_usage = BillingTemplateUsage.objects.count()
        
        # Most used template
        most_used = BillingTemplateUsage.objects.values('template__name').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        most_used_template = most_used['template__name'] if most_used else 'None'
        most_used_count = most_used['count'] if most_used else 0
        
        # Price statistics
        price_stats = BillingTemplate.objects.filter(is_active=True).aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Recent usage (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_usage = BillingTemplateUsage.objects.filter(
            used_at__gte=thirty_days_ago
        ).count()
        
        stats = {
            'total_templates': total_templates,
            'active_templates': active_templates,
            'popular_templates': popular_templates,
            'total_usage': total_usage,
            'recent_usage': recent_usage,
            'most_used_template': most_used_template,
            'most_used_count': most_used_count,
            'average_price': float(price_stats['avg_price'] or 0),
            'price_range': {
                'min': float(price_stats['min_price'] or 0),
                'max': float(price_stats['max_price'] or 0)
            }
        }
        
        serializer = BillingTemplateStatsSerializer(stats)
        return Response(serializer.data)


class BillingTemplateUsageView(generics.ListAPIView):
    """Get billing template usage records for authenticated user"""
    serializer_class = BillingTemplateUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BillingTemplateUsage.objects.filter(
            user=self.request.user
        ).select_related('template', 'generated_config').order_by('-used_at')


class BillingTemplateConfigDataView(APIView):
    """Get billing template configuration data for config generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, template_id):
        """Get billing template data formatted for config generation"""
        template = get_object_or_404(BillingTemplate, id=template_id, is_active=True)
        
        # Check if user has active subscription
        from subscriptions.models import Subscription
        try:
            subscription = Subscription.objects.filter(
                user=request.user,
                is_active=True,
                status='active'
            ).latest('created_at')
            
            if subscription.is_expired():
                return Response(
                    {'error': 'Subscription expired'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BillingTemplateConfigDataSerializer(template)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_billing_template_usage(request):
    """Track usage of a billing template"""
    template_id = request.data.get('template_id')
    config_id = request.data.get('config_id')
    
    if not template_id or not config_id:
        return Response(
            {'error': 'template_id and config_id are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        template = BillingTemplate.objects.get(id=template_id, is_active=True)
        config = get_object_or_404(
            'config_generator.GeneratedConfig',
            id=config_id,
            user=request.user
        )
        
        # Create usage record
        usage = BillingTemplateUsage.objects.create(
            template=template,
            user=request.user,
            generated_config=config
        )
        
        serializer = BillingTemplateUsageSerializer(usage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except BillingTemplate.DoesNotExist:
        return Response(
            {'error': 'Billing template not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class BillingTemplateSearchView(generics.ListAPIView):
    """Search billing templates by name, description, or bandwidth"""
    serializer_class = BillingTemplateListSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def get_queryset(self):
        queryset = BillingTemplate.objects.filter(is_active=True)
        
        # Search parameters
        search = self.request.query_params.get('search', None)
        min_mbps = self.request.query_params.get('min_mbps', None)
        max_mbps = self.request.query_params.get('max_mbps', None)
        duration_type = self.request.query_params.get('duration_type', None)
        max_price = self.request.query_params.get('max_price', None)
        popular_only = self.request.query_params.get('popular_only', None)
        
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        if min_mbps:
            queryset = queryset.filter(mbps__gte=min_mbps)
        
        if max_mbps:
            queryset = queryset.filter(mbps__lte=max_mbps)
        
        if duration_type:
            queryset = queryset.filter(duration_type=duration_type)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        if popular_only and popular_only.lower() == 'true':
            queryset = queryset.filter(is_popular=True)
        
        return queryset.order_by('sort_order', 'price')
