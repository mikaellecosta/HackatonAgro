from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from core.models import Prato, ItemPrato


class ItemPratoInline(TabularInline):
    model = ItemPrato
    extra = 1
    autocomplete_fields = ('insumo',)


@admin.register(Prato)
class PratoAdmin(ModelAdmin):
    list_display = ('nome', 'preco', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)
    inlines = [ItemPratoInline]
