# """
# Solicitação guiada de insumos.

# Fluxo:
# 1. GET /sugestao-pedido/  -> SugestaoPedidoView
#    Mostra os pedidos sugeridos por fornecedor + insumos sem fornecedor.
# 2. POST /sugestao-pedido/criar/  -> CriarPedidoFromSugestaoView
#    Recebe `fornecedor=<id>` no body, recomputa a sugestão e cria o
#    Pedido + ItemMovimentacao. Redireciona para o detalhe do pedido criado.

# Apenas usuários com filial vinculada (gerente) ou matriz com ?filial=
# selecionada conseguem agir — porque sugestão depende da filial.
# """
# from django.contrib import messages
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404, redirect
# from django.urls import reverse
# from django.views import View
# from django.views.generic import TemplateView

# from core.models import Filial, Fornecedor
# from core.permissions import is_gerente_filial, is_matriz
# from core.services import criar_pedido_da_sugestao, sugerir_pedido
# from core.views.base import GerenteFilialRequiredMixin


# def _resolver_filial(request):
#     """
#     Retorna a Filial alvo da sugestão:
#       - gerente: a própria filial (ignora ?filial=).
#       - matriz: precisa de ?filial=<id>.
#       - outros: None.
#     """
#     user = request.user
#     if is_gerente_filial(user) and not is_matriz(user):
#         return user.filial
#     if is_matriz(user):
#         filial_id = request.GET.get('filial') or request.POST.get('filial')
#         if filial_id:
#             return get_object_or_404(Filial, pk=filial_id)
#     return None


# class SugestaoPedidoView(GerenteFilialRequiredMixin, TemplateView):
#     """
#     Template: ``core/pedidos/sugestao.html``
#     Contexto:
#         filial            — Filial alvo (None se matriz não selecionou)
#         sugestoes         — list[dict] (ver core.services.pedidos.sugerir_pedido)
#         sem_fornecedor    — list[dict] de insumos órfãos
#         filiais_disponiveis — só para matriz (selector)
#     """
#     template_name = 'core/pedidos/sugestao.html'

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         filial = _resolver_filial(self.request)
#         ctx['filial'] = filial
#         if filial is not None:
#             sugestao = sugerir_pedido(filial)
#             ctx['sugestoes'] = sugestao['sugestoes']
#             ctx['sem_fornecedor'] = sugestao['sem_fornecedor']
#         else:
#             ctx['sugestoes'] = []
#             ctx['sem_fornecedor'] = []
#         if is_matriz(self.request.user):
#             ctx['filiais_disponiveis'] = Filial.objects.all()
#         else:
#             ctx['filiais_disponiveis'] = Filial.objects.none()
#         return ctx


# class CriarPedidoFromSugestaoView(GerenteFilialRequiredMixin, View):
#     """
#     POST-only. Espera ``fornecedor=<id>`` no body. Para matriz aceita
#     também ``filial=<id>``; pra gerente é sempre a própria filial.

#     Recomputa a sugestão server-side e cria o Pedido. Redireciona pro
#     detalhe do pedido criado, ou de volta pra sugestão com mensagem
#     de erro caso não haja itens pra esse fornecedor.
#     """

#     http_method_names = ['post']

#     def post(self, request, *args, **kwargs):
#         filial = _resolver_filial(request)
#         if filial is None:
#             messages.error(request, 'Selecione uma filial antes de criar pedidos.')
#             return redirect('core:sugestao_pedido')

#         fornecedor_id = request.POST.get('fornecedor')
#         if not fornecedor_id:
#             messages.error(request, 'Fornecedor não informado.')
#             return redirect('core:sugestao_pedido')

#         fornecedor = get_object_or_404(Fornecedor, pk=fornecedor_id)
#         pedido = criar_pedido_da_sugestao(
#             filial=filial,
#             fornecedor=fornecedor,
#             usuario=request.user,
#         )
#         if pedido is None:
#             messages.warning(
#                 request,
#                 f'Nenhum item em ruptura para o fornecedor "{fornecedor}". '
#                 f'Sugestão recalculada — talvez o estoque já tenha sido reposto.',
#             )
#             return redirect('core:sugestao_pedido')

#         messages.success(
#             request,
#             f'Pedido #{pedido.pk} criado para {fornecedor} — {pedido.itens.count()} '
#             f'insumo(s) — total estimado R$ {sum((i.quantidade for i in pedido.itens.all()), 0)}.',
#         )
#         return HttpResponseRedirect(reverse('core:pedido_detail', args=[pedido.pk]))
