from .common import *

DEBUG = False

INSTALLED_APPS += [
    
]

MIDDLEWARE += [
    
]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", None),
        "USER": os.environ.get("POSTGRES_USER", None),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", None),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Production: use Google Cloud Storage
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")  # e.g., "my-django-bucket"

STATIC_ROOT = "staticfiles"
STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/staticfiles/"

# Media files (uploads) optional
MEDIA_ROOT = "mediafiles"
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/mediafiles/"

# Email SMTP
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT", '25')
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = os.environ.get("EMAIL_TIMEOUT")
EMAIL_SSL_KEYFILE = os.environ.get("EMAIL_SSL_KEYFILE")
EMAIL_SSL_CERTFILE = os.environ.get("EMAIL_SSL_CERTFILE")
