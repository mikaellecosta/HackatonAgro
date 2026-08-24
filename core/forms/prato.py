from django import forms
from django.forms import inlineformset_factory

from core.models import ItemPrato, Prato


class PratoForm(forms.ModelForm):
    class Meta:
        model = Prato
        fields = ('nome', 'preco', 'ativo')


class ItemPratoForm(forms.ModelForm):
    class Meta:
        model = ItemPrato
        fields = ('insumo', 'quantidade')


# Formset para editar a receita do prato (M2M com Insumo via ItemPrato).
ItemPratoFormSet = inlineformset_factory(
    Prato,
    ItemPrato,
    form=ItemPratoForm,
    extra=1,
    can_delete=True,
)
