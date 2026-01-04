"""
Serializers pour l'application Accounts - Version Complète
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les informations utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'nom',
            'prenom',
            'telephone',
            'photo',
            'is_admin',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'nom',
            'prenom',
            'telephone',
            'password',
            'password_confirm',
        ]
    
    def validate(self, attrs):
        """Validation personnalisée"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Les mots de passe ne correspondent pas."
            })
        
        return attrs
    
    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nom=validated_data['nom'],
            prenom=validated_data['prenom'],
            telephone=validated_data['telephone'],
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Les mots de passe ne correspondent pas."
            })
        return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour le profil"""
    
    class Meta:
        model = User
        fields = ['nom', 'prenom', 'telephone', 'photo']
    
    def validate_photo(self, value):
        """Valider la taille de la photo"""
        if value and value.size > 2 * 1024 * 1024:  # 2MB
            raise serializers.ValidationError(
                "La taille de la photo ne doit pas dépasser 2MB."
            )
        return value


# ============================================================================
# NOUVEAUX SERIALIZERS POUR LA RÉINITIALISATION DE MOT DE PASSE
# ============================================================================

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour demander un code de réinitialisation"""
    email = serializers.EmailField(
        required=True,
        help_text="Adresse email du compte"
    )


class PasswordResetVerifyCodeSerializer(serializers.Serializer):
    """Serializer pour vérifier le code de réinitialisation"""
    email = serializers.EmailField(
        required=True,
        help_text="Adresse email du compte"
    )
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="Code à 6 chiffres reçu par email"
    )
    
    def validate_code(self, value):
        """Vérifier que le code ne contient que des chiffres"""
        if not value.isdigit():
            raise serializers.ValidationError("Le code doit contenir uniquement des chiffres.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation avec le nouveau mot de passe"""
    reset_token = serializers.CharField(
        required=True,
        help_text="Token de réinitialisation obtenu après vérification du code"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Nouveau mot de passe"
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmation du nouveau mot de passe"
    )
    
    def validate(self, attrs):
        """Vérifier que les deux mots de passe correspondent"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Les mots de passe ne correspondent pas."
            })
        return attrs