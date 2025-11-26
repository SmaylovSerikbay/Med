"""
Authentication URLs
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # WhatsApp OTP authentication
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    
    # Password authentication
    path('login-password/', views.login_password, name='login-password'),
    path('set-password/', views.set_password, name='set-password'),
    
    # Password reset
    path('reset-password/request/', views.reset_password_request, name='reset-password-request'),
    path('reset-password/confirm/', views.reset_password_confirm, name='reset-password-confirm'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
]

