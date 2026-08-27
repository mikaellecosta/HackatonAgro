# """
# CRUD de Fornecedor.

# - Leitura (list/detail): qualquer usuário logado.
# - Escrita (create/update/delete): apenas matriz.

# Listagem aceita query params para filtrar:
#     ?ramo=<RamoAlimenticio>
#     ?estado=<UF>
#     ?cidade=<texto>
#     ?regiao=cidade  -> filtra pela cidade da filial do gerente
#     ?regiao=estado  -> filtra pelo estado da filial do gerente
# """
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse_lazy
# from django.views.generic import (
#     CreateView,
#     DeleteView,
#     DetailView,
#     ListView,
#     UpdateView,
# )

# from core.forms import FornecedorForm
# from core.models import Fornecedor
# from core.views.base import MatrizRequiredMixin


# class FornecedorListView(LoginRequiredMixin, ListView):
#     """
#     Template: ``core/fornecedor/list.html``
#     Contexto:
#         object_list / fornecedores — queryset paginado de Fornecedor
#         filtros_ativos — dict com os filtros aplicados (echo do request)
#     """
#     model = Fornecedor
#     template_name = 'core/fornecedor/list.html'
#     context_object_name = 'fornecedores'
#     paginate_by = 25

#     def get_queryset(self):
#         qs = super().get_queryset()
#         params = self.request.GET

#         if ramo := params.get('ramo'):
#             qs = qs.filter(ramo_alimenticio=ramo)
#         if estado := params.get('estado'):
#             qs = qs.filter(estado=estado)
#         if cidade := params.get('cidade'):
#             qs = qs.filter(cidade__icontains=cidade)

#         # Atalho "minha região" — usa a filial do usuário logado.
#         regiao = params.get('regiao')
#         filial = getattr(self.request.user, 'filial', None)
#         if regiao == 'cidade' and filial and filial.cidade:
#             qs = qs.filter(cidade__iexact=filial.cidade)
#         elif regiao == 'estado' and filial and filial.estado:
#             qs = qs.filter(estado=filial.estado)

#         return qs

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         ctx['filtros_ativos'] = {
#             'ramo': self.request.GET.get('ramo', ''),
#             'estado': self.request.GET.get('estado', ''),
#             'cidade': self.request.GET.get('cidade', ''),
#             'regiao': self.request.GET.get('regiao', ''),
#         }
#         return ctx


# class FornecedorDetailView(LoginRequiredMixin, DetailView):
#     """Template: ``core/fornecedor/detail.html`` — `fornecedor` no contexto."""
#     model = Fornecedor
#     template_name = 'core/fornecedor/detail.html'
#     context_object_name = 'fornecedor'


# class FornecedorCreateView(MatrizRequiredMixin, CreateView):
#     """Template: ``core/fornecedor/form.html`` — `form` no contexto."""
#     model = Fornecedor
#     form_class = FornecedorForm
#     template_name = 'core/fornecedor/form.html'
#     success_url = reverse_lazy('core:fornecedor_list')


# class FornecedorUpdateView(MatrizRequiredMixin, UpdateView):
#     """Template: ``core/fornecedor/form.html``."""
#     model = Fornecedor
#     form_class = FornecedorForm
#     template_name = 'core/fornecedor/form.html'
#     success_url = reverse_lazy('core:fornecedor_list')


# class FornecedorDeleteView(MatrizRequiredMixin, DeleteView):
#     """Template: ``core/fornecedor/confirm_delete.html`` — `fornecedor` no contexto."""
#     model = Fornecedor
#     template_name = 'core/fornecedor/confirm_delete.html'
#     context_object_name = 'fornecedor'
#     success_url = reverse_lazy('core:fornecedor_list')
