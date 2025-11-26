#!/usr/bin/env python
"""
Скрипт для реального API-тестирования полного цикла через HTTP запросы
Проверяет работу всех endpoints через реальные HTTP запросы
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone

API_URL = 'http://localhost:8000/api'

# Тестовые данные
TEST_PHONES = {
    'clinic': '77085446945',
    'employer': '77776875411',
    'doctor': '77021491010',
    'employee': '77789171790'
}


class APITester:
    def __init__(self):
        self.tokens = {}
        self.organizations = {}
        self.documents = {}
        
    def send_otp(self, phone):
        """Отправка OTP"""
        response = requests.post(
            f'{API_URL}/auth/send-otp/',
            json={'phone_number': phone}
        )
        return response.json()
    
    def verify_otp(self, phone, code='123456'):  # В тестах используем фиксированный код
        """Верификация OTP и получение токена"""
        response = requests.post(
            f'{API_URL}/auth/verify-otp/',
            json={'phone_number': phone, 'code': code}
        )
        if response.status_code == 200:
            data = response.json()
            self.tokens[phone] = data.get('access_token')
            return data
        return None
    
    def get_auth_headers(self, phone):
        """Получить заголовки с токеном"""
        token = self.tokens.get(phone)
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def get_profile(self, phone):
        """Получить профиль пользователя"""
        response = requests.get(
            f'{API_URL}/auth/profile/',
            headers=self.get_auth_headers(phone)
        )
        return response.json() if response.status_code == 200 else None
    
    def get_organizations(self, phone):
        """Получить организации пользователя"""
        response = requests.get(
            f'{API_URL}/organizations/organizations/',
            headers=self.get_auth_headers(phone)
        )
        if response.status_code == 200:
            data = response.json()
            orgs = data.get('results', data) if isinstance(data, dict) else data
            self.organizations[phone] = orgs
            return orgs
        return []
    
    def test_partnership_flow(self):
        """Тест потока партнерства"""
        print("\n" + "="*70)
        print("ТЕСТ: Партнерство клиники и работодателя")
        print("="*70)
        
        # 1. Работодатель запрашивает партнерство
        print("\n1. Работодатель запрашивает партнерство...")
        employer_orgs = self.organizations.get(TEST_PHONES['employer'], [])
        clinic_orgs = self.organizations.get(TEST_PHONES['clinic'], [])
        
        if employer_orgs and clinic_orgs:
            employer_id = next((o['id'] for o in employer_orgs if o['org_type'] == 'employer'), None)
            clinic_id = next((o['id'] for o in clinic_orgs if o['org_type'] == 'clinic'), None)
            
            if employer_id and clinic_id:
                response = requests.post(
                    f'{API_URL}/organizations/partnerships/request_partnership/',
                    headers=self.get_auth_headers(TEST_PHONES['employer']),
                    json={
                        'employer_id': employer_id,
                        'clinic_id': clinic_id,
                        'default_price': 5000
                    }
                )
                if response.status_code in [200, 201]:
                    print(f"  ✅ Запрос на партнерство отправлен")
                else:
                    print(f"  ℹ️  {response.json().get('error', 'Партнерство уже существует')}")
        
        # 2. Клиника подтверждает
        print("\n2. Клиника подтверждает партнерство...")
        response = requests.get(
            f'{API_URL}/organizations/partnerships/',
            headers=self.get_auth_headers(TEST_PHONES['clinic'])
        )
        if response.status_code == 200:
            partnerships = response.json().get('results', response.json())
            pending = [p for p in partnerships if p.get('status') == 'pending']
            if pending:
                partnership_id = pending[0]['id']
                confirm_response = requests.post(
                    f'{API_URL}/organizations/partnerships/{partnership_id}/confirm/',
                    headers=self.get_auth_headers(TEST_PHONES['clinic']),
                    json={'default_price': 5000}
                )
                if confirm_response.status_code == 200:
                    print(f"  ✅ Партнерство подтверждено")
        
        return True
    
    def test_document_generation_flow(self):
        """Тест генерации документов"""
        print("\n" + "="*70)
        print("ТЕСТ: Генерация документов согласно Приказу 131")
        print("="*70)
        
        clinic_orgs = self.organizations.get(TEST_PHONES['clinic'], [])
        employer_orgs = self.organizations.get(TEST_PHONES['employer'], [])
        
        if not clinic_orgs or not employer_orgs:
            print("  ❌ Организации не найдены")
            return False
        
        employer_id = next((o['id'] for o in employer_orgs if o['org_type'] == 'employer'), None)
        clinic_id = next((o['id'] for o in clinic_orgs if o['org_type'] == 'clinic'), None)
        
        if not employer_id or not clinic_id:
            print("  ❌ ID организаций не найдены")
            return False
        
        year = timezone.now().year
        
        # 1. Генерация Приложения 3
        print("\n1. Генерация Приложения 3...")
        response = requests.post(
            f'{API_URL}/documents/documents/generate_appendix_3/',
            headers=self.get_auth_headers(TEST_PHONES['clinic']),
            json={'employer_id': employer_id, 'year': year}
        )
        if response.status_code == 200:
            doc = response.json()
            self.documents['appendix_3'] = doc
            print(f"  ✅ Приложение 3 создано: {doc.get('title')}")
        else:
            print(f"  ❌ Ошибка: {response.json().get('error', 'Неизвестная ошибка')}")
            return False
        
        # 2. Генерация Календарного плана
        print("\n2. Генерация Календарного плана...")
        start_date = (timezone.now() + timedelta(days=7)).isoformat()
        response = requests.post(
            f'{API_URL}/documents/documents/generate_calendar_plan/',
            headers=self.get_auth_headers(TEST_PHONES['clinic']),
            json={
                'employer_id': employer_id,
                'clinic_id': clinic_id,
                'year': year,
                'start_date': start_date
            }
        )
        if response.status_code == 200:
            plan = response.json()
            self.documents['calendar_plan'] = plan
            print(f"  ✅ Календарный план создан")
            
            # Проверяем созданные осмотры
            exams_response = requests.get(
                f'{API_URL}/examinations/examinations/',
                headers=self.get_auth_headers(TEST_PHONES['employer'])
            )
            if exams_response.status_code == 200:
                exams = exams_response.json().get('results', exams_response.json())
                print(f"  ✅ Создано осмотров: {len(exams)}")
                if exams:
                    print(f"  ✅ QR-код первого осмотра: {exams[0].get('qr_code')}")
        else:
            print(f"  ❌ Ошибка: {response.json().get('error', 'Неизвестная ошибка')}")
            return False
        
        return True
    
    def test_examinations_flow(self):
        """Тест потока осмотров"""
        print("\n" + "="*70)
        print("ТЕСТ: Проведение осмотров")
        print("="*70)
        
        # Получаем осмотры
        response = requests.get(
            f'{API_URL}/examinations/examinations/',
            headers=self.get_auth_headers(TEST_PHONES['clinic'])
        )
        if response.status_code != 200:
            print("  ❌ Не удалось получить осмотры")
            return False
        
        exams = response.json().get('results', response.json())
        if not exams:
            print("  ℹ️  Нет осмотров для проведения")
            return True
        
        exam = exams[0]
        exam_id = exam['id']
        
        # Начало осмотра
        print(f"\n1. Начало осмотра (ID: {exam_id})...")
        response = requests.post(
            f'{API_URL}/examinations/examinations/{exam_id}/start/',
            headers=self.get_auth_headers(TEST_PHONES['clinic'])
        )
        if response.status_code == 200:
            print("  ✅ Осмотр начат")
        
        # Получаем врача и вредный фактор
        orgs_response = requests.get(
            f'{API_URL}/organizations/organizations/{exam["clinic"]}/members/',
            headers=self.get_auth_headers(TEST_PHONES['clinic'])
        )
        if orgs_response.status_code == 200:
            members = orgs_response.json()
            doctor = next((m for m in members if m.get('role') == 'doctor'), None)
            
            if doctor:
                # Получаем вредные факторы
                factors_response = requests.get(
                    f'{API_URL}/compliance/factors/',
                    headers=self.get_auth_headers(TEST_PHONES['clinic'])
                )
                if factors_response.status_code == 200:
                    factors = factors_response.json().get('results', factors_response.json())
                    if factors:
                        factor_id = factors[0]['id']
                        
                        # Добавляем результат осмотра
                        print("\n2. Добавление результата осмотра врача...")
                        response = requests.post(
                            f'{API_URL}/examinations/examinations/{exam_id}/add_doctor_examination/',
                            headers=self.get_auth_headers(TEST_PHONES['clinic']),
                            json={
                                'doctor_id': doctor['id'],
                                'harmful_factor_id': factor_id,
                                'result': 'fit',
                                'findings': 'Органы слуха в норме',
                                'recommendations': 'Продолжить работу'
                            }
                        )
                        if response.status_code == 200:
                            print("  ✅ Результат осмотра добавлен")
        
        # Завершение осмотра профпатологом
        profpathologist = next((m for m in members if m.get('role') == 'profpathologist'), None) if 'members' in locals() else None
        if not profpathologist:
            profpathologist = doctor  # Используем врача как профпатолога
        
        if profpathologist:
            print("\n3. Завершение осмотра профпатологом...")
            response = requests.post(
                f'{API_URL}/examinations/examinations/{exam_id}/complete/',
                headers=self.get_auth_headers(TEST_PHONES['clinic']),
                json={
                    'result': 'fit',
                    'profpathologist_id': profpathologist['id']
                }
            )
            if response.status_code == 200:
                print("  ✅ Осмотр завершен")
                
                # Проверяем справку 075/у
                docs_response = requests.get(
                    f'{API_URL}/documents/documents/',
                    headers=self.get_auth_headers(TEST_PHONES['employer'])
                )
                if docs_response.status_code == 200:
                    docs = docs_response.json().get('results', docs_response.json())
                    certificates = [d for d in docs if d.get('document_type') == 'medical_certificate']
                    if certificates:
                        print(f"  ✅ Справка 075/у создана автоматически")
        
        return True
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("="*70)
        print("API ТЕСТИРОВАНИЕ ПОЛНОГО ЦИКЛА ProfMed.kz")
        print("="*70)
        print("\n⚠️  ВНИМАНИЕ: Для работы тестов нужны токены доступа.")
        print("   Сначала нужно авторизоваться через UI или использовать фиксированные OTP коды.")
        print("\n" + "="*70)
        
        # Получаем профили и организации для всех пользователей
        for phone_type, phone in TEST_PHONES.items():
            print(f"\n{phone_type.upper()}: {phone}")
            profile = self.get_profile(phone)
            if profile:
                print(f"  ✅ Профиль получен")
                orgs = self.get_organizations(phone)
                print(f"  ✅ Организаций: {len(orgs)}")
            else:
                print(f"  ⚠️  Профиль не получен (нужна авторизация)")
        
        # Тесты потоков
        self.test_partnership_flow()
        self.test_document_generation_flow()
        self.test_examinations_flow()
        
        print("\n" + "="*70)
        print("✅ API ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*70)
        print("\nДля полного тестирования:")
        print("1. Авторизуйтесь через UI с тестовыми номерами")
        print("2. Проверьте работу партнерств")
        print("3. Сгенерируйте документы")
        print("4. Проведите осмотры")


if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()

