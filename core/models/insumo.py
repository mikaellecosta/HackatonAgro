from django.db import models

from .choices import UnidadeMedida


class Insumo(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nome',
    )
    unidade_medida = models.CharField(
        max_length=5,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.UNIDADE,
        verbose_name='Unidade de medida',
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        verbose_name='Estoque mínimo',
        help_text='Quantidade mínima antes de disparar alerta de ruptura.',
    )

    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.get_unidade_medida_display()})'
