import os
from pathlib import Path
from datetime import timedelta
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'storages',  # Para o MinIO
    'profiles',  # Nosso App
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'profile_service.urls'

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

WSGI_APPLICATION = 'profile_service.wsgi.application'

# === DATABASE CONFIG (Schema Isolado) ===
DATABASES = {
    'default': env.db('DATABASE_URL')
}
# Força o uso do schema 'profile_db'
DATABASES['default']['OPTIONS'] = {
    'options': '-c search_path=profile_db'
}

# === CELERY / RABBITMQ ===
CELERY_BROKER_URL = env('RABBITMQ_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_TASK_ACKS_LATE = True

# === SWAGGER ===
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'Lykos Profile Service API',
    'DESCRIPTION': 'Gerenciamento de perfis e portfólios',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === CACHE (REDIS) ===
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env('REDIS_URL', default='redis://redis:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
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

# Tempo padrão de cache para tabelas estáticas (ex: 24h)
CACHE_TTL_STATIC_DATA = 60 * 60 * 24