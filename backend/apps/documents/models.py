"""
Document models - Документы согласно Приказу 131
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DocumentType(models.TextChoices):
    APPENDIX_3 = 'appendix_3', 'Приложение 3 (Список лиц)'
    CALENDAR_PLAN = 'calendar_plan', 'Календарный план'
    FINAL_ACT = 'final_act', 'Заключительный акт'
    MEDICAL_CERTIFICATE = 'medical_certificate', 'Справка 075/у'
    HEALTH_PASSPORT = 'health_passport', 'Паспорт здоровья'
    SANITARY_BOOK = 'sanitary_book', 'Санитарная книжка'


class DocumentStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    PENDING_SIGNATURE = 'pending_signature', 'Ожидает подписания'
    SIGNED = 'signed', 'Подписан'
    APPROVED = 'approved', 'Утвержден'


class Document(models.Model):
    """Документ (справка, акт, список и т.д.)"""
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        verbose_name='Тип документа'
    )
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default='draft',
        verbose_name='Статус'
    )
    title = models.CharField(max_length=500, verbose_name='Название')
    content = models.JSONField(default=dict, verbose_name='Содержимое документа')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Путь к файлу PDF')
    # Для кого документ
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Организация'
    )
    # Для справок - привязан к осмотру
    examination = models.ForeignKey(
        'medical_examinations.MedicalExamination',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='Осмотр'
    )
    year = models.IntegerField(verbose_name='Год')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_documents',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type', 'status']),
            models.Index(fields=['organization', 'year']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.organization.name} ({self.year})"


class DocumentSignature(models.Model):
    """Подписание документа через OTP"""
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='signatures',
        verbose_name='Документ'
    )
    signer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_signatures',
        verbose_name='Подписант'
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ('clinic', 'Клиника'),
            ('employer', 'Работодатель'),
            ('ses', 'СЭС'),
        ],
        verbose_name='Роль подписанта'
    )
    # OTP код для подписания
    otp_code = models.CharField(max_length=10, blank=True, verbose_name='OTP код')
    otp_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='OTP отправлен')
    otp_verified = models.BooleanField(default=False, verbose_name='OTP подтвержден')
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name='Подписан')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    user_agent = models.CharField(max_length=500, blank=True, verbose_name='User Agent')
    
    class Meta:
        verbose_name = 'Подпись документа'
        verbose_name_plural = 'Подписи документов'
        unique_together = ['document', 'signer', 'role']

    def __str__(self):
        return f"{self.document} - {self.get_role_display()} - {self.signer.phone_number}"


class CalendarPlan(models.Model):
    """Календарный план проведения осмотров"""
    employer = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='calendar_plans',
        limit_choices_to={'org_type': 'employer'},
        verbose_name='Работодатель'
    )
    clinic = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='calendar_plans_received',
        limit_choices_to={'org_type': 'clinic'},
        verbose_name='Клиника'
    )
    year = models.IntegerField(verbose_name='Год')
    plan_data = models.JSONField(default=dict, verbose_name='Данные плана (распределение по датам)')
    document = models.OneToOneField(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calendar_plan',
        verbose_name='Документ плана'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Календарный план'
        verbose_name_plural = 'Календарные планы'
        unique_together = ['employer', 'year']

    def __str__(self):
        return f"План {self.employer.name} на {self.year} год"
    
    def delete(self, *args, **kwargs):
        """При удалении календарного плана удаляем и связанный документ"""
        if self.document:
            self.document.delete()
        super().delete(*args, **kwargs)

