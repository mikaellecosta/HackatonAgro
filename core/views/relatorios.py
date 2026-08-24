"""
Views de relatórios — read-only, agregam dados via core/services.

Convenção de escopo:
- Matriz: vê dados globais (todas as filiais) por padrão. Pode filtrar
  por uma filial específica via ?filial=<id>.
- Gerente de Filial: sempre filtrado pela própria filial; ?filial é
  ignorado.

Todas as views aceitam ?dias=<n> (default 30) para o período de análise.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from core.models import Filial
from core.permissions import is_gerente_filial, is_matriz
from core.services import (
    consumo_no_periodo,
    estoque_por_filial,
    faturamento_no_periodo,
    faturamento_por_filial,
    insumos_em_ruptura,
    ticket_medio,
    top_insumos_consumidos,
    top_pratos_vendidos,
)


class _RelatorioContextMixin:
    """
    Resolve o escopo de filial e o período a partir dos query params.

    Coloca no contexto:
        filial         — Filial usada para filtrar (None = todas/global)
        filial_obrigatoria — bool: True quando o usuário é gerente
        dias           — período em dias (default 30, mín 1, máx 365)
        filiais_disponiveis — para o seletor (matriz vê todas; gerente só a sua)
    """

    DEFAULT_DIAS = 30
    MAX_DIAS = 365

    def _resolver_filial(self):
        user = self.request.user
        if is_gerente_filial(user) and not is_matriz(user):
            return user.filial  # gerente trava
        filial_id = self.request.GET.get('filial')
        if not filial_id:
            return None
        return get_object_or_404(Filial, pk=filial_id)

    def _resolver_dias(self):
        try:
            dias = int(self.request.GET.get('dias', self.DEFAULT_DIAS))
        except (TypeError, ValueError):
            dias = self.DEFAULT_DIAS
        return max(1, min(dias, self.MAX_DIAS))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        filial = self._resolver_filial()
        ctx['filial'] = filial
        ctx['dias'] = self._resolver_dias()
        ctx['filial_obrigatoria'] = is_gerente_filial(user) and not is_matriz(user)
        if is_matriz(user):
            ctx['filiais_disponiveis'] = Filial.objects.all()
        elif filial:
            ctx['filiais_disponiveis'] = Filial.objects.filter(pk=filial.pk)
        else:
            ctx['filiais_disponiveis'] = Filial.objects.none()
        return ctx


class EstoqueView(LoginRequiredMixin, _RelatorioContextMixin, TemplateView):
    """
    Saldo atual de cada insumo por filial.

    Template: ``core/relatorios/estoque.html``
    Contexto extra:
        saldos — list[dict]: {insumo, estoque_atual, estoque_minimo, em_ruptura}
    """
    template_name = 'core/relatorios/estoque.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filial = ctx['filial']
        saldos = []
        if filial is not None:
            from core.models import Insumo
            mapa = estoque_por_filial(filial)
            for insumo in Insumo.objects.all():
                atual = mapa.get(insumo.pk, 0)
                saldos.append({
                    'insumo': insumo,
                    'estoque_atual': atual,
                    'estoque_minimo': insumo.estoque_minimo,
                    'em_ruptura': atual <= insumo.estoque_minimo,
                })
            saldos.sort(key=lambda x: x['em_ruptura'], reverse=True)
        ctx['saldos'] = saldos
        return ctx


class RupturaView(LoginRequiredMixin, _RelatorioContextMixin, TemplateView):
    """
    Insumos abaixo do estoque mínimo na filial selecionada.

    Template: ``core/relatorios/ruptura.html``
    Contexto extra:
        em_ruptura — list[dict]: {insumo, estoque_atual, estoque_minimo, deficit}
    """
    template_name = 'core/relatorios/ruptura.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filial = ctx['filial']
        ctx['em_ruptura'] = insumos_em_ruptura(filial) if filial else []
        return ctx


class ConsumoView(LoginRequiredMixin, _RelatorioContextMixin, TemplateView):
    """
    Padrões de consumo no período.

    Template: ``core/relatorios/consumo.html``
    Contexto extra:
        consumo — queryset agregado: insumo, total, unidade_medida
        top_insumos — top 10 (lista)
    """
    template_name = 'core/relatorios/consumo.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filial = ctx['filial']
        dias = ctx['dias']
        ctx['consumo'] = list(consumo_no_periodo(filial=filial, dias=dias))
        ctx['top_insumos'] = top_insumos_consumidos(filial=filial, dias=dias, limit=10)
        return ctx


class FaturamentoView(LoginRequiredMixin, _RelatorioContextMixin, TemplateView):
    """
    KPIs de faturamento no período.

    Template: ``core/relatorios/faturamento.html``
    Contexto extra:
        faturamento_total       — Decimal
        ticket_medio            — Decimal
        faturamento_por_filial  — queryset (só matriz; gerente vê só a dele)
        top_pratos              — list dos 10 mais vendidos
    """
    template_name = 'core/relatorios/faturamento.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filial = ctx['filial']
        dias = ctx['dias']
        ctx['faturamento_total'] = faturamento_no_periodo(filial=filial, dias=dias)
        ctx['ticket_medio'] = ticket_medio(filial=filial, dias=dias)
        ctx['top_pratos'] = top_pratos_vendidos(filial=filial, dias=dias, limit=10)
        # Comparativo entre filiais só faz sentido pra matriz sem filtro.
        if is_matriz(self.request.user) and filial is None:
            ctx['faturamento_por_filial'] = list(faturamento_por_filial(dias=dias))
        else:
            ctx['faturamento_por_filial'] = []
        return ctx
