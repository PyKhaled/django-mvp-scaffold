from .common import *

DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY") or get_random_secret_key()

ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Polling responses must not cause the toolbar to fetch expired history entries
# and display an error overlay over the notification dropdown.
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "product.debug_toolbar_config.show_toolbar",
    # Our callback delegates to the default runtime DEBUG check, so it remains
    # disabled during tests despite using a custom callback path.
    "IS_RUNNING_TESTS": False,
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = Path.joinpath(BASE_DIR, 'staticfiles')

MEDIA_ROOT = Path.joinpath(BASE_DIR, 'mediafiles')
MEDIA_URL = '/media/'


# Email SMTP
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Shared by the local server and maintenance management command, without Redis.
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "maintenance_mode": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(BASE_DIR / ".cache" / "maintenance"),
        "TIMEOUT": None,
    },
}
