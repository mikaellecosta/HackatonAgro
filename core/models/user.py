from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    cpf = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        verbose_name='CPF',
    )

    telefone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Telefone',
    )

    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/',
        null=True,
        blank=True,
        verbose_name='Foto de perfil',
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def filial(self):
        """
        Filial gerenciada por este usuário (None se for matriz/sem vínculo).

        Conveniência para o permissionamento: hoje só gerentes têm vínculo
        com filial via `Filial.gerente`. Se um usuário gerencia mais de uma,
        retorna a primeira (caso de matriz/multi-unidade fica fora do MVP).
        """
        return self.filiais_gerenciadas.first()
