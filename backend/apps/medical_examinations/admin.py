"""
Admin configuration for medical_examinations app
"""
from django.contrib import admin
from .models import (
    MedicalExamination,
    ExaminationRoute,
    DoctorExamination,
    LaboratoryResult
)


@admin.register(MedicalExamination)
class MedicalExaminationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'examination_type', 'status', 'result', 'scheduled_date', 'clinic']
    list_filter = ['examination_type', 'status', 'result', 'scheduled_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'qr_code']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']


@admin.register(ExaminationRoute)
class ExaminationRouteAdmin(admin.ModelAdmin):
    list_display = ['examination', 'doctors_count']
    filter_horizontal = ['doctors_required']
    
    def doctors_count(self, obj):
        return obj.doctors_required.count()
    doctors_count.short_description = 'Количество врачей'


@admin.register(DoctorExamination)
class DoctorExaminationAdmin(admin.ModelAdmin):
    list_display = ['examination', 'doctor', 'harmful_factor', 'result', 'examined_at']
    list_filter = ['result', 'examined_at']
    search_fields = ['examination__employee__first_name', 'doctor__user__phone_number']


@admin.register(LaboratoryResult)
class LaboratoryResultAdmin(admin.ModelAdmin):
    list_display = ['examination', 'test_name', 'result_value', 'is_normal', 'performed_at']
    list_filter = ['is_normal', 'performed_at']
    search_fields = ['test_name', 'test_code']

