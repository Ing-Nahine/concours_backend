"""
Modèles pour l'application Concours
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class Concours(models.Model):
    """Concours disponibles sur la plateforme"""
    
    TYPE_CHOICES = [
        ('Direct', 'Concours Direct'),
        ('Professionnel', 'Concours Professionnel'),
    ]
    
    nom = models.CharField(_('nom du concours'), max_length=200)
    type= models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(_('description'))
    date_inscription = models.DateField(
        _('date limite d\'inscription'),
        help_text=_("Date limite pour s'inscrire au concours")
    )
    date_concours = models.DateField(
        _('date du concours'),
        help_text=_("Date à laquelle se déroulera le concours")
    )
    lieu = models.CharField(_('lieu'), max_length=200)
    frais_inscription = models.IntegerField(
        _('frais d\'inscription'),
        help_text=_("Montant en FCFA")
    )
    places_disponibles = models.IntegerField(_('places disponibles'))
    conditions = models.JSONField(
        _('conditions'),
        default=list,
        help_text=_("Liste des conditions d'inscription (array de strings)")
    )
    est_ouvert = models.BooleanField(_('est ouvert'), default=True)
    image = models.ImageField(
        _('image'),
        upload_to='concours/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('concours')
        verbose_name_plural = _('concours')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nom
    
    @property
    def total_inscrits(self):
        """Nombre total d'inscrits confirmés"""
        return self.inscriptions.filter(statut='confirmee').count()
    
    @property
    def places_restantes(self):
        """Nombre de places restantes"""
        return max(0, self.places_disponibles - self.total_inscrits)
    
    @property
    def est_complet(self):
        """Vérifie si le concours est complet"""
        return self.places_restantes == 0


class Inscription(models.Model):
    """Inscription d'un candidat à un concours"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée/Rejetée'),
    ]
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    # Relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name=_('utilisateur')
    )
    concours = models.ForeignKey(
        Concours,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name=_('concours')
    )
    
    # Informations personnelles (Étape 1)
    nom = models.CharField(_('nom'), max_length=100)
    prenom = models.CharField(_('prénom'), max_length=100)
    date_naissance = models.DateField(_('date de naissance'))
    ville = models.CharField(_('ville'), max_length=100)
    sexe = models.CharField(_('sexe'), max_length=1, choices=SEXE_CHOICES)
    
    # Documents (Étape 1)
    cni = models.FileField(
        _('CNI'),
        upload_to='inscriptions/cni/',
        help_text=_("Document CNI (PDF ou image)")
    )
    photo = models.ImageField(
        _('photo d\'identité'),
        upload_to='inscriptions/photos/'
    )
    
    # Contact (Étape 2)
    telephone = models.CharField(_('téléphone'), max_length=20)
    
    # Statut
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    numero_inscription = models.CharField(
        _('numéro d\'inscription'),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )
    raison_rejet = models.TextField(
        _('raison du rejet'),
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('inscription')
        verbose_name_plural = _('inscriptions')
        unique_together = ['user', 'concours']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.concours.nom}"
    
    def save(self, *args, **kwargs):
        """Générer le numéro d'inscription lors de la confirmation"""
        if self.statut == 'confirmee' and not self.numero_inscription:
            self.numero_inscription = self.generer_numero_inscription()
        super().save(*args, **kwargs)
    
    def generer_numero_inscription(self):
        """Génère un numéro unique : INS-YYYY-XXXXXX"""
        year = datetime.now().year
        count = Inscription.objects.filter(
            numero_inscription__startswith=f'INS-{year}'
        ).count() + 1
        return f'INS-{year}-{count:06d}'
    
    @property
    def a_paye(self):
        """Vérifie si le paiement est validé"""
        return hasattr(self, 'paiement') and self.paiement.statut == 'valide'


class Paiement(models.Model):
    """Paiement d'une inscription"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    
    METHODE_CHOICES = [
        ('orange_money', 'Orange Money'),
        ('moov_money', 'Moov Money'),
    ]
    
    inscription = models.OneToOneField(
        Inscription,
        on_delete=models.CASCADE,
        related_name='paiement',
        verbose_name=_('inscription')
    )
    methode_paiement = models.CharField(
        _('méthode de paiement'),
        max_length=20,
        choices=METHODE_CHOICES
    )
    reference_transaction = models.CharField(
        _('référence transaction'),
        max_length=100
    )
    montant = models.IntegerField(_('montant'), help_text=_("Montant en FCFA"))
    capture_ecran = models.ImageField(
        _('capture d\'écran'),
        upload_to='paiements/preuves/',
        help_text=_("Preuve de paiement")
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    raison_rejet = models.TextField(
        _('raison du rejet'),
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('paiement')
        verbose_name_plural = _('paiements')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Paiement {self.reference_transaction} - {self.get_statut_display()}"