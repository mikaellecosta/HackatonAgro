"""
URL configuration do app core.

Convenção:
- Paths em português, kebab-case.
- Namespace 'core' — use `{% url 'core:home' %}` nos templates.
- CRUD: <modelo>/, <modelo>/novo/, <modelo>/<pk>/, <modelo>/<pk>/editar/, <modelo>/<pk>/excluir/
- Auth: usa as views nativas do django.contrib.auth (LoginView/LogoutView).
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from core import views
from core.views import atividade_rural


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
       # Autenticação
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path('', views.HomeView.as_view(), name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += _crud('fornecedor', {
    'list': views.FornecedorListView,
    'detail': views.FornecedorDetailView,
    'create': views.FornecedorCreateView,
    'update': views.FornecedorUpdateView,
    'delete': views.FornecedorDeleteView,
})

urlpatterns += _crud('filial', {
    'list': views.FilialListView,
    'detail': views.FilialDetailView,
    'create': views.FilialCreateView,
    'update': views.FilialUpdateView,
    'delete': views.FilialDeleteView,
})

urlpatterns += _crud('insumo', {
    'list': views.InsumoListView,
    'detail': views.InsumoDetailView,
    'create': views.InsumoCreateView,
    'update': views.InsumoUpdateView,
    'delete': views.InsumoDeleteView,
})

urlpatterns += _crud('prato', {
    'list': views.PratoListView,
    'detail': views.PratoDetailView,
    'create': views.PratoCreateView,
    'update': views.PratoUpdateView,
    'delete': views.PratoDeleteView,
})

urlpatterns += _crud('movimentacao', {
    'list': views.MovimentacaoListView,
    'detail': views.MovimentacaoDetailView,
    'create': views.MovimentacaoCreateView,
    'update': views.MovimentacaoUpdateView,
    'delete': views.MovimentacaoDeleteView,
})

urlpatterns += _crud('pedido', {
    'list': views.PedidoListView,
    'detail': views.PedidoDetailView,
    'create': views.PedidoCreateView,
    'update': views.PedidoUpdateView,
    'delete': views.PedidoDeleteView,
})

urlpatterns += _crud('venda', {
    'list': views.VendaListView,
    'detail': views.VendaDetailView,
    'create': views.VendaCreateView,
    'update': views.VendaUpdateView,
    'delete': views.VendaDeleteView,
})

# Rotas de diagnóstico por imagem | precisamos do crud do diagnostico
urlpatterns += [ 
    path('diagnosticos/', views.DiagnosticoListView.as_view(), name='diagnosticos'),
    path('diagnosticos/novo/', views.DiagnosticoCreateView.as_view(), name='diagnostico_novo'),
    path('diagnosticos/<str:job_id>/status/', views.DiagnosticoStatusView.as_view(), name='diagnostico_status'),
    path('diagnosticos/<str:job_id>/imagem/<str:filename>/', views.DiagnosticoImageView.as_view(), name='diagnostico_imagem'),
]

urlpatterns += [
    path('sensoriamento/', views.SensoriamentoView.as_view(), name='sensoriamento'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('configuracoes/', views.ConfiguracoesView.as_view(), name='configuracoes'),
]


# Relatórios — read-only, agregam dados via core/services.
urlpatterns += [
    path('relatorios/estoque/', views.EstoqueView.as_view(), name='relatorio_estoque'),
    path('painel/', views.PainelView.as_view(), name='painel'),
    path('relatorios/ruptura/', views.RupturaView.as_view(), name='relatorio_ruptura'),
    path('relatorios/consumo/', views.ConsumoView.as_view(), name='relatorio_consumo'),
    path('relatorios/faturamento/', views.FaturamentoView.as_view(), name='relatorio_faturamento'),
]

# Solicitação guiada de insumos.
urlpatterns += [
    path(
        'sugestao-pedido/',
        views.SugestaoPedidoView.as_view(),
        name='sugestao_pedido',
    ),
    path(
        'sugestao-pedido/criar/',
        views.CriarPedidoFromSugestaoView.as_view(),
        name='sugestao_pedido_criar',
    ),
]

urlpatterns += _crud('atividade-rural', {
    'list': views.AtividadeRuralListView,
    'detail': views.AtividadeRuralDetailView,
    'create': views.AtividadeRuralCreateView,
    'update': views.AtividadeRuralUpdateView,
    'delete': views.AtividadeRuralDeleteView,
})

urlpatterns += [
    path(
        'atividade-rural/<int:pk>/insumos/',
        atividade_rural.AtividadeRuralInsumoCreateView.as_view(),
        name='atividade-rural_insumo_create',
    ),
    path(
        'atividade-rural/<int:pk>/insumos/<int:consumo_id>/excluir/',
        atividade_rural.AtividadeRuralInsumoDeleteView.as_view(),
        name='atividade-rural_insumo_delete',
    ),
    path(
        'atividade-rural/<int:pk>/insumos/<int:consumo_id>/editar/',
        atividade_rural.AtividadeRuralInsumoUpdateView.as_view(),
        name='atividade-rural_insumo_update',
    ),
]

urlpatterns += [
    path(
        'atividade-rural/<int:pk>/concluir/',
        views.AtividadeRuralCompleteView.as_view(),
        name='atividade-rural_complete',
    ),
]
