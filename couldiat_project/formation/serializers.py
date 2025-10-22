"""
Serializers pour l'application Formation avec Abonnement
"""
from rest_framework import serializers
from .models import Matiere, Chapitre, Question, ProgressionChapitre, Abonnement


class AbonnementSerializer(serializers.ModelSerializer):
    """Serializer pour l'abonnement"""
    est_actif = serializers.ReadOnlyField()
    jours_restants = serializers.ReadOnlyField()
    mois_restants = serializers.ReadOnlyField()
    
    class Meta:
        model = Abonnement
        fields = [
            'id',
            'date_debut',
            'date_fin',
            'statut',
            'montant_paye',
            'est_actif',
            'jours_restants',
            'mois_restants',
            'created_at',
        ]
        read_only_fields = ['id', 'date_fin', 'created_at']


class AbonnementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un abonnement"""
    
    class Meta:
        model = Abonnement
        fields = [
            'montant_paye',
            'reference_paiement',
        ]
    
    def create(self, validated_data):
        """Créer l'abonnement avec calcul automatique de la date de fin"""
        from datetime import date
        user = self.context['request'].user
        
        # Vérifier qu'un abonnement n'existe pas déjà
        if hasattr(user, 'abonnement'):
            raise serializers.ValidationError({
                'error': 'Vous avez déjà un abonnement actif.'
            })
        
        abonnement = Abonnement.objects.create(
            user=user,
            date_debut=date.today(),
            **validated_data
        )
        
        return abonnement


class MatiereListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des matières"""
    nombre_chapitres = serializers.ReadOnlyField()
    progression = serializers.SerializerMethodField()
    abonnement_requis = serializers.SerializerMethodField()
    
    class Meta:
        model = Matiere
        fields = [
            'id',
            'nom',
            'icon',
            'color',
            'nombre_chapitres',
            'progression',
            'abonnement_requis',
        ]
    
    def get_abonnement_requis(self, obj):
        """Vérifier si un abonnement est requis"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return True
        
        # Vérifier si l'utilisateur a un abonnement actif
        try:
            abonnement = request.user.abonnement
            return not abonnement.est_actif
        except Abonnement.DoesNotExist:
            return True
    
    def get_progression(self, obj):
        """Calculer la progression de l'utilisateur pour cette matière"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        user = request.user
        total_chapitres = obj.chapitres.count()
        
        if total_chapitres == 0:
            return 0
        
        chapitres_termines = ProgressionChapitre.objects.filter(
            user=user,
            chapitre__matiere=obj,
            statut='termine'
        ).count()
        
        return int((chapitres_termines / total_chapitres) * 100)


class ChapitreListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des chapitres"""
    statut = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    nombre_questions = serializers.ReadOnlyField()
    
    class Meta:
        model = Chapitre
        fields = [
            'id',
            'numero',
            'titre',
            'statut',
            'score',
            'nombre_questions',
        ]
    
    def get_statut(self, obj):
        """Récupérer le statut du chapitre pour l'utilisateur"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 'verrouille'
        
        try:
            progression = ProgressionChapitre.objects.get(
                user=request.user,
                chapitre=obj
            )
            return progression.statut
        except ProgressionChapitre.DoesNotExist:
            return 'verrouille'
    
    def get_score(self, obj):
        """Récupérer le score du chapitre pour l'utilisateur"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progression = ProgressionChapitre.objects.get(
                user=request.user,
                chapitre=obj
            )
            return progression.meilleur_score
        except ProgressionChapitre.DoesNotExist:
            return None


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer pour les questions (SANS la réponse correcte)"""
    
    class Meta:
        model = Question
        fields = [
            'id',
            'question',
            'options',
            'explication',
        ]


class QuestionAdminSerializer(serializers.ModelSerializer):
    """Serializer pour les questions (AVEC la réponse correcte - Admin only)"""
    
    class Meta:
        model = Question
        fields = [
            'id',
            'question',
            'options',
            'correct_answer',
            'explication',
            'ordre',
        ]


class ReponseSerializer(serializers.Serializer):
    """Serializer pour une réponse à une question"""
    question_id = serializers.IntegerField()
    reponse_index = serializers.IntegerField(min_value=0, max_value=3)


class SubmitQCMSerializer(serializers.Serializer):
    """Serializer pour soumettre les résultats d'un QCM"""
    chapitre_id = serializers.IntegerField()
    temps_ecoule = serializers.IntegerField(min_value=0)
    reponses = serializers.ListField(
        child=ReponseSerializer(),
        min_length=1
    )
    
    def validate_chapitre_id(self, value):
        """Valider que le chapitre existe"""
        try:
            chapitre = Chapitre.objects.get(id=value)
        except Chapitre.DoesNotExist:
            raise serializers.ValidationError("Ce chapitre n'existe pas.")
        return value
    
    def validate_reponses(self, value):
        """Valider que toutes les questions existent"""
        question_ids = [r['question_id'] for r in value]
        existing_questions = Question.objects.filter(id__in=question_ids).count()
        
        if existing_questions != len(question_ids):
            raise serializers.ValidationError(
                "Certaines questions n'existent pas."
            )
        
        return value


class ProgressionChapitreSerializer(serializers.ModelSerializer):
    """Serializer pour la progression d'un chapitre"""
    chapitre = ChapitreListSerializer(read_only=True)
    
    class Meta:
        model = ProgressionChapitre
        fields = [
            'id',
            'chapitre',
            'statut',
            'score',
            'meilleur_score',
            'temps_ecoule',
            'tentatives',
            'created_at',
            'updated_at',
        ]