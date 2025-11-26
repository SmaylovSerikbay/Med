"""
Compliance models - Приказ 131 логика
"""
from django.db import models


class HarmfulFactor(models.Model):
    """Вредный производственный фактор (из Приказа 131)"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код фактора')
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    periodicity_months = models.IntegerField(
        default=12,
        verbose_name='Периодичность осмотра (месяцев)'
    )
    # Какие врачи нужны для этого фактора
    required_doctors = models.JSONField(
        default=list,
        verbose_name='Требуемые врачи (список специализаций)'
    )
    required_tests = models.JSONField(
        default=list,
        verbose_name='Требуемые анализы (список)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Вредный фактор'
        verbose_name_plural = 'Вредные факторы'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Profession(models.Model):
    """Профессия/Должность"""
    name = models.CharField(max_length=255, unique=True, verbose_name='Название профессии')
    harmful_factors = models.ManyToManyField(
        HarmfulFactor,
        blank=True,
        related_name='professions',
        verbose_name='Вредные факторы'
    )
    is_decreted = models.BooleanField(
        default=False,
        verbose_name='Декретированная группа (санкнижка)'
    )
    # Для авто-маппинга по ключевым словам
    keywords = models.JSONField(
        default=list,
        verbose_name='Ключевые слова для авто-маппинга'
    )
    
    class Meta:
        verbose_name = 'Профессия'
        verbose_name_plural = 'Профессии'
        ordering = ['name']

    def __str__(self):
        return self.name


class MedicalContraindication(models.Model):
    """Медицинское противопоказание"""
    harmful_factor = models.ForeignKey(
        HarmfulFactor,
        on_delete=models.CASCADE,
        related_name='contraindications',
        verbose_name='Вредный фактор'
    )
    condition = models.CharField(max_length=500, verbose_name='Противопоказание')
    icd_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Код МКБ-10'
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Критическое'),
            ('moderate', 'Умеренное'),
            ('minor', 'Незначительное'),
        ],
        default='moderate',
        verbose_name='Степень тяжести'
    )
    
    class Meta:
        verbose_name = 'Противопоказание'
        verbose_name_plural = 'Противопоказания'

    def __str__(self):
        return f"{self.harmful_factor.code} - {self.condition}"
