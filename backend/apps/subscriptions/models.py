"""
Subscription models for SaaS access control
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Модель плана подписки"""
    PLAN_TYPES = [
        ('basic', 'Базовый'),
        ('business', 'Бизнес'),
        ('enterprise', 'Корпоративный'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    max_employees = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Максимум сотрудников (null = безлимит)'
    )
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена в месяц (тенге)'
    )
    features = models.JSONField(default=dict, verbose_name='Доступные функции')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'План подписки'
        verbose_name_plural = 'Планы подписок'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Модель подписки организации"""
    STATUS_CHOICES = [
        ('none', 'Нет подписки'),
        ('pending', 'Ожидает одобрения'),
        ('active', 'Активна'),
        ('expired', 'Истекла'),
        ('cancelled', 'Отменена'),
    ]
    
    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Организация'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        verbose_name='План'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='none',
        verbose_name='Статус'
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начало действия')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Истекает')
    auto_renew = models.BooleanField(default=True, verbose_name='Автопродление')
    # Кто одобрил подписку
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_subscriptions',
        verbose_name='Одобрено'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата одобрения')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.plan.name} ({self.get_status_display()})"

    @property
    def is_active(self):
        """Проверка активности подписки"""
        from django.utils import timezone
        return (
            self.status == 'active' and
            self.expires_at and
            self.expires_at > timezone.now()
        )

