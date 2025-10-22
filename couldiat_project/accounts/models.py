"""
Modèles pour l'application Accounts
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Créer et sauvegarder un utilisateur normal"""
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Créer et sauvegarder un superutilisateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour Couldiat
    Utilise l'email comme identifiant unique au lieu du username
    """
    username = None
    email = models.EmailField(_('adresse email'), unique=True)
    nom = models.CharField(_('nom'), max_length=100)
    prenom = models.CharField(_('prénom'), max_length=100)
    telephone = models.CharField(_('téléphone'), max_length=20)
    photo = models.ImageField(
        _('photo de profil'),
        upload_to='users/photos/',
        null=True,
        blank=True
    )
    is_admin = models.BooleanField(
        _('statut administrateur'),
        default=False,
        help_text=_('Désigne si l\'utilisateur peut accéder au dashboard admin')
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.prenom} {self.nom}"
    
    def get_short_name(self):
        """Retourne le prénom de l'utilisateur"""
        return self.prenom
    
    @property
    def nombre_inscriptions(self):
        """Retourne le nombre d'inscriptions de l'utilisateur"""
        return self.inscriptions.count()
    
    @property
    def inscriptions_confirmees(self):
        """Retourne le nombre d'inscriptions confirmées"""
        return self.inscriptions.filter(statut='confirmee').count()