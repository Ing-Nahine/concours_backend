"""
Vues pour la réinitialisation de mot de passe - Version Professionnelle
Utilise des codes OTP temporaires au lieu de tokens longs
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import secrets
import string
from datetime import datetime, timedelta
import traceback

from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetVerifyCodeSerializer
)

User = get_user_model()


def generate_reset_code():
    """Génère un code de réinitialisation à 6 chiffres"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))


class PasswordResetRequestView(APIView):
    """
    Demande de réinitialisation de mot de passe
    Envoie un code à 6 chiffres par email
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Demander un code de réinitialisation de mot de passe",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response('Code envoyé par email'),
            429: 'Trop de tentatives'
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Vérifier le rate limiting (max 3 tentatives par heure)
        rate_limit_key = f"password_reset_limit_{email}"
        attempts = cache.get(rate_limit_key, 0)
        
        if attempts >= 3:
            return Response({
                "error": "Trop de tentatives. Veuillez réessayer dans 1 heure."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Pour la sécurité, on retourne toujours success
            return Response({
                "message": "Si cet email existe, un code de réinitialisation a été envoyé.",
                "expires_in": 600  # 10 minutes
            }, status=status.HTTP_200_OK)
        
        # Générer le code de réinitialisation
        reset_code = generate_reset_code()
        
        # Stocker dans le cache (expire en 10 minutes)
        cache_key = f"password_reset_{email}"
        cache.set(cache_key, {
            'code': reset_code,
            'user_id': user.id,
            'created_at': datetime.now().isoformat()
        }, timeout=600)  # 10 minutes
        
        # Incrémenter le compteur de tentatives (expire en 1 heure)
        cache.set(rate_limit_key, attempts + 1, timeout=3600)
        
        # Envoyer l'email avec gestion d'erreur détaillée
        try:
            self._send_reset_code_email(user, reset_code)
            print(f"✅ Email envoyé avec succès à {user.email}")
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
            print("📋 Traceback complet:")
            traceback.print_exc()
            print(f"📧 Code généré (pour test): {reset_code}")
        
        return Response({
            "message": "Si cet email existe, un code de réinitialisation a été envoyé.",
            "expires_in": 600  # 10 minutes en secondes
        }, status=status.HTTP_200_OK)
    
    def _send_reset_code_email(self, user, code):
        """Envoyer l'email avec le code de réinitialisation"""
        subject = "Code de réinitialisation - Couldiat"
        
        context = {
            'user': user,
            'code': code,
            'expires_in': 10,  # minutes
            'site_name': 'Couldiatiformation',
        }
        
        # Version HTML
        try:
            html_message = render_to_string('emails/password_reset_code.html', context)
        except Exception as e:
            print(f"⚠️ Erreur chargement template HTML: {e}")
            # Fallback: email HTML simple
            html_message = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 30px; border-radius: 10px;">
        <h1 style="color: #6366F1;">🔐 Couldiatiformation</h1>
        <p>Bonjour {user.get_full_name()},</p>
        <p>Votre code de réinitialisation est :</p>
        <div style="background: white; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
            <h2 style="color: #6366F1; font-size: 36px; letter-spacing: 8px;">{code}</h2>
        </div>
        <p>Ce code expire dans 10 minutes.</p>
        <p style="color: #666;">Si vous n'avez pas demandé cette réinitialisation, ignorez ce message.</p>
    </div>
</body>
</html>
            """
        
        # Version texte
        text_message = f"""
Bonjour {user.get_full_name()},

Votre code de réinitialisation de mot de passe est :

{code}

Ce code est valide pendant 10 minutes.

Si vous n'avez pas demandé cette réinitialisation, ignorez ce message.

