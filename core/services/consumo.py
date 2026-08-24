"""
Padrões de consumo de insumos — agregações sobre `ItemMovimentacao`
em movimentações de SAIDA/DESPERDICIO concluídas.
"""
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from core.models import ItemMovimentacao
from core.models.choices import StatusMovimentacao, TipoMovimentacao


def _itens_consumo(filial=None, dias=30):
    """Itens de movimentação que representam consumo (saída/desperdício)."""
    desde = timezone.now() - timedelta(days=dias)
    qs = ItemMovimentacao.objects.filter(
        movimentacao__status=StatusMovimentacao.CONCLUIDA,
        movimentacao__tipo__in=(
            TipoMovimentacao.SAIDA,
            TipoMovimentacao.DESPERDICIO,
        ),
        movimentacao__data__gte=desde,
    )
    if filial is not None:
        qs = qs.filter(movimentacao__filial=filial)
    return qs


def consumo_no_periodo(filial=None, dias=30):
    """
    Consumo total por insumo no período, em formato de queryset agregado.

    Cada linha tem: insumo_id, insumo__nome, total, dias_no_periodo,
    media_diaria.
    """
    itens = _itens_consumo(filial=filial, dias=dias)
    return itens.values('insumo_id', 'insumo__nome', 'insumo__unidade_medida').annotate(
        total=Sum('quantidade'),
    ).order_by('-total')


def top_insumos_consumidos(filial=None, dias=30, limit=10):
    """Top N insumos mais consumidos no período (lista de dicts)."""
    return list(consumo_no_periodo(filial=filial, dias=dias)[:limit])
