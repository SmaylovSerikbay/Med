"""
Authentication services for WhatsApp OTP via Green-API
"""
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import requests
from .models import OTPCode


class GreenAPIService:
    """Service for interacting with Green-API"""
    
    @staticmethod
    def send_whatsapp_message(phone_number: str, message: str) -> dict:
        """
        Отправка сообщения через Green-API WhatsApp
        
        Args:
            phone_number: Номер телефона в формате 77001234567
            message: Текст сообщения
            
        Returns:
            dict: Ответ от API
        """
        url = f"{settings.GREEN_API_URL}/waInstance{settings.GREEN_API_ID_INSTANCE}/sendMessage/{settings.GREEN_API_TOKEN}"
        
        # Форматирование номера (убираем + и пробелы)
        formatted_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        
        payload = {
            "chatId": f"{formatted_phone}@c.us",
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Ошибка отправки WhatsApp сообщения: {str(e)}")


class OTPService:
    """Service for OTP code generation and validation"""
    
    @staticmethod
    def generate_code(length: int = None) -> str:
        """Генерация случайного OTP кода"""
        if length is None:
            length = settings.OTP_CODE_LENGTH
        
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        """Нормализация номера телефона"""
        # Убираем все нецифровые символы кроме +
        normalized = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        # Убираем + если есть
        normalized = normalized.replace('+', '')
        # Если начинается с 8, заменяем на 7
        if normalized.startswith('8'):
            normalized = '7' + normalized[1:]
        return normalized
    
    @staticmethod
    def create_otp(phone_number: str) -> OTPCode:
        """Создание OTP кода (без отправки)"""
        # Нормализуем номер телефона
        normalized_phone = OTPService.normalize_phone(phone_number)
        
        # Удаляем старые неиспользованные коды
        OTPCode.objects.filter(
            phone_number=normalized_phone,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Генерируем новый код
        code = OTPService.generate_code()
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        otp = OTPCode.objects.create(
            phone_number=normalized_phone,
            code=code,
            expires_at=expires_at
        )
        
        return otp
    
    @staticmethod
    def validate_otp(phone_number: str, code: str) -> tuple[bool, OTPCode | None]:
        """Проверка OTP кода
        
        Returns:
            tuple: (is_valid, otp_object)
        """
        # Нормализуем номер телефона
        normalized_phone = OTPService.normalize_phone(phone_number)
        
        try:
            otp = OTPCode.objects.get(
                phone_number=normalized_phone,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            otp.is_used = True
            otp.save()
            return True, otp
        except OTPCode.DoesNotExist:
            return False, None

