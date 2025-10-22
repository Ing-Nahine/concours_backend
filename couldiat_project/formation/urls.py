"""
URLs pour l'application Formation
"""
from django.urls import path
from . import views

app_name = 'formation'

urlpatterns = [
    
    path('abonnement/', views.mon_abonnement, name='mon_abonnement'),
    path('abonnement/souscrire/', views.souscrire_abonnement, name='souscrire_abonnement'),
    # Matières
    path('matieres/', views.liste_matieres, name='liste_matieres'),
    path('matieres/<int:matiere_id>/chapitres/', views.chapitres_matiere, name='chapitres_matiere'),
    
    # Chapitres et Questions
    path('chapitres/<int:chapitre_id>/questions/', views.questions_chapitre, name='questions_chapitre'),
    
    # QCM
    path('submit-qcm/', views.submit_qcm, name='submit_qcm'),
    
    # Progression
    path('progression/', views.ma_progression, name='ma_progression'),
    
  
    
]