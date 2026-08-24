"""
Mixins reutilizáveis para as CBVs do core.

Espelham o que o admin faz em `core/admin/mixins.py`, mas para views públicas:
- restringem listagem por filial do gerente
- pré-preenchem filial/usuário ao salvar
- bloqueiam acesso pra quem não é matriz
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from core.permissions import is_gerente_filial, is_matriz


class MatrizRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Bloqueia acesso pra quem não é matriz (superuser ou grupo Matriz)."""

    def test_func(self):
        return is_matriz(self.request.user)


class GerenteFilialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite apenas gerente de filial OU matriz."""

    def test_func(self):
        user = self.request.user
        return is_matriz(user) or is_gerente_filial(user)


class FilialScopedQuerysetMixin:
    """
    Filtra o queryset por filial do gerente logado.

    - Matriz vê tudo.
    - Gerente vê apenas registros cuja filial bate com `request.user.filial`.
    - Demais usuários autenticados recebem queryset vazio.

    Configurável via:
        filial_lookup — caminho ORM (default 'filial', use 'pk' para FilialList).
    """
    filial_lookup = 'filial'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_matriz(user):
            return qs
        if is_gerente_filial(user):
            filial = user.filial
            if filial is not None:
                return qs.filter(**{self.filial_lookup: filial.pk})
        return qs.none()


class FilialScopedFormMixin:
    """
    Esconde `filial`/`usuario` do form e os preenche automaticamente para
    o gerente de filial — matriz continua escolhendo manualmente.

    - get_form remove os campos do formulário quando o usuário é gerente
      (mesmo que estejam declarados no Meta.fields do ModelForm).
    - form_valid preenche os campos no instance antes de salvar.

    Configurável:
        autopopular_filial / autopopular_usuario — bool, defaults True.
    """
    autopopular_filial = True
    autopopular_usuario = True

    def _eh_gerente_puro(self):
        user = self.request.user
        return is_gerente_filial(user) and not is_matriz(user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self._eh_gerente_puro():
            if self.autopopular_filial and 'filial' in form.fields:
                del form.fields['filial']
            if self.autopopular_usuario and 'usuario' in form.fields:
                del form.fields['usuario']
        return form

    def form_valid(self, form):
        if self._eh_gerente_puro():
            user = self.request.user
            obj = form.instance
            if self.autopopular_filial and not getattr(obj, 'filial_id', None):
                obj.filial = user.filial
            if self.autopopular_usuario and not getattr(obj, 'usuario_id', None):
                obj.usuario = user
        return super().form_valid(form)
