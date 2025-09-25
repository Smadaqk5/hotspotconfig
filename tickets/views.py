"""
Views for tickets app
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import (
    TicketType, Ticket, TicketSale, TicketBatch, TicketUsage
)
from .serializers import (
    TicketTypeSerializer, TicketSerializer, TicketCreateSerializer,
    TicketSaleSerializer, TicketBatchSerializer, TicketUsageSerializer,
    TicketStatsSerializer, TicketTypeStatsSerializer
)

User = get_user_model()


class TicketTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketType model"""
    
    queryset = TicketType.objects.filter(is_active=True)
    serializer_class = TicketTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see active ticket types
        if not self.request.user.is_staff:
            return queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular ticket types"""
        popular_types = self.get_queryset().filter(is_popular=True)
        serializer = self.get_serializer(popular_types, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for Ticket model"""
    
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter tickets by user"""
        return Ticket.objects.filter(user=self.request.user).select_related(
            'ticket_type', 'user'
        )
    
    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer
    
    def perform_create(self, serializer):
        """Create ticket with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a ticket"""
        ticket = self.get_object()
        if ticket.status != 'active':
            return Response(
                {'error': 'Ticket is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.activate()
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def expire(self, request, pk=None):
        """Expire a ticket"""
        ticket = self.get_object()
        if ticket.status != 'active':
            return Response(
                {'error': 'Ticket is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.expire()
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get ticket statistics for user"""
        user = request.user
        
        # Basic stats
        total_tickets = Ticket.objects.filter(user=user).count()
        active_tickets = Ticket.objects.filter(user=user, status='active').count()
        used_tickets = Ticket.objects.filter(user=user, status='used').count()
        expired_tickets = Ticket.objects.filter(user=user, status='expired').count()
        
        # Revenue stats
        total_revenue = TicketSale.objects.filter(
            ticket__user=user, 
            ticket__status__in=['used', 'active']
        ).aggregate(total=Sum('sale_price'))['total'] or 0
        
        # Time-based stats
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=7)
        month_start = today - timezone.timedelta(days=30)
        
        today_sales = TicketSale.objects.filter(
            ticket__user=user,
            sold_at__date=today
        ).count()
        
        this_week_sales = TicketSale.objects.filter(
            ticket__user=user,
            sold_at__date__gte=week_start
        ).count()
        
        this_month_sales = TicketSale.objects.filter(
            ticket__user=user,
            sold_at__date__gte=month_start
        ).count()
        
        stats_data = {
            'total_tickets': total_tickets,
            'active_tickets': active_tickets,
            'used_tickets': used_tickets,
            'expired_tickets': expired_tickets,
            'total_revenue': total_revenue,
            'today_sales': today_sales,
            'this_week_sales': this_week_sales,
            'this_month_sales': this_month_sales,
        }
        
        serializer = TicketStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get ticket statistics by type"""
        user = request.user
        
        # Get stats by ticket type
        ticket_types = TicketType.objects.filter(is_active=True)
        stats_data = []
        
        for ticket_type in ticket_types:
            tickets = Ticket.objects.filter(user=user, ticket_type=ticket_type)
            sales = TicketSale.objects.filter(ticket__in=tickets)
            
            stats = {
                'ticket_type': ticket_type.name,
                'total_sold': tickets.count(),
                'total_revenue': sales.aggregate(total=Sum('sale_price'))['total'] or 0,
                'active_tickets': tickets.filter(status='active').count(),
                'used_tickets': tickets.filter(status='used').count(),
                'expired_tickets': tickets.filter(status='expired').count(),
            }
            stats_data.append(stats)
        
        serializer = TicketTypeStatsSerializer(stats_data, many=True)
        return Response(serializer.data)


class TicketSaleViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketSale model"""
    
    queryset = TicketSale.objects.all()
    serializer_class = TicketSaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter sales by user"""
        return TicketSale.objects.filter(
            ticket__user=self.request.user
        ).select_related('ticket', 'ticket__ticket_type', 'sold_by')
    
    def perform_create(self, serializer):
        """Create sale with current user as seller"""
        serializer.save(sold_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Get revenue statistics"""
        user = request.user
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        sales = TicketSale.objects.filter(ticket__user=user)
        
        if start_date:
            sales = sales.filter(sold_at__date__gte=start_date)
        if end_date:
            sales = sales.filter(sold_at__date__lte=end_date)
        
        total_revenue = sales.aggregate(total=Sum('sale_price'))['total'] or 0
        total_sales = sales.count()
        
        return Response({
            'total_revenue': total_revenue,
            'total_sales': total_sales,
            'average_sale': total_revenue / total_sales if total_sales > 0 else 0
        })


class TicketBatchViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketBatch model"""
    
    queryset = TicketBatch.objects.all()
    serializer_class = TicketBatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter batches by user"""
        return TicketBatch.objects.filter(user=self.request.user).select_related(
            'ticket_type', 'user'
        )
    
    def perform_create(self, serializer):
        """Create batch with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_tickets(self, request, pk=None):
        """Generate tickets for a batch"""
        batch = self.get_object()
        
        if batch.is_generated:
            return Response(
                {'error': 'Tickets already generated for this batch'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                batch.generate_tickets()
                return Response({'message': f'{batch.quantity} tickets generated successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to generate tickets: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get tickets for a batch"""
        batch = self.get_object()
        tickets = Ticket.objects.filter(
            user=request.user,
            ticket_type=batch.ticket_type,
            created_at__gte=batch.created_at
        ).order_by('username')
        
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class TicketUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for TicketUsage model (read-only)"""
    
    queryset = TicketUsage.objects.all()
    serializer_class = TicketUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter usage by user's tickets"""
        return TicketUsage.objects.filter(
            ticket__user=self.request.user
        ).select_related('ticket', 'ticket__ticket_type')
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get usage analytics"""
        user = request.user
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        usage = TicketUsage.objects.filter(ticket__user=user)
        
        if start_date:
            usage = usage.filter(timestamp__date__gte=start_date)
        if end_date:
            usage = usage.filter(timestamp__date__lte=end_date)
        
        # Aggregate data
        total_data_used = usage.aggregate(total=Sum('data_used_bytes'))['total'] or 0
        total_time_used = usage.aggregate(total=Sum('time_used_seconds'))['total'] or 0
        
        return Response({
            'total_data_used_gb': round(total_data_used / (1024 ** 3), 2),
            'total_time_used_hours': round(total_time_used / 3600, 2),
            'total_usage_sessions': usage.count()
        })