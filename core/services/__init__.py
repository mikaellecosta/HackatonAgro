"""
Camada de serviços do core — agregações e regras de domínio que
não cabem nem nos models, nem nas views.

Cada submódulo concentra um tópico:
    estoque     — saldo atual, ruptura
    consumo     — padrões de consumo de insumos no tempo
    faturamento — KPIs financeiros de venda
    pedidos     — sugestão e criação de pedidos a partir do estoque

Integração com WhatsApp foi extraída para o app `whatsapp`:
    from whatsapp.services import enviar_texto, EvolutionError
"""
from .consumo import consumo_no_periodo, top_insumos_consumidos
from .estoque import (
    estoque_atual,
    estoque_por_filial,
    insumos_em_ruptura,
)
from .faturamento import (
    faturamento_no_periodo,
    faturamento_por_filial,
    ticket_medio,
    top_pratos_vendidos,
)
from .pedidos import (
    criar_pedido_da_sugestao,
    sugerir_pedido,
    sugerir_pedido_da_cidade,
)
