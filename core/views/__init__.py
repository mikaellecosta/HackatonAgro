"""
Views públicas do core — CBVs do Django.

Templates esperados pelo front em frontend/templates/. Cada view define
seu `template_name` e o contrato do contexto está documentado no docstring
da classe.
"""
from core.views.painel import PainelView

from .relatorios import (
    ConsumoView,
    EstoqueView,
    FaturamentoView,
    RupturaView,
)

from .diagnostico import (
    DiagnosticoCreateView,
    DiagnosticoListView
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
from .insumo2 import(
    InsumoListView,
    InsumoDetailView,
    InsumoCreateView,
    InsumoUpdateView,
    InsumoDeleteView
)