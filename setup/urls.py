"""
URL configuration for setup project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # whatsapp vem antes de core porque ambos montam em '' — manter o
    # webhook estável em /webhooks/evolution/ (não retira nada do core,
    # só evita confusão se alguém futuramente adicionar overlap de path).
    path('', include('whatsapp.urls')),
    path('', include('core.urls', namespace='core')),
]

# Servir media files em modo DEBUG (uploads de foto de perfil etc.).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
