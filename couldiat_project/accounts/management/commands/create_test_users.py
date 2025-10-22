"""
Commande pour créer des utilisateurs de test
Usage: python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Créer des utilisateurs de test'

    def handle(self, *args, **options):
        # Admin
        if not User.objects.filter(email='admin@couldiat.com').exists():
            User.objects.create_superuser(
                email='admin@couldiat.com',
                password='admin123',
                nom='Admin',
                prenom='Super',
                telephone='+226 70 00 00 00',
                is_admin=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Admin créé: admin@couldiat.com / admin123'))
        
        # Candidat test
        if not User.objects.filter(email='candidat@test.com').exists():
            User.objects.create_user(
                email='candidat@test.com',
                password='test123',
                nom='Traoré',
                prenom='Fatou',
                telephone='+226 70 12 34 56'
            )
            self.stdout.write(self.style.SUCCESS('✓ Candidat créé: candidat@test.com / test123'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Utilisateurs de test créés avec succès!'))
