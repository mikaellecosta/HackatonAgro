from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View


mock_insumos = [
	{
		"id": 1,
		"nome": "Semente de milho híbrido",
		"categoria": "Sementes",
		"unidade_medida": "kg",
		"estoque_atual": 240,
		"estoque_minimo": 100,
		"cultura": "Milho",
	},
	{
		"id": 2,
		"nome": "Fertilizante NPK 10-10-10",
		"categoria": "Fertilizantes",
		"unidade_medida": "kg",
		"estoque_atual": 65,
		"estoque_minimo": 80,
		"cultura": "Milho e soja",
	},
	{
		"id": 3,
		"nome": "Defensivo agrícola",
		"categoria": "Defensivos",
		"unidade_medida": "L",
		"estoque_atual": 32,
		"estoque_minimo": 20,
		"cultura": "Soja",
	},
]
_next_id = 4

CATEGORIAS = [
	"Sementes",
	"Fertilizantes",
	"Defensivos",
	"Ração animal",
	"Insumos veterinários",
	"Outros",
]

UNIDADES_MEDIDA = ["Unidade (und)", "Tonelada (t)", "Kilograma (kg)", "Grama (g)", "Litro (L)", "Mililitros (mL)", "Saca"]


def _encontrar_insumo(insumo_id):
	return next((item for item in mock_insumos if item["id"] == insumo_id), None)


def _categoria_enviada(request):
	categoria = request.POST.get('categoria')
	if categoria == 'outro':
		return request.POST.get('categoria_outro') or 'Outros'
	return categoria or 'Outros'


class InsumoListView(LoginRequiredMixin, TemplateView):
	template_name = 'core/insumo/list.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		query = self.request.GET.get('q', '').strip().lower()
		ctx['insumos'] = [
			item for item in mock_insumos
			if not query or query in item['nome'].lower()
		]
		return ctx


class InsumoDetailView(LoginRequiredMixin, TemplateView):
	template_name = 'core/insumo/detail.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['insumo'] = _encontrar_insumo(self.kwargs['pk'])
		return ctx


class InsumoCreateView(LoginRequiredMixin, View):
	template_name = 'core/insumo/form.html'

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {
			'insumo': None,
			'categorias': CATEGORIAS,
			'unidades_medida': UNIDADES_MEDIDA,
		})

	def post(self, request, *args, **kwargs):
		global _next_id

		mock_insumos.insert(0, {
			'id': _next_id,
			'nome': request.POST.get('nome') or f'Insumo {_next_id}',
			'categoria': _categoria_enviada(request),
			'unidade_medida': request.POST.get('unidade_medida') or 'un',
			'estoque_atual': request.POST.get('estoque_atual') or 0,
			'estoque_minimo': request.POST.get('estoque_minimo') or 0,
			'cultura': request.POST.get('cultura') or 'Diversas culturas',
		})
		_next_id += 1
		return redirect('core:insumo_list')


class InsumoUpdateView(LoginRequiredMixin, View):
	template_name = 'core/insumo/form.html'

	def get(self, request, pk, *args, **kwargs):
		return render(request, self.template_name, {
			'insumo': _encontrar_insumo(pk),
			'categorias': CATEGORIAS,
			'unidades_medida': UNIDADES_MEDIDA,
		})

	def post(self, request, pk, *args, **kwargs):
		insumo = _encontrar_insumo(pk)
		if insumo:
			insumo['nome'] = request.POST.get('nome') or insumo['nome']
			insumo['categoria'] = _categoria_enviada(request)
			insumo['unidade_medida'] = request.POST.get('unidade_medida') or 'un'
			insumo['estoque_atual'] = request.POST.get('estoque_atual') or 0
			insumo['estoque_minimo'] = request.POST.get('estoque_minimo') or 0
			insumo['cultura'] = request.POST.get('cultura') or 'Diversas culturas'
		return redirect('core:insumo_list')


class InsumoDeleteView(LoginRequiredMixin, View):
	template_name = 'core/insumo/confirm_delete.html'

	def get(self, request, pk, *args, **kwargs):
		return render(request, self.template_name, {'insumo': _encontrar_insumo(pk)})

	def post(self, request, pk, *args, **kwargs):
		global mock_insumos
		mock_insumos = [item for item in mock_insumos if item['id'] != pk]
		return redirect('core:insumo_list')
