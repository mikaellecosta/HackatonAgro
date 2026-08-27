from django.db import models

class GestaoFinanceira(models.Model):
    area_plantio = models.ForeignKey('core.AreaPlantio', on_delete=models.CASCADE, related_name='movimentacoes_financeiras', null=True, blank=True)
    data_registro = models.DateField(auto_now_add=True)
    
    TIPO_MOVIMENTACAO_CHOICES = [
        ('CUSTO_PREVISTO', 'Custo Previsto'),
        ('CUSTO_REAL', 'Custo Real'),
        ('RECEITA_ESTIMADA', 'Receita Estimada'),
        ('RECEITA_REALIZADA', 'Receita Realizada'),
    ]
    tipo_movimentacao = models.CharField(max_length=20, choices=TIPO_MOVIMENTACAO_CHOICES)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descricao = models.TextField(help_text="Ex: Compra de fertilizante XYZ, Venda da safra de milho")

    def __str__(self):
        return f"{self.get_tipo_movimentacao_display()} - R$ {self.valor}"