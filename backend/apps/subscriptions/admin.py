"""
Admin configuration for subscriptions app
"""
from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'max_employees', 'price_monthly', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'status', 'expires_at', 'approved_by', 'is_active']
    list_filter = ['status', 'plan', 'expires_at']
    search_fields = ['organization__name', 'plan__name', 'approved_by__phone_number']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('organization', 'plan', 'status')
        }),
        ('Сроки', {
            'fields': ('started_at', 'expires_at', 'auto_renew')
        }),
        ('Одобрение', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_subscriptions', 'cancel_subscriptions']
    
    def approve_subscriptions(self, request, queryset):
        """Одобрить выбранные подписки"""
        from .services import SubscriptionService
        
        count = 0
        for subscription in queryset.filter(status='pending'):
            SubscriptionService.approve_subscription(
                subscription,
                approved_by=request.user,
                duration_months=1
            )
            count += 1
        
        self.message_user(request, f'Одобрено подписок: {count}')
    approve_subscriptions.short_description = 'Одобрить выбранные подписки'
    
    def cancel_subscriptions(self, request, queryset):
        """Отменить выбранные подписки"""
        count = queryset.update(status='cancelled')
        self.message_user(request, f'Отменено подписок: {count}')
    cancel_subscriptions.short_description = 'Отменить выбранные подписки'
