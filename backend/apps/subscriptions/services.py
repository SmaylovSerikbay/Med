"""
Subscription services
"""
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, SubscriptionPlan
from apps.organizations.models import Organization


class SubscriptionService:
    """Сервис для работы с подписками"""
    
    @staticmethod
    def request_subscription(organization: Organization, plan: SubscriptionPlan) -> Subscription:
        """
        Запросить подписку для организации
        
        Args:
            organization: Организация
            plan: План подписки
            
        Returns:
            Subscription объект со статусом 'pending'
        """
        # Проверяем существует ли уже подписка
        try:
            subscription = Subscription.objects.get(organization=organization)
            # Обновляем план и статус если подписка уже существует
            subscription.plan = plan
            subscription.status = 'pending'
            subscription.save()
        except Subscription.DoesNotExist:
            # Создаем новую подписку
            subscription = Subscription.objects.create(
                organization=organization,
                plan=plan,
                status='pending',
            )
        
        return subscription
    
    @staticmethod
    def approve_subscription(
        subscription: Subscription,
        approved_by,
        duration_months: int = 1
    ) -> Subscription:
        """
        Одобрить подписку
        
        Args:
            subscription: Подписка
            approved_by: Пользователь, который одобряет (админ)
            duration_months: Длительность подписки в месяцах
            
        Returns:
            Subscription объект со статусом 'active'
        """
        subscription.status = 'active'
        subscription.started_at = timezone.now()
        subscription.expires_at = timezone.now() + timedelta(days=30 * duration_months)
        subscription.approved_by = approved_by
        subscription.approved_at = timezone.now()
        subscription.save()
        
        return subscription
    
    @staticmethod
    def check_organization_access(organization: Organization) -> bool:
        """
        Проверить есть ли у организации активная подписка
        
        Args:
            organization: Организация
            
        Returns:
            bool: True если есть активная подписка
        """
        try:
            subscription = organization.subscription
            # Проверяем что статус 'active' и подписка не истекла
            return subscription.status == 'active' and subscription.is_active
        except Subscription.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_organizations_with_access(user) -> list:
        """
        Получить список организаций пользователя с активными подписками
        
        Args:
            user: Пользователь
            
        Returns:
            list: Список организаций с активными подписками
        """
        # Организации где пользователь владелец
        owned_orgs = Organization.objects.filter(owner=user)
        
        # Организации где пользователь участник
        from apps.organizations.models import OrganizationMember
        member_orgs = Organization.objects.filter(
            members__user=user,
            members__is_active=True
        )
        
        all_orgs = (owned_orgs | member_orgs).distinct()
        
        # Фильтруем только с активными подписками
        orgs_with_access = []
        for org in all_orgs:
            if SubscriptionService.check_organization_access(org):
                orgs_with_access.append(org)
        
        return orgs_with_access

