"""
Filtros customizados reutilizáveis para o admin.
"""
from django.contrib import admin


class MinhaRegiaoFilter(admin.SimpleListFilter):
    """
    Filtra registros pela cidade ou estado da filial do usuário logado.

    Útil em FornecedorAdmin para que o gerente clique em "Minha cidade"
    e veja só os fornecedores da sua região, sem precisar saber o nome
    da cidade.

    Funciona em qualquer modelo que tenha campos `cidade` e `estado`.
    Se o usuário não tem filial vinculada, o filtro não aparece.
    """
    title = 'Minha região'
    parameter_name = 'minha_regiao'

    def lookups(self, request, model_admin):
        filial = getattr(request.user, 'filial', None)
        if not filial:
            return []
        opcoes = []
        if filial.cidade:
            opcoes.append(('cidade', f'Minha cidade ({filial.cidade})'))
        if filial.estado:
            opcoes.append(('estado', f'Meu estado ({filial.get_estado_display()})'))
        return opcoes

    def queryset(self, request, queryset):
        filial = getattr(request.user, 'filial', None)
        if not filial:
            return queryset
        if self.value() == 'cidade' and filial.cidade:
            return queryset.filter(cidade__iexact=filial.cidade)
        if self.value() == 'estado' and filial.estado:
            return queryset.filter(estado=filial.estado)
        return queryset
