#!/usr/bin/env python
"""
Скрипт для запуска всех тестов проекта с подробным выводом
Использует тестовые номера:
- Клиника: 77085446945
- Работодатель: 77776875411
- Врач: 77021491010
- Сотрудник: 77789171790
"""
import os
import sys
import django

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
except Exception as e:
    print(f"Ошибка инициализации Django: {e}")
    print("Убедитесь, что все зависимости установлены и настройки корректны")
    sys.exit(1)

from django.test.utils import get_runner
from django.conf import settings


def main():
    """Запуск всех тестов"""
    print("="*70)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ ProfMed.kz")
    print("Согласно Приказу 131")
    print("="*70)
    print("\nТестовые номера:")
    print("  - Клиника: 77085446945")
    print("  - Работодатель: 77776875411")
    print("  - Врач: 77021491010")
    print("  - Сотрудник: 77789171790")
    print("\n" + "="*70 + "\n")
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=2,
        interactive=False,
        keepdb=False,
        failfast=False
    )
    
    # Тесты для запуска
    test_modules = [
        'apps.organizations.tests.ClinicEmployerPartnershipTestCase',
        'apps.documents.tests.DocumentGenerationTestCase',
        'apps.medical_examinations.tests.MedicalExaminationTestCase',
        'apps.integration_tests.FullWorkflowTestCase',
    ]
    
    print("Запуск тестов...\n")
    failures = test_runner.run_tests(test_modules)
    
    print("\n" + "="*70)
    if failures:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("="*70)
        sys.exit(1)
    else:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*70)
        sys.exit(0)


if __name__ == '__main__':
    main()

