from django.contrib import admin
from unfold.admin import ModelAdmin 
from core.models import (
    AreaPlantio, 
    MonitoramentoClimatico, 
    DeteccaoDoencaNutricao, 
    RecursoAgricola, 
    GestaoFinanceira, 
    Feedback
)

@admin.register(AreaPlantio)
class AreaPlantioAdmin(ModelAdmin):
    list_display = ('nome_area', 'produtor', 'tamanho_hectares', 'tipo_cultura')
    search_fields = ('nome_area', 'tipo_cultura')
    list_filter = ('tipo_cultura',)

@admin.register(MonitoramentoClimatico)
class MonitoramentoClimaticoAdmin(ModelAdmin):
    list_display = ('area_plantio', 'data_hora', 'temperatura', 'umidade', 'precipitacao_chuva')
    list_filter = ('data_hora', 'area_plantio')

@admin.register(DeteccaoDoencaNutricao)
class DeteccaoDoencaNutricaoAdmin(ModelAdmin):
    list_display = ('area_plantio', 'resultado_machine_learning', 'grau_severidade', 'status_tratamento')
    list_filter = ('grau_severidade', 'status_tratamento')

@admin.register(RecursoAgricola)
class RecursoAgricolaAdmin(ModelAdmin):
    list_display = ('nome_recurso', 'produtor', 'tipo', 'quantidade_estoque', 'custo_unitario')
    list_filter = ('tipo',)

@admin.register(GestaoFinanceira)
class GestaoFinanceiraAdmin(ModelAdmin):
    list_display = ('tipo_movimentacao', 'area_plantio', 'valor', 'data_registro')
    list_filter = ('tipo_movimentacao', 'data_registro')

@admin.register(Feedback)
class Feedback(ModelAdmin):
    list_display = ('tipo', 'produtor', 'data_contato', 'avaliacao_impacto')
    list_filter = ('tipo', 'avaliacao_impacto')