"""
Bot conversacional stateless da Tereza IA.

Toda a interação acontece sem persistir estado de conversa: cada
mensagem é interpretada de forma idempotente a partir do telefone do
remetente, do texto recebido e do que já existe no banco (Pedidos
PENDENTES, ruptura atual, etc).

Fluxos:

1. Gerente envia qualquer mensagem
   -> bot calcula a sugestão de reposição da cidade da filial
   -> responde com a lista detalhada e pede a palavra-chave de
      confirmação ("confirmar")

2. Gerente envia "confirmar" / "ok" / "pode"
   -> bot recalcula a sugestão (idempotente) e cria 1 Pedido PENDENTE
      por fornecedor escolhido
   -> dispara WhatsApp pra cada fornecedor pedindo confirmação

3. Fornecedor responde "sim" / "tenho"
   -> bot acha o Pedido PENDENTE mais recente desse fornecedor
   -> marca como CONCLUIDA (estoque é atualizado)
   -> avisa o gerente que cuidou da solicitação

4. Fornecedor responde "não"
   -> Pedido vai pra CANCELADA, gerente é avisado

Quem manda mensagem mas não bate com nenhum User/Fornecedor cadastrado
é silenciosamente ignorado — não é problema do bot decidir o que fazer
com remetentes desconhecidos.
"""
from __future__ import annotations

import logging
import re
from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from core.models import (
    Fornecedor,
    ItemMovimentacao,
    Pedido,
    User,
)
from core.models.GestaoFinanceira import StatusMovimentacao
from core.services.pedidos import sugerir_pedido_da_cidade
from whatsapp import phones
from whatsapp.services import EvolutionError, enviar_texto

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Detecção de intenção (palavras-chave tolerantes)
# ---------------------------------------------------------------------------
# Match é por token, não por igualdade da frase inteira: "sim, tenho 👍",
# "Tenho sim!" e "ok pode mandar" todos viram confirmação. Negação tem
# precedência sobre afirmação, então "sim, mas nao tenho tudo" cancela —
# evita marcar pedido como recebido quando o fornecedor está hesitando.
PALAVRAS_CONFIRMA = {
    'confirmar', 'confirma', 'confirmo',
    'sim', 's', 'pode', 'manda', 'ok', 'okay',
    'tenho', 'temos', 'positivo', 'fechado',
}

PALAVRAS_NEGA = {
    'nao', 'n', 'no', 'cancelar', 'cancela',
    'negativo', 'nego', 'sem',
}

# Qualquer caractere não-alfanumérico vira separador (vírgula, espaço,
# emoji, pontuação solta). É o que destrava "Sim 👍" e "Sim, tenho!".
_SEPARADORES = re.compile(r'[^a-z0-9]+')


def _normaliza(texto: str | None) -> str:
    """Lowercase + sem acento, pra comparar com keywords."""
    if not texto:
        return ''
    s = texto.strip().lower()
    # Acentos básicos do português que aparecem nas keywords ('não' -> 'nao')
    for ant, dep in (('á', 'a'), ('â', 'a'), ('ã', 'a'),
                     ('é', 'e'), ('ê', 'e'),
                     ('í', 'i'),
                     ('ó', 'o'), ('ô', 'o'), ('õ', 'o'),
                     ('ú', 'u'),
                     ('ç', 'c')):
        s = s.replace(ant, dep)
    return s


def _tokens(texto: str | None) -> set[str]:
    """Conjunto de tokens alfanuméricos do texto normalizado."""
    s = _normaliza(texto)
    if not s:
        return set()
    return {t for t in _SEPARADORES.split(s) if t}


def _quer_confirmar(texto: str) -> bool:
    """True só se houver afirmação E nenhuma negação no texto."""
    toks = _tokens(texto)
    if not toks or toks & PALAVRAS_NEGA:
        return False
    return bool(toks & PALAVRAS_CONFIRMA)


def _quer_negar(texto: str) -> bool:
    return bool(_tokens(texto) & PALAVRAS_NEGA)


# ---------------------------------------------------------------------------
# Formatação de mensagens
# ---------------------------------------------------------------------------
def _fmt_qtd(qtd: Decimal, unidade: str) -> str:
    """3.000 kg -> '3 kg'. Tira zeros à direita do Decimal."""
    q = Decimal(qtd).normalize()
    # Decimal('3').normalize() pode virar '3E+0'; força string fixed-point.
    txt = f'{q:f}'.rstrip('0').rstrip('.') if '.' in f'{q:f}' else f'{q:f}'
    return f'{txt} {unidade}'


