from django.db import models

from core.models import Produtor

class RecursoAgricola(models.Model):
    produtor = models.ForeignKey('core.Produtor', on_delete=models.CASCADE, related_name='recursos')
    nome_recurso = models.CharField(max_length=100)
    
    TIPO_RECURSO_CHOICES = [
        ('INSUMO', 'Insumo (Semente, Fertilizante, Defensivo)'),
        ('MAQUINARIO', 'Maquinário'),
        ('MAO_DE_OBRA', 'Mão de Obra'),
    ]
    tipo = models.CharField(max_length=15, choices=TIPO_RECURSO_CHOICES)
    quantidade_estoque = models.DecimalField(max_digits=10, decimal_places=2, help_text="Qtd em kg, litros, ou unidades")
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome_recurso} ({self.get_tipo_display()})"