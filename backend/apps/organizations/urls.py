"""
Organization URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, EmployeeViewSet, ClinicEmployerPartnershipViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'partnerships', ClinicEmployerPartnershipViewSet, basename='partnership')

urlpatterns = [
    path('', include(router.urls)),
]
