"""
Medical examination views
"""
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MedicalExamination, DoctorExamination, LaboratoryResult
from .serializers import (
    MedicalExaminationSerializer,
    MedicalExaminationCreateSerializer,
    DoctorExaminationSerializer,
    LaboratoryResultSerializer
)
from .services import ExaminationService
from apps.compliance.models import HarmfulFactor


class MedicalExaminationViewSet(viewsets.ModelViewSet):
    """ViewSet для медицинских осмотров"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MedicalExaminationCreateSerializer
        return MedicalExaminationSerializer
    
    def get_queryset(self):
        user = self.request.user
        from apps.organizations.models import Organization, Employee
        from django.db.models import Q
        
        # Работодатель: видит осмотры своих сотрудников
        employer_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user, members__role__in=['hr', 'admin', 'safety']),
            org_type='employer'
        ).values_list('id', flat=True)
        
        # Клиника: видит осмотры назначенные в их клинику
        clinic_ids = Organization.objects.filter(
            Q(owner=user) | Q(members__user=user),
            org_type='clinic'
        ).values_list('id', flat=True)
        
        # Пациент: видит только свои осмотры
        employee = Employee.objects.filter(user=user).first()
        
        queryset = MedicalExamination.objects.none()
        
        if employer_ids.exists():
            queryset = queryset | MedicalExamination.objects.filter(employer_id__in=employer_ids)
        
        if clinic_ids.exists():
            queryset = queryset | MedicalExamination.objects.filter(clinic_id__in=clinic_ids)
        
        if employee:
            queryset = queryset | MedicalExamination.objects.filter(employee=employee)
        
        return queryset.distinct()
    
    def create(self, request, *args, **kwargs):
        """Создание осмотра с автоматической генерацией маршрута"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee = serializer.validated_data['employee']
        clinic = serializer.validated_data['clinic']
        examination_type = serializer.validated_data['examination_type']
        scheduled_date = serializer.validated_data['scheduled_date']
        reason = serializer.validated_data.get('reason', '')
        
        # Проверяем активную подписку работодателя
        from apps.subscriptions.services import SubscriptionService
        if not SubscriptionService.check_organization_access(employee.employer):
            return Response(
                {'error': 'Для создания осмотров необходима активная подписка организации работодателя'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        examination = ExaminationService.create_examination(
            employee=employee,
            examination_type=examination_type,
            clinic=clinic,
            scheduled_date=scheduled_date,
            reason=reason
        )
        
        result_serializer = MedicalExaminationSerializer(examination)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Начать осмотр"""
        examination = self.get_object()
        examination = ExaminationService.start_examination(examination)
        serializer = self.get_serializer(examination)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_doctor_examination(self, request, pk=None):
        """Добавить результат осмотра врачом"""
        examination = self.get_object()
        
        doctor_id = request.data.get('doctor_id')
        harmful_factor_id = request.data.get('harmful_factor_id')
        result = request.data.get('result')
        findings = request.data.get('findings', '')
        recommendations = request.data.get('recommendations', '')
        
        try:
            from apps.organizations.models import OrganizationMember
            doctor = OrganizationMember.objects.get(id=doctor_id, role='doctor')
            harmful_factor = HarmfulFactor.objects.get(id=harmful_factor_id)
        except (OrganizationMember.DoesNotExist, HarmfulFactor.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        doctor_exam = ExaminationService.add_doctor_examination(
            examination=examination,
            doctor=doctor,
            harmful_factor=harmful_factor,
            result=result,
            findings=findings,
            recommendations=recommendations
        )
        
        serializer = DoctorExaminationSerializer(doctor_exam)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Завершить осмотр (профпатолог)"""
        examination = self.get_object()
        
        final_result = request.data.get('result')
        profpathologist_id = request.data.get('profpathologist_id')
        
        try:
            from apps.organizations.models import OrganizationMember
            profpathologist = OrganizationMember.objects.get(
                id=profpathologist_id,
                role='profpathologist'
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'Профпатолог не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        examination = ExaminationService.complete_examination(
            examination=examination,
            final_result=final_result,
            profpathologist=profpathologist
        )
        
        serializer = self.get_serializer(examination)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_qr(self, request):
        """Найти осмотр по QR коду"""
        qr_code = request.query_params.get('qr_code')
        if not qr_code:
            return Response(
                {'error': 'Укажите QR код'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            examination = MedicalExamination.objects.get(qr_code=qr_code)
            serializer = self.get_serializer(examination)
            return Response(serializer.data)
        except MedicalExamination.DoesNotExist:
            return Response(
                {'error': 'Осмотр не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

