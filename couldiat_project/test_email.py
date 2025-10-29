"""
Script de test pour vérifier la configuration email SendGrid
Placez ce fichier à la racine de votre projet Django
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'couldiat_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_configuration():
    """Test de configuration email"""
    print("=== TEST CONFIGURATION EMAIL ===\n")
    
    # Afficher la configuration
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NON DÉFINI'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"EMAIL_TIMEOUT: {settings.EMAIL_TIMEOUT}")
    print("\n" + "="*50 + "\n")
    
    # Vérifier que les variables critiques sont définies
    if not settings.EMAIL_HOST_PASSWORD:
        print("❌ ERREUR: EMAIL_HOST_PASSWORD n'est pas défini!")
        print("Vérifiez votre fichier .env")
        return False
    
    # Test d'envoi
    print("Envoi d'un email de test...")
    test_email = input("Entrez votre email pour le test: ").strip()
    
    if not test_email:
        print("❌ Email invalide")
        return False
    
    try:
        result = send_mail(
            subject='Test Email - Couldiat',
            message='Ceci est un email de test pour vérifier la configuration SendGrid.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result == 1:
            print(f"\n✅ Email envoyé avec succès à {test_email}!")
            print("Vérifiez votre boîte de réception (et spam)")
            return True
        else:
            print(f"\n❌ Échec de l'envoi (code retour: {result})")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'envoi:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        # Erreurs courantes et solutions
        if "authentication" in str(e).lower():
            print("\n💡 Solution: Vérifiez votre clé API SendGrid")
            print("   - Connectez-vous sur https://app.sendgrid.com/")
            print("   - Allez dans Settings > API Keys")
            print("   - Créez une nouvelle clé avec accès 'Mail Send'")
            print("   - Mettez à jour EMAIL_HOST_PASSWORD dans .env")
        
        elif "timeout" in str(e).lower():
            print("\n💡 Solution: Augmentez EMAIL_TIMEOUT dans settings.py")
            print("   ou vérifiez votre connexion internet")
        
        elif "connection" in str(e).lower():
            print("\n💡 Solution: Vérifiez que le port 587 n'est pas bloqué")
            print("   par votre pare-feu ou antivirus")
        
        return False

if __name__ == "__main__":
    test_email_configuration()