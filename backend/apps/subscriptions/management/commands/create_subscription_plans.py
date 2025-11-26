"""
Команда для создания начальных планов подписки
"""
from django.core.management.base import BaseCommand
from apps.subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Создает начальные планы подписки'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Базовый',
                'plan_type': 'basic',
                'max_employees': 50,
                'price_monthly': 15000,
                'features': {
                    'employee_management': True,
                    'basic_reports': True,
                    'calendar_planning': True,
                    'document_generation': True,
                    'api_access': False,
                    'white_label': False,
                }
            },
            {
                'name': 'Бизнес',
                'plan_type': 'business',
                'max_employees': 500,
                'price_monthly': 45000,
                'features': {
                    'employee_management': True,
                    'basic_reports': True,
                    'advanced_reports': True,
                    'calendar_planning': True,
                    'document_generation': True,
                    'api_access': True,
                    'integrations': True,
                    'white_label': False,
                }
            },
            {
                'name': 'Корпоративный',
                'plan_type': 'enterprise',
                'max_employees': None,  # Безлимит
                'price_monthly': 150000,
                'features': {
                    'employee_management': True,
                    'basic_reports': True,
                    'advanced_reports': True,
                    'calendar_planning': True,
                    'document_generation': True,
                    'api_access': True,
                    'integrations': True,
                    'white_label': True,
                    'dedicated_support': True,
                }
            },
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан план: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'План уже существует: {plan.name}')
                )

