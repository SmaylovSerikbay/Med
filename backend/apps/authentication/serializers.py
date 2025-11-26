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
    has_password = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'phone_verified', 'date_joined', 'has_password']
        read_only_fields = ['id', 'phone_verified', 'date_joined', 'has_password']
    
    def get_has_password(self, obj):
        return obj.has_usable_password()


class PasswordLoginSerializer(serializers.Serializer):
    """Serializer for password login"""
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)


class SetPasswordSerializer(serializers.Serializer):
    """Serializer for setting password"""
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, min_length=6)


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    phone_number = serializers.CharField(max_length=20)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True, min_length=6)

