from .common import *

DEBUG = False


def required_environment_value(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value


def environment_boolean(name, default=False):
    value = os.environ.get(name, str(default)).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off", ""}:
        return False
    raise RuntimeError(f"{name} environment variable must be a boolean")


SECRET_KEY = required_environment_value("SECRET_KEY")
if len(SECRET_KEY) < 50:
    raise RuntimeError("SECRET_KEY must contain at least 50 characters")
DEFAULT_FROM_EMAIL = required_environment_value("DEFAULT_FROM_EMAIL")
SITE_DOMAIN = required_environment_value("SITE_DOMAIN")

ALLOWED_HOSTS = [host.strip() for host in required_environment_value("ALLOWED_HOSTS").split(",") if host.strip()]
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must contain explicit hostnames")
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += [

]

MIDDLEWARE += [

]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": required_environment_value("POSTGRES_DB"),
        "USER": required_environment_value("POSTGRES_USER"),
        "PASSWORD": required_environment_value("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Production: use separate Google Cloud Storage prefixes for collected static
# assets and user-uploaded media.
GS_BUCKET_NAME = required_environment_value("GS_BUCKET_NAME")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {"location": "mediafiles"},
    },
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {"location": "staticfiles"},
    },
}

STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/staticfiles/"

# Media files (uploads) optional
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/mediafiles/"

REDIS_URL = required_environment_value("REDIS_URL").rstrip("/")

from urllib.parse import urlsplit

if urlsplit(REDIS_URL).path:
    raise RuntimeError("REDIS_URL must not include a database suffix; use cache URL overrides")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("CACHE_REDIS_URL", f"{REDIS_URL}/0"),
    },

    "maintenance_mode": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("MAINTENANCE_REDIS_URL", f"{REDIS_URL}/1"),
    },
}

# Security settings
# https://docs.djangoproject.com/en/5.2/topics/security/
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = environment_boolean("SECURE_SSL_REDIRECT", True)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = environment_boolean("SECURE_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = environment_boolean("SECURE_HSTS_PRELOAD")
if environment_boolean("TRUST_X_FORWARDED_PROTO"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Email SMTP
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = required_environment_value("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = environment_boolean("EMAIL_USE_TLS")
EMAIL_USE_SSL = environment_boolean("EMAIL_USE_SSL")
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise RuntimeError("EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be enabled")
EMAIL_TIMEOUT = float(os.environ.get("EMAIL_TIMEOUT", "10"))
if EMAIL_TIMEOUT <= 0:
    raise RuntimeError("EMAIL_TIMEOUT must be positive")
EMAIL_SSL_KEYFILE = os.environ.get("EMAIL_SSL_KEYFILE")
EMAIL_SSL_CERTFILE = os.environ.get("EMAIL_SSL_CERTFILE")
