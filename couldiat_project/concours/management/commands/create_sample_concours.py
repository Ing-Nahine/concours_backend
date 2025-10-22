"""
Commande pour créer des concours de test
Usage: python manage.py create_sample_concours
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from concours.models import Concours


class Command(BaseCommand):
    help = 'Créer des concours de test'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        concours_data = [
            {
                'nom': 'Inspecteur du Trésor 2024',
                'type': 'Direct',
                'description': 'Concours d\'entrée direct à la fonction publique pour le poste d\'Inspecteur du Trésor. Formation de 2 ans à l\'ENA.',
                'date_inscription': today + timedelta(days=30),
                'date_concours': today + timedelta(days=90),
                'lieu': 'Ouagadougou, Lycée Bogodogo',
                'frais_inscription': 6000,
                'places_disponibles': 150,
                'conditions': [
                    'Être de nationalité burkinabè',
                    'Avoir au minimum le Baccalauréat série G2 ou équivalent',
                    'Âge maximum: 30 ans',
                    'Jouir de ses droits civiques',
                ],
                'est_ouvert': True,
            },
            {
                'nom': 'Contrôleur des Impôts 2024',
                'type': 'Direct',
                'description': 'Recrutement de contrôleurs des impôts pour l\'administration fiscale. Formation spécialisée garantie.',
                'date_inscription': today + timedelta(days=45),
                'date_concours': today + timedelta(days=100),
                'lieu': 'Ouagadougou, Lycée Zinda Kaboré',
                'frais_inscription': 5000,
                'places_disponibles': 100,
                'conditions': [
                    'Être de nationalité burkinabè',
                    'Avoir le BAC série A, C, D ou G',
                    'Âge: 18 à 28 ans',
                    'Casier judiciaire vierge',
                ],
                'est_ouvert': True,
            },
            {
                'nom': 'Enseignants du Primaire - Professionnel',
                'type': 'Professionnel',
                'description': 'Concours professionnel pour enseignants contractuels justifiant de 3 ans d\'expérience minimum.',
                'date_inscription': today + timedelta(days=20),
                'date_concours': today + timedelta(days=70),
                'lieu': 'Bobo-Dioulasso, ENEP',
                'frais_inscription': 4000,
                'places_disponibles': 200,
                'conditions': [
                    'Être enseignant contractuel',
                    'Justifier de 3 ans d\'expérience minimum',
                    'Avoir le BEPC + CAP ou BAC',
                    'Évaluation positive du chef d\'établissement',
                ],
                'est_ouvert': True,
            },
            {
                'nom': 'Agent de Santé 2024',
                'type': 'Direct',
                'description': 'Recrutement d\'agents de santé pour renforcer le personnel médical dans les formations sanitaires.',
                'date_inscription': today + timedelta(days=60),
                'date_concours': today + timedelta(days=120),
                'lieu': 'Ouagadougou, CHU Yalgado',
                'frais_inscription': 5500,
                'places_disponibles': 80,
                'conditions': [
                    'Être de nationalité burkinabè',
                    'Avoir le BAC série D ou équivalent',
                    'Âge: 18 à 32 ans',
                    'Aptitude physique',
                ],
                'est_ouvert': True,
            },
        ]
        
        created_count = 0
        for data in concours_data:
            concours, created = Concours.objects.get_or_create(
                nom=data['nom'],
                defaults=data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Concours créé: {concours.nom}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {created_count} concours créés avec succès!'))

