import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-order-dev')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bibliotecas de Terceiros
    'rest_framework',
    'drf_spectacular',
    'corsheaders',

    # Meus Apps
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'order_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'order_service.wsgi.application'

# Banco de Dados (Schema Isolado: order_db)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'lykos'),
        'USER': os.environ.get('POSTGRES_USER', 'lykos'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'secret'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': 5432,
        'OPTIONS': {
            'options': '-c search_path=order_db'
        }
    }
}

# Configuração do AbacatePay (Variável que você deve por no .env)
ABACATEPAY_API_KEY = os.environ.get('ABACATEPAY_API_KEY', '')

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'SIGNING_KEY': os.environ.get('JWT_SECRET', 'sua_chave_secreta_aqui'), # Tem que ser a MESMA do Auth Service
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Lykos Order Service',
    'DESCRIPTION': 'Gestão de Pedidos e Pagamentos (AbacatePay)',
    'VERSION': '1.0.0',
}

if os.getenv('USE_S3', 'False') == 'True':
    # Backend de armazenamento
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    # Configurações de Conexão
    AWS_ACCESS_KEY_ID = os.getenv('MINIO_ROOT_USER', 'minioadmin')
    AWS_SECRET_ACCESS_KEY = os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', 'http://minio:9000')

    # Configurações do Bucket
    # Cada serviço deve definir seu bucket principal no .env ou hardcoded aqui se preferir separar por pasta
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'lykos-general')

    # Configurações de URL e Assinatura
    AWS_S3_REGION_NAME = 'us-east-1'  # MinIO ignora, mas boto3 exige
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False  # Não sobrescreve arquivos com mesmo nome
    AWS_QUERYSTRING_AUTH = False  # Para arquivos públicos (Profile/Catalog), deixe False. Para Orders, True.

    # Garante que a URL gerada seja acessível externamente (via localhost ou domínio)
    # Em produção, isso seria 'https://minio.lykos.com.br/bucket-name'
    AWS_S3_CUSTOM_DOMAIN = f"{os.getenv('MINIO_PUBLIC_HOST', 'localhost:9000')}/{AWS_STORAGE_BUCKET_NAME}"

else:
    # Fallback para local (desenvolvimento sem docker ou teste)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'