from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.models import ItemVenda, Venda


@receiver([post_save, post_delete], sender=ItemVenda)
def recalcular_itens_movimentacao_da_venda_signal(sender, instance, **kwargs):
    """
    Sempre que um ItemVenda é criado, atualizado ou removido,
    recalcula os ItemMovimentacao (insumos consumidos) da Venda associada
    a partir das receitas dos pratos vendidos.
    """
    try:
        venda = instance.venda
    except Venda.DoesNotExist:
        # Venda já foi deletada (cascade) — não há o que recalcular.
        return
    venda.recalcular_itens_movimentacao()
