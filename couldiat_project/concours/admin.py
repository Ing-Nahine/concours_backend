"""
Configuration de l'interface admin pour Concours
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Concours, Inscription, Paiement


@admin.register(Concours)
class ConcoursAdmin(admin.ModelAdmin):
    """Admin pour les concours"""
    
    list_display = [
        'nom',
        'type',
        'date_concours',
        'date_inscription',
        'total_inscrits',
        'places_disponibles',
        'est_ouvert_badge',
        'created_at'
    ]
    list_filter = ['type', 'est_ouvert', 'date_concours']
    search_fields = ['nom', 'description', 'lieu']
    readonly_fields = ['created_at', 'updated_at', 'total_inscrits']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'type', 'description', 'image')
        }),
        ('Dates et lieu', {
            'fields': ('date_inscription', 'date_concours', 'lieu')
        }),
        ('Places et frais', {
            'fields': ('places_disponibles', 'frais_inscription')
        }),
        ('Conditions', {
            'fields': ('conditions', 'est_ouvert')
        }),
        ('Statistiques', {
            'fields': ('total_inscrits',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def est_ouvert_badge(self, obj):
        if obj.est_ouvert:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Ouvert</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Fermé</span>'
        )
    est_ouvert_badge.short_description = 'Statut'


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    """Admin pour les inscriptions"""
    
    list_display = [
        'numero_inscription',
        'get_candidat',
        'get_concours',
        'statut_badge',
        'a_paye_badge',
        'created_at'
    ]
    list_filter = ['statut', 'sexe', 'concours__type', 'created_at']
    search_fields = [
        'nom',
        'prenom',
        'telephone',
        'numero_inscription',
        'user__email',
        'concours__nom'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'numero_inscription',
        'a_paye'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Inscription', {
            'fields': ('user', 'concours', 'statut', 'numero_inscription')
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'ville', 'sexe')
        }),
        ('Documents', {
            'fields': ('cni', 'photo')
        }),
        ('Contact', {
            'fields': ('telephone',)
        }),
        ('Validation', {
            'fields': ('raison_rejet',)
        }),
        ('Paiement', {
            'fields': ('a_paye',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_candidat(self, obj):
        return f"{obj.prenom} {obj.nom}"
    get_candidat.short_description = 'Candidat'
    
    def get_concours(self, obj):
        return obj.concours.nom
    get_concours.short_description = 'Concours'
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': 'orange',
            'confirmee': 'green',
            'annulee': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.statut, 'gray'),
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    
    def a_paye_badge(self, obj):
        if obj.a_paye:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Payé</span>'
            )
        return format_html(
            '<span style="color: orange;">En attente</span>'
        )
    a_paye_badge.short_description = 'Paiement'


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    """Admin pour les paiements"""
    
    list_display = [
        'reference_transaction',
        'get_candidat',
        'methode_paiement',
        'montant',
        'statut_badge',
        'created_at'
    ]
    list_filter = ['statut', 'methode_paiement', 'created_at']
    search_fields = [
        'reference_transaction',
        'inscription__nom',
        'inscription__prenom',
        'inscription__user__email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Paiement', {
            'fields': (
                'inscription',
                'methode_paiement',
                'reference_transaction',
                'montant'
            )
        }),
        ('Preuve', {
            'fields': ('capture_ecran',)
        }),
        ('Validation', {
            'fields': ('statut', 'raison_rejet')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_candidat(self, obj):
        return f"{obj.inscription.prenom} {obj.inscription.nom}"
    get_candidat.short_description = 'Candidat'
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': 'orange',
            'valide': 'green',
            'rejete': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.statut, 'gray'),
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'