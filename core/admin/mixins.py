"""
Mixins reutilizáveis para o admin do core.

Centralizam o comportamento "matriz vê tudo / gerente só vê a própria filial"
para que cada ModelAdmin não precise duplicar a lógica de queryset, exclusão
de campos e auto-preenchimento de filial/usuário.
"""
from core.permissions import is_gerente_filial, is_matriz


class FilialScopedAdminMixin:
    """
    Restringe o ModelAdmin pelo escopo de filial do usuário logado.

    - Matriz (e superuser): enxerga tudo, sem filtros.
    - Gerente de Filial: enxerga apenas registros cuja filial é a dele,
      e ao salvar tem `filial`/`usuario` preenchidos automaticamente
      a partir do request (campos saem do form via get_exclude).
    - Demais usuários autenticados: queryset vazio (defesa em profundidade).

    Atributos configuráveis (override por admin):
        filial_lookup       — caminho ORM até a Filial (ex.: 'filial', 'pk',
                              'movimentacao__filial' para inlines).
        autopopular_filial  — se True, save_model preenche obj.filial.
        autopopular_usuario — se True, save_model preenche obj.usuario.
    """

    filial_lookup = 'filial'
    autopopular_filial = True
    autopopular_usuario = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_matriz(request.user):
            return qs
        if is_gerente_filial(request.user):
            filial = request.user.filial
            if filial is not None:
                # Sempre filtra por ID — funciona tanto para lookup direto
                # ('pk') quanto para FK ('filial', 'movimentacao__filial').
                return qs.filter(**{self.filial_lookup: filial.pk})
        return qs.none()

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if is_gerente_filial(request.user) and not is_matriz(request.user):
            if self.autopopular_filial and 'filial' not in excluded:
                excluded.append('filial')
            if self.autopopular_usuario and 'usuario' not in excluded:
                excluded.append('usuario')
        return excluded

    def save_model(self, request, obj, form, change):
        if is_gerente_filial(request.user) and not is_matriz(request.user):
            if self.autopopular_filial and not getattr(obj, 'filial_id', None):
                obj.filial = request.user.filial
            if self.autopopular_usuario and not getattr(obj, 'usuario_id', None):
                obj.usuario = request.user
        super().save_model(request, obj, form, change)
