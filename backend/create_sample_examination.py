#!/usr/bin/env python
"""
Создание тестового осмотра для проверки
"""
import os
import sys
import django
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Organization, Employee, OrganizationMember
from apps.medical_examinations.models import MedicalExamination
from apps.medical_examinations.services import ExaminationService

User = get_user_model()

# Получаем тестовые данные
clinic_user = User.objects.filter(phone_number='77085446945').first()
employer_user = User.objects.filter(phone_number='77776875411').first()
employee_user = User.objects.filter(phone_number='77789171790').first()

if clinic_user and employer_user and employee_user:
    clinic = Organization.objects.filter(owner=clinic_user, org_type='clinic').first()
    employer = Organization.objects.filter(owner=employer_user, org_type='employer').first()
    employee = Employee.objects.filter(user=employee_user).first()
    
    if clinic and employer and employee:
        # Создаем тестовый осмотр
        scheduled_date = timezone.now() + timedelta(days=7)
        
        examination = ExaminationService.create_examination(
            employee=employee,
            examination_type='periodic',
            clinic=clinic,
            scheduled_date=scheduled_date,
            employer=employer
        )
        
        print(f"✅ Осмотр создан!")
        print(f"   Сотрудник: {employee.full_name}")
        print(f"   Клиника: {clinic.name}")
        print(f"   Дата: {scheduled_date.strftime('%d.%m.%Y %H:%M')}")
        print(f"   QR-код: {examination.qr_code}")
        print(f"   Статус: {examination.get_status_display()}")
    else:
        print("❌ Не найдены организации или сотрудник")
        print(f"   Клиника: {clinic}")
        print(f"   Работодатель: {employer}")
        print(f"   Сотрудник: {employee}")
else:
    print("❌ Не найдены пользователи")

