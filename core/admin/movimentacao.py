# from django.contrib import admin
# from django.utils.html import format_html_join
# from django.utils.safestring import mark_safe

# from unfold.admin import ModelAdmin, TabularInline

# from core.admin.mixins import FilialScopedAdminMixin
# from core.models import (
#     ItemMovimentacao,
#     ItemVenda,
#     Movimentacao,
#     Pedido,
#     Venda,
# )


# class ItemMovimentacaoInline(TabularInline):
#     model = ItemMovimentacao
#     extra = 1
#     autocomplete_fields = ('insumo',)


# class ItemVendaInline(TabularInline):
#     model = ItemVenda
#     extra = 1
#     autocomplete_fields = ('prato',)


# @admin.register(Movimentacao)
# class MovimentacaoAdmin(FilialScopedAdminMixin, ModelAdmin):
#     list_display = ('data', 'tipo', 'status', 'filial', 'usuario')
#     list_filter = ('status', 'tipo', 'filial', 'data')
#     search_fields = ('filial__nome', 'usuario__username', 'usuario__first_name')
#     autocomplete_fields = ('filial', 'usuario')
#     date_hierarchy = 'data'
#     inlines = [ItemMovimentacaoInline]


# @admin.register(Pedido)
# class PedidoAdmin(FilialScopedAdminMixin, ModelAdmin):
#     list_display = ('data', 'status', 'fornecedor', 'filial', 'usuario')
#     list_filter = ('status', 'fornecedor', 'filial', 'data')
#     search_fields = (
#         'fornecedor__nome',
#         'filial__nome',
#         'usuario__username',
#         'usuario__first_name',
#     )
#     autocomplete_fields = ('fornecedor', 'filial', 'usuario')
#     date_hierarchy = 'data'
#     exclude = ('tipo',)  # Pedido é sempre entrada — preenchido no save()
#     inlines = [ItemMovimentacaoInline]


# @admin.register(Venda)
# class VendaAdmin(FilialScopedAdminMixin, ModelAdmin):
#     list_display = ('data', 'status', 'preco', 'filial', 'usuario')
#     list_filter = ('status', 'filial', 'data')
#     search_fields = ('filial__nome', 'usuario__username', 'usuario__first_name')
#     autocomplete_fields = ('filial', 'usuario')
#     date_hierarchy = 'data'
#     exclude = ('tipo',)  # Venda é sempre saída — preenchido no save()
#     inlines = [ItemVendaInline]
#     readonly_fields = ('insumos_consumidos',)

#     def insumos_consumidos(self, obj):
#         if not obj.pk:
#             return '—'
#         itens = obj.itens.select_related('insumo')
#         if not itens.exists():
#             return '—'
#         return format_html_join(
#             mark_safe('<br>'),
#             '{}: {} {}',
#             (
#                 (item.insumo.nome, item.quantidade, item.insumo.get_unidade_medida_display())
#                 for item in itens
#             ),
#         )
#     insumos_consumidos.short_description = 'Insumos consumidos (calculado)'
