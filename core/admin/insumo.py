from django.contrib import admin

from unfold.admin import ModelAdmin

from core.models import Insumo


@admin.register(Insumo)
class InsumoAdmin(ModelAdmin):
    list_display = ('nome', 'unidade_medida', 'estoque_minimo')
    search_fields = ('nome',)
    list_filter = ('unidade_medida',)
