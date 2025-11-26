"""
Admin configuration for compliance app
"""
from django.contrib import admin
from .models import HarmfulFactor, Profession, MedicalContraindication


@admin.register(HarmfulFactor)
class HarmfulFactorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'periodicity_months', 'is_active']
    list_filter = ['is_active', 'periodicity_months']
    search_fields = ['code', 'name']


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_decreted']
    list_filter = ['is_decreted']
    search_fields = ['name']
    filter_horizontal = ['harmful_factors']


@admin.register(MedicalContraindication)
class MedicalContraindicationAdmin(admin.ModelAdmin):
    list_display = ['harmful_factor', 'condition', 'icd_code', 'severity']
    list_filter = ['severity', 'harmful_factor']
    search_fields = ['condition', 'icd_code']

