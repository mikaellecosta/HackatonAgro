"""
URLs do app whatsapp.

Inclui apenas o webhook que a Evolution chama. Mantemos sem `app_name`
(sem namespace) porque é um endpoint externo — ninguém faz `reverse()`
dele dentro do Django, a URL é registrada na Evolution via
`POST /webhook/set/<instance>`.

A URL final fica `/webhooks/evolution/` quando este urls.py é incluído
em `setup/urls.py` com prefixo vazio. Mudar o caminho aqui obriga a
re-registrar o webhook na Evolution — evite.
"""
from django.urls import path

from whatsapp.views import evolution_webhook


urlpatterns = [
    path(
        'webhooks/evolution/',
        evolution_webhook,
        name='evolution_webhook',
    ),
]
