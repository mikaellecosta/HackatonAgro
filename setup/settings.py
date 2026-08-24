import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-)38ia0y%r0$0o!w3_wh=*$9k=b+p2rhm7m^5_zt($^om*o#%p_'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', 'host.docker.internal', '0.0.0.0'] if DEBUG else []

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.forms',
    'unfold.contrib.filters',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'whatsapp',
]

AUTH_USER_MODEL = 'core.User'

# Login/logout — apontam para as URLs do app core (core/urls.py).
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:painel'
LOGOUT_REDIRECT_URL = 'core:login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

UNFOLD = {
    'SITE_TITLE': 'Tereza IA',
    'SITE_HEADER': 'Tereza IA',
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': _('Catálogo'),
                'separator': True,
                'items': [
                    {
                        'title': _('Insumos'),
                        'icon': 'kitchen',
                        'link': reverse_lazy('admin:core_insumo_changelist'),
                    },
                    {
                        'title': _('Fornecedores'),
                        'icon': 'local_shipping',
                        'link': reverse_lazy('admin:core_fornecedor_changelist'),
                    },
                    {
                        'title': _('Pratos'),
                        'icon': 'restaurant_menu',
                        'link': reverse_lazy('admin:core_prato_changelist'),
                    },
                    {
                        'title': _('Filiais'),
                        'icon': 'store',
                        'link': reverse_lazy('admin:core_filial_changelist'),
                    },
                ],
            },
            {
                'title': _('Operações'),
                'separator': True,
                'items': [
                    {
                        'title': _('Pedidos'),
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:core_pedido_changelist'),
                    },
                    {
                        'title': _('Vendas'),
                        'icon': 'point_of_sale',
                        'link': reverse_lazy('admin:core_venda_changelist'),
                    },
                    {
                        'title': _('Movimentações'),
                        'icon': 'swap_horiz',
                        'link': reverse_lazy('admin:core_movimentacao_changelist'),
                    },
                ],
            },
            {
                'title': _('Usuários & Permissionamento'),
                'separator': True,
                'items': [
                    {
                        'title': _('Usuários'),
                        'icon': 'person',
                        'link': reverse_lazy('admin:core_user_changelist'),
                    },
                    {
                        'title': _('Grupos'),
                        'icon': 'groups',
                        'link': reverse_lazy('admin:auth_group_changelist'),
                    },
                ],
            },
        ],
    },
}

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'frontend/templates'],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'setup.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'frontend/static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'

MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===========================================================================
# Evolution API (WhatsApp)
# ---------------------------------------------------------------------------
# Configuração da Evolution rodando em ./evolution-api (docker compose).
# Consumida por core/services/whatsapp.py (envio) e core/views/webhooks.py
# (recebimento). Em produção, mova esses valores para variáveis de ambiente.
# ===========================================================================
EVOLUTION_BASE_URL = os.environ.get(
    'EVOLUTION_BASE_URL', 'http://127.0.0.1:8081',
)
EVOLUTION_API_KEY = os.environ.get(
    'EVOLUTION_API_KEY',
    '6ec2da00d49d0952f047c87f69b5b1c08bd1011c2bfa18bffa0666743697a01b',
)
EVOLUTION_INSTANCE = os.environ.get('EVOLUTION_INSTANCE', 'Tereza IA')

# Token opcional para validar o webhook por header `X-Webhook-Token`.
# Se vazio, valida pela própria apikey global da Evolution (header `apikey`).
EVOLUTION_WEBHOOK_TOKEN = os.environ.get('EVOLUTION_WEBHOOK_TOKEN', '')

# Timeout (segundos) para chamadas HTTP à Evolution.
EVOLUTION_HTTP_TIMEOUT = int(os.environ.get('EVOLUTION_HTTP_TIMEOUT', '15'))