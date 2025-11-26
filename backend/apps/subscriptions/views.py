"""
Subscription views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Subscription, SubscriptionPlan
from .serializers import SubscriptionSerializer, SubscriptionPlanSerializer
from .services import SubscriptionService
from apps.organizations.models import Organization


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для планов подписки (только чтение)"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet для подписок"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Показываем подписки организаций пользователя
        from apps.organizations.models import Organization
        from django.db.models import Q
        
        org_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).values_list('id', flat=True)
        
        # Возвращаем подписки, включая те организации где подписки нет (через LEFT JOIN)
        # Но для этого нужно использовать другой подход - показываем все организации пользователя
        # и для каждой проверяем есть ли подписка
        return Subscription.objects.filter(organization_id__in=org_ids)
    
    @action(detail=False, methods=['post'])
    def request_subscription(self, request):
        """Запросить подписку для организации"""
        organization_id = request.data.get('organization_id')
        plan_id = request.data.get('plan_id')
        
        try:
            organization = Organization.objects.get(id=organization_id)
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except (Organization.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
            return Response(
                {'error': 'Организация или план не найдены'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем права - только владелец может запросить подписку
        if organization.owner != request.user:
            return Response(
                {'error': 'Только владелец организации может запросить подписку'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription = SubscriptionService.request_subscription(organization, plan)
        serializer = self.get_serializer(subscription)
        
        return Response({
            'message': 'Подписка запрошена и ожидает одобрения администратора',
            'subscription': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Одобрить подписку (только для админов)"""
        subscription = self.get_object()
        
        # TODO: Проверить что пользователь админ
        # if not request.user.is_staff:
        #     return Response(
        #         {'error': 'Только администраторы могут одобрять подписки'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        duration_months = request.data.get('duration_months', 1)
        
        subscription = SubscriptionService.approve_subscription(
            subscription,
            approved_by=request.user,
            duration_months=duration_months
        )
        
        serializer = self.get_serializer(subscription)
        return Response({
            'message': 'Подписка одобрена и активирована',
            'subscription': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        """Мои подписки"""
        subscriptions = self.get_queryset()
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Текущие подписки (алиас для my_subscriptions)"""
        return self.my_subscriptions(request)
