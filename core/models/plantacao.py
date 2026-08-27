from django.db import models

class Plantacao(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nome',
    )
    unidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço',
    )
    local = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Pratos inativos não aparecem no cardápio.',
    )
    insumos = models.ManyToManyField(
        'Insumo',
        through='ItemPrato',
        related_name='pratos',
        blank=True,
        verbose_name='Insumos da receita',
    )

    class Meta:
        verbose_name = 'Prato'
        verbose_name_plural = 'Pratos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ItemPrato(models.Model):
    prato = models.ForeignKey(
        Prato,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Prato',
    )
    insumo = models.ForeignKey(
        'Insumo',
        on_delete=models.CASCADE,
        related_name='itens_prato',
        verbose_name='Insumo',
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name='Quantidade',
        help_text='Quantidade do insumo na receita (na unidade definida no cadastro do insumo).',
    )

    class Meta:
        verbose_name = 'Item do prato'
        verbose_name_plural = 'Itens do prato'
        unique_together = [['prato', 'insumo']]
        ordering = ['prato__nome', 'insumo__nome']

    def __str__(self):
        return f'{self.prato.nome} — {self.insumo.nome}: {self.quantidade}'
