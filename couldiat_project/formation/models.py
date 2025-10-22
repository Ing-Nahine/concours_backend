"""
Modèles pour l'application Formation (QCM) avec Abonnement
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime, date


class Abonnement(models.Model):
    """
    Abonnement à la formation
    Période : 1er Octobre - 31 Juillet (année scolaire)
    """
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('suspendu', 'Suspendu'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='abonnement',
        verbose_name=_('utilisateur')
    )
    date_debut = models.DateField(
        _('date de début'),
        help_text=_("Date d'activation de l'abonnement")
    )
    date_fin = models.DateField(
        _('date de fin'),
        help_text=_("Toujours le 31 juillet de l'année scolaire en cours")
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif'
    )
    montant_paye = models.IntegerField(
        _('montant payé'),
        help_text=_("Montant de l'abonnement en FCFA")
    )
    reference_paiement = models.CharField(
        _('référence paiement'),
        max_length=100,
        blank=True
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('abonnement')
        verbose_name_plural = _('abonnements')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Abonnement {self.user.get_full_name()} - {self.get_statut_display()}"
    
    def save(self, *args, **kwargs):
        """Calculer automatiquement la date de fin au 31 juillet"""
        if not self.date_fin:
            self.date_fin = self.calculer_date_fin()
        super().save(*args, **kwargs)
    
    @staticmethod
    def calculer_date_fin():
        """
        Calculer la date de fin : toujours le 31 juillet
        
        Logique :
        - Si inscription entre le 1er octobre et le 31 juillet : fin au 31 juillet de la même année scolaire
        - Si inscription entre le 1er août et le 30 septembre : fin au 31 juillet de l'année suivante
        """
        today = date.today()
        current_year = today.year
        
        # Si on est entre août et septembre (avant le début de l'année scolaire)
        if today.month >= 8:
            # La fin est au 31 juillet de l'année SUIVANTE
            return date(current_year + 1, 7, 31)
        else:
            # La fin est au 31 juillet de l'année EN COURS
            return date(current_year, 7, 31)
    
    @property
    def est_actif(self):
        """Vérifie si l'abonnement est toujours actif"""
        today = date.today()
        return self.statut == 'actif' and self.date_fin >= today
    
    @property
    def jours_restants(self):
        """Calcule le nombre de jours restants"""
        if not self.est_actif:
            return 0
        today = date.today()
        delta = self.date_fin - today
        return max(0, delta.days)
    
    @property
    def mois_restants(self):
        """Calcule le nombre de mois restants (approximatif)"""
        return round(self.jours_restants / 30)
    
    def verifier_expiration(self):
        """Vérifier et mettre à jour le statut si expiré"""
        if self.est_actif and date.today() > self.date_fin:
            self.statut = 'expire'
            self.save()
            return True
        return False


class Matiere(models.Model):
    """Matières de formation (QCM)"""
    
    nom = models.CharField(_('nom'), max_length=100, unique=True)
    icon = models.CharField(
        _('icône'),
        max_length=10,
        help_text=_("Emoji ou icône (ex: 📘, 🔬)")
    )
    color = models.CharField(
        _('couleur'),
        max_length=7,
        help_text=_("Couleur hex (ex: #6366F1)")
    )
    ordre = models.IntegerField(_('ordre'), default=0)
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('matière')
        verbose_name_plural = _('matières')
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    @property
    def nombre_chapitres(self):
        """Retourne le nombre de chapitres"""
        return self.chapitres.count()
    
    @property
    def nombre_questions(self):
        """Retourne le nombre total de questions"""
        return sum(chapitre.questions.count() for chapitre in self.chapitres.all())


class Chapitre(models.Model):
    """Chapitres d'une matière"""
    
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='chapitres',
        verbose_name=_('matière')
    )
    numero = models.IntegerField(_('numéro'))
    titre = models.CharField(_('titre'), max_length=200)
    ordre = models.IntegerField(_('ordre'), default=0)
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('chapitre')
        verbose_name_plural = _('chapitres')
        ordering = ['ordre', 'numero']
        unique_together = ['matiere', 'numero']
    
    def __str__(self):
        return f"{self.matiere.nom} - Chapitre {self.numero}: {self.titre}"
    
    @property
    def nombre_questions(self):
        """Retourne le nombre de questions du chapitre"""
        return self.questions.count()


class Question(models.Model):
    """Questions QCM d'un chapitre"""
    
    chapitre = models.ForeignKey(
        Chapitre,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('chapitre')
    )
    question = models.TextField(_('question'))
    options = models.JSONField(
        _('options'),
        default=list,
        help_text=_("Tableau de 4 options ['opt1', 'opt2', 'opt3', 'opt4']")
    )
    correct_answer = models.IntegerField(
        _('réponse correcte'),
        help_text=_("Index de la bonne réponse (0-3)")
    )
    explication = models.TextField(_('explication'), blank=True)
    ordre = models.IntegerField(_('ordre'), default=0)
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ['ordre', 'id']
    
    def __str__(self):
        return f"Question {self.id} - {self.chapitre}"
    
    def clean(self):
        """Validation du modèle"""
        from django.core.exceptions import ValidationError
        
        # Vérifier que options contient 4 éléments
        if not isinstance(self.options, list) or len(self.options) != 4:
            raise ValidationError({
                'options': _('Les options doivent être un tableau de 4 éléments.')
            })
        
        # Vérifier que correct_answer est entre 0 et 3
        if not (0 <= self.correct_answer <= 3):
            raise ValidationError({
                'correct_answer': _('La réponse correcte doit être entre 0 et 3.')
            })


class ProgressionChapitre(models.Model):
    """Progression d'un utilisateur sur un chapitre"""
    
    STATUT_CHOICES = [
        ('verrouille', 'Verrouillé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progressions',
        verbose_name=_('utilisateur')
    )
    chapitre = models.ForeignKey(
        Chapitre,
        on_delete=models.CASCADE,
        related_name='progressions',
        verbose_name=_('chapitre')
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUT_CHOICES,
        default='verrouille'
    )
    score = models.IntegerField(
        _('score'),
        null=True,
        blank=True,
        help_text=_("Score en pourcentage (0-100)")
    )
    temps_ecoule = models.IntegerField(
        _('temps écoulé'),
        null=True,
        blank=True,
        help_text=_("Temps en secondes")
    )
    tentatives = models.IntegerField(_('nombre de tentatives'), default=0)
    meilleur_score = models.IntegerField(
        _('meilleur score'),
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('progression chapitre')
        verbose_name_plural = _('progressions chapitres')
        unique_together = ['user', 'chapitre']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.chapitre} ({self.get_statut_display()})"
    
    def save(self, *args, **kwargs):
        """Mettre à jour le meilleur score"""
        if self.score is not None:
            if self.meilleur_score is None or self.score > self.meilleur_score:
                self.meilleur_score = self.score
        super().save(*args, **kwargs)