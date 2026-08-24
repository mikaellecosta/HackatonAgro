from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from core.admin.filters import MinhaRegiaoFilter
from core.models import Fornecedor, ItemFornecedor


class ItemFornecedorInline(TabularInline):
    model = ItemFornecedor
    extra = 1
    autocomplete_fields = ('insumo',)


@admin.register(Fornecedor)
class FornecedorAdmin(ModelAdmin):
    list_display = (
        'nome', 'ramo_alimenticio', 'cidade', 'estado',
        'telefone', 'representante',
    )
    list_display_links = ('nome',)
    search_fields = (
        'nome',
        'cnpj',
        'representante',
        'cidade',
        'email',
    )
    list_filter = (MinhaRegiaoFilter, 'ramo_alimenticio', 'estado', 'cidade')
    inlines = [ItemFornecedorInline]
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'cnpj', 'ramo_alimenticio'),
        }),
        ('Contato', {
            'fields': ('representante', 'email', 'telefone'),
        }),
        ('Localização', {
            'fields': ('cidade', 'estado', 'endereco'),
        }),
    )
