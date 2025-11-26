#!/usr/bin/env python
"""
Быстрая проверка наличия тестовых данных в базе
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership
from django.contrib.auth import get_user_model

User = get_user_model()

TEST_PHONES = {
    'clinic': '77085446945',
    'employer': '77776875411',
    'doctor': '77021491010',
    'employee': '77789171790'
}

print("="*70)
print("ПРОВЕРКА ТЕСТОВЫХ ДАННЫХ")
print("="*70)

# Проверка пользователей
print("\n1. Пользователи:")
for name, phone in TEST_PHONES.items():
    user = User.objects.filter(phone_number=phone).first()
    if user:
        print(f"  ✅ {name}: {phone} - существует")
    else:
        print(f"  ❌ {name}: {phone} - НЕ НАЙДЕН")

# Проверка организаций
print("\n2. Организации:")
clinic_user = User.objects.filter(phone_number=TEST_PHONES['clinic']).first()
employer_user = User.objects.filter(phone_number=TEST_PHONES['employer']).first()

if clinic_user:
    clinics = Organization.objects.filter(owner=clinic_user, org_type='clinic')
    print(f"  Клиник для {TEST_PHONES['clinic']}: {clinics.count()}")
    for c in clinics:
        print(f"    - {c.name} (ID: {c.id})")

if employer_user:
    employers = Organization.objects.filter(owner=employer_user, org_type='employer')
    print(f"  Работодателей для {TEST_PHONES['employer']}: {employers.count()}")
    for e in employers:
        print(f"    - {e.name} (ID: {e.id})")

# Проверка партнерств
print("\n3. Партнерства:")
partnerships = ClinicEmployerPartnership.objects.filter(status='active')
print(f"  Активных партнерств: {partnerships.count()}")
for p in partnerships:
    print(f"    - {p.clinic.name} ↔ {p.employer.name} (Статус: {p.get_status_display()})")

# Проверка сотрудников
print("\n4. Сотрудники:")
employees = Employee.objects.filter(is_active=True)
print(f"  Активных сотрудников: {employees.count()}")
for emp in employees[:5]:  # Показываем первые 5
    print(f"    - {emp.full_name} ({emp.employer.name})")

# Проверка врачей
print("\n5. Врачи:")
doctors = OrganizationMember.objects.filter(role__in=['doctor', 'profpathologist'], is_active=True)
print(f"  Врачей и профпатологов: {doctors.count()}")
for doc in doctors:
    print(f"    - {doc.get_role_display()} ({doc.specialization or 'Без специализации'}) в {doc.organization.name}")

print("\n" + "="*70)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("="*70)

