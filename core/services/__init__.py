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
