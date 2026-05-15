"""
Django settings for the EviFlow-Vis local studio (project package: vizforge).

Production: set DEBUG=False, tighten ALLOWED_HOSTS, and provide DJANGO_SECRET_KEY via env.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or str(raw).strip() == "":
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _split_csv(name: str) -> list[str]:
    raw = os.environ.get(name, "")
    return [p.strip() for p in raw.split(",") if p.strip()]


SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'skI7kGkfCzo6Rron1YhQ05Nf9PolIjzwDbFIwSSYMd-1Sq2B9nS310s8BQMQTJEgfQjnesZAk4hQrn0uHSFGzg',
)

# Default True for frictionless local work; set DJANGO_DEBUG=False for any shared or public demo host.
DEBUG = _env_truthy("DJANGO_DEBUG", default=True)

# Host header allow-list. Prefer explicit DJANGO_ALLOWED_HOSTS in demos; use DJANGO_ALLOW_ALL_HOSTS=1 only when needed.
_allowed_hosts = _split_csv("DJANGO_ALLOWED_HOSTS")
if _allowed_hosts:
    ALLOWED_HOSTS = _allowed_hosts
elif _env_truthy("DJANGO_ALLOW_ALL_HOSTS"):
    ALLOWED_HOSTS = ["*"]
elif DEBUG:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]", "0.0.0.0"]
else:
    # Production-like: never default to '*'.
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'corsheaders',
    'eviflow_vis',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Prototype: CSRF middleware disabled; views that need exemption use @csrf_exempt.
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vizforge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'vizforge.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# --- CORS ---
# Relaxed (allow-all) only when DEBUG and no explicit CORS_ALLOWED_ORIGINS — good for local hacking.
# When DEBUG is False, or when CORS_ALLOWED_ORIGINS is set, we use an explicit origin list (stricter).
_cors_origins = _split_csv("CORS_ALLOWED_ORIGINS")
if (not DEBUG) or _cors_origins:
    CORS_ORIGIN_ALLOW_ALL = False
    if _cors_origins:
        CORS_ALLOWED_ORIGINS = _cors_origins
    else:
        CORS_ALLOWED_ORIGINS = [
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ]
    CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
    try:
        from corsheaders.defaults import default_headers

        CORS_ALLOW_HEADERS = list(default_headers) + ["x-csrf-token", "x-requested-with"]
    except Exception:  # pragma: no cover - defensive
        CORS_ALLOW_HEADERS = ["accept", "authorization", "content-type", "origin", "user-agent", "x-csrf-token"]
    CORS_ALLOW_CREDENTIALS = True
else:
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_METHODS = "*"
    CORS_ALLOW_HEADERS = "*"
    CORS_ALLOW_CREDENTIALS = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ASGI + Channels (Redis channel layer for websocket-capable stack).
ASGI_APPLICATION = 'vizforge.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

# Dev-only: allow async views under Django's threaded runserver.
DJANGO_ALLOW_ASYNC_UNSAFE = True
