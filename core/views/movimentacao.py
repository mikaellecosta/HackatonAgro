# """
# CRUD das operações: Movimentacao, Pedido, Venda.

# Todas filial-scoped:
# - Listagem/detalhe: gerente só vê da própria filial; matriz vê todas.
# - Criar/editar: gerente cria na própria filial (filial/usuario auto-preenchidos);
#   matriz pode escolher livremente.
# - Excluir: gerente da própria filial OU matriz.

# Pedido e Venda têm formsets para os itens (insumos / pratos).
# """
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.db import transaction
# from django.urls import reverse_lazy
# from django.views.generic import (
#     CreateView,
#     DeleteView,
#     DetailView,
#     ListView,
#     UpdateView,
# )

# from core.forms import (
#     ItemMovimentacaoFormSet,
#     ItemVendaFormSet,
#     MovimentacaoForm,
#     PedidoForm,
#     VendaForm,
# )
# from core.models import Movimentacao, Pedido, Venda
# from core.views.base import (
#     FilialScopedFormMixin,
#     FilialScopedQuerysetMixin,
#     GerenteFilialRequiredMixin,
# )


# # ---------------------------------------------------------------------------
# # Movimentação genérica
# # ---------------------------------------------------------------------------

# class MovimentacaoListView(
#     LoginRequiredMixin,
#     FilialScopedQuerysetMixin,
#     ListView,
# ):
#     """Template: ``core/movimentacao/list.html`` — `movimentacoes` no contexto."""
#     model = Movimentacao
#     template_name = 'core/movimentacao/list.html'
#     context_object_name = 'movimentacoes'
#     paginate_by = 25

#     def get_queryset(self):
#         qs = super().get_queryset().select_related('filial', 'usuario')
#         params = self.request.GET
#         if status := params.get('status'):
#             qs = qs.filter(status=status)
#         if tipo := params.get('tipo'):
#             qs = qs.filter(tipo=tipo)
#         return qs


# class MovimentacaoDetailView(
#     LoginRequiredMixin,
#     FilialScopedQuerysetMixin,
#     DetailView,
# ):
#     """
#     Template: ``core/movimentacao/detail.html``
#     Contexto: `movimentacao`, `itens` (queryset de ItemMovimentacao com insumo).
#     """
#     model = Movimentacao
#     template_name = 'core/movimentacao/detail.html'
#     context_object_name = 'movimentacao'

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx['itens'] = self.object.itens.select_related('insumo')
#         return ctx


# class _ItemMovimentacaoFormsetMixin:
#     """Salva form + formset de itens em transação."""

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         if 'itens_formset' not in ctx:
#             if self.request.method == 'POST':
#                 ctx['itens_formset'] = ItemMovimentacaoFormSet(
#                     self.request.POST, instance=self.object,
#                 )
#             else:
#                 ctx['itens_formset'] = ItemMovimentacaoFormSet(instance=self.object)
#         return ctx

#     def form_valid(self, form):
#         ctx = self.get_context_data()
#         itens = ctx['itens_formset']
#         with transaction.atomic():
#             response = super().form_valid(form)
#             itens.instance = self.object
#             if not itens.is_valid():
#                 return self.form_invalid(form)
#             itens.save()
#         return response


# class MovimentacaoCreateView(
#     GerenteFilialRequiredMixin,
#     FilialScopedFormMixin,
#     _ItemMovimentacaoFormsetMixin,
#     CreateView,
# ):
#     """
#     Template: ``core/movimentacao/form.html``
#     Contexto: `form` + `itens_formset`.
#     """
#     model = Movimentacao
#     form_class = MovimentacaoForm
#     template_name = 'core/movimentacao/form.html'
#     success_url = reverse_lazy('core:movimentacao_list')


# class MovimentacaoUpdateView(
#     GerenteFilialRequiredMixin,
#     FilialScopedQuerysetMixin,
#     FilialScopedFormMixin,
#     _ItemMovimentacaoFormsetMixin,
#     UpdateView,
# ):
#     """Template: ``core/movimentacao/form.html``."""
#     model = Movimentacao
#     form_class = MovimentacaoForm
#     template_name = 'core/movimentacao/form.html'
#     success_url = reverse_lazy('core:movimentacao_list')


# class MovimentacaoDeleteView(
#     GerenteFilialRequiredMixin,
#     FilialScopedQuerysetMixin,
#     DeleteView,
# ):
#     """Template: ``core/movimentacao/confirm_delete.html``."""
#     model = Movimentacao
#     template_name = 'core/movimentacao/confirm_delete.html'
#     context_object_name = 'movimentacao'
#     success_url = reverse_lazy('core:movimentacao_list')


# # ---------------------------------------------------------------------------
# # Pedido (entrada — vem de fornecedor)
# # ---------------------------------------------------------------------------

# class PedidoListView(
#     LoginRequiredMixin,
#     FilialScopedQuerysetMixin,
#     ListView,
# ):
#     """Template: ``core/pedido/list.html`` — `pedidos` no contexto."""
#     model = Pedido
#     template_name = 'core/pedido/list.html'
#     context_object_name = 'pedidos'
#     paginate_by = 25

#     def get_queryset(self):
#         qs = super().get_queryset().select_related('filial', 'usuario', 'fornecedor')
#         if status := self.request.GET.get('status'):
#             qs = qs.filter(status=status)
#         if fornecedor := self.request.GET.get('fornecedor'):
#             qs = qs.filter(fornecedor_id=fornecedor)
#         return qs


