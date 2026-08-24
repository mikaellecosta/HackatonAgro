"""
Forms das operações: Movimentacao, Pedido, Venda + formsets de itens.

Os campos `filial` e `usuario` ficam declarados no form para que a matriz
possa escolher livremente. Para o gerente, o FilialScopedFormMixin remove
esses campos do form antes do render e preenche no save.

`tipo` é omitido em PedidoForm/VendaForm porque é forçado no save() do
modelo (Pedido = ENTRADA, Venda = SAIDA).
"""
from django import forms
from django.forms import inlineformset_factory

from core.models import (
    ItemMovimentacao,
    ItemVenda,
    Movimentacao,
    Pedido,
    Venda,
)


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ('filial', 'usuario', 'tipo', 'status', 'data')


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ('filial', 'usuario', 'fornecedor', 'status', 'data')


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ('filial', 'usuario', 'preco', 'status', 'data')


class _ItemMovimentacaoForm(forms.ModelForm):
    class Meta:
        model = ItemMovimentacao
        fields = ('insumo', 'quantidade')


# Formset para os insumos de uma Movimentação ou Pedido (Pedido é
# Movimentacao via multi-table, então usa o mesmo through).
ItemMovimentacaoFormSet = inlineformset_factory(
    Movimentacao,
    ItemMovimentacao,
    form=_ItemMovimentacaoForm,
    extra=1,
    can_delete=True,
)


class _ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ('prato', 'quantidade')


# Formset para os pratos vendidos. Os insumos consumidos são calculados
# automaticamente pelo signal post_save em core/signals/venda.py.
ItemVendaFormSet = inlineformset_factory(
    Venda,
    ItemVenda,
    form=_ItemVendaForm,
    extra=1,
    can_delete=True,
)
