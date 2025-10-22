"""
URL Configuration principale pour Couldiat Backend
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

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

# Vue simple pour permettre le téléchargement direct du JSON
def download_doc(request):
    """
    Permet de télécharger la documentation Swagger au format JSON
    """
    from drf_yasg.generators import OpenAPISchemaGenerator
    generator = OpenAPISchemaGenerator(info=schema_view.info)
    schema = generator.get_schema(request=request, public=True)
    return JsonResponse(schema, safe=False)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # Documentation API
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # ✅ URL pour télécharger la doc JSON
    path('api/docs/download/', download_doc, name='download_doc'),

    # API Endpoints
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
