"""
Admin configuration for organizations app
"""
from django.contrib import admin
from .models import Organization, OrganizationMember, Employee, ClinicEmployerPartnership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'org_type', 'bin', 'owner', 'created_at']
    list_filter = ['org_type', 'created_at']
    search_fields = ['name', 'bin']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ['organization', 'user', 'role', 'specialization', 'is_active']
    list_filter = ['role', 'is_active', 'organization']
    search_fields = ['user__phone_number', 'organization__name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employer', 'position', 'department', 'is_active']
    list_filter = ['is_active', 'employer', 'position']
    search_fields = ['first_name', 'last_name', 'iin', 'user__phone_number']


@admin.register(ClinicEmployerPartnership)
class ClinicEmployerPartnershipAdmin(admin.ModelAdmin):
    list_display = ['clinic', 'employer', 'status', 'is_public', 'requested_at', 'confirmed_at']
    list_filter = ['status', 'is_public', 'requested_at']
    search_fields = ['clinic__name', 'employer__name']
    readonly_fields = ['requested_at', 'confirmed_at', 'created_at', 'updated_at']

