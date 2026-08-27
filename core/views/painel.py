from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from core.models import AreaPlantio, DeteccaoDoencaNutricao


from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import AreaPlantio

# ==========================================
# VIEWS PRINCIPAIS (Protegidas)
# ==========================================

class HomeView(TemplateView):
    template_name = 'core/home.html'
    # A Home geralmente é pública, então não usamos o LoginRequiredMixin aqui.

class PainelView(LoginRequiredMixin, TemplateView):
    template_name = 'core/painel.html'
    # Se tentar acessar /painel/ sem login, o Django joga para /login/?next=/painel/
    # Quando logar, volta automático pra cá!

# ==========================================
# CRUD: ÁREA DE PLANTIO
# ==========================================

class AreaPlantioListView(LoginRequiredMixin, ListView):
    model = AreaPlantio
    template_name = 'core/area_plantio/list.html'
    context_object_name = 'areas'

    def get_queryset(self):
        # Exemplo de segurança: O produtor só vê as SUAS áreas de plantio, e não as de outros.
        return AreaPlantio.objects.filter(produtor=self.request.user)

class AreaPlantioDetailView(LoginRequiredMixin, DetailView):
    model = AreaPlantio
    template_name = 'core/area_plantio/detail.html'

class AreaPlantioCreateView(LoginRequiredMixin, CreateView):
    model = AreaPlantio
    template_name = 'core/area_plantio/form.html'
    fields = ['nome_area', 'tamanho_hectares', 'tipo_cultura', 'data_plantio']
    success_url = reverse_lazy('core:area-plantio_list')

    def form_valid(self, form):
        # Associa automaticamente a área de plantio ao usuário logado
        form.instance.produtor = self.request.user
        return super().form_valid(form)

class AreaPlantioUpdateView(LoginRequiredMixin, UpdateView):
    model = AreaPlantio
    template_name = 'core/area_plantio/form.html'
    fields = ['nome_area', 'tamanho_hectares', 'tipo_cultura']
    success_url = reverse_lazy('core:area-plantio_list')

class AreaPlantioDeleteView(LoginRequiredMixin, DeleteView):
    model = AreaPlantio
    template_name = 'core/area_plantio/confirm_delete.html'
    success_url = reverse_lazy('core:area-plantio_list')
    
# View de Login Customizada
class UserLoginView(LoginView):
    template_name = 'core/login.html' # Aponta para o seu arquivo HTML
    redirect_authenticated_user = True # Se já estiver logado, não mostra a tela de login
    # O redirecionamento de sucesso já é gerido pelo LOGIN_REDIRECT_URL no settings.py

# View do Painel do Produtor (Protegida)
class PainelView(LoginRequiredMixin, TemplateView):
    template_name = 'core/painel.html'
    
    # Se o usuário tentar acessar sem login, será jogado para LOGIN_URL
    # Se logar com sucesso, vem para cá e vê apenas os PRÓPRIOS dados
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Enviamos para o HTML apenas as áreas e alertas que pertencem a este usuário
        context['minhas_areas'] = AreaPlantio.objects.filter(produtor=user)
        # Exemplo de IA: buscando detecções ligadas às áreas do produtor
        context['alertas_ia'] = DeteccaoDoencaNutricao.objects.filter(area_plantio__produtor=user)
        
        return context