from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'core'

def _crud(prefix, viewset):
    """Gera os 5 paths padrão de CRUD para um modelo."""
    return [
        path(f'{prefix}/', viewset['list'].as_view(), name=f'{prefix}_list'),
        path(f'{prefix}/novo/', viewset['create'].as_view(), name=f'{prefix}_create'),
        path(f'{prefix}/<int:pk>/', viewset['detail'].as_view(), name=f'{prefix}_detail'),
        path(f'{prefix}/<int:pk>/editar/', viewset['update'].as_view(), name=f'{prefix}_update'),
        path(f'{prefix}/<int:pk>/excluir/', viewset['delete'].as_view(), name=f'{prefix}_delete'),
    ]

urlpatterns = [
    # Autenticação Nativa
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # No logout, redirecionamos o usuário de volta para a tela de login
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),
    
    # Home e Dashboards
    path('', views.HomeView.as_view(), name='home'),
    path('painel/', views.PainelView.as_view(), name='painel'),
    
    # (Adicione aqui as outras URLs de relatórios que você tinha...)
]

# Adicionando as rotas de CRUD (Exemplo: Área de Plantio)
urlpatterns += _crud('area-plantio', {
    'list': views.AreaPlantioListView,
    'detail': views.AreaPlantioDetailView,
    'create': views.AreaPlantioCreateView,
    'update': views.AreaPlantioUpdateView,
    'delete': views.AreaPlantioDeleteView,
})

# NOTA: Você fará o mesmo `urlpatterns += _crud(...)` para os outros modelos (Clima, Detecção, etc).