"""
Webhooks de eventos da Evolution API.

Como decidimos não persistir mensagens no Django (o histórico fica no
Postgres da Evolution), este endpoint apenas roteia eventos para
handlers de domínio. Nenhuma escrita em modelo é feita aqui — quem
precisar reagir a uma mensagem importa de `whatsapp.services` e
dispara o fluxo apropriado.

Eventos relevantes (registrados em /webhook/set):
    MESSAGES_UPSERT   — chegada/atualização de mensagem (entrada e saída)
    CONNECTION_UPDATE — mudança de estado da instância (open/close/...)
    SEND_MESSAGE      — confirmação de envio iniciado pelo Django

Resposta sempre rápida (204) — a Evolution refaz a chamada se demorar
mais do que ~30s, então qualquer trabalho pesado deve ir para um
worker/cron, não acontecer aqui.
"""
from __future__ import annotations

import json
import logging

from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


def _autorizado(request) -> bool:
    """
    Valida origem do webhook. Se EVOLUTION_WEBHOOK_TOKEN está configurado,
    exigimos o header `X-Webhook-Token`; caso contrário, validamos pela
    apikey global da Evolution (header `apikey`, que ela envia por padrão).
    """
    token_esperado = settings.EVOLUTION_WEBHOOK_TOKEN
    if token_esperado:
        return request.headers.get('X-Webhook-Token') == token_esperado
    return request.headers.get('apikey') == settings.EVOLUTION_API_KEY


def _extrair_texto(message: dict) -> str | None:
    """
    Mensagens do WhatsApp vêm em formatos diferentes dependendo do tipo
    (texto curto, texto longo com preview, resposta a outra mensagem).
    Esta função pega o texto pragmaticamente sem cobrir mídia/áudio.
    """
    if not isinstance(message, dict):
        return None
    if message.get('conversation'):
        return message['conversation']
    extended = message.get('extendedTextMessage') or {}
    if extended.get('text'):
        return extended['text']
    return None


def _handle_messages_upsert(instance: str, data: dict) -> None:
    """
    Mensagem nova chegou ou foi atualizada.

    `data.key.fromMe = True`  → mensagem enviada por nós (eco do envio).
                                Ignoramos pra não entrar em loop com o
                                próprio bot.
    `data.key.fromMe = False` → repassamos pro bot decidir.
    """
    key = data.get('key') or {}
    remote_jid = key.get('remoteJid')
    from_me = bool(key.get('fromMe'))
    push_name = data.get('pushName')
    texto = _extrair_texto(data.get('message') or {})

    direcao = 'OUT' if from_me else 'IN '
    logger.info(
        '[WA %s] inst=%s jid=%s nome=%r texto=%r',
        direcao, instance, remote_jid, push_name, texto,
    )

    if from_me or not remote_jid:
        return

    # Import local pra não puxar a árvore de models do core até a hora
    # do primeiro evento — mantém o startup do Django leve.
    from whatsapp.bot import process_incoming_message

    process_incoming_message(remote_jid, texto, push_name)


def _handle_connection_update(instance: str, data: dict) -> None:
    """Estado da instância mudou. Útil pra alertar quando cair sessão."""
    state = data.get('state')
    reason = data.get('statusReason')
    logger.info('[WA conn] inst=%s state=%s reason=%s', instance, state, reason)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@csrf_exempt
@require_POST
def evolution_webhook(request):
    """Único entry point para todos os eventos da Evolution."""
    if not _autorizado(request):
        return HttpResponseForbidden('webhook nao autorizado')

    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest('json invalido')

    event = (payload.get('event') or '').lower()
    instance = payload.get('instance') or ''
    data = payload.get('data') or {}

    try:
        if event == 'messages.upsert':
            _handle_messages_upsert(instance, data)
        elif event == 'connection.update':
            _handle_connection_update(instance, data)
        else:
            # Eventos não tratados ainda — log em DEBUG para não poluir.
            logger.debug('[WA evt] inst=%s event=%s', instance, event)
    except Exception:
        # Nunca quebre o webhook por erro de handler — a Evolution faria
        # retry agressivo e a fila ficaria atrasada. Logamos e seguimos.
        logger.exception('Erro processando webhook event=%s', event)

    return HttpResponse(status=204)
