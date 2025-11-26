"""
Medical examination URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalExaminationViewSet

router = DefaultRouter()
router.register(r'examinations', MedicalExaminationViewSet, basename='examination')

urlpatterns = [
    path('', include(router.urls)),
]
