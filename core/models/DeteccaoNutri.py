from django.db import models

from core.models import AreaPlantio


class DeteccaoDoencaNutricao(models.Model):
    area_plantio = models.ForeignKey('core.AreaPlantio', on_delete=models.CASCADE, related_name='deteccoes_doencas')
    data_deteccao = models.DateTimeField(auto_now_add=True)
    imagem_analisada = models.ImageField(upload_to='analises_plantas/', blank=True, null=True)
    resultado_machine_learning = models.CharField(max_length=255, help_text="Doença ou deficiência detectada")
    
    GRAU_SEVERIDADE_CHOICES = [
        ('BAIXO', 'Baixo'),
        ('MEDIO', 'Médio'),
        ('ALTO', 'Alto'),
        ('CRITICO', 'Crítico'),
    ]
    grau_severidade = models.CharField(max_length=10, choices=GRAU_SEVERIDADE_CHOICES)
    
    STATUS_TRATAMENTO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_TRATAMENTO', 'Em tratamento'),
        ('RESOLVIDO', 'Resolvido'),
    ]
    status_tratamento = models.CharField(max_length=15, choices=STATUS_TRATAMENTO_CHOICES, default='PENDENTE')

    def __str__(self):
        return f"{self.resultado_machine_learning} ({self.grau_severidade}) - {self.area_plantio.nome_area}"