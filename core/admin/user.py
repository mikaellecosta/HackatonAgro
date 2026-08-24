from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from unfold.admin import ModelAdmin
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from core.models import User
from core.permissions import is_gerente_filial


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações adicionais', {
            'fields': ('cpf', 'telefone', 'foto_perfil'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações adicionais', {
            'fields': ('cpf', 'telefone', 'foto_perfil'),
        }),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'cpf', 'telefone', 'is_staff',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'cpf')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        # Quem está no grupo "Gerente de Filial" precisa ter alguma filial
        # vinculada via Filial.gerente — caso contrário o permissionamento
        # por filial filtra tudo e o usuário não enxerga nada.
        if is_gerente_filial(user) and not user.filiais_gerenciadas.exists():
            messages.warning(
                request,
                f'O usuário "{user}" está no grupo "Gerente de Filial" mas '
                f'ainda não foi vinculado como gerente de nenhuma filial. '
                f'Vá em Filiais e defina este usuário como gerente, senão '
                f'ele não verá nenhum dado ao logar.',
            )
