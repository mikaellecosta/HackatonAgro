"""
Mixins reutilizáveis para as CBVs do core (AgroTech).

- restringem listagem pelo produtor dono do registro
- pré-preenchem o produtor ao salvar formulários
- bloqueiam acesso para quem não é administrador do sistema
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# ==========================================
# Funções auxiliares de permissão
# ==========================================
def is_admin(user):
    """Verifica se o usuário é administrador (equipe do Hackathon/suporte)."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_produtor(user):
    """Verifica se o usuário é um produtor comum."""
    return user.is_authenticated and not is_admin(user)


# ==========================================
# Mixins de Bloqueio de Tela
# ==========================================
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Bloqueia acesso pra quem não é Administrador do sistema."""
    
    def test_func(self):
        return is_admin(self.request.user)


# ==========================================
# Mixins de Filtragem de Dados (Segurança)
# ==========================================
class ProdutorScopedQuerysetMixin:
    """
    Filtra o queryset pelo produtor logado.

    - Admin vê tudo.
    - Produtor vê apenas registros cujo campo produtor bate com ele mesmo.
    - Demais usuários recebem queryset vazio.

    Configurável via:
        produtor_lookup — nome do campo no banco (default 'produtor').
    """
    produtor_lookup = 'produtor'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if is_admin(user):
            return qs
            
        if is_produtor(user):
            # Filtra dinamicamente: ex: qs.filter(produtor=user)
            return qs.filter(**{self.produtor_lookup: user})
            
        return qs.none()


class ProdutorScopedFormMixin:
    """
    Esconde o campo `produtor` do form e o preenche automaticamente para
    o produtor comum — Admin continua escolhendo manualmente se quiser.

    - get_form: remove o campo do formulário visualmente.
    - form_valid: preenche o campo nos bastidores antes de salvar no banco.
    """
    autopopular_produtor = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Se for um produtor comum, tira o campo da tela para ele não alterar
        if is_produtor(self.request.user):
            if self.autopopular_produtor and 'produtor' in form.fields:
                del form.fields['produtor']
        return form

    def form_valid(self, form):
        # Se for um produtor comum, injeta o ID dele no objeto salvo
        if is_produtor(self.request.user):
            obj = form.instance
            if self.autopopular_produtor and not getattr(obj, 'produtor_id', None):
                obj.produtor = self.request.user
                
        return super().form_valid(form)