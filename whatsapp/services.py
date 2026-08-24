"""
Cliente do Evolution API (WhatsApp).

Toda comunicação saindo do Django para o WhatsApp passa por este módulo —
nenhuma view, model ou signal deve falar HTTP direto com a Evolution.
Falhas de rede viram `EvolutionError`, deixando para quem chamou decidir
se loga, retenta ou ignora silenciosamente.

Como o histórico de chats é mantido apenas no Postgres da Evolution
(decisão de arquitetura: não persistir mensagens no Django), as funções
de leitura (`listar_chats`, `listar_mensagens`) são wrappers finos sobre
os endpoints `/chat/findChats` e `/chat/findMessages` da Evolution.

Importação típica:
    from whatsapp.services import enviar_texto, EvolutionError
"""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EvolutionError(RuntimeError):
    """Falha de comunicação com a Evolution (rede, 4xx ou 5xx)."""


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _instance_segment() -> str:
    """A instância pode ter espaços (ex: 'Tereza IA') — precisa URL-encode."""
    return quote(settings.EVOLUTION_INSTANCE, safe='')


def _url(path: str) -> str:
    base = settings.EVOLUTION_BASE_URL.rstrip('/')
    return f"{base}{path}/{_instance_segment()}"


def _headers() -> dict[str, str]:
    return {
        'Content-Type': 'application/json',
        'apikey': settings.EVOLUTION_API_KEY,
    }


def _post(path: str, payload: dict[str, Any]) -> Any:
    url = _url(path)
    try:
        r = requests.post(
            url, json=payload, headers=_headers(),
            timeout=settings.EVOLUTION_HTTP_TIMEOUT,
        )
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.RequestException as exc:
        logger.exception('Evolution falhou em POST %s payload=%s', path, payload)
        raise EvolutionError(f'POST {path}: {exc}') from exc


def _get(path: str) -> Any:
    url = _url(path)
    try:
        r = requests.get(url, headers=_headers(),
                         timeout=settings.EVOLUTION_HTTP_TIMEOUT)
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.RequestException as exc:
        logger.exception('Evolution falhou em GET %s', path)
        raise EvolutionError(f'GET {path}: {exc}') from exc


# ---------------------------------------------------------------------------
# Normalização de número
# ---------------------------------------------------------------------------
def to_e164(numero: str) -> str:
    """
    Normaliza um telefone para o formato E.164 que a Evolution espera
    (apenas dígitos, com DDI 55 quando ausente).

        '88 99377-0177'    -> '5588993770177'
        '8899377017'       -> '558899377017'
        '+55 11 9 9999-...' -> '551199999...'
    """
    digits = ''.join(c for c in numero if c.isdigit())
    if not digits:
        raise ValueError(f'Número vazio após sanitização: {numero!r}')
    if not digits.startswith('55'):
        digits = '55' + digits
    return digits


# ---------------------------------------------------------------------------
# Envio
# ---------------------------------------------------------------------------
def enviar_texto(numero: str, texto: str) -> dict[str, Any]:
    """
    Envia uma mensagem de texto. Devolve o JSON cru da Evolution
    (contém `key.id`, `status`, `messageTimestamp`, etc).

    Erros de rede/HTTP sobem como `EvolutionError`. Se o número não
    existir no WhatsApp, a Evolution responde 400 — chame
    `numero_existe()` antes em fluxos críticos.
    """
    payload = {'number': to_e164(numero), 'text': texto}
    return _post('/message/sendText', payload)


def numero_existe(numero: str) -> bool:
    """
    Confirma se o telefone tem WhatsApp ativo. Útil antes de envios em
    massa para não queimar tentativas e poluir o log.
    """
    payload = {'numbers': [to_e164(numero)]}
    resp = _post('/chat/whatsappNumbers', payload)
    if not resp:
        return False
    return bool(resp[0].get('exists'))


# ---------------------------------------------------------------------------
# Leitura (consulta direta na Evolution — não persistimos no Django)
# ---------------------------------------------------------------------------
def estado_conexao() -> dict[str, Any]:
    """Retorna o estado atual da instância: open/connecting/close."""
    return _get('/instance/connectionState')


def listar_chats(where: dict | None = None) -> list[dict[str, Any]]:
    """
    Lista chats salvos no Postgres da Evolution.
    `where` aceita o formato Prisma (ex: `{"remoteJid": "...@s.whatsapp.net"}`).
    """
    payload: dict[str, Any] = {}
    if where:
        payload['where'] = where
    resp = _post('/chat/findChats', payload)
    return resp if isinstance(resp, list) else []


def listar_mensagens(remote_jid: str, limit: int = 50) -> list[dict[str, Any]]:
    """Mensagens trocadas com um JID específico, mais recentes primeiro."""
    payload = {
        'where': {'key': {'remoteJid': remote_jid}},
        'limit': limit,
    }
    resp = _post('/chat/findMessages', payload)
    if isinstance(resp, dict):
        # Algumas versões devolvem {messages: {records: [...]}}.
        return (resp.get('messages') or {}).get('records', []) or []
    return resp if isinstance(resp, list) else []
