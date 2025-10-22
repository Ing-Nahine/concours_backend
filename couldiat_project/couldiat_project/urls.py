"""
URL Configuration principale pour Couldiat Backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuration Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Couldiat API",
        default_version='v1',
        description="Documentation de l'API Couldiat - Plateforme de gestion de concours",
        terms_of_service="https://www.couldiat.com/terms/",
        contact=openapi.Contact(email="contact@couldiat.com"),
        license=openapi.License(name="Couldiati"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Documentation Swagger
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # ✅ Téléchargement direct du schéma
    path('api/docs.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    path('auth/', include('accounts.urls')),
    path('concours/', include('concours.urls')),
    path('formation/', include('formation.urls')),
    path('api/admin/', include('admin_dashboard.urls')),
]


# Configuration pour servir les media files en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personnalisation de l'admin
admin.site.site_header = "Couldiat Administration"
admin.site.site_title = "Couldiat Admin"
admin.site.index_title = "Panneau d'administration"