from rest_framework import serializers
from .models import Payment, PaymentItem


class PaymentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentItem
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    items = PaymentItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'completed_at')


class CreatePaymentSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ('amount', 'currency', 'description', 'plan_id')
    
    def create(self, validated_data):
        plan_id = validated_data.pop('plan_id')
        user = self.context['request'].user
        
        # Get plan details (you'll need to import SubscriptionPlan)
        from subscriptions.models import SubscriptionPlan
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid plan")
        
        payment = Payment.objects.create(
            user=user,
            amount=plan.price,
            currency='KES',
            description=f"Subscription to {plan.name}",
            **validated_data
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment,
            name=plan.name,
            description=plan.description,
            quantity=1,
            unit_price=plan.price,
            total_price=plan.price
        )
        
        return payment
