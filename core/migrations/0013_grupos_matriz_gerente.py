"""
Cria os grupos `Matriz` e `Gerente de Filial` com as permissões padrão.

Idempotente — pode rodar mais de uma vez (set substitui o conjunto anterior).
"""
from django.db import migrations


GRUPO_MATRIZ = 'Matriz'
GRUPO_GERENTE_FILIAL = 'Gerente de Filial'

# Matriz: acesso total ao core + gestão de usuários e grupos.
PERMISSOES_MATRIZ = {
    'core': {
        'fornecedor': ['add', 'change', 'delete', 'view'],
        'itemfornecedor': ['add', 'change', 'delete', 'view'],
        'insumo': ['add', 'change', 'delete', 'view'],
        'prato': ['add', 'change', 'delete', 'view'],
        'itemprato': ['add', 'change', 'delete', 'view'],
        'filial': ['add', 'change', 'delete', 'view'],
        'movimentacao': ['add', 'change', 'delete', 'view'],
        'itemmovimentacao': ['add', 'change', 'delete', 'view'],
        'pedido': ['add', 'change', 'delete', 'view'],
        'venda': ['add', 'change', 'delete', 'view'],
        'itemvenda': ['add', 'change', 'delete', 'view'],
        'user': ['add', 'change', 'delete', 'view'],
    },
    'auth': {
        'group': ['add', 'change', 'delete', 'view'],
    },
}

# Gerente de filial: opera as movimentações da própria unidade.
# Os demais cadastros são apenas leitura — quem mantém é a matriz.
PERMISSOES_GERENTE_FILIAL = {
    'core': {
        'movimentacao': ['add', 'change', 'view'],
        'itemmovimentacao': ['add', 'change', 'view'],
        'pedido': ['add', 'change', 'view'],
        'venda': ['add', 'change', 'view'],
        'itemvenda': ['add', 'change', 'view'],
        'insumo': ['view'],
        'fornecedor': ['view'],
        'itemfornecedor': ['view'],
        'filial': ['view'],
        'prato': ['view'],
        'itemprato': ['view'],
    },
}


def _coletar_permissions(apps, spec):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    perms = []
    for app_label, modelos in spec.items():
        for model_name, acoes in modelos.items():
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                continue
            for acao in acoes:
                codename = f'{acao}_{model_name}'
                try:
                    perms.append(Permission.objects.get(content_type=ct, codename=codename))
                except Permission.DoesNotExist:
                    continue
    return perms


def aplicar_permissoes(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    matriz, _ = Group.objects.get_or_create(name=GRUPO_MATRIZ)
    matriz.permissions.set(_coletar_permissions(apps, PERMISSOES_MATRIZ))

    gerente, _ = Group.objects.get_or_create(name=GRUPO_GERENTE_FILIAL)
    gerente.permissions.set(_coletar_permissions(apps, PERMISSOES_GERENTE_FILIAL))


def remover_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=[GRUPO_MATRIZ, GRUPO_GERENTE_FILIAL]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_filial_options_remove_fornecedor_contato_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(aplicar_permissoes, remover_grupos),
    ]
