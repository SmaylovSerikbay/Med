"""
Authentication serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .services import OTPService
from .models import OTPCode

User = get_user_model()


class PhoneNumberSerializer(serializers.Serializer):
    """Serializer for phone number input"""
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Номер телефона в формате 77001234567"
    )


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=10)

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        code = attrs['code']
        
        if not OTPService.validate_otp(phone_number, code):
            raise serializers.ValidationError("Неверный или истекший код")
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'phone_verified', 'date_joined']
        read_only_fields = ['id', 'phone_verified', 'date_joined']

