"""
Admin configuration for documents app
"""
from django.contrib import admin
from .models import Document, DocumentSignature, CalendarPlan


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'status', 'organization', 'year', 'created_at']
    list_filter = ['document_type', 'status', 'year', 'created_at']
    search_fields = ['title', 'organization__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    list_display = ['document', 'signer', 'role', 'otp_verified', 'signed_at']
    list_filter = ['role', 'otp_verified', 'signed_at']
    search_fields = ['document__title', 'signer__phone_number']
    readonly_fields = ['otp_sent_at', 'signed_at']


@admin.register(CalendarPlan)
class CalendarPlanAdmin(admin.ModelAdmin):
    list_display = ['employer', 'clinic', 'year', 'created_at']
    list_filter = ['year', 'created_at']
    search_fields = ['employer__name', 'clinic__name']

