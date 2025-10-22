"""
Views pour l'Admin Dashboard
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.permissions import IsAdminUser
from concours.models import Concours, Inscription, Paiement
from concours.serializers import (
    InscriptionDetailSerializer,
    PaiementDetailSerializer,
    ConcoursDetailSerializer
)
from accounts.models import User


@swagger_auto_schema(
    method='get',
    responses={200: 'Statistiques du dashboard'}
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """
    Statistiques générales du dashboard admin
    """
    today = timezone.now().date()
    
    stats = {
        # Inscriptions
        'inscriptions_du_jour': Inscription.objects.filter(
            created_at__date=today
        ).count(),
        'inscriptions_en_attente': Inscription.objects.filter(
            statut='en_attente'
        ).count(),
        'inscriptions_confirmees': Inscription.objects.filter(
            statut='confirmee'
        ).count(),
        
        # Paiements
        'paiements_en_attente': Paiement.objects.filter(
            statut='en_attente'
        ).count(),
        'paiements_valides': Paiement.objects.filter(
            statut='valide'
        ).count(),
        
        # Candidats
        'candidats_actifs': User.objects.filter(
            is_active=True,
            is_admin=False
        ).count(),
        'nouveaux_candidats_semaine': User.objects.filter(
            created_at__gte=today - timedelta(days=7),
            is_admin=False
        ).count(),
        
        # Concours
        'concours_ouverts': Concours.objects.filter(
            est_ouvert=True
        ).count(),
        'concours_total': Concours.objects.count(),
    }
    
    return Response(stats)


@swagger_auto_schema(
    method='get',
    responses={200: InscriptionDetailSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def inscriptions_en_attente(request):
    """
    Liste de toutes les inscriptions en attente de validation
    """
    inscriptions = Inscription.objects.filter(
        statut='en_attente'
    ).select_related('user', 'concours').order_by('-created_at')
    
    serializer = InscriptionDetailSerializer(inscriptions, many=True)
    
    return Response(serializer.data)


@swagger_auto_schema(
    method='patch',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['confirmer', 'rejeter']
            ),
            'raison_rejet': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['action']
    ),
    responses={200: 'Inscription validée/rejetée'}
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def valider_inscription(request, pk):
    """
    Valider ou rejeter une inscription
    
    Body:
    {
        "action": "confirmer" | "rejeter",
        "raison_rejet": "..." (si rejet)
    }
    """
    try:
        inscription = Inscription.objects.get(id=pk)
    except Inscription.DoesNotExist:
        return Response({
            'error': 'Inscription non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')
    
    if action == 'confirmer':
        inscription.statut = 'confirmee'
        inscription.save()
        
        return Response({
            'message': 'Inscription confirmée avec succès',
            'numero_inscription': inscription.numero_inscription,
            'inscription': InscriptionDetailSerializer(inscription).data
        })
    
    elif action == 'rejeter':
        raison_rejet = request.data.get('raison_rejet')
        
        if not raison_rejet:
            return Response({
                'error': 'La raison du rejet est obligatoire'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        inscription.statut = 'annulee'
        inscription.raison_rejet = raison_rejet
        inscription.save()
        
        return Response({
            'message': 'Inscription rejetée',
            'inscription': InscriptionDetailSerializer(inscription).data
        })
    
    else:
        return Response({
            'error': 'Action invalide. Utilisez "confirmer" ou "rejeter"'
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: PaiementDetailSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def paiements_en_attente(request):
    """
    Liste de tous les paiements en attente de validation
    """
    paiements = Paiement.objects.filter(
        statut='en_attente'
    ).select_related('inscription', 'inscription__user', 'inscription__concours').order_by('-created_at')
    
    serializer = PaiementDetailSerializer(paiements, many=True)
    
    return Response(serializer.data)


@swagger_auto_schema(
    method='patch',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['valider', 'rejeter']
            ),
            'raison_rejet': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['action']
    ),
    responses={200: 'Paiement validé/rejeté'}
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def valider_paiement(request, pk):
    """
    Valider ou rejeter un paiement
    
    Body:
    {
        "action": "valider" | "rejeter",
        "raison_rejet": "..." (si rejet)
    }
    """
    try:
        paiement = Paiement.objects.get(id=pk)
    except Paiement.DoesNotExist:
        return Response({
            'error': 'Paiement non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')
    
    if action == 'valider':
        paiement.statut = 'valide'
        paiement.save()
        
        return Response({
            'message': 'Paiement validé avec succès',
            'paiement': PaiementDetailSerializer(paiement).data
        })
    
    elif action == 'rejeter':
        raison_rejet = request.data.get('raison_rejet')
        
        if not raison_rejet:
            return Response({
                'error': 'La raison du rejet est obligatoire'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        paiement.statut = 'rejete'
        paiement.raison_rejet = raison_rejet
        paiement.save()
        
        return Response({
            'message': 'Paiement rejeté',
            'paiement': PaiementDetailSerializer(paiement).data
        })
    
    else:
        return Response({
            'error': 'Action invalide. Utilisez "valider" ou "rejeter"'
        }, status=status.HTTP_400_BAD_REQUEST)