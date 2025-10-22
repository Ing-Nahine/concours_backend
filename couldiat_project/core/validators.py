"""
Validateurs personnalisés pour les fichiers
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_size(file, max_size_mb=5):
    """
    Valider la taille d'un fichier
    
    Args:
        file: Le fichier à valider
        max_size_mb: Taille maximale en MB (défaut: 5MB)
    """
    max_size = max_size_mb * 1024 * 1024  # Conversion en bytes
    
    if file.size > max_size:
        raise ValidationError(
            _(f'La taille du fichier ne doit pas dépasser {max_size_mb}MB. '
              f'Taille actuelle: {file.size / (1024 * 1024):.2f}MB')
        )


def validate_image(file):
    """
    Valider qu'un fichier est bien une image
    
    Args:
        file: Le fichier à valider
    """
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    valid_mime_types = ['image/jpeg', 'image/png', 'image/webp']
    
    # Vérifier l'extension
    ext = file.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            _(f'Format non supporté. Utilisez: {", ".join(valid_extensions).upper()}')
        )
    
    # Vérifier le MIME type
    if hasattr(file, 'content_type') and file.content_type not in valid_mime_types:
        raise ValidationError(
            _('Le type de fichier n\'est pas valide. Utilisez une image JPG, PNG ou WEBP.')
        )


def validate_pdf(file):
    """
    Valider qu'un fichier est bien un PDF
    
    Args:
        file: Le fichier à valider
    """
    valid_extensions = ['pdf']
    valid_mime_types = ['application/pdf']
    
    # Vérifier l'extension
    ext = file.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            _('Format non supporté. Le fichier doit être un PDF.')
        )
    
    # Vérifier le MIME type
    if hasattr(file, 'content_type') and file.content_type not in valid_mime_types:
        raise ValidationError(
            _('Le type de fichier n\'est pas valide. Utilisez un PDF.')
        )


def validate_document(file):
    """
    Valider qu'un fichier est une image ou un PDF
    
    Args:
        file: Le fichier à valider
    """
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp', 'pdf']
    
    ext = file.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            _(f'Format non supporté. Utilisez: {", ".join(valid_extensions).upper()}')
        )