from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from datetime import date
from core.views.insumo2 import mock_insumos


mock_atividades = [
    {
        "id": 1,
        "titulo": "Preparo do Solo",
        "tipo": "Plantio",
        "status": "Concluído",
        "num_integrantes": 5,
        "data_inicio": "2026-08-10",
        "latitude": "-6.4011",
        "longitude": "-38.8578",
        "data_termino": "2026-08-20",
    },
    {
        "id": 2,
        "titulo": "Plantio de Milho",
        "tipo": "Plantio",
        "status": "Em andamento",
        "num_integrantes": 3,
        "data_inicio": "2026-08-25",
        "latitude": "",
        "longitude": "",
        "data_termino": "",
    },
]
_next_id = 3

# Estrutura equivalente a uma futura tabela de itens_consumidos:
# cada registro relaciona uma atividade a um insumo por seus IDs.
mock_insumos_utilizados = [
    {"id": 1, "atividade_id": 1, "insumo_id": 1, "quantidade": 18, "data_adicionado": "2026-08-27"},
]
_next_insumo_utilizado_id = 2

TIPOS_FIXOS = [
    "Plantio",
    "Colheita",
    "Pecuária",
    "Irrigação",
    "Manutenção de Cercas",
]


class AtividadeRuralListView(LoginRequiredMixin, TemplateView):
    template_name = 'core/atividade_rural/list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Força o envio da lista atualizada para o HTML
        ctx['atividades'] = mock_atividades
        return ctx


class AtividadeRuralDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'core/atividade_rural/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        atividade_id = self.kwargs.get('pk')
        atividade = next((item for item in mock_atividades if item["id"] == atividade_id), None)
        ctx['atividade'] = atividade
        ctx['insumos_disponiveis'] = mock_insumos
        ctx['insumos_utilizados'] = [
            {
                **registro,
                'insumo': next(
                    (item for item in mock_insumos if item['id'] == registro['insumo_id']),
                    None,
                ),
            }
            for registro in mock_insumos_utilizados
            if registro['atividade_id'] == atividade_id
        ]
        return ctx


class AtividadeRuralInsumoCreateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        global _next_insumo_utilizado_id

        atividade = next((item for item in mock_atividades if item['id'] == pk), None)
        insumo_id = request.POST.get('insumo_id')
        insumo = next((item for item in mock_insumos if str(item['id']) == insumo_id), None)

        try:
            quantidade = float(request.POST.get('quantidade', 0))
        except (TypeError, ValueError):
            quantidade = 0

        if atividade and insumo and 0 < quantidade <= insumo['estoque_atual']:
            mock_insumos_utilizados.append({
                'id': _next_insumo_utilizado_id,
                'atividade_id': pk,
                'insumo_id': insumo['id'],
                'quantidade': quantidade,
                'data_adicionado': date.today().isoformat(),
            })
            _next_insumo_utilizado_id += 1
            insumo['estoque_atual'] -= quantidade

        return redirect('core:atividade-rural_detail', pk=pk)


class AtividadeRuralInsumoUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, consumo_id, *args, **kwargs):
        registro = next(
            (
                item for item in mock_insumos_utilizados
                if item['id'] == consumo_id and item['atividade_id'] == pk
            ),
            None,
        )
        insumo = next(
            (item for item in mock_insumos if registro and item['id'] == registro['insumo_id']),
            None,
        )

        try:
            quantidade = float(request.POST.get('quantidade', 0))
        except (TypeError, ValueError):
            quantidade = 0

        if registro and insumo and quantidade > 0:
            variacao = quantidade - registro['quantidade']
            if variacao <= insumo['estoque_atual']:
                insumo['estoque_atual'] -= variacao
                registro['quantidade'] = quantidade

        return redirect('core:atividade-rural_detail', pk=pk)


class AtividadeRuralInsumoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, consumo_id, *args, **kwargs):
        registro = next(
            (
                item for item in mock_insumos_utilizados
                if item['id'] == consumo_id and item['atividade_id'] == pk
            ),
            None,
        )
        if registro:
            insumo = next(
                (item for item in mock_insumos if item['id'] == registro['insumo_id']),
                None,
            )
            if insumo:
                insumo['estoque_atual'] += registro['quantidade']
            mock_insumos_utilizados.remove(registro)

        return redirect('core:atividade-rural_detail', pk=pk)


class AtividadeRuralCreateView(LoginRequiredMixin, View):
    template_name = 'core/atividade_rural/form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'atividade': None,
            'tipos_fixos': TIPOS_FIXOS,
        })

    def post(self, request, *args, **kwargs):
        global _next_id
        
        tipo = request.POST.get('tipo')
        if tipo == 'outro':
            tipo = request.POST.get('tipo_outro') or 'Outro'

        
        titulo_informado = request.POST.get('titulo') or f"Atividade {_next_id}"

        nova_atividade = {
            "id": _next_id,
            "titulo": titulo_informado,
            "tipo": tipo or "Não informado",
            "status": request.POST.get('status') or "Em andamento",
            "num_integrantes": request.POST.get('num_integrantes') or None,
            "data_inicio": request.POST.get('data_inicio') or "",
            "latitude": request.POST.get('latitude') or "",
            "longitude": request.POST.get('longitude') or "",
            "data_termino": request.POST.get('data_termino') or "",
        }
        
        # Insere no início da lista para aparecer primeiro na tabela
        mock_atividades.insert(0, nova_atividade)
        _next_id += 1
        return redirect('core:atividade-rural_list')


class AtividadeRuralUpdateView(LoginRequiredMixin, View):
    template_name = 'core/atividade_rural/form.html'

    def get(self, request, pk, *args, **kwargs):
        atividade = next((item for item in mock_atividades if item["id"] == pk), None)
        return render(request, self.template_name, {
            'atividade': atividade,
            'tipos_fixos': TIPOS_FIXOS,
        })

    def post(self, request, pk, *args, **kwargs):
        atividade = next((item for item in mock_atividades if item["id"] == pk), None)
        if atividade:
            tipo = request.POST.get('tipo')
            if tipo == 'outro':
                tipo = request.POST.get('tipo_outro') or 'Outro'

            atividade['titulo'] = request.POST.get('titulo') or atividade['titulo']
            atividade['tipo'] = tipo or atividade['tipo']
            atividade['status'] = request.POST.get('status') or "Em andamento"
            atividade['num_integrantes'] = request.POST.get('num_integrantes') or None
            atividade['data_inicio'] = request.POST.get('data_inicio') or ""
            atividade['latitude'] = request.POST.get('latitude') or ""
            atividade['longitude'] = request.POST.get('longitude') or ""
            atividade['data_termino'] = request.POST.get('data_termino') or ""

        return redirect('core:atividade-rural_list')


class AtividadeRuralCompleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        atividade = next((item for item in mock_atividades if item["id"] == pk), None)
        if atividade:
            atividade['status'] = 'Concluído'

        return redirect('core:atividade-rural_detail', pk=pk)


class AtividadeRuralDeleteView(LoginRequiredMixin, View):
    template_name = 'core/atividade_rural/confirm_delete.html'

    def get(self, request, pk, *args, **kwargs):
        atividade = next((item for item in mock_atividades if item["id"] == pk), None)
        return render(request, self.template_name, {'atividade': atividade})

    def post(self, request, pk, *args, **kwargs):
        global mock_atividades
        mock_atividades = [item for item in mock_atividades if item["id"] != pk]
        return redirect('core:atividade-rural_list')