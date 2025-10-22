from django.core.management.base import BaseCommand
from accounts.models import User
import os

class Command(BaseCommand):
    help = 'Crée le superuser initial si inexistant'

    def handle(self, *args, **kwargs):
        # Récupérer les infos depuis les variables d'environnement (Render)
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'combarinahine@gmail.com')
        nom = os.environ.get('DJANGO_SUPERUSER_NOM', 'GBABLI MATHIEU')
        prenom = os.environ.get('DJANGO_SUPERUSER_PRENOM', 'Nahine')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'BARIcom0622')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                nom=nom,
                prenom=prenom,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} créé !"))
        else:
            self.stdout.write("Superuser existe déjà.")
