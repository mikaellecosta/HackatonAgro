from django import forms

from core.models import Fornecedor


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = (
            'nome',
            'cnpj',
            'ramo_alimenticio',
            'representante',
            'email',
            'telefone',
            'cidade',
            'estado',
            'endereco',
        )
