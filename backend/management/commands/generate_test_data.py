"""
Django management команда для генерации тестовых данных
Использование: python manage.py generate_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
import uuid

from apps.organizations.models import (
    Organization, OrganizationType, OrganizationMember, 
    Employee, ClinicEmployerPartnership
)
from apps.compliance.models import HarmfulFactor, Profession, MedicalContraindication
from apps.medical_examinations.models import (
    MedicalExamination, ExaminationType, ExaminationStatus,
    ExaminationResult, DoctorExamination, LaboratoryResult
)
from apps.documents.models import Document, DocumentType, DocumentStatus, CalendarPlan
from apps.subscriptions.models import SubscriptionPlan, Subscription

User = get_user_model()


class Command(BaseCommand):
    help = 'Генерация тестовых данных (минимум 20 записей по каждой сущности)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Начинаем генерацию тестовых данных...'))
        self.stdout.write('=' * 60)
        
        # Генерация данных
        self.create_subscription_plans()
        users = self.create_users(30)
        self.create_harmful_factors()
        self.create_professions()
        employers = self.create_employers(10, users[:10])
        clinics = self.create_clinics(5, users[10:15])
        employees = self.create_employees(50, employers, users[15:])
        doctors = self.create_doctors(25, clinics)
        self.create_partnerships(clinics, employers)
        examinations = self.create_examinations(100, employees, clinics)
        self.create_doctor_examinations(examinations, doctors)
        self.create_laboratory_results(examinations)
        self.create_documents(employers, examinations)
        self.create_calendar_plans(employers, clinics)
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Генерация завершена!'))
        self.print_summary()

    def create_subscription_plans(self):
        """Создание планов подписок"""
        self.stdout.write('\n📋 Создание планов подписок...')
        
        plans = [
            {'name': 'Базовый', 'plan_type': 'basic', 'max_employees': 50, 'price_monthly': Decimal('50000')},
            {'name': 'Бизнес', 'plan_type': 'business', 'max_employees': 200, 'price_monthly': Decimal('150000')},
            {'name': 'Корпоративный', 'plan_type': 'enterprise', 'max_employees': None, 'price_monthly': Decimal('500000')},
        ]
        
        for plan_data in plans:
            SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults={**plan_data, 'features': {}}
            )
        
        self.stdout.write(f'  ✓ Создано планов: {SubscriptionPlan.objects.count()}')

    def create_users(self, count):
        """Создание пользователей"""
        self.stdout.write(f'\n👥 Создание {count} пользователей...')
        users = []
        
        for i in range(1, count + 1):
            phone = f"7702{1000000 + i}"
            user, _ = User.objects.get_or_create(
                phone_number=phone,
                defaults={'phone_verified': True, 'is_active': True}
            )
            users.append(user)
        
        self.stdout.write(f'  ✓ Всего пользователей: {User.objects.count()}')
        return users

    def create_harmful_factors(self):
        """Создание вредных факторов"""
        self.stdout.write('\n⚠️  Создание вредных факторов...')
        
        factors = [
            {'code': 'HF001', 'name': 'Шум', 'doctors': ['Отоларинголог', 'Терапевт']},
            {'code': 'HF002', 'name': 'Вибрация локальная', 'doctors': ['Невролог', 'Терапевт']},
            {'code': 'HF003', 'name': 'Вибрация общая', 'doctors': ['Невролог', 'Терапевт']},
            {'code': 'HF004', 'name': 'Пыль фиброгенная', 'doctors': ['Пульмонолог', 'Терапевт']},
            {'code': 'HF005', 'name': 'Химические вещества', 'doctors': ['Терапевт', 'Дерматолог']},
            {'code': 'HF006', 'name': 'Биологические факторы', 'doctors': ['Инфекционист', 'Терапевт']},
            {'code': 'HF007', 'name': 'Физические перегрузки', 'doctors': ['Хирург', 'Терапевт']},
            {'code': 'HF008', 'name': 'Работа на высоте', 'doctors': ['Невролог', 'Офтальмолог', 'Терапевт']},
            {'code': 'HF009', 'name': 'Электромагнитные поля', 'doctors': ['Невролог', 'Терапевт']},
            {'code': 'HF010', 'name': 'Ионизирующее излучение', 'doctors': ['Терапевт', 'Гематолог']},
            {'code': 'HF011', 'name': 'Ультразвук', 'doctors': ['Невролог', 'Терапевт']},
            {'code': 'HF012', 'name': 'Инфразвук', 'doctors': ['Невролог', 'Терапевт']},
            {'code': 'HF013', 'name': 'Лазерное излучение', 'doctors': ['Офтальмолог', 'Терапевт']},
            {'code': 'HF014', 'name': 'Микроклимат нагревающий', 'doctors': ['Терапевт', 'Кардиолог']},
            {'code': 'HF015', 'name': 'Микроклимат охлаждающий', 'doctors': ['Терапевт', 'Пульмонолог']},
            {'code': 'HF016', 'name': 'Освещенность недостаточная', 'doctors': ['Офтальмолог', 'Терапевт']},
            {'code': 'HF017', 'name': 'Работа с ПЭВМ', 'doctors': ['Офтальмолог', 'Невролог', 'Терапевт']},
            {'code': 'HF018', 'name': 'Нервно-эмоциональные нагрузки', 'doctors': ['Психиатр', 'Терапевт']},
            {'code': 'HF019', 'name': 'Работа в ночную смену', 'doctors': ['Терапевт', 'Невролог']},
            {'code': 'HF020', 'name': 'Монотонность труда', 'doctors': ['Невролог', 'Терапевт']},
        ]
        
        for factor_data in factors:
            HarmfulFactor.objects.get_or_create(
                code=factor_data['code'],
                defaults={
                    'name': factor_data['name'],
                    'periodicity_months': 12,
                    'required_doctors': factor_data['doctors'],
                    'required_tests': ['Общий анализ крови', 'Общий анализ мочи']
                }
            )
        
        self.stdout.write(f'  ✓ Создано факторов: {HarmfulFactor.objects.count()}')

    def create_professions(self):
        """Создание профессий"""
        self.stdout.write('\n💼 Создание профессий...')
        
        professions = [
            {'name': 'Электросварщик', 'factors': ['HF001', 'HF004', 'HF008']},
            {'name': 'Токарь', 'factors': ['HF001', 'HF002', 'HF004']},
            {'name': 'Слесарь', 'factors': ['HF001', 'HF002', 'HF007']},
            {'name': 'Маляр', 'factors': ['HF005', 'HF008']},
            {'name': 'Водитель', 'factors': ['HF001', 'HF003', 'HF019']},
            {'name': 'Оператор ПЭВМ', 'factors': ['HF017', 'HF018']},
            {'name': 'Медицинская сестра', 'factors': ['HF006', 'HF018'], 'decreted': True},
            {'name': 'Повар', 'factors': ['HF014', 'HF007'], 'decreted': True},
            {'name': 'Грузчик', 'factors': ['HF007', 'HF015']},
            {'name': 'Уборщик', 'factors': ['HF005', 'HF007']},
            {'name': 'Шахтер', 'factors': ['HF001', 'HF004', 'HF007', 'HF015']},
            {'name': 'Крановщик', 'factors': ['HF001', 'HF008', 'HF018']},
            {'name': 'Лаборант', 'factors': ['HF005', 'HF006', 'HF017']},
            {'name': 'Рентгенолог', 'factors': ['HF010', 'HF017']},
            {'name': 'Диспетчер', 'factors': ['HF017', 'HF018', 'HF019']},
            {'name': 'Охранник', 'factors': ['HF018', 'HF019']},
            {'name': 'Строитель', 'factors': ['HF001', 'HF004', 'HF007', 'HF008']},
            {'name': 'Электрик', 'factors': ['HF008', 'HF009']},
            {'name': 'Механик', 'factors': ['HF001', 'HF002', 'HF005']},
            {'name': 'Оператор станков ЧПУ', 'factors': ['HF001', 'HF002', 'HF017']},
        ]
        
        for prof_data in professions:
            profession, _ = Profession.objects.get_or_create(
                name=prof_data['name'],
                defaults={'is_decreted': prof_data.get('decreted', False)}
            )
            factors = HarmfulFactor.objects.filter(code__in=prof_data['factors'])
            profession.harmful_factors.set(factors)
        
        self.stdout.write(f'  ✓ Создано профессий: {Profession.objects.count()}')

    def create_employers(self, count, users):
        """Создание работодателей"""
        self.stdout.write(f'\n🏢 Создание {count} работодателей...')
        employers = []
        plan = SubscriptionPlan.objects.filter(plan_type='business').first()
        
        company_names = [
            'ТОО "Казахстанский завод"', 'АО "Промышленность Казахстана"',
            'ТОО "Строительная компания Астана"', 'АО "Металлургический комбинат"',
            'ТОО "Нефтегазовая компания"', 'АО "Энергетика Казахстана"',
            'ТОО "Транспортная логистика"', 'АО "Горнодобывающая компания"',
            'ТОО "Пищевая промышленность"', 'АО "Химический завод"',
        ]
        
        for i, name in enumerate(company_names[:count]):
            org, _ = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'org_type': OrganizationType.EMPLOYER,
                    'bin': f'12345678901{i}',
                    'owner': users[i],
                    'address': f'г. Алматы, ул. Промышленная {i+1}',
                    'phone': f'7727{1000000 + i}'
                }
            )
            employers.append(org)
            
            # Создаем подписку
            Subscription.objects.get_or_create(
                organization=org,
                defaults={
                    'plan': plan,
                    'status': 'active',
                    'started_at': timezone.now(),
                    'expires_at': timezone.now() + timedelta(days=365)
                }
            )
        
        self.stdout.write(f'  ✓ Создано работодателей: {len(employers)}')
        return employers

    def create_clinics(self, count, users):
        """Создание клиник"""
        self.stdout.write(f'\n🏥 Создание {count} клиник...')
        clinics = []
        plan = SubscriptionPlan.objects.filter(plan_type='business').first()
        
        clinic_names = [
            'Поликлиника №1', 'Медицинский центр "Здоровье"',
            'Клиника "Профмед"', 'Центр профпатологии',
            'Многопрофильная клиника "Медикер"',
        ]
        
        for i, name in enumerate(clinic_names[:count]):
            org, _ = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'org_type': OrganizationType.CLINIC,
                    'bin': f'98765432101{i}',
                    'owner': users[i],
                    'address': f'г. Алматы, пр. Абая {i+1}',
                    'phone': f'7727{2000000 + i}',
                    'capacity_per_day': random.randint(30, 100)
                }
            )
            clinics.append(org)
            
            # Создаем подписку
            Subscription.objects.get_or_create(
                organization=org,
                defaults={
                    'plan': plan,
                    'status': 'active',
                    'started_at': timezone.now(),
                    'expires_at': timezone.now() + timedelta(days=365)
                }
            )
        
        self.stdout.write(f'  ✓ Создано клиник: {len(clinics)}')
        return clinics

    def create_employees(self, count, employers, users):
        """Создание сотрудников"""
        self.stdout.write(f'\n👷 Создание {count} сотрудников...')
        employees = []
        professions = list(Profession.objects.all())
        
        first_names = ['Алексей', 'Дмитрий', 'Сергей', 'Андрей', 'Иван', 'Максим', 'Артем', 'Владимир']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Соколов', 'Лебедев']
        
        for i in range(count):
            user = users[i % len(users)]
            employer = employers[i % len(employers)]
            profession = professions[i % len(professions)]
            
            employee, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employer': employer,
                    'first_name': first_names[i % len(first_names)],
                    'last_name': last_names[i % len(last_names)],
                    'middle_name': 'Александрович',
                    'position': profession,
                    'hire_date': timezone.now().date() - timedelta(days=random.randint(30, 1000)),
                    'is_active': True
                }
            )
            employees.append(employee)
        
        self.stdout.write(f'  ✓ Создано сотрудников: {len(employees)}')
        return employees

    def create_doctors(self, count, clinics):
        """Создание врачей"""
        self.stdout.write(f'\n👨‍⚕️ Создание {count} врачей...')
        doctors = []
        
        specializations = [
            'Терапевт', 'Невролог', 'Офтальмолог', 'Отоларинголог', 'Хирург',
            'Кардиолог', 'Пульмонолог', 'Дерматолог', 'Профпатолог', 'Психиатр'
        ]
        
        for i in range(count):
            phone = f"7701{3000000 + i}"
            user, _ = User.objects.get_or_create(
                phone_number=phone,
                defaults={'phone_verified': True, 'is_active': True}
            )
            
            clinic = clinics[i % len(clinics)]
            specialization = specializations[i % len(specializations)]
            role = 'profpathologist' if specialization == 'Профпатолог' else 'doctor'
            
            member, _ = OrganizationMember.objects.get_or_create(
                organization=clinic,
                user=user,
                defaults={
                    'role': role,
                    'specialization': specialization,
                    'license_number': f'LIC{100000 + i}',
                    'is_active': True
                }
            )
            doctors.append(member)
        
        self.stdout.write(f'  ✓ Создано врачей: {len(doctors)}')
        return doctors

    def create_partnerships(self, clinics, employers):
        """Создание партнерств"""
        self.stdout.write('\n🤝 Создание партнерств...')
        count = 0
        
        for clinic in clinics:
            for employer in employers[:3]:  # Каждая клиника с 3 работодателями
                ClinicEmployerPartnership.objects.get_or_create(
                    clinic=clinic,
                    employer=employer,
                    defaults={
                        'status': 'active',
                        'default_price': Decimal('5000.00'),
                        'requested_by': clinic.owner,
                        'confirmed_by': employer.owner,
                        'confirmed_at': timezone.now()
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ Создано партнерств: {count}')

    def create_examinations(self, count, employees, clinics):
        """Создание осмотров"""
        self.stdout.write(f'\n🔬 Создание {count} осмотров...')
        examinations = []
        
        exam_types = list(ExaminationType.choices)
        statuses = list(ExaminationStatus.choices)
        
        for i in range(count):
            employee = employees[i % len(employees)]
            clinic = clinics[i % len(clinics)]
            exam_type = exam_types[i % len(exam_types)][0]
            status = statuses[i % len(statuses)][0]
            
            exam, _ = MedicalExamination.objects.get_or_create(
                employee=employee,
                examination_type=exam_type,
                scheduled_date=timezone.now() + timedelta(days=random.randint(1, 90)),
                defaults={
                    'clinic': clinic,
                    'employer': employee.employer,
                    'status': status,
                    'qr_code': str(uuid.uuid4())[:8].upper()
                }
            )
            examinations.append(exam)
        
        self.stdout.write(f'  ✓ Создано осмотров: {len(examinations)}')
        return examinations

    def create_doctor_examinations(self, examinations, doctors):
        """Создание результатов осмотров врачей"""
        self.stdout.write('\n📋 Создание результатов осмотров врачей...')
        count = 0
        
        completed_exams = [e for e in examinations if e.status == 'completed'][:20]
        results = list(ExaminationResult.choices)
        
        for exam in completed_exams:
            factors = exam.employee.position.harmful_factors.all()[:2]
            for factor in factors:
                doctor = doctors[count % len(doctors)]
                DoctorExamination.objects.get_or_create(
                    examination=exam,
                    doctor=doctor,
                    harmful_factor=factor,
                    defaults={
                        'result': results[count % len(results)][0],
                        'findings': 'Осмотр проведен, патологий не выявлено',
                        'recommendations': 'Продолжить работу'
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ Создано результатов: {count}')

    def create_laboratory_results(self, examinations):
        """Создание лабораторных результатов"""
        self.stdout.write('\n🧪 Создание лабораторных результатов...')
        count = 0
        
        completed_exams = [e for e in examinations if e.status == 'completed'][:20]
        tests = [
            {'name': 'Общий анализ крови', 'value': '120', 'unit': 'г/л', 'range': '120-160'},
            {'name': 'Общий анализ мочи', 'value': 'Норма', 'unit': '', 'range': ''},
            {'name': 'Глюкоза крови', 'value': '5.2', 'unit': 'ммоль/л', 'range': '3.3-5.5'},
        ]
        
        for exam in completed_exams:
            for test in tests:
                LaboratoryResult.objects.get_or_create(
                    examination=exam,
                    test_name=test['name'],
                    defaults={
                        'result_value': test['value'],
                        'unit': test['unit'],
                        'reference_range': test['range'],
                        'is_normal': True
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ Создано результатов: {count}')

    def create_documents(self, employers, examinations):
        """Создание документов"""
        self.stdout.write('\n📄 Создание документов...')
        count = 0
        
        doc_types = [DocumentType.APPENDIX_3, DocumentType.CALENDAR_PLAN, DocumentType.FINAL_ACT]
        
        for employer in employers[:5]:
            for doc_type in doc_types:
                Document.objects.get_or_create(
                    organization=employer,
                    document_type=doc_type,
                    year=2025,
                    defaults={
                        'title': f'{doc_type} - {employer.name} (2025)',
                        'status': DocumentStatus.DRAFT,
                        'content': {'generated': True},
                        'created_by': employer.owner
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ Создано документов: {count}')

    def create_calendar_plans(self, employers, clinics):
        """Создание календарных планов"""
        self.stdout.write('\n📅 Создание календарных планов...')
        count = 0
        
        for employer in employers[:5]:
            clinic = clinics[count % len(clinics)]
            CalendarPlan.objects.get_or_create(
                employer=employer,
                year=2025,
                defaults={
                    'clinic': clinic,
                    'plan_data': {'months': {}}
                }
            )
            count += 1
        
        self.stdout.write(f'  ✓ Создано планов: {count}')

    def print_summary(self):
        """Вывод итоговой статистики"""
        self.stdout.write('\n📊 ИТОГОВАЯ СТАТИСТИКА:')
        self.stdout.write(f'  • Пользователи: {User.objects.count()}')
        self.stdout.write(f'  • Планы подписок: {SubscriptionPlan.objects.count()}')
        self.stdout.write(f'  • Подписки: {Subscription.objects.count()}')
        self.stdout.write(f'  • Работодатели: {Organization.objects.filter(org_type="employer").count()}')
        self.stdout.write(f'  • Клиники: {Organization.objects.filter(org_type="clinic").count()}')
        self.stdout.write(f'  • Сотрудники: {Employee.objects.count()}')
        self.stdout.write(f'  • Врачи: {OrganizationMember.objects.filter(role__in=["doctor", "profpathologist"]).count()}')
        self.stdout.write(f'  • Вредные факторы: {HarmfulFactor.objects.count()}')
        self.stdout.write(f'  • Профессии: {Profession.objects.count()}')
        self.stdout.write(f'  • Партнерства: {ClinicEmployerPartnership.objects.count()}')
        self.stdout.write(f'  • Осмотры: {MedicalExamination.objects.count()}')
        self.stdout.write(f'  • Результаты врачей: {DoctorExamination.objects.count()}')
        self.stdout.write(f'  • Лабораторные результаты: {LaboratoryResult.objects.count()}')
        self.stdout.write(f'  • Документы: {Document.objects.count()}')
        self.stdout.write(f'  • Календарные планы: {CalendarPlan.objects.count()}')
