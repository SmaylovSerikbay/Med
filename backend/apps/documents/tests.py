"""
Tests for documents app - Проверка логики Приказа 131
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from apps.organizations.models import Organization, Employee, ClinicEmployerPartnership
from apps.compliance.models import Profession, HarmfulFactor
from apps.medical_examinations.models import MedicalExamination
from .models import Document, DocumentType, CalendarPlan
from .services import DocumentService

User = get_user_model()


class DocumentGenerationTestCase(TestCase):
    """Тесты генерации документов согласно Приказу 131"""
    
    def setUp(self):
        # Тестовые номера
        self.clinic_phone = '77085446945'
        self.employer_phone = '77776875411'
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
        self.employee_user = User.objects.create_user(
            username=self.employee_phone,
            phone_number=self.employee_phone,
            phone_verified=True
        )
        
        # Создаем организации
        self.clinic = Organization.objects.create(
            name='Тестовая Клиника',
            org_type='clinic',
            owner=self.clinic_user,
            capacity_per_day=30
        )
        self.employer = Organization.objects.create(
            name='Тестовая Организация',
            org_type='employer',
            owner=self.employer_user
        )
        
        # Создаем партнерство
        self.partnership = ClinicEmployerPartnership.objects.create(
            clinic=self.clinic,
            employer=self.employer,
            status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE,
            requested_by=self.employer_user,
            confirmed_by=self.clinic_user,
            confirmed_at=timezone.now(),
            default_price=5000
        )
        
        # Создаем профессию и вредный фактор
        self.harmful_factor = HarmfulFactor.objects.create(
            code='1.1.1',
            name='Шум',
            periodicity_months=12,
            required_doctors=['ЛОР'],
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
            position=self.profession,
            department='Цех №1',
            hire_date=timezone.now().date() - timedelta(days=365)
        )
    
    def test_generate_appendix_3(self):
        """Тест генерации Приложения 3"""
        year = timezone.now().year
        doc = DocumentService.generate_appendix_3(self.employer, year)
        
        self.assertEqual(doc.document_type, DocumentType.APPENDIX_3)
        self.assertEqual(doc.organization, self.employer)
        self.assertEqual(doc.year, year)
        self.assertIn('employees', doc.content)
        self.assertGreaterEqual(len(doc.content['employees']), 0)
    
    def test_generate_calendar_plan_creates_examinations(self):
        """Тест: календарный план автоматически создает осмотры"""
        year = timezone.now().year
        
        # Сначала создаем Приложение 3
        appendix_3 = DocumentService.generate_appendix_3(self.employer, year)
        self.assertIsNotNone(appendix_3)
        
        # Создаем календарный план
        start_date = timezone.now() + timedelta(days=7)
        calendar_plan = DocumentService.generate_calendar_plan(
            employer=self.employer,
            clinic=self.clinic,
            year=year,
            start_date=start_date
        )
        
        self.assertIsNotNone(calendar_plan)
        
        # Проверяем, что осмотры созданы автоматически
        examinations_count = MedicalExamination.objects.filter(
            employer=self.employer,
            clinic=self.clinic,
            examination_type='periodic'
        ).count()
        
        self.assertGreater(examinations_count, 0, "Осмотры должны быть созданы автоматически")
    
    def test_final_act_generation(self):
        """Тест генерации заключительного акта"""
        year = timezone.now().year
        
        # Создаем завершенный осмотр
        examination = MedicalExamination.objects.create(
            examination_type='periodic',
            employee=self.employee,
            employer=self.employer,
            clinic=self.clinic,
            scheduled_date=timezone.now(),
            completed_date=timezone.now(),
            status='completed',
            result='fit'
        )
        
        # Генерируем акт
        act = DocumentService.generate_final_act(
            employer=self.employer,
            clinic=self.clinic,
            year=year
        )
        
        self.assertEqual(act.document_type, DocumentType.FINAL_ACT)
        self.assertEqual(act.organization, self.employer)
        self.assertIn('statistics', act.content)

