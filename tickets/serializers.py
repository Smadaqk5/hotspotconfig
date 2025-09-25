"""
Serializers for tickets app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    TicketType, Ticket, TicketSale, TicketBatch, TicketUsage
)

User = get_user_model()


class TicketTypeSerializer(serializers.ModelSerializer):
    """Serializer for TicketType model"""
    
    duration_display = serializers.ReadOnlyField()
    price_display = serializers.ReadOnlyField()
    bandwidth_display = serializers.ReadOnlyField()
    
    class Meta:
        model = TicketType
        fields = [
            'id', 'name', 'ticket_type', 'description', 'duration_hours', 
            'data_limit_gb', 'price', 'currency', 'is_active', 'is_popular', 
            'sort_order', 'duration_display', 'price_display', 'bandwidth_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket model"""
    
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    ticket_type_price = serializers.DecimalField(source='ticket_type.price', max_digits=10, decimal_places=2, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    remaining_data = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    is_used = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_type', 'ticket_type_name', 'ticket_type_price',
            'user', 'user_email', 'username', 'password', 'status',
            'created_at', 'activated_at', 'expires_at', 'data_used_bytes',
            'time_used_seconds', 'mikrotik_username', 'mikrotik_profile',
            'is_synced_to_router', 'notes', 'remaining_data', 'remaining_time',
            'is_expired', 'is_used'
        ]
        read_only_fields = [
            'id', 'created_at', 'activated_at', 'data_used_bytes',
            'time_used_seconds', 'is_expired', 'is_used'
        ]
    
    def get_remaining_data(self, obj):
        """Get remaining data in GB"""
        return obj.get_remaining_data()
    
    def get_remaining_time(self, obj):
        """Get remaining time in hours"""
        return obj.get_remaining_time()
    
    def get_is_expired(self, obj):
        """Check if ticket is expired"""
        return obj.is_expired()
    
    def get_is_used(self, obj):
        """Check if ticket is used"""
        return obj.is_used()


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets"""
    
    class Meta:
        model = Ticket
        fields = [
            'ticket_type', 'username', 'password', 'notes'
        ]
    
    def create(self, validated_data):
        """Create ticket with user from context"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TicketSaleSerializer(serializers.ModelSerializer):
    """Serializer for TicketSale model"""
    
    ticket_username = serializers.CharField(source='ticket.username', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket.ticket_type.name', read_only=True)
    sold_by_email = serializers.CharField(source='sold_by.email', read_only=True)
    
    class Meta:
        model = TicketSale
        fields = [
            'id', 'ticket', 'ticket_username', 'ticket_type_name',
            'sold_by', 'sold_by_email', 'sale_price', 'payment_method',
            'payment_reference', 'customer_name', 'customer_phone',
            'customer_email', 'notes', 'sold_at'
        ]
        read_only_fields = ['id', 'sold_at']
    
    def create(self, validated_data):
        """Create sale with seller from context"""
        validated_data['sold_by'] = self.context['request'].user
        return super().create(validated_data)


class TicketBatchSerializer(serializers.ModelSerializer):
    """Serializer for TicketBatch model"""
    
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    generated_tickets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketBatch
        fields = [
            'id', 'name', 'ticket_type', 'ticket_type_name', 'user', 'user_email',
            'quantity', 'username_prefix', 'password_length', 'is_generated',
            'generated_at', 'created_at', 'generated_tickets_count'
        ]
        read_only_fields = ['id', 'is_generated', 'generated_at', 'created_at']
    
    def get_generated_tickets_count(self, obj):
        """Get count of generated tickets"""
        if obj.is_generated:
            return obj.ticket_set.count()
        return 0
    
    def create(self, validated_data):
        """Create batch with user from context"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TicketUsageSerializer(serializers.ModelSerializer):
    """Serializer for TicketUsage model"""
    
    ticket_username = serializers.CharField(source='ticket.username', read_only=True)
    data_used_gb = serializers.SerializerMethodField()
    time_used_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketUsage
        fields = [
            'id', 'ticket', 'ticket_username', 'timestamp', 'data_used_bytes',
            'data_used_gb', 'time_used_seconds', 'time_used_hours',
            'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_data_used_gb(self, obj):
        """Convert bytes to GB"""
        return round(obj.data_used_bytes / (1024 ** 3), 2)
    
    def get_time_used_hours(self, obj):
        """Convert seconds to hours"""
        return round(obj.time_used_seconds / 3600, 2)


class TicketStatsSerializer(serializers.Serializer):
    """Serializer for ticket statistics"""
    
    total_tickets = serializers.IntegerField()
    active_tickets = serializers.IntegerField()
    used_tickets = serializers.IntegerField()
    expired_tickets = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    today_sales = serializers.IntegerField()
    this_week_sales = serializers.IntegerField()
    this_month_sales = serializers.IntegerField()


class TicketTypeStatsSerializer(serializers.Serializer):
    """Serializer for ticket type statistics"""
    
    ticket_type = serializers.CharField()
    total_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_tickets = serializers.IntegerField()
    used_tickets = serializers.IntegerField()
    expired_tickets = serializers.IntegerField()
