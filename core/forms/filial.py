from django import forms

from core.models import Filial


class FilialForm(forms.ModelForm):
    class Meta:
        model = Filial
        fields = (
            'nome',
            'cnpj',
            'is_matriz',
            'email',
            'telefone',
            'cidade',
            'estado',
            'endereco',
            'gerente',
        )
