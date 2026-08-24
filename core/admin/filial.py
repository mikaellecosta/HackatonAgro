from django.contrib import admin

from unfold.admin import ModelAdmin

from core.admin.mixins import FilialScopedAdminMixin
from core.models import Filial


@admin.register(Filial)
class FilialAdmin(FilialScopedAdminMixin, ModelAdmin):
    # Filial não tem campo "filial" — o registro é a própria filial.
    filial_lookup = 'pk'
    autopopular_filial = False
    autopopular_usuario = False

    list_display = ('nome', 'is_matriz', 'cidade', 'estado', 'telefone', 'gerente')
    list_display_links = ('nome',)
    search_fields = (
        'nome',
        'cnpj',
        'cidade',
        'email',
        'gerente__username',
        'gerente__first_name',
    )
    list_filter = ('is_matriz', 'estado', 'cidade')
    autocomplete_fields = ('gerente',)
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'cnpj', 'is_matriz'),
        }),
        ('Contato', {
            'fields': ('email', 'telefone'),
        }),
        ('Localização', {
            'fields': ('cidade', 'estado', 'endereco'),
        }),
        ('Gestão', {
            'fields': ('gerente',),
        }),
    )
