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
#     AreaPlantio,
# )
# from core.permissions import is_gerente_filial, is_matriz
# # from core.services import (
 
# # )


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

        

#         return ctx
