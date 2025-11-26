"""
Medical examination models - Полная логика осмотров
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class ExaminationType(models.TextChoices):
    PRELIMINARY = 'preliminary', 'Предварительный'
    PERIODIC = 'periodic', 'Периодический'
    EXTRAORDINARY = 'extraordinary', 'Внеочередной'


class ExaminationStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Запланирован'
    IN_PROGRESS = 'in_progress', 'В процессе'
    COMPLETED = 'completed', 'Завершен'
    CANCELLED = 'cancelled', 'Отменен'


class ExaminationResult(models.TextChoices):
    FIT = 'fit', 'Годен'
    UNFIT = 'unfit', 'Не годен'
    LIMITED = 'limited', 'Годен с ограничениями'


class MedicalExamination(models.Model):
    """Медицинский осмотр"""
    examination_type = models.CharField(
        max_length=20,
        choices=ExaminationType.choices,
        verbose_name='Тип осмотра'
    )
    status = models.CharField(
        max_length=20,
        choices=ExaminationStatus.choices,
        default='scheduled',
        verbose_name='Статус'
    )
    employee = models.ForeignKey(
        'organizations.Employee',
        on_delete=models.CASCADE,
        related_name='examinations',
        verbose_name='Сотрудник'
    )
    employer = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='employer_examinations',
        limit_choices_to={'org_type': 'employer'},
        null=True,
        blank=True,
        verbose_name='Работодатель'
    )
    clinic = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='clinic_examinations',
        limit_choices_to={'org_type': 'clinic'},
        verbose_name='Клиника'
    )
    scheduled_date = models.DateTimeField(verbose_name='Запланированная дата')
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    result = models.CharField(
        max_length=20,
        choices=ExaminationResult.choices,
        null=True,
        blank=True,
        verbose_name='Результат'
    )
    # Для внеочередных осмотров
    reason = models.TextField(blank=True, verbose_name='Причина (для внеочередных)')
    # QR код для доступа
    qr_code = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='QR код')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Медицинский осмотр'
        verbose_name_plural = 'Медицинские осмотры'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['qr_code']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_examination_type_display()}"


class ExaminationRoute(models.Model):
    """Маршрутный лист осмотра - какие врачи нужны"""
    examination = models.OneToOneField(
        MedicalExamination,
        on_delete=models.CASCADE,
        related_name='route',
        verbose_name='Осмотр'
    )
    doctors_required = models.ManyToManyField(
        'organizations.OrganizationMember',
        related_name='routes',
        verbose_name='Требуемые врачи'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Маршрутный лист'
        verbose_name_plural = 'Маршрутные листы'

    def __str__(self):
        return f"Маршрут для {self.examination}"


class DoctorExamination(models.Model):
    """Результат осмотра конкретным врачом"""
    examination = models.ForeignKey(
        MedicalExamination,
        on_delete=models.CASCADE,
        related_name='doctor_examinations',
        verbose_name='Осмотр'
    )
    doctor = models.ForeignKey(
        'organizations.OrganizationMember',
        on_delete=models.PROTECT,
        related_name='examinations_performed',
        limit_choices_to={'role': 'doctor'},
        verbose_name='Врач'
    )
    harmful_factor = models.ForeignKey(
        'compliance.HarmfulFactor',
        on_delete=models.PROTECT,
        related_name='doctor_examinations',
        verbose_name='Вредный фактор'
    )
    result = models.CharField(
        max_length=20,
        choices=ExaminationResult.choices,
        verbose_name='Результат'
    )
    findings = models.TextField(blank=True, verbose_name='Заключение')
    recommendations = models.TextField(blank=True, verbose_name='Рекомендации')
    contraindications_found = models.ManyToManyField(
        'compliance.MedicalContraindication',
        blank=True,
        verbose_name='Выявленные противопоказания'
    )
    examined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата осмотра')
    
    class Meta:
        verbose_name = 'Осмотр врача'
        verbose_name_plural = 'Осмотры врачей'
        unique_together = ['examination', 'doctor', 'harmful_factor']

    def __str__(self):
        return f"{self.doctor.user.phone_number} - {self.harmful_factor.name}"


class LaboratoryResult(models.Model):
    """Результаты лабораторных исследований"""
    examination = models.ForeignKey(
        MedicalExamination,
        on_delete=models.CASCADE,
        related_name='laboratory_results',
        verbose_name='Осмотр'
    )
    test_name = models.CharField(max_length=200, verbose_name='Название анализа')
    test_code = models.CharField(max_length=50, blank=True, verbose_name='Код анализа')
    result_value = models.CharField(max_length=100, verbose_name='Результат')
    unit = models.CharField(max_length=20, blank=True, verbose_name='Единица измерения')
    reference_range = models.CharField(max_length=100, blank=True, verbose_name='Референсные значения')
    is_normal = models.BooleanField(default=True, verbose_name='В норме')
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата выполнения')
    
    class Meta:
        verbose_name = 'Лабораторный результат'
        verbose_name_plural = 'Лабораторные результаты'

    def __str__(self):
        return f"{self.test_name} - {self.result_value}"
