"""
Medical examination serializers
"""
from rest_framework import serializers
from .models import (
    MedicalExamination,
    ExaminationRoute,
    DoctorExamination,
    LaboratoryResult
)
from apps.organizations.serializers import EmployeeSerializer


class LaboratoryResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryResult
        fields = [
            'id', 'examination', 'test_name', 'test_code', 'result_value',
            'unit', 'reference_range', 'is_normal', 'performed_at'
        ]


class DoctorExaminationSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.phone_number', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    harmful_factor_name = serializers.CharField(source='harmful_factor.name', read_only=True)
    
    class Meta:
        model = DoctorExamination
        fields = [
            'id', 'examination', 'doctor', 'harmful_factor', 'result',
            'findings', 'recommendations', 'contraindications_found',
            'doctor_name', 'doctor_specialization', 'harmful_factor_name',
            'examined_at'
        ]


class ExaminationRouteSerializer(serializers.ModelSerializer):
    doctors_required_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ExaminationRoute
        fields = ['id', 'examination', 'doctors_required', 'doctors_required_info']
    
    def get_doctors_required_info(self, obj):
        result = []
        for doc in obj.doctors_required.all():
            # Формируем полное имя врача
            user = doc.user
            full_name_parts = []
            if user.last_name:
                full_name_parts.append(user.last_name)
            if user.first_name:
                full_name_parts.append(user.first_name)
            if user.email:  # Отчество временно хранится в email
                full_name_parts.append(user.email)
            
            full_name = ' '.join(full_name_parts) if full_name_parts else user.phone_number
            
            result.append({
                'id': doc.id,
                'specialization': doc.specialization or 'Врач',
                'full_name': full_name,
                'name': full_name,
                'phone': user.phone_number
            })
        return result


class MedicalExaminationSerializer(serializers.ModelSerializer):
    employee_info = EmployeeSerializer(source='employee', read_only=True)
    employer_name = serializers.CharField(source='employer.name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    route = ExaminationRouteSerializer(read_only=True)
    doctor_examinations = DoctorExaminationSerializer(many=True, read_only=True)
    laboratory_results = LaboratoryResultSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalExamination
        fields = [
            'id', 'examination_type', 'status', 'employee', 'employee_info',
            'employer', 'employer_name', 'clinic', 'clinic_name',
            'scheduled_date', 'completed_date', 'result', 'reason',
            'qr_code', 'route', 'doctor_examinations', 'laboratory_results',
            'progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'qr_code']
    
    def get_progress(self, obj):
        from .services import ExaminationService
        return ExaminationService.get_examination_progress(obj)


class MedicalExaminationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalExamination
        fields = [
            'examination_type', 'employee', 'clinic', 'scheduled_date', 'reason'
        ]

