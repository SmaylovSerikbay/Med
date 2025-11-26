"""
Document URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, CalendarPlanViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'calendar-plans', CalendarPlanViewSet, basename='calendar-plan')

urlpatterns = [
    path('', include(router.urls)),
]

