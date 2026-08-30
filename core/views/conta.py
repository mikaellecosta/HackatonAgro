from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'core/conta/perfil.html'


class ConfiguracoesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/conta/configuracoes.html'
