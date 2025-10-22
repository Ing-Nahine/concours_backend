"""
Views pour l'application Accounts
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer
)

User = get_user_model()


@swagger_auto_schema(
    method='post',
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Inscription réussie', UserSerializer),
        400: 'Erreur de validation'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Inscription réussie',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    responses={
        200: openapi.Response('Connexion réussie'),
        401: 'Identifiants incorrects'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Connexion d'un utilisateur
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'Email ou mot de passe incorrect'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.check_password(password):
        return Response({
            'error': 'Email ou mot de passe incorrect'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'Ce compte a été désactivé'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Générer les tokens JWT
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Connexion réussie',
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={200: UserSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Récupérer le profil de l'utilisateur connecté
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=UpdateProfileSerializer,
    responses={200: UserSerializer}
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Mettre à jour le profil de l'utilisateur
    """
    serializer = UpdateProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès',
            'user': UserSerializer(request.user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=ChangePasswordSerializer,
    responses={200: 'Mot de passe modifié avec succès'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Changer le mot de passe de l'utilisateur
    """
    serializer = ChangePasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Vérifier l'ancien mot de passe
    if not user.check_password(serializer.validated_data['old_password']):
        return Response({
            'old_password': ['Mot de passe incorrect']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Définir le nouveau mot de passe
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    return Response({
        'message': 'Mot de passe modifié avec succès'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Déconnexion de l'utilisateur (blacklist du refresh token)
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Token invalide'
        }, status=status.HTTP_400_BAD_REQUEST)