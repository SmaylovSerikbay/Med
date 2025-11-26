"""
Интеграционные тесты полного цикла согласно Приказу 131
Использует реальные номера телефонов для тестирования
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from apps.organizations.models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership
from apps.compliance.models import Profession, HarmfulFactor
from apps.medical_examinations.models import MedicalExamination, ExaminationStatus, ExaminationResult, DoctorExamination
from apps.documents.models import Document, DocumentType, CalendarPlan
from apps.documents.services import DocumentService
from apps.medical_examinations.services import ExaminationService

User = get_user_model()


class FullWorkflowTestCase(TransactionTestCase):
    """
    Полный интеграционный тест всего цикла согласно Приказу 131
    Использует реальные тестовые номера:
    - Клиника: 77085446945
    - Работодатель: 77776875411
    - Врач: 77021491010
    - Сотрудник: 77789171790
    """
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Тестовые номера
        self.clinic_phone = '77085446945'
        self.employer_phone = '77776875411'
        self.doctor_phone = '77021491010'
        self.employee_phone = '77789171790'
        
        # Создаем пользователей
        self.clinic_user = User.objects.create_user(
            username=self.clinic_phone,
            phone_number=self.clinic_phone,
            phone_verified=True
        )
        self.employer_user = User.objects.create_user(
            username=self.employer_phone,
            phone_number=self.employer_phone,
            phone_verified=True
        )
        self.doctor_user = User.objects.create_user(
            username=self.doctor_phone,
            phone_number=self.doctor_phone,
            phone_verified=True
        )
        self.employee_user = User.objects.create_user(
            username=self.employee_phone,
            phone_number=self.employee_phone,
            phone_verified=True
        )
        
        # Создаем организации
        self.clinic = Organization.objects.create(
            name='Тестовая Клиника МедПро',
            org_type='clinic',
            owner=self.clinic_user,
            capacity_per_day=30,
            address='г. Алматы, ул. Тестовая, 1',
            phone='+7 (727) 123-45-67'
        )
        self.employer = Organization.objects.create(
            name='Тестовая Организация Производство',
            org_type='employer',
            owner=self.employer_user,
            address='г. Алматы, ул. Промышленная, 10'
        )
        
        # Создаем партнерство (ЭТАП 1: Запрос и подтверждение партнерства)
        self.partnership = ClinicEmployerPartnership.objects.create(
            clinic=self.clinic,
            employer=self.employer,
            status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE,
            requested_by=self.employer_user,
            confirmed_by=self.clinic_user,
            confirmed_at=timezone.now(),
            default_price=5000
        )
        
        # Создаем вредный фактор и профессию
        self.harmful_factor = HarmfulFactor.objects.create(
            code='1.1.1',
            name='Шум производственный',
            periodicity_months=12,
            required_doctors=['ЛОР', 'Невролог'],
            required_tests=['Аудиометрия']
        )
        self.profession = Profession.objects.create(name='Электросварщик')
        self.profession.harmful_factors.add(self.harmful_factor)
        
        # Создаем сотрудника
        self.employee = Employee.objects.create(
            user=self.employee_user,
            employer=self.employer,
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            iin='123456789012',
            position=self.profession,
            department='Цех №1',
            hire_date=timezone.now().date() - timedelta(days=400)
        )
        
        # Создаем врача в клинике (который также может быть профпатологом)
        # Используем get_or_create для избежания конфликтов
        self.doctor, _ = OrganizationMember.objects.get_or_create(
            organization=self.clinic,
            user=self.doctor_user,
            defaults={
                'role': 'doctor',
                'specialization': 'ЛОР',
                'license_number': 'DOC-12345'
            }
        )
        # Профпатолог может быть тот же пользователь, но с другой ролью
        # Из-за unique_together (organization, user) используем врача как профпатолога
        # В реальной системе профпатолог должен быть отдельным участником, но для тестов используем врача
        self.profpathologist = self.doctor  # Используем врача как профпатолога
    
    def test_full_workflow_order_131(self):
        """
        Полный тест всего цикла согласно Приказу 131:
        1. Генерация Приложения 3 (список лиц)
        2. Генерация Календарного плана
        3. Автоматическое создание осмотров
        4. Отправка уведомлений с QR-кодами
        5. Проведение осмотра
        6. Генерация справки 075/у
        7. Генерация Заключительного акта
        """
        year = timezone.now().year
        
        # ЭТАП 1: Генерация Приложения 3
        print("\n=== ЭТАП 1: Генерация Приложения 3 ===")
        appendix_3 = DocumentService.generate_appendix_3(self.employer, year)
        self.assertEqual(appendix_3.document_type, DocumentType.APPENDIX_3)
        self.assertGreaterEqual(len(appendix_3.content['employees']), 1)
        print(f"✅ Приложение 3 создано: {len(appendix_3.content['employees'])} сотрудников")
        
        # ЭТАП 2: Генерация Календарного плана
        print("\n=== ЭТАП 2: Генерация Календарного плана ===")
        start_date = timezone.now() + timedelta(days=7)
        calendar_plan = DocumentService.generate_calendar_plan(
            employer=self.employer,
            clinic=self.clinic,
            year=year,
            start_date=start_date
        )
        self.assertIsNotNone(calendar_plan)
        print(f"✅ Календарный план создан")
        
        # ЭТАП 3: Проверка автоматического создания осмотров
        print("\n=== ЭТАП 3: Проверка создания осмотров ===")
        examinations = MedicalExamination.objects.filter(
            employer=self.employer,
            clinic=self.clinic,
            examination_type='periodic'
        )
        self.assertGreater(examinations.count(), 0, "Осмотры должны быть созданы автоматически")
        print(f"✅ Создано осмотров: {examinations.count()}")
        
        examination = examinations.first()
        self.assertIsNotNone(examination.qr_code)
        print(f"✅ QR-код создан: {examination.qr_code}")
        
        # ЭТАП 4: Проведение осмотра
        print("\n=== ЭТАП 4: Проведение осмотра ===")
        examination = ExaminationService.start_examination(examination)
        self.assertEqual(examination.status, 'in_progress')
        
        # Добавляем результаты осмотра врача
        doctor_exam = ExaminationService.add_doctor_examination(
            examination=examination,
            doctor=self.doctor,
            harmful_factor=self.harmful_factor,
            result='fit',
            findings='Органы слуха в норме',
            recommendations='Продолжить работу'
        )
        self.assertIsNotNone(doctor_exam)
        print(f"✅ Осмотр врача добавлен")
        
        # Завершаем осмотр профпатологом
        completed = ExaminationService.complete_examination(
            examination=examination,
            final_result='fit',
            profpathologist=self.profpathologist
        )
        self.assertEqual(completed.status, 'completed')
        self.assertEqual(completed.result, 'fit')
        print(f"✅ Осмотр завершен")
        
        # ЭТАП 5: Проверка генерации справки 075/у
        print("\n=== ЭТАП 5: Проверка справки 075/у ===")
        certificates = Document.objects.filter(
            examination=examination,
            document_type=DocumentType.MEDICAL_CERTIFICATE
        )
        self.assertGreater(certificates.count(), 0, "Справка 075/у должна быть создана автоматически")
        print(f"✅ Справка 075/у создана автоматически")
        
        # ЭТАП 6: Генерация Заключительного акта
        print("\n=== ЭТАП 6: Генерация Заключительного акта ===")
        final_act = DocumentService.generate_final_act(
            employer=self.employer,
            clinic=self.clinic,
            year=year
        )
        self.assertEqual(final_act.document_type, DocumentType.FINAL_ACT)
        self.assertIn('statistics', final_act.content)
        print(f"✅ Заключительный акт создан")
        print(f"   Статистика: {final_act.content['statistics']}")
        
        print("\n✅✅✅ ВСЕ ЭТАПЫ ПРОЙДЕНЫ УСПЕШНО! ✅✅✅")

