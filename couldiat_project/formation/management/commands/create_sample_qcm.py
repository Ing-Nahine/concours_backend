"""
Commande pour créer des QCM de test
Usage: python manage.py create_sample_qcm
"""
from django.core.management.base import BaseCommand
from formation.models import Matiere, Chapitre, Question


class Command(BaseCommand):
    help = 'Créer des QCM de test'

    def handle(self, *args, **options):
        # Créer la matière Français
        matiere, created = Matiere.objects.get_or_create(
            nom='Français',
            defaults={
                'icon': '📘',
                'color': '#6366F1',
                'ordre': 1
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Matière créée: {matiere.nom}'))
        
        # Créer le Chapitre 1
        chapitre1, created = Chapitre.objects.get_or_create(
            matiere=matiere,
            numero=1,
            defaults={
                'titre': 'Les bases de la grammaire',
                'ordre': 1
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Chapitre créé: {chapitre1.titre}'))
            
            # Créer des questions pour le chapitre 1
            questions_data = [
                {
                    'question': 'Quelle est la nature du mot "rapidement" ?',
                    'options': ['Adjectif', 'Adverbe', 'Verbe', 'Nom'],
                    'correct_answer': 1,
                    'explication': 'Un adverbe est un mot invariable qui modifie le sens d\'un verbe, d\'un adjectif ou d\'un autre adverbe.',
                    'ordre': 1
                },
                {
                    'question': 'Combien y a-t-il de groupes de verbes en français ?',
                    'options': ['2 groupes', '3 groupes', '4 groupes', '5 groupes'],
                    'correct_answer': 1,
                    'explication': 'Il existe 3 groupes de verbes en français : 1er groupe (-er), 2ème groupe (-ir), 3ème groupe (irréguliers).',
                    'ordre': 2
                },
                {
                    'question': 'Quel est le COD dans la phrase "Marie mange une pomme" ?',
                    'options': ['Marie', 'mange', 'une pomme', 'Il n\'y a pas de COD'],
                    'correct_answer': 2,
                    'explication': 'Le COD (Complément d\'Objet Direct) répond à la question "quoi ?" ou "qui ?". Marie mange QUOI ? Une pomme.',
                    'ordre': 3
                },
                {
                    'question': 'Quelle est la fonction de "très" dans "Il est très grand" ?',
                    'options': ['Adverbe', 'Adjectif', 'Pronom', 'Préposition'],
                    'correct_answer': 0,
                    'explication': '"Très" est un adverbe qui modifie l\'adjectif "grand" en intensifiant son sens.',
                    'ordre': 4
                },
            ]
            
            for q_data in questions_data:
                Question.objects.create(chapitre=chapitre1, **q_data)
            
            self.stdout.write(self.style.SUCCESS(f'✓ {len(questions_data)} questions créées'))
        
        # Créer le Chapitre 2
        chapitre2, created = Chapitre.objects.get_or_create(
            matiere=matiere,
            numero=2,
            defaults={
                'titre': 'La conjugaison des verbes',
                'ordre': 2
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Chapitre créé: {chapitre2.titre}'))
            
            questions_data2 = [
                {
                    'question': 'Quelle est la terminaison du verbe "finir" au présent (je) ?',
                    'options': ['finis', 'finit', 'finissons', 'finissent'],
                    'correct_answer': 0,
                    'explication': 'Le verbe "finir" du 2ème groupe se conjugue : je finis, tu finis, il finit...',
                    'ordre': 1
                },
                {
                    'question': 'Quel est l\'auxiliaire du verbe "aller" au passé composé ?',
                    'options': ['avoir', 'être', 'les deux', 'aucun'],
                    'correct_answer': 1,
                    'explication': 'Le verbe "aller" utilise l\'auxiliaire ÊTRE au passé composé : je suis allé(e).',
                    'ordre': 2
                },
            ]
            
            for q_data in questions_data2:
                Question.objects.create(chapitre=chapitre2, **q_data)
            
            self.stdout.write(self.style.SUCCESS(f'✓ {len(questions_data2)} questions créées'))
        
        # Créer la matière Mathématiques
        matiere_math, created = Matiere.objects.get_or_create(
            nom='Mathématiques',
            defaults={
                'icon': '🔢',
                'color': '#10B981',
                'ordre': 2
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Matière créée: {matiere_math.nom}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ QCM de test créés avec succès!'))

