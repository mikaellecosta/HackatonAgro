"""
Saldo de estoque por filial e detecção de ruptura.

Convenção:
- Apenas movimentações com status `CONCLUIDA` afetam o estoque
  (pendentes/canceladas ficam de fora — ainda não aconteceram).
- ENTRADA e AJUSTE somam ao saldo; SAIDA e DESPERDICIO subtraem.
- Quantidades em `ItemMovimentacao` são sempre positivas — o sinal
  vem do `tipo` da movimentação pai.
"""
from decimal import Decimal

from django.db.models import Sum

from core.models import Insumo, ItemMovimentacao
from core.models.choices import StatusMovimentacao, TipoMovimentacao


# Tipos que somam ao estoque vs subtraem.
TIPOS_ENTRADA = (TipoMovimentacao.ENTRADA, TipoMovimentacao.AJUSTE)
TIPOS_SAIDA = (TipoMovimentacao.SAIDA, TipoMovimentacao.DESPERDICIO)


def _itens_concluidos(filial=None):
    """Queryset de ItemMovimentacao apenas de movimentações concluídas."""
    qs = ItemMovimentacao.objects.filter(
        movimentacao__status=StatusMovimentacao.CONCLUIDA,
    )
    if filial is not None:
        qs = qs.filter(movimentacao__filial=filial)
    return qs


def estoque_atual(insumo, filial) -> Decimal:
    """
    Saldo do `insumo` na `filial` (somando entradas/ajustes e
    subtraindo saídas/desperdícios concluídos).
    """
    itens = _itens_concluidos(filial=filial).filter(insumo=insumo)
    entradas = itens.filter(
        movimentacao__tipo__in=TIPOS_ENTRADA,
    ).aggregate(total=Sum('quantidade'))['total'] or Decimal('0')
    saidas = itens.filter(
        movimentacao__tipo__in=TIPOS_SAIDA,
    ).aggregate(total=Sum('quantidade'))['total'] or Decimal('0')
    return entradas - saidas


def estoque_por_filial(filial) -> dict:
    """
    Devolve {insumo_id: saldo_decimal} para todos os insumos com
    movimentação na `filial`.
    """
    itens = _itens_concluidos(filial=filial)
    saldos = {}
    for item in itens.values('insumo_id', 'movimentacao__tipo').annotate(
        total=Sum('quantidade'),
    ):
        ins_id = item['insumo_id']
        tipo = item['movimentacao__tipo']
        sinal = 1 if tipo in TIPOS_ENTRADA else (-1 if tipo in TIPOS_SAIDA else 0)
        saldos[ins_id] = saldos.get(ins_id, Decimal('0')) + sinal * (item['total'] or 0)
    return saldos


def insumos_em_ruptura(filial) -> list:
    """
    Lista insumos cujo estoque atual na `filial` está abaixo (ou igual)
    do `estoque_minimo` cadastrado.

    Retorna lista de dicts: {insumo, estoque_atual, estoque_minimo, deficit}.
    """
    saldos = estoque_por_filial(filial)
    em_ruptura = []
    for insumo in Insumo.objects.all():
        atual = saldos.get(insumo.pk, Decimal('0'))
        if atual <= insumo.estoque_minimo:
            em_ruptura.append({
                'insumo': insumo,
                'estoque_atual': atual,
                'estoque_minimo': insumo.estoque_minimo,
                'deficit': insumo.estoque_minimo - atual,
            })
    em_ruptura.sort(key=lambda x: x['deficit'], reverse=True)
    return em_ruptura
