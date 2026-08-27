from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AreaPlantio(models.Model):
    produtor = models.ForeignKey('core.Produtor', on_delete=models.CASCADE, related_name='areas_plantio')
    nome_area = models.CharField(max_length=100, help_text="Ex: Lote Sul, Fazenda Boa Esperança")
    tamanho_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    coordenadas_gps = models.CharField(max_length=100, blank=True, null=True, help_text="Lat, Long")
    tipo_cultura = models.CharField(max_length=100, help_text="Ex: Milho, Soja, Tomate")
    
  
