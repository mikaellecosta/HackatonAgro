"""
KPIs financeiros baseados em `Venda`.

Apenas vendas concluídas entram no faturamento — pendentes e canceladas
ficam de fora.
"""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.utils import timezone

from core.models import ItemVenda, Venda
from core.models.GestaoFinanceira import StatusMovimentacao


def _vendas_concluidas(filial=None, dias=30):
    desde = timezone.now() - timedelta(days=dias)
    qs = Venda.objects.filter(
        status=StatusMovimentacao.CONCLUIDA,
        data__gte=desde,
    )
    if filial is not None:
        qs = qs.filter(filial=filial)
    return qs


def faturamento_no_periodo(filial=None, dias=30) -> Decimal:
    """Soma de Venda.preco no período (filial opcional)."""
    total = _vendas_concluidas(filial=filial, dias=dias).aggregate(
        total=Sum('preco'),
    )['total']
    return total or Decimal('0')


def faturamento_por_filial(dias=30):
    """
    Faturamento agregado por filial, ordenado do maior pro menor.
    Cada linha: {filial_id, filial__nome, total, qtd_vendas}.
    """
    desde = timezone.now() - timedelta(days=dias)
    return (
        Venda.objects
        .filter(status=StatusMovimentacao.CONCLUIDA, data__gte=desde)
        .values('filial_id', 'filial__nome')
        .annotate(total=Sum('preco'), qtd_vendas=Count('id'))
        .order_by('-total')
    )


def ticket_medio(filial=None, dias=30) -> Decimal:
    """Valor médio de Venda.preco no período."""
    media = _vendas_concluidas(filial=filial, dias=dias).aggregate(
        media=Avg('preco'),
    )['media']
    return media or Decimal('0')


def top_pratos_vendidos(filial=None, dias=30, limit=10):
    """Top N pratos mais vendidos no período (lista de dicts)."""
    desde = timezone.now() - timedelta(days=dias)
    qs = ItemVenda.objects.filter(
        venda__status=StatusMovimentacao.CONCLUIDA,
        venda__data__gte=desde,
    )
    if filial is not None:
        qs = qs.filter(venda__filial=filial)
    return list(
        qs.values('prato_id', 'prato__nome')
          .annotate(total=Sum('quantidade'))
          .order_by('-total')[:limit]
    )
