"""
Views públicas do core — CBVs do Django.

Templates esperados pelo front em frontend/templates/. Cada view define
seu `template_name` e o contrato do contexto está documentado no docstring
da classe.
"""
from core.views.painel import PainelView

from .filial import (
    FilialCreateView,
    FilialDeleteView,
    FilialDetailView,
    FilialListView,
    FilialUpdateView,
)
from .fornecedor import (
    FornecedorCreateView,
    FornecedorDeleteView,
    FornecedorDetailView,
    FornecedorListView,
    FornecedorUpdateView,
)
from .home import HomeView
from .insumo import (
    InsumoCreateView,
    InsumoDeleteView,
    InsumoDetailView,
    InsumoListView,
    InsumoUpdateView,
)
from .movimentacao import (
    MovimentacaoCreateView,
    MovimentacaoDeleteView,
    MovimentacaoDetailView,
    MovimentacaoListView,
    MovimentacaoUpdateView,
    PedidoCreateView,
    PedidoDeleteView,
    PedidoDetailView,
    PedidoListView,
    PedidoUpdateView,
    VendaCreateView,
    VendaDeleteView,
    VendaDetailView,
    VendaListView,
    VendaUpdateView,
)
from .pedidos_sugestao import (
    CriarPedidoFromSugestaoView,
    SugestaoPedidoView,
)
from .relatorios import (
    ConsumoView,
    EstoqueView,
    FaturamentoView,
    RupturaView,
)
from .prato import (
    PratoCreateView,
    PratoDeleteView,
    PratoDetailView,
    PratoListView,
    PratoUpdateView,
)

from .diagnostico import (
    DiagnosticoCreateView,
    DiagnosticoListView,
    DiagnosticoStatusView,
    DiagnosticoImageView,
)

from .atividade_rural import(
    AtividadeRuralListView,
    AtividadeRuralDetailView,
    AtividadeRuralCreateView,
    AtividadeRuralUpdateView,
    AtividadeRuralCompleteView,
    AtividadeRuralDeleteView
)
from .sensoriamento import SensoriamentoView