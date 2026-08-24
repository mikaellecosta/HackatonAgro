"""
CRUD de Insumo.

- Leitura: qualquer usuário logado.
- Escrita: apenas matriz.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import InsumoForm
from core.models import Insumo
from core.views.base import MatrizRequiredMixin


class InsumoListView(LoginRequiredMixin, ListView):
    """
    Template: ``core/insumo/list.html``
    Aceita ?q=<texto> para busca por nome.
    """
    model = Insumo
    template_name = 'core/insumo/list.html'
    context_object_name = 'insumos'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        if q := self.request.GET.get('q'):
            qs = qs.filter(nome__icontains=q)
        return qs


class InsumoDetailView(LoginRequiredMixin, DetailView):
    """Template: ``core/insumo/detail.html`` — `insumo` no contexto."""
    model = Insumo
    template_name = 'core/insumo/detail.html'
    context_object_name = 'insumo'


class InsumoCreateView(MatrizRequiredMixin, CreateView):
    """Template: ``core/insumo/form.html``."""
    model = Insumo
    form_class = InsumoForm
    template_name = 'core/insumo/form.html'
    success_url = reverse_lazy('core:insumo_list')


class InsumoUpdateView(MatrizRequiredMixin, UpdateView):
    """Template: ``core/insumo/form.html``."""
    model = Insumo
    form_class = InsumoForm
    template_name = 'core/insumo/form.html'
    success_url = reverse_lazy('core:insumo_list')


class InsumoDeleteView(MatrizRequiredMixin, DeleteView):
    """Template: ``core/insumo/confirm_delete.html``."""
    model = Insumo
    template_name = 'core/insumo/confirm_delete.html'
    context_object_name = 'insumo'
    success_url = reverse_lazy('core:insumo_list')
