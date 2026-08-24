from django.db import models

from .choices import Estado, RamoAlimenticio


class Fornecedor(models.Model):
    nome = models.CharField(
        max_length=150,
        verbose_name='Nome / Razão social',
    )
    representante = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Nome do representante',
        help_text='Pessoa de contato comercial.',
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
    ramo_alimenticio = models.CharField(
        max_length=30,
        choices=RamoAlimenticio.choices,
        default=RamoAlimenticio.OUTROS,
        verbose_name='Ramo alimentício',
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
    insumos = models.ManyToManyField(
        'Insumo',
        through='ItemFornecedor',
        related_name='fornecedores',
        blank=True,
        verbose_name='Insumos disponíveis',
    )

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ItemFornecedor(models.Model):
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Fornecedor',
    )
    insumo = models.ForeignKey(
        'Insumo',
        on_delete=models.CASCADE,
        related_name='itens_fornecedor',
        verbose_name='Insumo',
    )
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço',
        help_text='Preço por unidade do insumo (na unidade definida no cadastro do insumo).',
    )
    prazo_entrega_dias = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Prazo de entrega (dias)',
    )

    class Meta:
        verbose_name = 'Item de fornecedor'
        verbose_name_plural = 'Itens de fornecedor'
        unique_together = [['fornecedor', 'insumo']]
        ordering = ['fornecedor__nome', 'insumo__nome']

    def __str__(self):
        return f'{self.fornecedor.nome} — {self.insumo.nome}: R$ {self.preco}'
