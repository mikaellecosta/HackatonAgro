from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # O AbstractUser já traz: username, password, email, first_name, last_name, is_active, is_staff, etc.
    
    # Adicionando campos extras específicos para o seu negócio
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    
    TIPO_PLANO_CHOICES = [
        ('GRATUITO', 'Gratuito (com Ads)'),
        ('ASSINATURA', 'Assinatura Premium'),
        ('PERSONALIZADO', 'Infraestrutura Personalizada'),
    ]
    tipo_plano = models.CharField(
        max_length=15, 
        choices=TIPO_PLANO_CHOICES, 
        default='GRATUITO',
        verbose_name="Tipo de Plano"
    )

    # Você pode forçar o email a ser único (o padrão do Django não exige isso)
    email = models.EmailField(unique=True, verbose_name="E-mail")

    def __str__(self):
        # Retorna o nome completo se existir, senão retorna o email ou username
        return self.get_full_name() or self.email or self.username