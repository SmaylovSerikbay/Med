"""
Document serializers
"""
from rest_framework import serializers
from .models import Document, DocumentSignature, CalendarPlan


class DocumentSignatureSerializer(serializers.ModelSerializer):
    signer_phone = serializers.CharField(source='signer.phone_number', read_only=True)
    
    class Meta:
        model = DocumentSignature
        fields = [
            'id', 'document', 'signer', 'role', 'signed_at',
            'signer_phone', 'otp_verified'
        ]
        read_only_fields = ['signed_at', 'otp_verified']


class DocumentSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    signatures = DocumentSignatureSerializer(many=True, read_only=True)
    created_by_phone = serializers.CharField(source='created_by.phone_number', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'document_type', 'status', 'title', 'content',
            'file_path', 'organization', 'organization_name',
            'examination', 'year', 'created_by', 'created_by_phone',
            'signatures', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CalendarPlanSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    document_id = serializers.IntegerField(source='document.id', read_only=True)
    
    class Meta:
        model = CalendarPlan
        fields = [
            'id', 'employer', 'employer_name', 'clinic', 'clinic_name',
            'year', 'plan_data', 'document', 'document_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

