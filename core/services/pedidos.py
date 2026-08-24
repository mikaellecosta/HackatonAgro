"""
Sugestão guiada de pedidos a partir do estoque atual.

Para cada insumo em ruptura na filial, escolhe o fornecedor mais barato
(via `ItemFornecedor.preco`) e propõe uma quantidade. Insumos sem
fornecedor cadastrado vão pra um grupo separado para o usuário tratar
manualmente.

A quantidade sugerida tenta cobrir o déficit + uma margem de reposição:
    quantidade = max(deficit * 2, estoque_minimo)
"""
from decimal import Decimal

from django.db import transaction

from core.models import (
    Fornecedor,
    ItemFornecedor,
    ItemMovimentacao,
    Pedido,
)
from core.models.choices import StatusMovimentacao
from core.services.estoque import insumos_em_ruptura


def _quantidade_sugerida(deficit, estoque_minimo) -> Decimal:
    """
    Quantidade pra repor cobrindo o déficit com margem.
    Mínimo: o estoque_minimo cadastrado (evita pedido microscópico).
    """
    proposta = (deficit or Decimal('0')) * 2
    return max(proposta, estoque_minimo or Decimal('0'), Decimal('1'))


def sugerir_pedido_da_cidade(filial) -> dict:
    """
    Mesma lógica do `sugerir_pedido`, mas restringe os fornecedores aos
    que estão na mesma cidade da filial. Se a filial não tem cidade
    cadastrada, cai no comportamento padrão (sem filtro geográfico).

    Pra cada insumo em ruptura: ranqueia os fornecedores da cidade por
    preço (mais barato primeiro, desempate por prazo de entrega) e
    escolhe o melhor. Insumos sem fornecedor na cidade vão pra
    `sem_fornecedor` — o solicitante decide se aceita um de fora.

    Devolve a mesma estrutura de `sugerir_pedido`.
    """
    em_ruptura = insumos_em_ruptura(filial)
    cidade = (filial.cidade or '').strip()

    por_fornecedor: dict = {}
    sem_fornecedor: list = []

    for ruptura in em_ruptura:
        insumo = ruptura['insumo']
        deficit = ruptura['deficit']
        quantidade = _quantidade_sugerida(deficit, insumo.estoque_minimo)

        candidatos = ItemFornecedor.objects.filter(insumo=insumo)
        if cidade:
            candidatos = candidatos.filter(fornecedor__cidade__iexact=cidade)
        melhor = (
            candidatos
            .select_related('fornecedor')
            .order_by('preco', 'prazo_entrega_dias')
            .first()
        )
        if melhor is None:
            sem_fornecedor.append({
                'insumo': insumo,
                'quantidade': quantidade,
                'deficit': deficit,
            })
            continue

        bucket = por_fornecedor.setdefault(melhor.fornecedor_id, {
            'fornecedor': melhor.fornecedor,
            'itens': [],
            'total': Decimal('0'),
        })
        subtotal = quantidade * melhor.preco
        bucket['itens'].append({
            'insumo': insumo,
            'quantidade': quantidade,
            'preco_unitario': melhor.preco,
            'subtotal': subtotal,
            'prazo_entrega_dias': melhor.prazo_entrega_dias,
        })
        bucket['total'] += subtotal

    sugestoes = sorted(
        por_fornecedor.values(),
        key=lambda b: b['total'],
        reverse=True,
    )
    return {'sugestoes': sugestoes, 'sem_fornecedor': sem_fornecedor}


def sugerir_pedido(filial) -> dict:
    """
    Devolve a estrutura:
        {
            'sugestoes': [
                {
                    'fornecedor': Fornecedor,
                    'itens': [
                        {
                            'insumo': Insumo,
                            'quantidade': Decimal,
                            'preco_unitario': Decimal,
                            'subtotal': Decimal,
                            'prazo_entrega_dias': int | None,
                        },
                        ...
                    ],
                    'total': Decimal,
                },
                ...
            ],
            'sem_fornecedor': [
                {'insumo': Insumo, 'quantidade': Decimal, 'deficit': Decimal},
                ...
            ],
        }
    """
    em_ruptura = insumos_em_ruptura(filial)
    por_fornecedor: dict = {}
    sem_fornecedor: list = []

    for ruptura in em_ruptura:
        insumo = ruptura['insumo']
        deficit = ruptura['deficit']
        quantidade = _quantidade_sugerida(deficit, insumo.estoque_minimo)

        # Fornecedor mais barato pra esse insumo.
        melhor = (
            ItemFornecedor.objects
            .filter(insumo=insumo)
            .select_related('fornecedor')
            .order_by('preco', 'prazo_entrega_dias')
            .first()
        )
        if melhor is None:
            sem_fornecedor.append({
                'insumo': insumo,
                'quantidade': quantidade,
                'deficit': deficit,
            })
            continue

        bucket = por_fornecedor.setdefault(melhor.fornecedor_id, {
            'fornecedor': melhor.fornecedor,
            'itens': [],
            'total': Decimal('0'),
        })
        subtotal = quantidade * melhor.preco
        bucket['itens'].append({
            'insumo': insumo,
            'quantidade': quantidade,
            'preco_unitario': melhor.preco,
            'subtotal': subtotal,
            'prazo_entrega_dias': melhor.prazo_entrega_dias,
        })
        bucket['total'] += subtotal

    # Ordena por maior total (fornecedor mais relevante no topo).
    sugestoes = sorted(
        por_fornecedor.values(),
        key=lambda b: b['total'],
        reverse=True,
    )
    return {'sugestoes': sugestoes, 'sem_fornecedor': sem_fornecedor}


def criar_pedido_da_sugestao(filial, fornecedor: Fornecedor, usuario):
    """
    Recalcula a sugestão pra esse fornecedor e cria o Pedido + itens.
    Retorna o Pedido criado, ou None se não há nada a sugerir agora.
    Nunca confia em valores vindos do form — sempre recomputa.
    """
    sugestao = sugerir_pedido(filial)
    bucket = next(
        (b for b in sugestao['sugestoes'] if b['fornecedor'].pk == fornecedor.pk),
        None,
    )
    if bucket is None or not bucket['itens']:
        return None

    with transaction.atomic():
        pedido = Pedido.objects.create(
            filial=filial,
            usuario=usuario,
            fornecedor=fornecedor,
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
    return pedido
