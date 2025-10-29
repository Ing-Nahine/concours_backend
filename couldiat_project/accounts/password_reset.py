"""
Vues pour la réinitialisation de mot de passe
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decouple import config
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


class PasswordResetRequestView(APIView):
    """
    Demande de réinitialisation de mot de passe
    Envoie un email avec un lien de réinitialisation
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Demander une réinitialisation de mot de passe",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response('Email envoyé'),
            404: 'Utilisateur non trouvé'
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Pour des raisons de sécurité, on retourne toujours success
            # même si l'email n'existe pas (évite l'énumération d'utilisateurs)
            return Response({
                "message": "Si cet email existe, un lien de réinitialisation a été envoyé."
            }, status=status.HTTP_200_OK)
        
        # Générer le token de réinitialisation
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # URL du frontend pour la réinitialisation
        frontend_url = config('FRONTEND_URL', default='http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password/{uid}/{token}/"
        
        # Préparer le contexte de l'email
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'Couldiat',
        }
        
        # Envoyer l'email
        try:
            self._send_password_reset_email(user, context)
        except Exception as e:
            # Logger l'erreur mais ne pas révéler au client
            print(f"Erreur envoi email: {e}")
        
        return Response({
            "message": "Si cet email existe, un lien de réinitialisation a été envoyé."
        }, status=status.HTTP_200_OK)
    
    def _send_password_reset_email(self, user, context):
        """Envoyer l'email de réinitialisation"""
        subject = "Réinitialisation de votre mot de passe - Couldiat"
        
        # Version HTML de l'email
        html_message = render_to_string('emails/password_reset.html', context)
        
        # Version texte simple (fallback)
        text_message = f"""
Bonjour {user.get_full_name()},

Vous avez demandé la réinitialisation de votre mot de passe sur Couldiat.

Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :
{context['reset_url']}

Ce lien est valide pendant 24 heures.

Si vous n'avez pas demandé cette réinitialisation, ignorez ce message.

Cordialement,
L'équipe Couldiat
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class PasswordResetConfirmView(APIView):
    """
    Confirmation de réinitialisation de mot de passe
    Vérifie le token et change le mot de passe
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Confirmer la réinitialisation avec le nouveau mot de passe",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response('Mot de passe réinitialisé'),
            400: 'Token invalide ou expiré'
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        try:
            # Décoder l'UID pour récupérer l'utilisateur
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                "error": "Le lien de réinitialisation est invalide."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le token
        if not default_token_generator.check_token(user, token):
            return Response({
                "error": "Le lien de réinitialisation est invalide ou a expiré."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Changer le mot de passe
        user.set_password(password)
        user.save()
        
        # Envoyer email de confirmation
        try:
            self._send_password_changed_email(user)
        except Exception as e:
            print(f"Erreur envoi email confirmation: {e}")
        
        return Response({
            "message": "Votre mot de passe a été réinitialisé avec succès."
        }, status=status.HTTP_200_OK)
    
    def _send_password_changed_email(self, user):
        """Envoyer l'email de confirmation de changement"""
        subject = "Votre mot de passe a été modifié - Couldiati"
        
        context = {
            'user': user,
            'site_name': 'Couldiati',
        }
        
        # Version HTML
        html_message = render_to_string('emails/password_changed.html', context)
        
        # Version texte
        text_message = f"""
Bonjour {user.get_full_name()},

Votre mot de passe sur Couldiati a été modifié avec succès.

Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.

Cordialement,
L'équipe Couldiati
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class PasswordResetVerifyTokenView(APIView):
    """
    Vérifier la validité d'un token de réinitialisation
    Utile pour valider le lien avant d'afficher le formulaire
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Vérifier la validité d'un token de réinitialisation",
        manual_parameters=[
            openapi.Parameter('uid', openapi.IN_PATH, type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Token valide',
            400: 'Token invalide'
        }
    )
    def get(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                return Response({
                    "valid": True,
                    "message": "Le lien est valide."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "valid": False,
                    "error": "Le lien est invalide ou a expiré."
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                "valid": False,
                "error": "Le lien est invalide."
            }, status=status.HTTP_400_BAD_REQUEST)