Cordialement,
L'équipe Couldiatiformation
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class PasswordResetVerifyCodeView(APIView):
    """
    Vérifier le code de réinitialisation
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Vérifier un code de réinitialisation",
        request_body=PasswordResetVerifyCodeSerializer,
        responses={
            200: openapi.Response('Code valide'),
            400: 'Code invalide ou expiré'
        }
    )
    def post(self, request):
        serializer = PasswordResetVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        # Récupérer le code stocké
        cache_key = f"password_reset_{email}"
        stored_data = cache.get(cache_key)
        
        if not stored_data:
            return Response({
                "error": "Code invalide ou expiré."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le code
        if stored_data['code'] != code:
            return Response({
                "error": "Code incorrect."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Générer un token temporaire pour le changement de mot de passe
        temp_token = secrets.token_urlsafe(32)
        temp_token_key = f"password_reset_token_{temp_token}"
        
        # Stocker le token (expire en 5 minutes)
        cache.set(temp_token_key, {
            'user_id': stored_data['user_id'],
            'email': email
        }, timeout=300)  # 5 minutes
        
        return Response({
            "message": "Code vérifié avec succès.",
            "reset_token": temp_token,
            "expires_in": 300  # 5 minutes
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirmation de réinitialisation avec le nouveau mot de passe
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Réinitialiser le mot de passe avec le token",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response('Mot de passe réinitialisé'),
            400: 'Token invalide ou expiré'
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data['reset_token']
        password = serializer.validated_data['password']
        
        # Vérifier le token
        token_key = f"password_reset_token_{reset_token}"
        token_data = cache.get(token_key)
        
        if not token_data:
            return Response({
                "error": "Token invalide ou expiré."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=token_data['user_id'])
        except User.DoesNotExist:
            return Response({
                "error": "Utilisateur non trouvé."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Changer le mot de passe
        user.set_password(password)
        user.save()
        
        # Supprimer tous les tokens et codes liés à cet email
        email = token_data['email']
        cache.delete(f"password_reset_{email}")
        cache.delete(token_key)
        cache.delete(f"password_reset_limit_{email}")
        
        # Envoyer email de confirmation avec gestion d'erreur
        try:
            self._send_password_changed_email(user)
            print(f"✅ Email de confirmation envoyé à {user.email}")
        except Exception as e:
            print(f"❌ Erreur envoi email confirmation: {e}")
            print("📋 Traceback complet:")
            traceback.print_exc()
        
        return Response({
            "message": "Votre mot de passe a été réinitialisé avec succès."
        }, status=status.HTTP_200_OK)
    
    def _send_password_changed_email(self, user):
        """Envoyer l'email de confirmation"""
        subject = "Mot de passe modifié - Couldiat"
        
        context = {
            'user': user,
            'site_name': 'Couldiatiformation',
            'site_url': settings.FRONTEND_URL,
            'changed_at': datetime.now().strftime('%d/%m/%Y à %H:%M')
        }
        
        # Version HTML avec fallback
        try:
            html_message = render_to_string('emails/password_changed.html', context)
        except Exception as e:
            print(f"⚠️ Erreur chargement template HTML: {e}")
            # Fallback: email HTML simple
            html_message = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 30px; border-radius: 10px;">
        <h1 style="color: #10B981;">✅ Couldiatiformation</h1>
        <p>Bonjour {user.get_full_name()},</p>
        <p>Votre mot de passe a été modifié avec succès le {context['changed_at']}.</p>
        <p style="color: #666;">Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.</p>
        <p><a href="mailto:support@couldiat.com" style="color: #10B981;">support@couldiat.com</a></p>
    </div>
</body>
</html>
            """
        
        text_message = f"""
Bonjour {user.get_full_name()},

Votre mot de passe sur Couldiatiformation a été modifié avec succès le {context['changed_at']}.

Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement à support@couldiat.com

Cordialement,
L'équipe Couldiatiformation
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class PasswordResetResendCodeView(APIView):
    """
    Renvoyer un nouveau code de réinitialisation
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Renvoyer un code de réinitialisation",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: 'Nouveau code envoyé',
            429: 'Trop de tentatives'
        }
    )
    def post(self, request):
        # Réutilise la même logique que PasswordResetRequestView
        return PasswordResetRequestView().post(request)