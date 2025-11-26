"""
URL configuration for ProfMed.kz project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/compliance/', include('apps.compliance.urls')),
    path('api/organizations/', include('apps.organizations.urls')),
    path('api/examinations/', include('apps.medical_examinations.urls')),
    path('api/documents/', include('apps.documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

