from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
  

class PainelView(LoginRequiredMixin, TemplateView):
      template_name = 'components/dashboard.html'
  
      def get_context_data(self, **kwargs):
          ctx = super().get_context_data(**kwargs)
          user = self.request.user

          ctx['clientes_atendidos'] = ...   # definir regra
          ctx['avaliacao_media'] = 4.9      # placeholder até ter modelo de avaliação
          ctx['anos_tradicao'] = 31
        
          return ctx