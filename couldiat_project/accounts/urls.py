"""
URLs pour l'application Accounts
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Imports des nouvelles vues de réinitialisation
from .password_reset_views import (
    PasswordResetRequestView,
    PasswordResetVerifyCodeView,
    PasswordResetConfirmView,
    PasswordResetResendCodeView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Password Reset - Nouvelle approche avec code OTP
    path('password-reset/request/', 
         PasswordResetRequestView.as_view(), 
         name='password_reset_request'),
    
    path('password-reset/verify/', 
         PasswordResetVerifyCodeView.as_view(), 
         name='password_reset_verify'),
    
    path('password-reset/confirm/', 
         PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    
    path('password-reset/resend/', 
         PasswordResetResendCodeView.as_view(), 
         name='password_reset_resend'),
]