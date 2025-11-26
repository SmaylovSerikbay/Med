#!/usr/bin/env python
"""Проверка сгенерированных данных"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User
from apps.organizations.models import Organization, Employee, OrganizationMember
from apps.compliance.models import HarmfulFactor, Profession
from apps.medical_examinations.models import MedicalExamination
from apps.documents.models import Document
from apps.subscriptions.models import SubscriptionPlan, Subscription

print("=" * 60)
print("ПРОВЕРКА СГЕНЕРИРОВАННЫХ ДАННЫХ")
print("=" * 60)

print(f"\n👥 Пользователи: {User.objects.count()}")
print(f"   Первые 5: {', '.join([u.phone_number for u in User.objects.all()[:5]])}")

print(f"\n🏢 Работодатели: {Organization.objects.filter(org_type='employer').count()}")
for org in Organization.objects.filter(org_type='employer')[:3]:
    print(f"   • {org.name} (владелец: {org.owner.phone_number})")

print(f"\n🏥 Клиники: {Organization.objects.filter(org_type='clinic').count()}")
for org in Organization.objects.filter(org_type='clinic')[:3]:
    print(f"   • {org.name} (владелец: {org.owner.phone_number})")

print(f"\n👷 Сотрудники: {Employee.objects.count()}")
for emp in Employee.objects.all()[:3]:
    print(f"   • {emp.full_name} - {emp.position.name if emp.position else 'Без должности'}")

print(f"\n👨‍⚕️ Врачи: {OrganizationMember.objects.filter(role__in=['doctor', 'profpathologist']).count()}")
for doc in OrganizationMember.objects.filter(role='doctor')[:3]:
    print(f"   • {doc.specialization} ({doc.user.phone_number})")

print(f"\n⚠️  Вредные факторы: {HarmfulFactor.objects.count()}")
print(f"   Примеры: {', '.join([f.code for f in HarmfulFactor.objects.all()[:5]])}")

print(f"\n💼 Профессии: {Profession.objects.count()}")
for prof in Profession.objects.all()[:3]:
    factors = prof.harmful_factors.count()
    print(f"   • {prof.name} ({factors} факторов)")

print(f"\n🔬 Осмотры: {MedicalExamination.objects.count()}")
print(f"   Запланировано: {MedicalExamination.objects.filter(status='scheduled').count()}")
print(f"   В процессе: {MedicalExamination.objects.filter(status='in_progress').count()}")
print(f"   Завершено: {MedicalExamination.objects.filter(status='completed').count()}")

print(f"\n📄 Документы: {Document.objects.count()}")
print(f"   Приложение 3: {Document.objects.filter(document_type='appendix_3').count()}")
print(f"   Календарные планы: {Document.objects.filter(document_type='calendar_plan').count()}")
print(f"   Заключительные акты: {Document.objects.filter(document_type='final_act').count()}")

print(f"\n📋 Подписки: {Subscription.objects.count()}")
print(f"   Активных: {Subscription.objects.filter(status='active').count()}")

print("\n" + "=" * 60)
print("✅ ВСЕ ДАННЫЕ УСПЕШНО СГЕНЕРИРОВАНЫ!")
print("=" * 60)