def _msg_sugestao_para_gerente(filial, sugestao: dict) -> str:
    """Resumo da reposição proposta — o gerente confirma com 'confirmar'."""
    sugestoes = sugestao['sugestoes']
    sem_forn = sugestao['sem_fornecedor']

    if not sugestoes and not sem_forn:
        return (
            f'Olá! Verifiquei a {filial.nome} e nenhum insumo está em ruptura '
            f'agora. Nada a solicitar. ✅'
        )

    linhas = [f'Olá! Estes são os insumos em ruptura na {filial.nome}:', '']
    for bucket in sugestoes:
        forn = bucket['fornecedor']
        linhas.append(f'• {forn.nome} (R$ {bucket["total"]:.2f}):')
        for item in bucket['itens']:
            linhas.append(
                f'   - {item["insumo"].nome}: '
                f'{_fmt_qtd(item["quantidade"], item["insumo"].get_unidade_medida_display())}'
            )
    if sem_forn:
        linhas.append('')
        linhas.append('⚠ Sem fornecedor na sua cidade para:')
        for item in sem_forn:
            linhas.append(
                f'   - {item["insumo"].nome}: '
                f'{_fmt_qtd(item["quantidade"], item["insumo"].get_unidade_medida_display())}'
            )
    linhas.append('')
    linhas.append('Responda *confirmar* pra eu solicitar aos fornecedores.')
    return '\n'.join(linhas)


def _msg_solicitacao_para_fornecedor(pedido: Pedido) -> str:
    """O texto que o fornecedor recebe pedindo confirmação de disponibilidade."""
    filial = pedido.filial
    cidade = filial.cidade or ''
    cabecalho = (
        f'Olá, {pedido.fornecedor.nome}! '
        f'A {filial.nome}{f" ({cidade})" if cidade else ""} '
        f'gostaria de saber se você tem disponíveis:'
    )
    linhas = [cabecalho, '']
    for item in pedido.itens.select_related('insumo').all():
        linhas.append(
            f'• {item.insumo.nome}: '
            f'{_fmt_qtd(item.quantidade, item.insumo.get_unidade_medida_display())}'
        )
    linhas.append('')
    linhas.append('Pode atender? Responda *sim* ou *não*.')
    return '\n'.join(linhas)


def _msg_resumo_solicitacao_para_gerente(pedidos: list[Pedido]) -> str:
    if not pedidos:
        return 'Nenhum fornecedor pra solicitar agora.'
    linhas = ['Solicitações enviadas pros fornecedores:', '']
    for p in pedidos:
        linhas.append(f'• Pedido #{p.pk} — {p.fornecedor.nome}')
    linhas.append('')
    linhas.append('Aviso aqui assim que cada um responder.')
    return '\n'.join(linhas)


# ---------------------------------------------------------------------------
# Ações
# ---------------------------------------------------------------------------
def _criar_pedidos_da_sugestao(filial, usuario, sugestao: dict) -> list[Pedido]:
    """Cria 1 Pedido PENDENTE por fornecedor da sugestão (atomic)."""
    pedidos: list[Pedido] = []
    with transaction.atomic():
        for bucket in sugestao['sugestoes']:
            pedido = Pedido.objects.create(
                filial=filial,
                usuario=usuario,
                fornecedor=bucket['fornecedor'],
                status=StatusMovimentacao.PENDENTE,
            )
            ItemMovimentacao.objects.bulk_create([
                ItemMovimentacao(
                    movimentacao=pedido,
                    insumo=item['insumo'],
                    quantidade=item['quantidade'],
                )
                for item in bucket['itens']
            ])
            pedidos.append(pedido)
    return pedidos


def _disparar_solicitacoes(pedidos: Iterable[Pedido]) -> None:
    """Manda WhatsApp pra cada fornecedor. Falhas viram log, não interrompem."""
    for pedido in pedidos:
        telefone = pedido.fornecedor.telefone
        if not telefone:
            logger.warning(
                'Pedido #%s: fornecedor %s sem telefone, não dá pra avisar',
                pedido.pk, pedido.fornecedor.nome,
            )
            continue
        try:
            enviar_texto(telefone, _msg_solicitacao_para_fornecedor(pedido))
        except EvolutionError:
            logger.exception('Falha enviando solicitação pro pedido #%s', pedido.pk)


def _avisar_gerente_resposta(pedido: Pedido, confirmou: bool) -> None:
    """Notifica o gerente da filial sobre a resposta de um fornecedor."""
    gerente = pedido.filial.gerente
    if gerente is None or not gerente.telefone:
        return
    if confirmou:
        msg = (
            f'✅ {pedido.fornecedor.nome} confirmou a disponibilidade do '
            f'pedido #{pedido.pk}. Marcado como concluído.'
        )
    else:
        msg = (
            f'❌ {pedido.fornecedor.nome} recusou o pedido #{pedido.pk}. '
            f'Marcado como cancelado.'
        )
    try:
        enviar_texto(gerente.telefone, msg)
    except EvolutionError:
        logger.exception('Falha avisando gerente do pedido #%s', pedido.pk)


