from django.conf import settings
from django.db import models
from django.utils import timezone

from .choices import StatusMovimentacao, TipoMovimentacao


class Movimentacao(models.Model):
    filial = models.ForeignKey(
        'Filial',
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name='Filial',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name='Usuário',
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimentacao.choices,
        verbose_name='Tipo',
    )
    status = models.CharField(
        max_length=20,
        choices=StatusMovimentacao.choices,
        default=StatusMovimentacao.PENDENTE,
        verbose_name='Status',
    )
    data = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data',
    )
    insumos = models.ManyToManyField(
        'Insumo',
        through='ItemMovimentacao',
        related_name='movimentacoes',
        blank=True,
        verbose_name='Insumos movimentados',
    )

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.filial.nome} — {self.data:%d/%m/%Y %H:%M}'


class ItemMovimentacao(models.Model):
    movimentacao = models.ForeignKey(
        Movimentacao,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Movimentação',
    )
    insumo = models.ForeignKey(
        'Insumo',
        on_delete=models.PROTECT,
        related_name='itens_movimentacao',
        verbose_name='Insumo',
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name='Quantidade',
        help_text='Sempre positiva. O sinal vem do tipo da movimentação (entrada soma, saída/desperdício subtrai).',
    )

    class Meta:
        verbose_name = 'Item da movimentação'
        verbose_name_plural = 'Itens da movimentação'
        ordering = ['movimentacao__data', 'insumo__nome']

    def __str__(self):
        return f'{self.insumo.nome}: {self.quantidade}'


class Pedido(Movimentacao):
    fornecedor = models.ForeignKey(
        'Fornecedor',
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Fornecedor',
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data']

    def save(self, *args, **kwargs):
        # Pedido é sempre uma entrada (chegada de mercadoria do fornecedor).
        self.tipo = TipoMovimentacao.ENTRADA
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Pedido — {self.fornecedor.nome} → {self.filial.nome} — {self.data:%d/%m/%Y %H:%M}'


class Venda(Movimentacao):
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço',
        help_text='Valor total cobrado do cliente nesta venda.',
    )
    pratos = models.ManyToManyField(
        'Prato',
        through='ItemVenda',
        related_name='vendas',
        blank=True,
        verbose_name='Pratos vendidos',
    )

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data']

    def save(self, *args, **kwargs):
        # Venda é sempre uma saída (consumo de insumos do estoque).
        self.tipo = TipoMovimentacao.SAIDA
        super().save(*args, **kwargs)

    def recalcular_itens_movimentacao(self):
        """
        Recalcula os ItemMovimentacao (insumos consumidos) somando os insumos
        de cada prato vendido, multiplicados pela quantidade vendida.
        Substitui completamente os itens existentes.
        """
        from collections import defaultdict
        from decimal import Decimal

        consumo = defaultdict(lambda: Decimal('0'))

        itens_venda = self.itens_venda.select_related('prato').prefetch_related('prato__itens')
        for item_venda in itens_venda:
            for item_prato in item_venda.prato.itens.all():
                consumo[item_prato.insumo_id] += (
                    Decimal(item_venda.quantidade) * item_prato.quantidade
                )

        self.itens.all().delete()
        if consumo:
            ItemMovimentacao.objects.bulk_create([
                ItemMovimentacao(movimentacao=self, insumo_id=insumo_id, quantidade=qtd)
                for insumo_id, qtd in consumo.items()
                if qtd > 0
            ])

    def __str__(self):
        return f'Venda — {self.filial.nome} — R$ {self.preco} — {self.data:%d/%m/%Y %H:%M}'


class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens_venda',
        verbose_name='Venda',
    )
    prato = models.ForeignKey(
        'Prato',
        on_delete=models.PROTECT,
        related_name='itens_venda',
        verbose_name='Prato',
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantidade',
        help_text='Quantos pratos foram vendidos.',
    )

    class Meta:
        verbose_name = 'Item da venda'
        verbose_name_plural = 'Itens da venda'
        unique_together = [['venda', 'prato']]
        ordering = ['venda__data', 'prato__nome']

    def __str__(self):
        return f'{self.quantidade}× {self.prato.nome}'
