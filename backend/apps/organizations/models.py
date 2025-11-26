"""
Organization models - Работодатели и Клиники
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class OrganizationType(models.TextChoices):
    EMPLOYER = 'employer', 'Работодатель'
    CLINIC = 'clinic', 'Клиника'


class Organization(models.Model):
    """Организация (Работодатель или Клиника)"""
    name = models.CharField(max_length=255, verbose_name='Название')
    org_type = models.CharField(
        max_length=20,
        choices=OrganizationType.choices,
        verbose_name='Тип организации'
    )
    bin = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        verbose_name='БИН'
    )
    address = models.TextField(blank=True, verbose_name='Адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_organizations',
        verbose_name='Владелец'
    )
    # Для клиник
    capacity_per_day = models.IntegerField(
        default=50,
        verbose_name='Пропускная способность в день (для клиник)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['name']

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    """Участник организации (сотрудник HR, врач и т.д.)"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('hr', 'HR менеджер'),
        ('safety', 'Инженер по ТБ'),
        ('doctor', 'Врач'),
        ('registrar', 'Регистратор'),
        ('profpathologist', 'Профпатолог'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Организация'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        verbose_name='Пользователь'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Роль'
    )
    # Для врачей
    specialization = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Специализация (для врачей)'
    )
    license_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Номер лицензии'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Участник организации'
        verbose_name_plural = 'Участники организаций'
        unique_together = ['organization', 'user']

    def __str__(self):
        return f"{self.user.phone_number} - {self.organization.name}"


class Employee(models.Model):
    """Сотрудник (пациент) - работает у работодателя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name='Пользователь'
    )
    employer = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employees',
        limit_choices_to={'org_type': OrganizationType.EMPLOYER},
        verbose_name='Работодатель'
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    iin = models.CharField(max_length=12, blank=True, verbose_name='ИИН')
    position = models.ForeignKey(
        'compliance.Profession',
        on_delete=models.PROTECT,
        related_name='employees',
        null=True,
        blank=True,
        verbose_name='Должность'
    )
    department = models.CharField(max_length=200, blank=True, verbose_name='Отдел/Цех')
    hire_date = models.DateField(verbose_name='Дата приема на работу')
    position_start_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Дата начала работы на должности',
        help_text='Для расчета стажа по занимаемой должности'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения',
        help_text='Можно извлечь из ИИН или указать вручную'
    )
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Мужской'), ('female', 'Женский')],
        blank=True,
        null=True,
        verbose_name='Пол',
        help_text='Можно определить из ИИН или указать вручную'
    )
    notes = models.TextField(blank=True, verbose_name='Примечание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.position.name}"
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()


class ClinicEmployerPartnership(models.Model):
    """Партнерство между клиникой и работодателем"""
    class PartnershipStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        ACTIVE = 'active', 'Активно'
        REJECTED = 'rejected', 'Отклонено'
        SUSPENDED = 'suspended', 'Приостановлено'
        EXPIRED = 'expired', 'Истекло'
    
    clinic = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employer_partnerships',
        limit_choices_to={'org_type': OrganizationType.CLINIC},
        verbose_name='Клиника'
    )
    employer = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='clinic_partnerships',
        limit_choices_to={'org_type': OrganizationType.EMPLOYER},
        verbose_name='Работодатель'
    )
    status = models.CharField(
        max_length=20,
        choices=PartnershipStatus.choices,
        default=PartnershipStatus.PENDING,
        verbose_name='Статус'
    )
    # Цены на услуги (JSON формат: {"periodic_exam": 5000, "preliminary_exam": 3000, ...})
    pricing = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Цены на услуги'
    )
    # Стандартная цена по умолчанию (используется если не указана индивидуальная)
    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стандартная цена'
    )
    # Для открытых клиник (любой работодатель может использовать)
    is_public = models.BooleanField(
        default=False,
        verbose_name='Открытая клиника (публичная)'
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='partnership_requests',
        verbose_name='Запросил'
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partnership_confirmations',
        verbose_name='Подтвердил'
    )
    notes = models.TextField(blank=True, verbose_name='Примечания')
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Запрошено')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Подтверждено')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Действует до')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Партнерство клиники и работодателя'
        verbose_name_plural = 'Партнерства клиник и работодателей'
        unique_together = ['clinic', 'employer']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['clinic', 'status']),
            models.Index(fields=['employer', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.clinic.name} ↔ {self.employer.name} ({self.get_status_display()})"
    
    def is_active(self):
        """Проверка, активно ли партнерство"""
        if self.status != self.PartnershipStatus.ACTIVE:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
