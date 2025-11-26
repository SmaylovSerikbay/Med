"""
Authentication models for ProfMed.kz
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for phone number authentication"""
    
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Номер телефона обязателен')
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('phone_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with phone number authentication"""
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=False,
        verbose_name='Username'
    )
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name='Номер телефона'
    )
    phone_verified = models.BooleanField(
        default=False,
        verbose_name='Телефон подтвержден'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # Убираем уникальность username, так как используем phone_number
        constraints = [
            models.UniqueConstraint(fields=['phone_number'], name='unique_phone_number')
        ]

    def __str__(self):
        return self.phone_number
    
    def save(self, *args, **kwargs):
        # Автоматически генерируем username из phone_number если не указан
        if not self.username:
            self.username = f"user_{self.phone_number}"
        super().save(*args, **kwargs)


class OTPCode(models.Model):
    """OTP codes for WhatsApp authentication"""
    phone_number = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'OTP код'
        verbose_name_plural = 'OTP коды'
        indexes = [
            models.Index(fields=['phone_number', 'code', 'is_used']),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

