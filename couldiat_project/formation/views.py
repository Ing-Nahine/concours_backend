"""
Views pour l'application Formation avec gestion d'abonnement
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Matiere, Chapitre, Question, ProgressionChapitre, Abonnement
from .serializers import (
    MatiereListSerializer,
    ChapitreListSerializer,
    QuestionSerializer,
    SubmitQCMSerializer,
    ProgressionChapitreSerializer,
    AbonnementSerializer,
    AbonnementCreateSerializer
)


def verifier_abonnement(user):
    """
    Vérifier si l'utilisateur a un abonnement actif
    Retourne (est_actif, abonnement, message)
    """
    try:
        abonnement = user.abonnement
        abonnement.verifier_expiration()  # Mettre à jour le statut si expiré
        
        if not abonnement.est_actif:
            return False, abonnement, f"Votre abonnement a expiré le {abonnement.date_fin}. Veuillez renouveler."
        
        return True, abonnement, None
        
    except Abonnement.DoesNotExist:
        return False, None, "Vous devez souscrire à un abonnement pour accéder à la formation."


@swagger_auto_schema(
    method='get',
    responses={200: AbonnementSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mon_abonnement(request):
    """
    Récupérer les informations de l'abonnement de l'utilisateur
    """
    try:
        abonnement = request.user.abonnement
        abonnement.verifier_expiration()
        serializer = AbonnementSerializer(abonnement)
        return Response(serializer.data)
    except Abonnement.DoesNotExist:
        return Response({
            'message': 'Aucun abonnement trouvé',
            'abonnement_requis': True
        }, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    request_body=AbonnementCreateSerializer,
    responses={
        201: AbonnementSerializer,
        400: 'Erreur de validation'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def souscrire_abonnement(request):
    """
    Souscrire à un abonnement formation
    
    Body:
    {
        "montant_paye": 25000,
        "reference_paiement": "OM2024031512345"
    }
    
    L'abonnement démarre immédiatement et prend fin le 31 juillet
    """
    serializer = AbonnementCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        abonnement = serializer.save()
        
        return Response({
            'message': 'Abonnement créé avec succès',
            'abonnement': AbonnementSerializer(abonnement).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: MatiereListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_matieres(request):
    """
    Liste de toutes les matières avec progression de l'utilisateur
    Nécessite un abonnement actif
    """
    # Vérifier l'abonnement
    est_actif, abonnement, message = verifier_abonnement(request.user)
    
    matieres = Matiere.objects.all()
    serializer = MatiereListSerializer(
        matieres,
        many=True,
        context={'request': request}
    )
    
    response_data = {
        'matieres': serializer.data,
        'abonnement': AbonnementSerializer(abonnement).data if abonnement else None,
        'abonnement_actif': est_actif
    }
    
    if not est_actif:
        response_data['message'] = message
    
    return Response(response_data)


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response(
        'Liste des chapitres',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'matiere_name': openapi.Schema(type=openapi.TYPE_STRING),
                'chapitres': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            }
        )
    )}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chapitres_matiere(request, matiere_id):
    """
    Liste des chapitres d'une matière avec leur statut pour l'utilisateur
    Nécessite un abonnement actif
    """
    # Vérifier l'abonnement
    est_actif, abonnement, message = verifier_abonnement(request.user)
    
    if not est_actif:
        return Response({
            'error': message,
            'abonnement_requis': True
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        matiere = Matiere.objects.get(id=matiere_id)
    except Matiere.DoesNotExist:
        return Response({
            'error': 'Matière non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    chapitres = matiere.chapitres.all()
    
    # Initialiser la progression pour le premier chapitre si nécessaire
    if chapitres.exists():
        premier_chapitre = chapitres.first()
        ProgressionChapitre.objects.get_or_create(
            user=request.user,
            chapitre=premier_chapitre,
            defaults={'statut': 'en_cours'}
        )
    
    serializer = ChapitreListSerializer(
        chapitres,
        many=True,
        context={'request': request}
    )
    
    return Response({
        'matiere_name': matiere.nom,
        'chapitres': serializer.data,
        'abonnement': {
            'jours_restants': abonnement.jours_restants,
            'date_fin': abonnement.date_fin
        }
    })


@swagger_auto_schema(
    method='get',
    responses={200: QuestionSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def questions_chapitre(request, chapitre_id):
    """
    Liste des questions d'un chapitre (SANS les réponses correctes)
    Nécessite un abonnement actif
    """
    # Vérifier l'abonnement
    est_actif, abonnement, message = verifier_abonnement(request.user)
    
    if not est_actif:
        return Response({
            'error': message,
            'abonnement_requis': True
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        chapitre = Chapitre.objects.get(id=chapitre_id)
    except Chapitre.DoesNotExist:
        return Response({
            'error': 'Chapitre non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier que le chapitre est accessible (en_cours ou termine)
    try:
        progression = ProgressionChapitre.objects.get(
            user=request.user,
            chapitre=chapitre
        )
        
        if progression.statut == 'verrouille':
            return Response({
                'error': 'Ce chapitre est verrouillé. Complétez le chapitre précédent.'
            }, status=status.HTTP_403_FORBIDDEN)
    except ProgressionChapitre.DoesNotExist:
        return Response({
            'error': 'Ce chapitre n\'est pas encore disponible.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    questions = chapitre.questions.all()
    serializer = QuestionSerializer(questions, many=True)
    
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=SubmitQCMSerializer,
    responses={
        200: openapi.Response('Résultats enregistrés'),
        400: 'Erreur de validation'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_qcm(request):
    """
    Soumettre les résultats d'un QCM
    Nécessite un abonnement actif
    """
    # Vérifier l'abonnement
    est_actif, abonnement, message = verifier_abonnement(request.user)
    
    if not est_actif:
        return Response({
            'error': message,
            'abonnement_requis': True
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = SubmitQCMSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    chapitre_id = serializer.validated_data['chapitre_id']
    temps_ecoule = serializer.validated_data['temps_ecoule']
    reponses = serializer.validated_data['reponses']
    
    # Récupérer le chapitre
    chapitre = Chapitre.objects.get(id=chapitre_id)
    
    # Calculer le score
    total_questions = len(reponses)
    bonnes_reponses = 0
    
    for reponse in reponses:
        try:
            question = Question.objects.get(id=reponse['question_id'])
            if question.correct_answer == reponse['reponse_index']:
                bonnes_reponses += 1
        except Question.DoesNotExist:
            continue
    
    score = int((bonnes_reponses / total_questions) * 100) if total_questions > 0 else 0
    
    # Mettre à jour la progression
    progression, created = ProgressionChapitre.objects.get_or_create(
        user=request.user,
        chapitre=chapitre,
        defaults={
            'statut': 'termine',
            'score': score,
            'temps_ecoule': temps_ecoule,
            'tentatives': 1
        }
    )
    
    if not created:
        progression.statut = 'termine'
        progression.score = score
        progression.temps_ecoule = temps_ecoule
        progression.tentatives += 1
        progression.save()
    
    # Débloquer le chapitre suivant
    chapitre_suivant = None
    chapitre_suivant_obj = Chapitre.objects.filter(
        matiere=chapitre.matiere,
        ordre=chapitre.ordre + 1
    ).first()
    
    if chapitre_suivant_obj:
        ProgressionChapitre.objects.get_or_create(
            user=request.user,
            chapitre=chapitre_suivant_obj,
            defaults={'statut': 'en_cours'}
        )
        
        chapitre_suivant = {
            'id': chapitre_suivant_obj.id,
            'titre': chapitre_suivant_obj.titre
        }
    
    return Response({
        'message': 'Résultats enregistrés avec succès',
        'score': score,
        'bonnes_reponses': bonnes_reponses,
        'total_questions': total_questions,
        'nouveau_statut_chapitre': 'termine',
        'chapitre_suivant_debloque': chapitre_suivant
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={200: ProgressionChapitreSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ma_progression(request):
    """
    Récupérer toute la progression de l'utilisateur
    """
    progressions = ProgressionChapitre.objects.filter(
        user=request.user
    ).select_related('chapitre', 'chapitre__matiere')
    
    serializer = ProgressionChapitreSerializer(progressions, many=True)
    
    return Response(serializer.data)