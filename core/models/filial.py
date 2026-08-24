from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .choices import Estado


class Filial(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nome',
    )
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        verbose_name='CNPJ',
        help_text='Somente dígitos.',
    )
    email = models.EmailField(
        blank=True,
        verbose_name='E-mail',
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone',
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Cidade',
    )
    estado = models.CharField(
        max_length=2,
        choices=Estado.choices,
        blank=True,
        verbose_name='Estado (UF)',
    )
    endereco = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Endereço',
        help_text='Logradouro, número, bairro, CEP.',
    )
    is_matriz = models.BooleanField(
        default=False,
        verbose_name='É matriz?',
        help_text='Marque apenas em uma filial — a sede do grupo.',
    )
    gerente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filiais_gerenciadas',
        verbose_name='Gerente',
    )

    class Meta:
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiais'
        ordering = ['-is_matriz', 'nome']

    def __str__(self):
        return f'{self.nome} (matriz)' if self.is_matriz else self.nome

    def clean(self):
        super().clean()
        if self.is_matriz:
            outras_matrizes = Filial.objects.filter(is_matriz=True).exclude(pk=self.pk)
            if outras_matrizes.exists():
                raise ValidationError({
                    'is_matriz': 'Já existe uma filial marcada como matriz. '
                                 'Desmarque a outra antes de definir esta.',
                })
