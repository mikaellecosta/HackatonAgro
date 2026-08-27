from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class Produtor(models.Model):
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='produtor'
    )
    
    telefone = models.CharField(max_length=20, blank=True, null=True)
    
    TIPO_PLANO_CHOICES = [
        ('GRATUITO', 'Gratuito (com Ads)'),
        ('ASSINATURA', 'Assinatura Premium'),
        ('PERSONALIZADO', 'Infraestrutura Personalizada'),
    ]
    tipo_plano = models.CharField(max_length=15, choices=TIPO_PLANO_CHOICES, default='GRATUITO')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.tipo_plano})"