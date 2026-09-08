from .common import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"].strip()

ALLOWED_HOSTS = [os.environ["ALLOWED_HOSTS"].strip()]
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
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Production: use separate Google Cloud Storage prefixes for collected static
# assets and user-uploaded media.
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME").strip()

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

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/")

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

SECURE_SSL_REDIRECT = (
    os.environ.get("SECURE_SSL_REDIRECT", "true").strip().lower()
    in {"1", "true", "yes", "on"}
)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "").strip().lower()
    in {"1", "true", "yes", "on"}
)
SECURE_HSTS_PRELOAD = (
    os.environ.get("SECURE_HSTS_PRELOAD", "").strip().lower()
    in {"1", "true", "yes", "on"}
)

if (
    os.environ.get("TRUST_X_FORWARDED_PROTO", "").strip().lower()
    in {"1", "true", "yes", "on"}
):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")



# Email SMTP
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ["EMAIL_HOST"].strip()
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = (
    os.environ.get("EMAIL_USE_TLS", "").strip().lower()
    in {"1", "true", "yes", "on"}
)
EMAIL_USE_SSL = (
    os.environ.get("EMAIL_USE_SSL", "").strip().lower()
    in {"1", "true", "yes", "on"}
)
EMAIL_TIMEOUT = (
    float(os.environ["EMAIL_TIMEOUT"])
    if os.environ.get("EMAIL_TIMEOUT")
    else None
)
EMAIL_SSL_KEYFILE = os.environ.get("EMAIL_SSL_KEYFILE")
EMAIL_SSL_CERTFILE = os.environ.get("EMAIL_SSL_CERTFILE")