# class PedidoDetailView(
#     LoginRequiredMixin,
#     FilialScopedQuerysetMixin,
#     DetailView,
# ):
#     """
#     Template: ``core/pedido/detail.html``
#     Contexto: `pedido`, `itens` (queryset de ItemMovimentacao com insumo).
#     """
#     model = Pedido
#     template_name = 'core/pedido/detail.html'
#     context_object_name = 'pedido'

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx['itens'] = self.object.itens.select_related('insumo')
#         return ctx


# class PedidoCreateView(
#     GerenteFilialRequiredMixin,
#     FilialScopedFormMixin,
#     _ItemMovimentacaoFormsetMixin,
#     CreateView,
# ):
#     """
#     Template: ``core/pedido/form.html``
#     Contexto: `form` (PedidoForm) + `itens_formset` (ItemMovimentacaoFormSet).
#     `tipo` é forçado para ENTRADA pelo Pedido.save().
#     """
#     model = Pedido
#     form_class = PedidoForm
#     template_name = 'core/pedido/form.html'
#     success_url = reverse_lazy('core:pedido_list')


# class PedidoUpdateView(
#     GerenteFilialRequiredMixin,
#     FilialScopedQuerysetMixin,
#     FilialScopedFormMixin,
#     _ItemMovimentacaoFormsetMixin,
#     UpdateView,
# ):
#     """Template: ``core/pedido/form.html``."""
#     model = Pedido
#     form_class = PedidoForm
#     template_name = 'core/pedido/form.html'
#     success_url = reverse_lazy('core:pedido_list')


# class PedidoDeleteView(
#     GerenteFilialRequiredMixin,
#     FilialScopedQuerysetMixin,
#     DeleteView,
# ):
#     """Template: ``core/pedido/confirm_delete.html``."""
#     model = Pedido
#     template_name = 'core/pedido/confirm_delete.html'
#     context_object_name = 'pedido'
#     success_url = reverse_lazy('core:pedido_list')


# # ---------------------------------------------------------------------------
# # Venda (saída — pratos consumidos)
# # ---------------------------------------------------------------------------

# class VendaListView(
#     LoginRequiredMixin,
#     FilialScopedQuerysetMixin,
#     ListView,
# ):
#     """Template: ``core/venda/list.html`` — `vendas` no contexto."""
#     model = Venda
#     template_name = 'core/venda/list.html'
#     context_object_name = 'vendas'
#     paginate_by = 25

#     def get_queryset(self):
#         qs = super().get_queryset().select_related('filial', 'usuario')
#         if status := self.request.GET.get('status'):
#             qs = qs.filter(status=status)
#         return qs


# class VendaDetailView(
#     LoginRequiredMixin,
#     FilialScopedQuerysetMixin,
#     DetailView,
# ):
#     """
#     Template: ``core/venda/detail.html``
#     Contexto:
#         venda            — instância
#         itens_venda      — pratos vendidos (com prato pré-fetchado)
#         insumos_consumidos — ItemMovimentacao auto-calculados pelo signal
#     """
#     model = Venda
#     template_name = 'core/venda/detail.html'
#     context_object_name = 'venda'

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx['itens_venda'] = self.object.itens_venda.select_related('prato')
#         ctx['insumos_consumidos'] = self.object.itens.select_related('insumo')
#         return ctx


# class _ItemVendaFormsetMixin:
#     """Salva VendaForm + ItemVendaFormSet em transação."""

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         if 'itens_formset' not in ctx:
#             if self.request.method == 'POST':
#                 ctx['itens_formset'] = ItemVendaFormSet(
#                     self.request.POST, instance=self.object,
#                 )
#             else:
#                 ctx['itens_formset'] = ItemVendaFormSet(instance=self.object)
#         return ctx

#     def form_valid(self, form):
#         ctx = self.get_context_data()
#         itens = ctx['itens_formset']
#         with transaction.atomic():
#             response = super().form_valid(form)
#             itens.instance = self.object
#             if not itens.is_valid():
#                 return self.form_invalid(form)
#             itens.save()  # signal recalcula ItemMovimentacao da venda
#         return response


# class VendaCreateView(
#     GerenteFilialRequiredMixin,
#     FilialScopedFormMixin,
#     _ItemVendaFormsetMixin,
#     CreateView,
# ):
#     """
#     Template: ``core/venda/form.html``
#     Contexto: `form` (VendaForm) + `itens_formset` (ItemVendaFormSet).
#     `tipo` é forçado para SAIDA pelo Venda.save().
#     Os ItemMovimentacao são preenchidos automaticamente pelos signals.
#     """
#     model = Venda
#     form_class = VendaForm
#     template_name = 'core/venda/form.html'
#     success_url = reverse_lazy('core:venda_list')


# class VendaUpdateView(
#     GerenteFilialRequiredMixin,
#     FilialScopedQuerysetMixin,
#     FilialScopedFormMixin,
#     _ItemVendaFormsetMixin,
#     UpdateView,
# ):
#     """Template: ``core/venda/form.html``."""
#     model = Venda
#     form_class = VendaForm
#     template_name = 'core/venda/form.html'
#     success_url = reverse_lazy('core:venda_list')


# class VendaDeleteView(
#     GerenteFilialRequiredMixin,
#     FilialScopedQuerysetMixin,
#     DeleteView,
# ):
#     """Template: ``core/venda/confirm_delete.html``."""
#     model = Venda
#     template_name = 'core/venda/confirm_delete.html'
#     context_object_name = 'venda'
#     success_url = reverse_lazy('core:venda_list')
