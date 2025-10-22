"""
Configuration de l'interface admin pour Formation
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Matiere, Chapitre, Question, ProgressionChapitre


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    """Admin pour les matières"""
    
    list_display = ['nom', 'icon', 'color_badge', 'nombre_chapitres', 'ordre', 'created_at']
    list_editable = ['ordre']
    search_fields = ['nom']
    ordering = ['ordre', 'nom']
    
    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_badge.short_description = 'Couleur'


class QuestionInline(admin.TabularInline):
    """Inline pour les questions d'un chapitre"""
    model = Question
    extra = 1
    fields = ['question', 'correct_answer', 'ordre']
    ordering = ['ordre']


@admin.register(Chapitre)
class ChapitreAdmin(admin.ModelAdmin):
    """Admin pour les chapitres"""
    
    list_display = ['__str__', 'matiere', 'numero', 'nombre_questions', 'ordre']
    list_filter = ['matiere']
    search_fields = ['titre', 'matiere__nom']
    list_editable = ['ordre']
    ordering = ['matiere', 'ordre']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Chapitre', {
            'fields': ('matiere', 'numero', 'titre', 'ordre')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin pour les questions"""
    
    list_display = ['id', 'get_chapitre', 'question_preview', 'correct_answer', 'ordre']
    list_filter = ['chapitre__matiere', 'chapitre']
    search_fields = ['question', 'chapitre__titre']
    list_editable = ['ordre']
    ordering = ['chapitre', 'ordre']
    
    fieldsets = (
        ('Question', {
            'fields': ('chapitre', 'question', 'options', 'correct_answer', 'explication', 'ordre')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_chapitre(self, obj):
        return obj.chapitre
    get_chapitre.short_description = 'Chapitre'
    
    def question_preview(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Question'


@admin.register(ProgressionChapitre)
class ProgressionChapitreAdmin(admin.ModelAdmin):
    """Admin pour les progressions"""
    
    list_display = [
        'get_user',
        'get_matiere',
        'chapitre',
        'statut_badge',
        'score_badge',
        'tentatives',
        'updated_at'
    ]
    list_filter = ['statut', 'chapitre__matiere', 'updated_at']
    search_fields = [
        'user__email',
        'user__nom',
        'user__prenom',
        'chapitre__titre'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_user(self, obj):
        return obj.user.get_full_name()
    get_user.short_description = 'Utilisateur'
    
    def get_matiere(self, obj):
        return obj.chapitre.matiere.nom
    get_matiere.short_description = 'Matière'
    
    def statut_badge(self, obj):
        colors = {
            'verrouille': 'gray',
            'en_cours': 'orange',
            'termine': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.statut, 'gray'),
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    
    def score_badge(self, obj):
        if obj.meilleur_score is None:
            return '-'
        
        color = 'green' if obj.meilleur_score >= 70 else 'orange' if obj.meilleur_score >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            obj.meilleur_score
        )
    score_badge.short_description = 'Meilleur score'