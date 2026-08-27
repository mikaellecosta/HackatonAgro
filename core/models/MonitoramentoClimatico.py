from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import AreaPlantio

class MonitoramentoClimatico(models.Model):
    area_plantio = models.ForeignKey('core.AreaPlantio', on_delete=models.CASCADE, related_name='monitoramentos_climaticos')
    data_hora = models.DateTimeField(auto_now_add=True)
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, help_text="Graus Celsius")
    umidade = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentagem")
    precipitacao_chuva = models.DecimalField(max_digits=8, decimal_places=2, help_text="Milímetros (mm)")
    alertas_risco = models.CharField(max_length=255, blank=True, null=True, help_text="Ex: Risco de Geada, Seca Extrema")

    def __str__(self):
        return f"Clima: {self.area_plantio.nome_area} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"