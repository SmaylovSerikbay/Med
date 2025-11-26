"""
Subscription serializers
"""
from rest_framework import serializers
from .models import Subscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'max_employees',
            'price_monthly', 'features', 'is_active'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_type = serializers.CharField(source='organization.org_type', read_only=True)
    plan_name = serializers.SerializerMethodField()
    approved_by_phone = serializers.CharField(source='approved_by.phone_number', read_only=True, allow_null=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'organization', 'organization_name', 'organization_type',
            'plan', 'plan_name', 'status', 'started_at', 'expires_at',
            'auto_renew', 'approved_by', 'approved_by_phone', 'approved_at',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'approved_at']
    
    def get_plan_name(self, obj):
        # Не показываем план если статус 'none'
        if obj.status == 'none' or not obj.plan:
            return None
        return obj.plan.name
    
    def get_is_active(self, obj):
        return obj.is_active
