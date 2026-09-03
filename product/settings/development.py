from .common import *

DEBUG = True

ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

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
