"""
Medical examination services - Логика осмотров
"""
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from .models import MedicalExamination, ExaminationRoute, DoctorExamination
from apps.compliance.models import HarmfulFactor
from apps.compliance.services import ComplianceService
from apps.organizations.models import OrganizationMember


class ExaminationService:
    """Сервис для работы с медицинскими осмотрами"""
    
    @staticmethod
    def generate_qr_code() -> str:
        """Генерация уникального QR кода"""
        return str(uuid.uuid4())
    
    @staticmethod
    @transaction.atomic
    def create_examination(
        employee,
        examination_type: str,
        clinic,
        scheduled_date: datetime,
        employer=None,
        reason: str = ''
    ) -> MedicalExamination:
        """
        Создание нового медицинского осмотра с маршрутным листом
        
        Args:
            employee: Объект Employee
            examination_type: Тип осмотра
            clinic: Клиника (Organization)
            scheduled_date: Запланированная дата
            employer: Работодатель (если не указан, берется из employee)
            reason: Причина (для внеочередных)
            
        Returns:
            MedicalExamination объект
        """
        if not employer:
            employer = employee.employer
        
        # Генерируем QR код
        qr_code = ExaminationService.generate_qr_code()
        
        # Создаем осмотр
        examination = MedicalExamination.objects.create(
            examination_type=examination_type,
            employee=employee,
            employer=employer,
            clinic=clinic,
            scheduled_date=scheduled_date,
            qr_code=qr_code,
            reason=reason,
            status='scheduled'
        )
        
        # Получаем вредные факторы сотрудника
        factors = []
        if employee.position:
            factors = list(employee.position.harmful_factors.filter(is_active=True))
        
        # Создаем маршрутный лист
        route = ExaminationRoute.objects.create(examination=examination)
        
        # Находим нужных врачей в клинике
        if factors:
            required_doctor_specializations = ComplianceService.get_required_doctors_for_factors(factors)
            
            # Ищем врачей с нужными специализациями
            doctors = OrganizationMember.objects.filter(
                organization=clinic,
                role='doctor',
                is_active=True,
                specialization__in=required_doctor_specializations
            )
            
            # Также добавляем профпатолога (обязателен для завершения осмотра)
            profpathologist = OrganizationMember.objects.filter(
                organization=clinic,
                role='profpathologist',
                is_active=True
            ).first()
            
            if profpathologist:
                route.doctors_required.add(profpathologist)
            if doctors.exists():
                route.doctors_required.add(*doctors)
        else:
            # Если нет факторов, назначаем профпатолога для общего осмотра
            profpathologist = OrganizationMember.objects.filter(
                organization=clinic,
                role__in=['profpathologist', 'doctor'],  # Может быть врач выполняет роль профпатолога
                is_active=True
            ).first()
            if profpathologist:
                route.doctors_required.add(profpathologist)
        
        return examination
    
    @staticmethod
    def start_examination(examination: MedicalExamination) -> MedicalExamination:
        """Начать осмотр (изменить статус на IN_PROGRESS)"""
        examination.status = 'in_progress'
        examination.save()
        return examination
    
    @staticmethod
    @transaction.atomic
    def add_doctor_examination(
        examination: MedicalExamination,
        doctor: OrganizationMember,
        harmful_factor: HarmfulFactor,
        result: str,
        findings: str = '',
        recommendations: str = ''
    ) -> DoctorExamination:
        """
        Добавить результат осмотра врачом
        
        Args:
            examination: Осмотр
            doctor: Врач
            harmful_factor: Вредный фактор
            result: Результат (fit/unfit/limited)
            findings: Заключение
            recommendations: Рекомендации
            
        Returns:
            DoctorExamination объект
        """
        doctor_exam = DoctorExamination.objects.create(
            examination=examination,
            doctor=doctor,
            harmful_factor=harmful_factor,
            result=result,
            findings=findings,
            recommendations=recommendations
        )
        
        # Проверяем противопоказания
        contraindications = ComplianceService.check_contraindications(
            harmful_factor,
            findings
        )
        
        if contraindications:
            from apps.compliance.models import MedicalContraindication
            contraindication_ids = [c['id'] for c in contraindications]
            doctor_exam.contraindications_found.set(
                MedicalContraindication.objects.filter(id__in=contraindication_ids)
            )
        
        return doctor_exam
    
    @staticmethod
    @transaction.atomic
    def complete_examination(
        examination: MedicalExamination,
        final_result: str,
        profpathologist: OrganizationMember
    ) -> MedicalExamination:
        """
        Завершить осмотр (вынести финальное заключение профпатологом)
        Автоматически генерирует справку 075/у
        
        Args:
            examination: Осмотр
            final_result: Финальный результат
            profpathologist: Профпатолог
            
        Returns:
            MedicalExamination объект
        """
        examination.status = 'completed'
        examination.result = final_result
        examination.completed_date = timezone.now()
        examination.save()
        
        # Автоматически генерируем справку 075/у
        from apps.documents.services import DocumentService
        DocumentService.generate_medical_certificate(examination)
        
        # Отправляем уведомление работодателю о завершении осмотра
        from apps.authentication.services import GreenAPIService
        if examination.employer and examination.employer.owner.phone_number:
            message = (
                f"Осмотр сотрудника {examination.employee.full_name} завершен.\n"
                f"📊 Результат: {examination.get_result_display()}\n"
                f"🏥 Клиника: {examination.clinic.name}\n"
                f"📄 Справка 075/у сформирована и доступна в системе."
            )
            try:
                GreenAPIService.send_whatsapp_message(
                    examination.employer.owner.phone_number,
                    message
                )
            except Exception:
                pass  # Не критично
        
        return examination
    
    @staticmethod
    def get_examination_progress(examination: MedicalExamination) -> dict:
        """
        Получить прогресс осмотра
        
        Returns:
            Словарь с информацией о прогрессе
        """
        route = examination.route
        total_doctors = route.doctors_required.count()
        completed_exams = examination.doctor_examinations.count()
        
        return {
            'total_doctors': total_doctors,
            'completed_exams': completed_exams,
            'progress_percent': int((completed_exams / total_doctors * 100)) if total_doctors > 0 else 0,
            'is_complete': completed_exams >= total_doctors,
        }

