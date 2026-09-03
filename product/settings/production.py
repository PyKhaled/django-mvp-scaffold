from .common import *


def required_environment_value(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} environment variable is required in production")
    return value


def environment_boolean(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} environment variable must be a boolean")


DEBUG = False

SECRET_KEY = required_environment_value("SECRET_KEY")
if len(SECRET_KEY) < 50:
    raise RuntimeError("SECRET_KEY must contain at least 50 characters in production")

INSTALLED_APPS += [

]

MIDDLEWARE += [

]

ALLOWED_HOSTS = [
    host.strip()
    for host in required_environment_value("ALLOWED_HOSTS").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must contain at least one hostname")
DEFAULT_FROM_EMAIL = required_environment_value("DEFAULT_FROM_EMAIL")
SITE_DOMAIN = required_environment_value("SITE_DOMAIN")
SITE_NAME = os.environ.get("SITE_NAME", SITE_DOMAIN).strip() or SITE_DOMAIN
HELPDESK_DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL

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

# Email SMTP
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = required_environment_value("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = environment_boolean("EMAIL_USE_TLS")
EMAIL_USE_SSL = environment_boolean("EMAIL_USE_SSL")
EMAIL_TIMEOUT = (
    float(os.environ["EMAIL_TIMEOUT"])
    if os.environ.get("EMAIL_TIMEOUT")
    else None
)
EMAIL_SSL_KEYFILE = os.environ.get("EMAIL_SSL_KEYFILE")
EMAIL_SSL_CERTFILE = os.environ.get("EMAIL_SSL_CERTFILE")

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise RuntimeError("EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be enabled")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = environment_boolean("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = environment_boolean(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS"
)
SECURE_HSTS_PRELOAD = environment_boolean("SECURE_HSTS_PRELOAD")

if environment_boolean("TRUST_X_FORWARDED_PROTO"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Public ticket access is provided by the secret-key-protected integration
# route rather than django-helpdesk's email-only public view.
HELPDESK_VIEW_A_TICKET_PUBLIC = False
HELPDESK_USE_HTTPS_IN_EMAIL_LINK = True

REDIS_URL = required_environment_value("REDIS_URL").rstrip("/")

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

MAINTENANCE_MODE_STATE_BACKEND = ("maintenance_mode.backends.CacheBackend")
MAINTENANCE_MODE_CACHE_BACKEND = "maintenance_mode"
