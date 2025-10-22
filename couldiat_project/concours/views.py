"""
Views pour l'application Concours
"""
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Concours, Inscription, Paiement
from .serializers import (
    ConcoursListSerializer,
    ConcoursDetailSerializer,
    InscriptionCreateSerializer,
    InscriptionListSerializer,
    InscriptionDetailSerializer,
    PaiementCreateSerializer,
    PaiementDetailSerializer
)


class ConcoursListView(generics.ListAPIView):
    """
    Liste de tous les concours disponibles
    
    Query Parameters:
    - type: Filter par type (Direct ou Professionnel)
    - est_ouvert: Filter par statut (true/false)
    - search: Recherche par nom
    """
    queryset = Concours.objects.all()
    serializer_class = ConcoursListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'est_ouvert']
    search_fields = ['nom', 'description', 'lieu']
    ordering_fields = ['date_concours', 'created_at']
    ordering = ['-created_at']


class ConcoursDetailView(generics.RetrieveAPIView):
    """
    Détail d'un concours spécifique
    """
    queryset = Concours.objects.all()
    serializer_class = ConcoursDetailSerializer
    permission_classes = [IsAuthenticated]


@swagger_auto_schema(
    method='post',
    request_body=InscriptionCreateSerializer,
    responses={
        201: openapi.Response('Inscription créée', InscriptionDetailSerializer),
        400: 'Erreur de validation'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_inscription(request):
    """
    Créer une nouvelle inscription à un concours
    
    Required fields:
    - concours_id: ID du concours
    - nom, prenom, date_naissance, ville, sexe
    - cni: Document CNI (File)
    - photo: Photo d'identité (File)
    - telephone: Numéro de téléphone
    """
    serializer = InscriptionCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        inscription = serializer.save()
        
        return Response({
            'message': 'Inscription créée avec succès',
            'inscription': InscriptionDetailSerializer(inscription).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: InscriptionListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_inscriptions(request):
    """
    Récupérer toutes les inscriptions de l'utilisateur connecté
    """
    inscriptions = Inscription.objects.filter(user=request.user).select_related('concours')
    serializer = InscriptionListSerializer(inscriptions, many=True)
    
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: InscriptionDetailSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inscription_detail(request, pk):
    """
    Détail d'une inscription spécifique
    """
    try:
        inscription = Inscription.objects.select_related('user', 'concours').get(
            id=pk,
            user=request.user
        )
    except Inscription.DoesNotExist:
        return Response({
            'error': 'Inscription non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = InscriptionDetailSerializer(inscription)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=PaiementCreateSerializer,
    responses={
        201: openapi.Response('Paiement créé', PaiementDetailSerializer),
        400: 'Erreur de validation'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def valider_paiement(request):
    """
    Soumettre un paiement pour validation
    
    Required fields:
    - inscription_id: ID de l'inscription
    - methode_paiement: orange_money ou moov_money
    - reference_transaction: Référence de la transaction
    - montant: Montant payé en FCFA
    - capture_ecran: Capture d'écran de la preuve (File)
    """
    serializer = PaiementCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        paiement = serializer.save()
        
        return Response({
            'message': 'Paiement soumis avec succès. En attente de validation.',
            'paiement': PaiementDetailSerializer(paiement).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: PaiementDetailSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def paiement_detail(request, inscription_id):
    """
    Détail du paiement d'une inscription
    """
    try:
        inscription = Inscription.objects.get(id=inscription_id, user=request.user)
        paiement = inscription.paiement
    except Inscription.DoesNotExist:
        return Response({
            'error': 'Inscription non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    except Paiement.DoesNotExist:
        return Response({
            'error': 'Aucun paiement trouvé pour cette inscription'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PaiementDetailSerializer(paiement)
    return Response(serializer.data)