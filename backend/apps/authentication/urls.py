"""
Authentication URLs
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('profile/', views.profile, name='profile'),
]

