"""
Tests for organizations app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership
from apps.compliance.models import Profession, HarmfulFactor

User = get_user_model()


class ClinicEmployerPartnershipTestCase(TestCase):
    """Тесты для партнерств клиник и работодателей"""
    
    def setUp(self):
        # Тестовые номера телефонов
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
    
    def test_create_partnership_request(self):
        """Тест создания запроса на партнерство"""
        partnership = ClinicEmployerPartnership.objects.create(
            clinic=self.clinic,
            employer=self.employer,
            status=ClinicEmployerPartnership.PartnershipStatus.PENDING,
            requested_by=self.employer_user,
            default_price=5000
        )
        
        self.assertEqual(partnership.status, ClinicEmployerPartnership.PartnershipStatus.PENDING)
        self.assertFalse(partnership.is_active())
    
    def test_confirm_partnership(self):
        """Тест подтверждения партнерства"""
        partnership = ClinicEmployerPartnership.objects.create(
            clinic=self.clinic,
            employer=self.employer,
            status=ClinicEmployerPartnership.PartnershipStatus.PENDING,
            requested_by=self.employer_user,
            default_price=5000
        )
        
        partnership.status = ClinicEmployerPartnership.PartnershipStatus.ACTIVE
        partnership.confirmed_by = self.clinic_user
        partnership.confirmed_at = timezone.now()
        partnership.save()
        
        self.assertTrue(partnership.is_active())
        self.assertEqual(partnership.confirmed_by, self.clinic_user)
    
    def test_public_clinic(self):
        """Тест публичной клиники"""
        partnership = ClinicEmployerPartnership.objects.create(
            clinic=self.clinic,
            employer=self.employer,
            status=ClinicEmployerPartnership.PartnershipStatus.ACTIVE,
            is_public=True,
            requested_by=self.employer_user,
            confirmed_by=self.clinic_user,
            default_price=5000
        )
        
        self.assertTrue(partnership.is_public)

