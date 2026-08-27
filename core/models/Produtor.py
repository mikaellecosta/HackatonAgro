from django.contrib.auth.models import AbstractUser
from django.db import models

class Produtor(AbstractUser):
    # se você usa username como login:
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    # se quiser campos extras:
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=11, unique=True, blank=True, null=True)

    class Meta:
        app_label = "core"

