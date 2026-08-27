from django.db import models

from core.models import Produtor

class Feedback(models.Model):
    produtor = models.ForeignKey('core.Produtor', on_delete=models.CASCADE, related_name='feedbacks')
    data_contato = models.DateTimeField(auto_now_add=True)
    
    TIPO_CONTATO_CHOICES = [
        ('FEEDBACK', 'Feedback da Plataforma'),
        ('SUPORTE', 'Pedido de Suporte'),
        ('TREINAMENTO', 'Solicitação de Treinamento'),
    ]
    tipo = models.CharField(max_length=15, choices=TIPO_CONTATO_CHOICES)
    descricao = models.TextField()
    
    avaliacao_impacto = models.PositiveSmallIntegerField(
        blank=True, null=True, 
        help_text="Nota de 1 a 5 sobre o impacto positivo na produção"
    )

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produtor.usuario.get_short_name()}"
   
