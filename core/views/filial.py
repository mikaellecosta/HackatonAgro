# """
# CRUD de Filial.

# - Listagem/detalhe: gerente vê apenas a própria filial; matriz vê todas.
# - Criar/editar/excluir: matriz only.
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

# from core.forms import FilialForm
# from core.models import Filial
# from core.views.base import (
#     FilialScopedQuerysetMixin,
#     MatrizRequiredMixin,
# )


# class FilialListView(LoginRequiredMixin, FilialScopedQuerysetMixin, ListView):
#     """Template: ``core/filial/list.html`` — `filiais` no contexto."""
#     model = Filial
#     template_name = 'core/filial/list.html'
#     context_object_name = 'filiais'
#     paginate_by = 25
#     filial_lookup = 'pk'  # Filial em si


# class FilialDetailView(LoginRequiredMixin, FilialScopedQuerysetMixin, DetailView):
#     """Template: ``core/filial/detail.html`` — `filial` no contexto."""
#     model = Filial
#     template_name = 'core/filial/detail.html'
#     context_object_name = 'filial'
#     filial_lookup = 'pk'


# class FilialCreateView(MatrizRequiredMixin, CreateView):
#     """Template: ``core/filial/form.html``."""
#     model = Filial
#     form_class = FilialForm
#     template_name = 'core/filial/form.html'
#     success_url = reverse_lazy('core:filial_list')


# class FilialUpdateView(MatrizRequiredMixin, UpdateView):
#     """Template: ``core/filial/form.html``."""
#     model = Filial
#     form_class = FilialForm
#     template_name = 'core/filial/form.html'
#     success_url = reverse_lazy('core:filial_list')


# class FilialDeleteView(MatrizRequiredMixin, DeleteView):
#     """Template: ``core/filial/confirm_delete.html``."""
#     model = Filial
#     template_name = 'core/filial/confirm_delete.html'
#     context_object_name = 'filial'
#     success_url = reverse_lazy('core:filial_list')
