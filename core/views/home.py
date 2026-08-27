# """
# Home — landing pública.

# A rota ``/`` é o ponto de entrada do site: visitantes anônimos veem a
# landing institucional (com link para o login no navbar) e usuários
# autenticados continuam vendo a mesma landing — KPIs e área operacional
# moram em ``/painel/`` (PainelView), pra onde o login redireciona.

# Mantemos o cálculo de KPIs no contexto porque a landing também mostra
# contadores; quando o usuário é anônimo, o branch ``else`` devolve
# valores vazios e o template renderiza normalmente.
# """
# from django.views.generic import TemplateView

# from core.models import (
#     Filial,
#     Fornecedor,
#     Insumo,
#     Movimentacao,
#     Pedido,
#     Prato,
#     Venda,
# )
# from core.permissions import is_gerente_filial, is_matriz
# from core.services import (
#     faturamento_no_periodo,
#     insumos_em_ruptura,
#     ticket_medio,
# )


# class HomeView(TemplateView):
#     """
#     Template esperado: ``core/home.html``

#     Contexto fornecido:
#         papel              — string: 'matriz' | 'gerente' | 'sem_papel'
#         filial             — Filial do gerente, ou None
#         contadores         — dict[str, int] com KPIs base
#         faturamento_30d    — Decimal: faturamento dos últimos 30 dias
#         ticket_medio_30d   — Decimal: ticket médio dos últimos 30 dias
#         ruptura            — list[dict]: insumos em ruptura na filial
#                              (vazio para matriz se não houver filtro)
#     """
#     template_name = 'components/inicio.html'

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         user = self.request.user

#         if is_matriz(user):
#             ctx['papel'] = 'matriz'
#             ctx['filial'] = None
#             ctx['contadores'] = {
#                 'fornecedores': Fornecedor.objects.count(),
#                 'filiais': Filial.objects.count(),
#                 'insumos': Insumo.objects.count(),
#                 'pratos': Prato.objects.filter(ativo=True).count(),
#                 'pedidos': Pedido.objects.count(),
#                 'vendas': Venda.objects.count(),
#                 'movimentacoes': Movimentacao.objects.count(),
#             }
#             ctx['faturamento_30d'] = faturamento_no_periodo(dias=30)
#             ctx['ticket_medio_30d'] = ticket_medio(dias=30)
#             ctx['ruptura'] = []  # matriz consulta no relatório dedicado
#         elif is_gerente_filial(user) and user.filial:
#             filial = user.filial
#             ctx['papel'] = 'gerente'
#             ctx['filial'] = filial
#             ctx['contadores'] = {
#                 'fornecedores': Fornecedor.objects.count(),
#                 'insumos': Insumo.objects.count(),
#                 'pratos': Prato.objects.filter(ativo=True).count(),
#                 'pedidos': Pedido.objects.filter(filial=filial).count(),
#                 'vendas': Venda.objects.filter(filial=filial).count(),
#                 'movimentacoes': Movimentacao.objects.filter(filial=filial).count(),
#             }
#             ctx['faturamento_30d'] = faturamento_no_periodo(filial=filial, dias=30)
#             ctx['ticket_medio_30d'] = ticket_medio(filial=filial, dias=30)
#             ctx['ruptura'] = insumos_em_ruptura(filial)
#         else:
#             ctx['papel'] = 'sem_papel'
#             ctx['filial'] = None
#             ctx['contadores'] = {}
#             ctx['faturamento_30d'] = 0
#             ctx['ticket_medio_30d'] = 0
#             ctx['ruptura'] = []

#         return ctx
