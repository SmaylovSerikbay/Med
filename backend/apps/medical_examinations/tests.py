"""
Tests for medical examinations app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from apps.organizations.models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership
from apps.compliance.models import Profession, HarmfulFactor
from .models import MedicalExamination, ExaminationStatus, ExaminationResult
from .services import ExaminationService

User = get_user_model()


class MedicalExaminationTestCase(TestCase):
    """Тесты медицинских осмотров"""
    
    def setUp(self):
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
        
        # Создаем врача
        self.doctor = OrganizationMember.objects.create(
            organization=self.clinic,
            user=self.doctor_user,
            role='doctor',
            specialization='ЛОР'
        )
        
        # Создаем вредный фактор и профессию
        self.harmful_factor = HarmfulFactor.objects.create(
            code='1.1.1',
            name='Шум',
            periodicity_months=12,
            required_doctors=['ЛОР']
        )
        self.profession = Profession.objects.create(name='Электросварщик')
        self.profession.harmful_factors.add(self.harmful_factor)
        
        # Создаем сотрудника
        self.employee = Employee.objects.create(
            user=self.employee_user,
            employer=self.employer,
            first_name='Иван',
            last_name='Иванов',
            position=self.profession,
            hire_date=timezone.now().date() - timedelta(days=365)
        )
    
    def test_create_examination_with_route(self):
        """Тест создания осмотра с маршрутным листом"""
        scheduled_date = timezone.now() + timedelta(days=7)
        
        examination = ExaminationService.create_examination(
            employee=self.employee,
            examination_type='periodic',
            clinic=self.clinic,
            scheduled_date=scheduled_date,
            employer=self.employer
        )
        
        self.assertIsNotNone(examination)
        self.assertEqual(examination.status, 'scheduled')
        self.assertIsNotNone(examination.qr_code)
        self.assertIsNotNone(examination.route)
    
    def test_complete_examination_generates_certificate(self):
        """Тест: завершение осмотра автоматически генерирует справку 075/у"""
        from apps.documents.models import Document, DocumentType
        
        examination = ExaminationService.create_examination(
            employee=self.employee,
            examination_type='periodic',
            clinic=self.clinic,
            scheduled_date=timezone.now() + timedelta(days=7),
            employer=self.employer
        )
        
        # Используем врача как профпатолога (в тестах это допустимо)
        # В реальной системе профпатолог должен быть отдельным участником
        profpathologist = self.doctor
        
        # Завершаем осмотр
        completed = ExaminationService.complete_examination(
            examination=examination,
            final_result='fit',
            profpathologist=profpathologist
        )
        
        self.assertEqual(completed.status, 'completed')
        self.assertEqual(completed.result, 'fit')
        
        # Проверяем, что справка создана
        certificates = Document.objects.filter(
            examination=examination,
            document_type=DocumentType.MEDICAL_CERTIFICATE
        )
        self.assertGreater(certificates.count(), 0, "Справка 075/у должна быть создана автоматически")

