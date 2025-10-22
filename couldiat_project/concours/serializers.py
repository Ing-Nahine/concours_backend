"""
Serializers pour l'application Concours
"""
from rest_framework import serializers
from .models import Concours, Inscription, Paiement
from accounts.serializers import UserSerializer
from core.validators import validate_file_size, validate_image


class ConcoursListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des concours"""
    est_inscrit = serializers.SerializerMethodField()
    total_inscrits = serializers.ReadOnlyField()
    places_restantes = serializers.ReadOnlyField()
    
    class Meta:
        model = Concours
        fields = [
            'id',
            'nom',
            'type',
            'description',
            'date_inscription',
            'date_concours',
            'lieu',
            'frais_inscription',
            'places_disponibles',
            'places_restantes',
            'total_inscrits',
            'conditions',
            'est_ouvert',
            'est_inscrit',
            'image',
        ]
    
    def get_est_inscrit(self, obj):
        """Vérifie si l'utilisateur est déjà inscrit"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.inscriptions.filter(user=request.user).exists()
        return False


class ConcoursDetailSerializer(ConcoursListSerializer):
    """Serializer pour le détail d'un concours"""
    est_complet = serializers.ReadOnlyField()
    
    class Meta(ConcoursListSerializer.Meta):
        fields = ConcoursListSerializer.Meta.fields + ['est_complet', 'created_at']


class InscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une inscription"""
    concours_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Inscription
        fields = [
            'concours_id',
            'nom',
            'prenom',
            'date_naissance',
            'ville',
            'sexe',
            'cni',
            'photo',
            'telephone',
        ]
    
    def validate_cni(self, value):
        """Valider le fichier CNI"""
        validate_file_size(value, max_size_mb=5)
        return value
    
    def validate_photo(self, value):
        """Valider la photo"""
        validate_image(value)
        validate_file_size(value, max_size_mb=2)
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        user = self.context['request'].user
        concours_id = attrs.get('concours_id')
        
        # Vérifier que le concours existe
        try:
            concours = Concours.objects.get(id=concours_id)
        except Concours.DoesNotExist:
            raise serializers.ValidationError({
                'concours_id': 'Ce concours n\'existe pas.'
            })
        
        # Vérifier si le concours est ouvert
        if not concours.est_ouvert:
            raise serializers.ValidationError({
                'concours_id': 'Ce concours est fermé aux inscriptions.'
            })
        
        # Vérifier si le concours est complet
        if concours.est_complet:
            raise serializers.ValidationError({
                'concours_id': 'Ce concours est complet.'
            })
        
        # Vérifier si l'utilisateur est déjà inscrit
        if Inscription.objects.filter(user=user, concours=concours).exists():
            raise serializers.ValidationError({
                'concours_id': 'Vous êtes déjà inscrit à ce concours.'
            })
        
        attrs['concours'] = concours
        return attrs
    
    def create(self, validated_data):
        """Créer l'inscription"""
        concours = validated_data.pop('concours')
        validated_data.pop('concours_id')
        user = self.context['request'].user
        
        inscription = Inscription.objects.create(
            user=user,
            concours=concours,
            **validated_data
        )
        
        return inscription


class InscriptionListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les inscriptions"""
    nom_concours = serializers.CharField(source='concours.nom', read_only=True)
    date_concours = serializers.DateField(source='concours.date_concours', read_only=True)
    lieu = serializers.CharField(source='concours.lieu', read_only=True)
    a_paye = serializers.ReadOnlyField()
    
    class Meta:
        model = Inscription
        fields = [
            'id',
            'nom_concours',
            # 'date_inscription',
            'date_concours',
            'lieu',
            'statut',
            'numero_inscription',
            'a_paye',
            'created_at',
        ]


class InscriptionDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'une inscription"""
    concours = ConcoursListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    a_paye = serializers.ReadOnlyField()
    
    class Meta:
        model = Inscription
        fields = [
            'id',
            'user',
            'concours',
            'nom',
            'prenom',
            'date_naissance',
            'ville',
            'sexe',
            'cni',
            'photo',
            'telephone',
            'statut',
            'numero_inscription',
            'raison_rejet',
            'a_paye',
            'created_at',
        ]


class PaiementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un paiement"""
    inscription_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Paiement
        fields = [
            'inscription_id',
            'methode_paiement',
            'reference_transaction',
            'montant',
            'capture_ecran',
        ]
    
    def validate_capture_ecran(self, value):
        """Valider la capture d'écran"""
        validate_image(value)
        validate_file_size(value, max_size_mb=3)
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        user = self.context['request'].user
        inscription_id = attrs.get('inscription_id')
        
        # Vérifier que l'inscription existe et appartient à l'utilisateur
        try:
            inscription = Inscription.objects.get(id=inscription_id, user=user)
        except Inscription.DoesNotExist:
            raise serializers.ValidationError({
                'inscription_id': 'Cette inscription n\'existe pas ou ne vous appartient pas.'
            })
        
        # Vérifier qu'un paiement n'existe pas déjà
        if hasattr(inscription, 'paiement'):
            raise serializers.ValidationError({
                'inscription_id': 'Un paiement existe déjà pour cette inscription.'
            })
        
        # Vérifier que le montant correspond
        if attrs['montant'] != inscription.concours.frais_inscription:
            raise serializers.ValidationError({
                'montant': f'Le montant doit être de {inscription.concours.frais_inscription} FCFA.'
            })
        
        attrs['inscription'] = inscription
        return attrs
    
    def create(self, validated_data):
        """Créer le paiement"""
        inscription = validated_data.pop('inscription')
        validated_data.pop('inscription_id')
        
        paiement = Paiement.objects.create(
            inscription=inscription,
            **validated_data
        )
        
        return paiement


class PaiementDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'un paiement"""
    inscription = InscriptionDetailSerializer(read_only=True)
    
    class Meta:
        model = Paiement
        fields = [
            'id',
            'inscription',
            'methode_paiement',
            'reference_transaction',
            'montant',
            'capture_ecran',
            'statut',
            'raison_rejet',
            'created_at',
        ]