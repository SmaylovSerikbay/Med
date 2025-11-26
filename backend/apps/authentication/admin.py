"""
Admin configuration for authentication app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone_number', 'phone_verified', 'date_joined', 'is_staff']
    list_filter = ['phone_verified', 'is_staff', 'date_joined']
    search_fields = ['phone_number']
    ordering = ['-date_joined']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'code', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['phone_number']
    readonly_fields = ['created_at', 'expires_at']

