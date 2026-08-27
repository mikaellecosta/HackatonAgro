from django.db import models


class Insumo(models.Model):
    CATEGORIA_CHOICES = [
        ("Sementes", "Sementes"),
        ("Fertilizantes", "Fertilizantes"),
        ("Defensivos", "Defensivos"),
        ("Ração animal", "Ração animal"),
        ("Insumos veterinários", "Insumos veterinários"),
        ("Outros", "Outros"),
    ]

    UNIDADE_CHOICES = [
        ("und", "Unidade (und)"),
        ("t", "Tonelada (t)"),
        ("kg", "Kilograma (kg)"),
        ("g", "Grama (g)"),
        ("L", "Litro (L)"),
        ("mL", "Mililitros (mL)"),
        ("saca", "Saca"),
    ]

    nome = models.CharField(max_length=200)
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default="Outros",
    )
    unidade_medida = models.CharField(
        max_length=20,
        choices=UNIDADE_CHOICES,
        default="und",
    )
    estoque_atual = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    cultura = models.CharField(
        max_length=150,
        default="Diversas culturas",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

    def __str__(self):
        return self.nome

    @property
    def estoque_baixo(self):
        return self.estoque_atual < self.estoque_minimo