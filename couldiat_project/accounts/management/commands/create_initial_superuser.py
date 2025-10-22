from django.core.management.base import BaseCommand
from accounts.models import User
import os

class Command(BaseCommand):
    help = 'Crée ou met à jour le superuser initial'

    def handle(self, *args, **kwargs):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'combarinahine@gmail.com')
        nom = os.environ.get('DJANGO_SUPERUSER_NOM', 'GBABLI MATHIEU')
        prenom = os.environ.get('DJANGO_SUPERUSER_PRENOM', 'Nahine')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'BARIcom0622')

        user, created = User.objects.get_or_create(email=email)
        user.nom = nom
        user.prenom = prenom
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} créé !"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} mis à jour !"))
