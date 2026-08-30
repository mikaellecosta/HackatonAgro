from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from core.models import Venda, Prato
from core.permissions import is_gerente_filial, is_matriz
from core.services import faturamento_no_periodo, ticket_medio


class PainelView(LoginRequiredMixin, TemplateView):
      template_name = 'components/dashboard.html'
  
      def get_context_data(self, **kwargs):
          ctx = super().get_context_data(**kwargs)
          user = self.request.user
          filial = user.filial if is_gerente_filial(user) else None

          ctx['pratos_servidos'] = Venda.objects.filter(
              **({'filial': filial} if filial else {})
          ).count()
          ctx['clientes_atendidos'] = ...   # definir regra
          ctx['avaliacao_media'] = 4.9      # placeholder até ter modelo de avaliação
          ctx['anos_tradicao'] = 31
          ctx['faturamento_30d'] = faturamento_no_periodo(filial=filial, dias=30)
          ctx['ticket_medio_30d'] = ticket_medio(filial=filial, dias=30)
          ctx['top_pratos'] = Prato.objects.filter(ativo=True)[:5]  # ajustar com agregação real
          return ctx