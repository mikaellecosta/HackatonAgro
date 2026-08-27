from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DiagnosticoCreateView(LoginRequiredMixin, TemplateView):
    """Tela para iniciar um diagnóstico por imagem."""

    template_name = 'core/diagnostico/novo.html'


class DiagnosticoListView(LoginRequiredMixin, TemplateView):
    """Tela inicial para acompanhar diagnósticos e iniciar uma nova análise."""

    template_name = 'core/diagnostico/lista.html'
