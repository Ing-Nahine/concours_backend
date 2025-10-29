"""
URLs pour l'application Accounts
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .password_reset import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordResetVerifyTokenView
)

app_name = 'accounts'


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
    
   
    # Password Reset (NOUVEAU)
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/verify/<str:uid>/<str:token>/', PasswordResetVerifyTokenView.as_view(), name='password_reset_verify'),

]