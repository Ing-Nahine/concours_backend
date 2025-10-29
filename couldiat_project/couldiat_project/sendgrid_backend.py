"""
Backend Email personnalisé utilisant l'API SendGrid
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import requests
import json
import logging

logger = logging.getLogger(__name__)


class SendGridAPIBackend(BaseEmailBackend):
    """
    Backend email utilisant l'API HTTP de SendGrid
    Plus fiable que SMTP sur les plateformes cloud
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
        
        if not self.api_key:
            logger.error("SENDGRID_API_KEY n'est pas configuré dans settings!")
    
    def send_messages(self, email_messages):
        """
        Envoie une liste de messages email
        """
        if not email_messages:
            return 0
        
        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        
        return num_sent
    
    def _send(self, message):
        """
        Envoie un seul message via l'API SendGrid
        """
        if not self.api_key:
            logger.error("❌ SENDGRID_API_KEY manquant - email non envoyé")
            return False
        
        try:
            # Préparer les données pour l'API SendGrid
            data = {
                "personalizations": [
                    {
                        "to": [{"email": recipient} for recipient in message.to],
                        "subject": message.subject
                    }
                ],
                "from": {
                    "email": self._extract_email(message.from_email),
                    "name": self._extract_name(message.from_email)
                },
                "content": []
            }
            
            # Ajouter le contenu texte
            if message.body:
                data["content"].append({
                    "type": "text/plain",
                    "value": message.body
                })
            
            # Ajouter le contenu HTML si disponible
            if hasattr(message, 'alternatives') and message.alternatives:
                for content, mimetype in message.alternatives:
                    if mimetype == "text/html":
                        data["content"].append({
                            "type": "text/html",
                            "value": content
                        })
            
            # Envoyer la requête à l'API SendGrid
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )
            
            # Vérifier le statut
            if response.status_code in [200, 202]:
                logger.info(f"✅ Email envoyé avec succès à {message.to}")
                return True
            else:
                error_msg = f"SendGrid API Error {response.status_code}: {response.text}"
                logger.error(f"❌ {error_msg}")
                if not self.fail_silently:
                    print(f"❌ {error_msg}")
                return False
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout lors de l'appel à l'API SendGrid"
            logger.error(f"❌ {error_msg}")
            if not self.fail_silently:
                print(f"❌ {error_msg}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur SendGrid API: {e}")
            if not self.fail_silently:
                print(f"❌ Erreur SendGrid API: {e}")
            return False
    
    def _extract_email(self, email_string):
        """
        Extrait l'email de 'Name <email@example.com>'
        """
        if '<' in email_string and '>' in email_string:
            return email_string.split('<')[1].split('>')[0].strip()
        return email_string.strip()
    
    def _extract_name(self, email_string):
        """
        Extrait le nom de 'Name <email@example.com>'
        """
        if '<' in email_string:
            return email_string.split('<')[0].strip()
        return ""