"""
URLs pour l'Admin Dashboard
"""
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Gestion des inscriptions
    path('inscriptions/en-attente/', views.inscriptions_en_attente, name='inscriptions_en_attente'),
    path('inscriptions/<int:pk>/valider/', views.valider_inscription, name='valider_inscription'),
    
    # Gestion des paiements
    path('paiements/en-attente/', views.paiements_en_attente, name='paiements_en_attente'),
    path('paiements/<int:pk>/valider/', views.valider_paiement, name='valider_paiement'),
]