"""
URLs pour l'application Concours
"""
from django.urls import path
from . import views

app_name = 'concours'

urlpatterns = [
    # Concours
    path('', views.ConcoursListView.as_view(), name='concours_list'),
    path('<int:pk>/', views.ConcoursDetailView.as_view(), name='concours_detail'),
    
    # Inscriptions
    path('inscriptions/create/', views.create_inscription, name='create_inscription'),
    path('inscriptions/mes-inscriptions/', views.mes_inscriptions, name='mes_inscriptions'),
    path('inscriptions/<int:pk>/', views.inscription_detail, name='inscription_detail'),
    
    # Paiements
    path('paiements/valider/', views.valider_paiement, name='valider_paiement'),
    path('paiements/inscription/<int:inscription_id>/', views.paiement_detail, name='paiement_detail'),
]