# ---------------------------------------------------------------------------
# Handlers de fluxo
# ---------------------------------------------------------------------------
def _handle_gerente(user: User, texto: str) -> None:
    """Lida com mensagem vinda de um gerente cadastrado."""
    filial = user.filial  # property: primeira filial gerenciada
    if filial is None:
        try:
            enviar_texto(
                user.telefone or '',
                'Você está cadastrado, mas não é gerente de nenhuma filial. '
                'Fale com a matriz pra ajustar seu vínculo.',
            )
        except EvolutionError:
            logger.exception('Falha avisando user sem filial')
        return

    sugestao = sugerir_pedido_da_cidade(filial)

    if _quer_confirmar(texto):
        if not sugestao['sugestoes']:
            _safe_send(user.telefone, (
                f'Não há nada pra solicitar agora — nenhuma ruptura com '
                f'fornecedor na cidade de {filial.cidade or "sua filial"}.'
            ))
            return
        pedidos = _criar_pedidos_da_sugestao(filial, user, sugestao)
        _disparar_solicitacoes(pedidos)
        _safe_send(user.telefone, _msg_resumo_solicitacao_para_gerente(pedidos))
        return

    # Qualquer outra coisa: re-apresenta a sugestão. Stateless e idempotente.
    _safe_send(user.telefone, _msg_sugestao_para_gerente(filial, sugestao))


def _handle_fornecedor(fornecedores: list[Fornecedor], texto: str) -> None:
    """
    Lida com resposta de um fornecedor sobre o pedido mais recente.

    Recebe uma *lista* de fornecedores porque dois cadastros podem
    compartilhar o mesmo telefone (ver `phones.find_fornecedores_by_jid`).
    A gente acha o pedido pendente mais recente entre todos eles e
    responde por aquele — assim quem responde é sempre o cadastro que
    realmente tem pedido aberto.
    """
    pedido = (
        Pedido.objects
        .filter(fornecedor__in=fornecedores, status=StatusMovimentacao.PENDENTE)
        .order_by('-data')
        .select_related('fornecedor', 'filial')
        .first()
    )
    if pedido is None:
        # Nenhum pedido aberto: ignora pra não responder em conversa não solicitada.
        logger.info(
            'Mensagem de fornecedor(es) %s sem pedido pendente — ignorando',
            [f.nome for f in fornecedores],
        )
        return
    fornecedor = pedido.fornecedor

    if _quer_confirmar(texto):
        with transaction.atomic():
            pedido.status = StatusMovimentacao.CONCLUIDA
            pedido.data = timezone.now()  # registra quando foi confirmado
            pedido.save(update_fields=['status', 'data'])
        _safe_send(
            fornecedor.telefone,
            f'Obrigado! Pedido #{pedido.pk} marcado como recebido.',
        )
        _avisar_gerente_resposta(pedido, confirmou=True)
        return

    if _quer_negar(texto):
        pedido.status = StatusMovimentacao.CANCELADA
        pedido.save(update_fields=['status'])
        _safe_send(
            fornecedor.telefone,
            f'Tudo bem, cancelei o pedido #{pedido.pk} aqui.',
        )
        _avisar_gerente_resposta(pedido, confirmou=False)
        return

    # Resposta ambígua — pede pra esclarecer sem mudar nada.
    _safe_send(
        fornecedor.telefone,
        f'Não entendi. Sobre o pedido #{pedido.pk}, responda *sim* (tenho) '
        f'ou *não* (não tenho).',
    )


def _safe_send(numero: str | None, texto: str) -> None:
    if not numero:
        return
    try:
        enviar_texto(numero, texto)
    except EvolutionError:
        logger.exception('Falha enviando WhatsApp para %s', numero)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def process_incoming_message(jid: str, texto: str | None, push_name: str | None) -> None:
    """
    Roteador principal — chamado pelo webhook a cada `messages.upsert`
    com `fromMe=False` que não seja de grupo.
    """
    if phones.is_group_jid(jid):
        return
    if not texto:
        # Mensagens de mídia/áudio sem texto: ignora por enquanto.
        logger.debug('Mensagem sem texto de %s — ignorando', jid)
        return

    user = phones.find_user_by_jid(jid)
    if user is not None:
        logger.info('Mensagem de gerente %s: %r', user.username, texto)
        _handle_gerente(user, texto)
        return

    fornecedores = phones.find_fornecedores_by_jid(jid)
    if fornecedores:
        logger.info(
            'Mensagem de fornecedor(es) %s: %r',
            [f.nome for f in fornecedores], texto,
        )
        _handle_fornecedor(fornecedores, texto)
        return

    logger.info('Mensagem de remetente desconhecido %s (%s) — ignorando',
                jid, push_name)
