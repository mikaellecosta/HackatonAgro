"""
Helpers para checagem de papel do usuário no sistema Tereza.

Em vez de adicionar um campo `papel` no modelo de usuário, usamos os Groups
nativos do Django. Estes helpers centralizam o "como descobrir o papel" para
não espalhar `user.groups.filter(name='...').exists()` por todo lado.
"""

GRUPO_MATRIZ = 'Matriz'
GRUPO_GERENTE_FILIAL = 'Gerente de Filial'


def is_matriz(user) -> bool:
    """Superusers e membros do grupo Matriz têm acesso global."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=GRUPO_MATRIZ).exists()


def is_gerente_filial(user) -> bool:
    """Membros do grupo Gerente de Filial — escopo limitado à própria filial."""
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=GRUPO_GERENTE_FILIAL).exists()
