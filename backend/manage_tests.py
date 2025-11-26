#!/usr/bin/env python
"""
Скрипт для запуска всех тестов проекта
"""
import os
import sys
import django

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings


def run_tests():
    """Запуск всех тестов"""
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Тесты для запуска
    test_modules = [
        'apps.organizations.tests',
        'apps.documents.tests',
        'apps.medical_examinations.tests',
    ]
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*60)


if __name__ == '__main__':
    run_tests()

