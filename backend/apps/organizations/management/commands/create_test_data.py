"""
Management команда для создания тестовых данных
Создает реальных пользователей и организации для тестирования полного цикла
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership, OrganizationType
from apps.compliance.models import Profession, HarmfulFactor

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовые данные для проверки полного цикла Приказа 131'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ'))
        self.stdout.write('=' * 70)
        
        # Тестовые номера
        clinic_phone = '77085446945'
        employer_phone = '77776875411'
        doctor_phone = '77021491010'
        employee_phone = '77789171790'
        
        # 1. Создание пользователей
        self.stdout.write('\n1. Создание пользователей...')
        
        clinic_user, created = User.objects.get_or_create(
            username=clinic_phone,
            defaults={
                'phone_number': clinic_phone,
                'phone_verified': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь клиники: {clinic_phone}'))
        else:
            self.stdout.write(f'  ℹ️  Пользователь клиники уже существует: {clinic_phone}')
        
        employer_user, created = User.objects.get_or_create(
            username=employer_phone,
            defaults={
                'phone_number': employer_phone,
                'phone_verified': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь работодателя: {employer_phone}'))
        else:
            self.stdout.write(f'  ℹ️  Пользователь работодателя уже существует: {employer_phone}')
        
        doctor_user, created = User.objects.get_or_create(
            username=doctor_phone,
            defaults={
                'phone_number': doctor_phone,
                'phone_verified': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь врача: {doctor_phone}'))
        else:
            self.stdout.write(f'  ℹ️  Пользователь врача уже существует: {doctor_phone}')
        
        employee_user, created = User.objects.get_or_create(
            username=employee_phone,
            defaults={
                'phone_number': employee_phone,
                'phone_verified': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан пользователь сотрудника: {employee_phone}'))
        else:
            self.stdout.write(f'  ℹ️  Пользователь сотрудника уже существует: {employee_phone}')
        
        # 2. Создание организаций
        self.stdout.write('\n2. Создание организаций...')
        
        clinic, created = Organization.objects.get_or_create(
            owner=clinic_user,
            org_type=OrganizationType.CLINIC,
            defaults={
                'name': 'Тестовая Клиника МедПро',
                'capacity_per_day': 30,
                'address': 'г. Алматы, ул. Тестовая, 1',
                'phone': '+7 (727) 123-45-67',
                'bin': '123456789012'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создана клиника: {clinic.name}'))
        else:
            self.stdout.write(f'  ℹ️  Клиника уже существует: {clinic.name}')
            clinic.name = 'Тестовая Клиника МедПро'
            clinic.capacity_per_day = 30
            clinic.save()
        
        employer, created = Organization.objects.get_or_create(
            owner=employer_user,
            org_type=OrganizationType.EMPLOYER,
            defaults={
                'name': 'Тестовая Организация Производство',
                'address': 'г. Алматы, ул. Промышленная, 10',
                'phone': '+7 (727) 234-56-78',
                'bin': '987654321098'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан работодатель: {employer.name}'))
        else:
            self.stdout.write(f'  ℹ️  Работодатель уже существует: {employer.name}')
            employer.name = 'Тестовая Организация Производство'
            employer.save()
        
        # 3. Создание партнерства
        self.stdout.write('\n3. Создание партнерства...')
        
        partnership, created = ClinicEmployerPartnership.objects.get_or_create(
            clinic=clinic,
            employer=employer,
            defaults={
                'status': ClinicEmployerPartnership.PartnershipStatus.ACTIVE,
                'requested_by': employer_user,
                'confirmed_by': clinic_user,
                'confirmed_at': timezone.now(),
                'default_price': 5000
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создано активное партнерство'))
        else:
            if partnership.status != ClinicEmployerPartnership.PartnershipStatus.ACTIVE:
                partnership.status = ClinicEmployerPartnership.PartnershipStatus.ACTIVE
                partnership.confirmed_at = timezone.now()
                partnership.save()
                self.stdout.write(self.style.SUCCESS(f'  ✅ Партнерство активировано'))
            else:
                self.stdout.write(f'  ℹ️  Партнерство уже активно')
        
        # 4. Создание вредного фактора и профессии
        self.stdout.write('\n4. Создание вредных факторов и профессий...')
        
        harmful_factor, created = HarmfulFactor.objects.get_or_create(
            code='1.1.1',
            defaults={
                'name': 'Шум производственный',
                'periodicity_months': 12,
                'required_doctors': ['ЛОР', 'Невролог'],
                'required_tests': ['Аудиометрия'],
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан вредный фактор: {harmful_factor.name}'))
        else:
            self.stdout.write(f'  ℹ️  Вредный фактор уже существует: {harmful_factor.name}')
        
        profession, created = Profession.objects.get_or_create(
            name='Электросварщик',
            defaults={
                'is_decreted': False,
                'keywords': ['сварщик', 'электросварщик', 'welder']
            }
        )
        if created:
            profession.harmful_factors.add(harmful_factor)
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создана профессия: {profession.name}'))
        else:
            if not profession.harmful_factors.filter(id=harmful_factor.id).exists():
                profession.harmful_factors.add(harmful_factor)
            self.stdout.write(f'  ℹ️  Профессия уже существует: {profession.name}')
        
        # 5. Создание врачей в клинике
        self.stdout.write('\n5. Создание врачей в клинике...')
        
        doctor, created = OrganizationMember.objects.get_or_create(
            organization=clinic,
            user=doctor_user,
            defaults={
                'role': 'doctor',
                'specialization': 'ЛОР',
                'license_number': 'DOC-12345',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Добавлен врач ЛОР: {doctor_user.phone_number}'))
        else:
            doctor.role = 'doctor'
            doctor.specialization = 'ЛОР'
            doctor.is_active = True
            doctor.save()
            self.stdout.write(f'  ℹ️  Врач уже существует, обновлен: {doctor_user.phone_number}')
        
        # Профпатолог - проверяем существует ли отдельный профпатолог
        # Если врач уже существует, используем его как профпатолога (в тестах допустимо)
        profpathologist = OrganizationMember.objects.filter(
            organization=clinic,
            role='profpathologist',
            is_active=True
        ).first()
        
        if not profpathologist:
            # Пытаемся создать профпатолога с тем же пользователем что и врач
            # Если не получается из-за unique_together - используем врача
            try:
                profpathologist = OrganizationMember.objects.create(
                    organization=clinic,
                    user=doctor_user,
                    role='profpathologist',
                    specialization='Профпатолог',
                    license_number='PROF-12345',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'  ✅ Добавлен профпатолог'))
            except:
                # Если не получилось (из-за unique_together), используем врача
                profpathologist = doctor
                self.stdout.write(f'  ℹ️  Профпатолог будет использовать того же пользователя что и врач')
        else:
            self.stdout.write(f'  ℹ️  Профпатолог уже существует')
        
        # 6. Создание сотрудника
        self.stdout.write('\n6. Создание сотрудника...')
        
        employee, created = Employee.objects.get_or_create(
            user=employee_user,
            defaults={
                'employer': employer,
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'middle_name': 'Иванович',
                'iin': '123456789012',
                'position': profession,
                'department': 'Цех №1',
                'hire_date': timezone.now().date() - timedelta(days=400),
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Создан сотрудник: {employee.full_name}'))
        else:
            # Обновляем все данные сотрудника
            employee.employer = employer
            employee.position = profession
            employee.first_name = 'Иван'
            employee.last_name = 'Иванов'
            employee.middle_name = 'Иванович'
            employee.is_active = True
            employee.save()
            self.stdout.write(self.style.SUCCESS(f'  ✅ Сотрудник обновлен: {employee.full_name}'))
        
        # 7. Проверка подписок
        self.stdout.write('\n7. Проверка подписок...')
        from apps.subscriptions.services import SubscriptionService
        from apps.subscriptions.models import Subscription, SubscriptionPlan
        
        # Проверяем подписку клиники
        if not SubscriptionService.check_organization_access(clinic):
            plan = SubscriptionPlan.objects.filter(is_active=True).first()
            if plan:
                subscription, created = Subscription.objects.get_or_create(
                    organization=clinic,
                    defaults={
                        'plan': plan,
                        'status': 'active',
                        'started_at': timezone.now(),
                        'expires_at': timezone.now() + timedelta(days=30)
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Создана подписка для клиники'))
                else:
                    subscription.status = 'active'
                    subscription.save()
                    self.stdout.write(f'  ✅ Подписка клиники активирована')
        
        # Проверяем подписку работодателя
        if not SubscriptionService.check_organization_access(employer):
            plan = SubscriptionPlan.objects.filter(is_active=True).first()
            if plan:
                subscription, created = Subscription.objects.get_or_create(
                    organization=employer,
                    defaults={
                        'plan': plan,
                        'status': 'active',
                        'started_at': timezone.now(),
                        'expires_at': timezone.now() + timedelta(days=30)
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Создана подписка для работодателя'))
                else:
                    subscription.status = 'active'
                    subscription.save()
                    self.stdout.write(f'  ✅ Подписка работодателя активирована')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!'))
        self.stdout.write('=' * 70)
        self.stdout.write('\nДанные для входа:')
        self.stdout.write(f'  📱 Клиника: {clinic_phone}')
        self.stdout.write(f'  📱 Работодатель: {employer_phone}')
        self.stdout.write(f'  📱 Врач: {doctor_phone}')
        self.stdout.write(f'  📱 Сотрудник: {employee_phone}')
        self.stdout.write('\nМожно тестировать полный цикл через UI!')

