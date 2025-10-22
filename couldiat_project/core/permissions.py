"""
Permissions personnalisées
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission pour les administrateurs uniquement
    """
    message = "Vous devez être administrateur pour effectuer cette action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission pour le propriétaire de l'objet ou un administrateur
    """
    message = "Vous n'avez pas la permission d'accéder à cette ressource."
    
    def has_object_permission(self, request, view, obj):
        # Les admins ont toujours accès
        if request.user.is_admin:
            return True
        
        # Vérifier si l'objet a un attribut 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Sinon, vérifier si l'objet est l'utilisateur lui-même
        return obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission pour lecture pour tous, écriture pour le propriétaire uniquement
    """
    def has_object_permission(self, request, view, obj):
        # Les méthodes GET, HEAD ou OPTIONS sont autorisées
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Les méthodes d'écriture sont autorisées pour le propriétaire
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user