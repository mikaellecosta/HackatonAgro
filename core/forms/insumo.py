from django import forms

from core.models import Insumo


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ('nome', 'unidade_medida', 'estoque_minimo')
