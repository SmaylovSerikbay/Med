"""
Compliance URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HarmfulFactorViewSet,
    ProfessionViewSet,
    MedicalContraindicationViewSet
)

router = DefaultRouter()
router.register(r'factors', HarmfulFactorViewSet, basename='harmful-factor')
router.register(r'professions', ProfessionViewSet, basename='profession')
router.register(r'contraindications', MedicalContraindicationViewSet, basename='contraindication')

urlpatterns = [
    path('', include(router.urls)),
]
