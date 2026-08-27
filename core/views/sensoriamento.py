from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


mock_estacoes = [
    {
        'id': 1,
        'nome': 'Estacao Norte',
        'area': 'Talhao 01 - Milho',
        'latitude': '-6.4011',
        'longitude': '-38.8578',
        'descricao': 'Estacao dedicada ao acompanhamento do desenvolvimento do milho e das condicoes do solo.',
        'status': 'Ativa',
        'ultima_leitura': 'Hoje, 10:42',
        'temperatura': '28.4 C',
        'umidade_solo': '63%',
        'chuva': '4.8 mm',
        'leituras': [58, 64, 61, 70, 67, 63],
        'temperatura_leituras': [25, 26, 27, 29, 28, 28],
        'chuva_leituras': [1, 2, 0, 4, 3, 5],
    },
    {
        'id': 2,
        'nome': 'Estacao Leste',
        'area': 'Talhao 02 - Soja',
        'latitude': '-6.3984',
        'longitude': '-38.8421',
        'descricao': 'Monitora a umidade e a temperatura do talhao de soja durante o ciclo de cultivo.',
        'status': 'Ativa',
        'ultima_leitura': 'Hoje, 10:39',
        'temperatura': '27.1 C',
        'umidade_solo': '71%',
        'chuva': '6.2 mm',
        'leituras': [68, 72, 69, 75, 73, 71],
        'temperatura_leituras': [24, 25, 26, 27, 28, 27],
        'chuva_leituras': [2, 3, 4, 5, 6, 6],
    },
    {
        'id': 3,
        'nome': 'Estacao Sul',
        'area': 'Pasto 03',
        'latitude': '-6.4147',
        'longitude': '-38.8652',
        'descricao': 'Acompanha as condicoes do pasto e indica periodos de baixa disponibilidade de agua.',
        'status': 'Atencao',
        'ultima_leitura': 'Hoje, 09:58',
        'temperatura': '30.2 C',
        'umidade_solo': '39%',
        'chuva': '0.0 mm',
        'leituras': [48, 45, 43, 41, 40, 39],
        'temperatura_leituras': [27, 28, 29, 30, 31, 30],
        'chuva_leituras': [4, 3, 2, 1, 0, 0],
    },
]


class SensoriamentoView(LoginRequiredMixin, TemplateView):
    template_name = 'core/sensoriamento.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estacoes'] = mock_estacoes
        return context