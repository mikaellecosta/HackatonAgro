# """
# CRUD de Prato — com receita inline (ItemPratoFormSet).

# - Leitura: qualquer usuário logado.
# - Escrita: apenas matriz.

# Create/Update lidam com formset da receita: o template recebe `form` e
# `receita_formset` separadamente; ambos precisam ser submetidos no POST.
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

# from core.forms import ItemPratoFormSet, PratoForm
# from core.models import Prato
# from core.views.base import MatrizRequiredMixin


# class PratoListView(LoginRequiredMixin, ListView):
#     """
#     Template: ``core/prato/list.html``
#     Aceita ?q=<nome>&ativo=<0|1> para filtrar.
#     """
#     model = Prato
#     template_name = 'core/prato/list.html'
#     context_object_name = 'pratos'
#     paginate_by = 25

#     def get_queryset(self):
#         qs = super().get_queryset()
#         if q := self.request.GET.get('q'):
#             qs = qs.filter(nome__icontains=q)
#         ativo = self.request.GET.get('ativo')
#         if ativo in ('0', '1'):
#             qs = qs.filter(ativo=ativo == '1')
#         return qs


# class PratoDetailView(LoginRequiredMixin, DetailView):
#     """
#     Template: ``core/prato/detail.html``
#     Contexto: `prato`, `receita` (queryset de ItemPrato com `insumo` join).
#     """
#     model = Prato
#     template_name = 'core/prato/detail.html'
#     context_object_name = 'prato'

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx['receita'] = self.object.itens.select_related('insumo')
#         return ctx


# class _PratoFormsetMixin:
#     """
#     Compartilha a lógica de POST que valida `form` + `receita_formset`
#     em transação, entre Create e Update.
#     """
#     success_url = reverse_lazy('core:prato_list')

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         if 'receita_formset' not in ctx:
#             if self.request.method == 'POST':
#                 ctx['receita_formset'] = ItemPratoFormSet(
#                     self.request.POST, instance=self.object,
#                 )
#             else:
#                 ctx['receita_formset'] = ItemPratoFormSet(instance=self.object)
#         return ctx

#     def form_valid(self, form):
#         ctx = self.get_context_data()
#         receita_formset = ctx['receita_formset']
#         with transaction.atomic():
#             self.object = form.save()
#             receita_formset.instance = self.object
#             if not receita_formset.is_valid():
#                 return self.form_invalid(form)
#             receita_formset.save()
#         return super().form_valid(form)


# class PratoCreateView(MatrizRequiredMixin, _PratoFormsetMixin, CreateView):
#     """
#     Template: ``core/prato/form.html``
#     Contexto: `form` (PratoForm) + `receita_formset` (ItemPratoFormSet).
#     """
#     model = Prato
#     form_class = PratoForm
#     template_name = 'core/prato/form.html'


# class PratoUpdateView(MatrizRequiredMixin, _PratoFormsetMixin, UpdateView):
#     """Template: ``core/prato/form.html`` — mesmo contexto do Create."""
#     model = Prato
#     form_class = PratoForm
#     template_name = 'core/prato/form.html'


# class PratoDeleteView(MatrizRequiredMixin, DeleteView):
#     """Template: ``core/prato/confirm_delete.html``."""
#     model = Prato
#     template_name = 'core/prato/confirm_delete.html'
#     context_object_name = 'prato'
#     success_url = reverse_lazy('core:prato_list')
