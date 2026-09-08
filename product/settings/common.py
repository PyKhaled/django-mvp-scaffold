import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())


# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")


# Application definition
# continued in development.py and production.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.redirects',

    'bootstrap4form',
    'maintenance_mode',
    'helpdesk',
    'product.accounts.apps.AccountsConfig',
    'notifications',
    'hijack',
    'hijack.contrib.admin',
    'simple_history',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hijack.middleware.HijackUserMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

ROOT_URLCONF = 'product.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Keep account templates ahead of contrib.admin's templates so the
        # product's authentication screens win regardless of app ordering.
        'DIRS': [
            SOURCE_DIR / 'accounts' / 'templates',
            SOURCE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'maintenance_mode.context_processors.maintenance_mode',
            ],
        },
    },
]

ASGI_APPLICATION = 'product.asgi.application'
WSGI_APPLICATION = 'product.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


LOGIN_REDIRECT_URL = "/dashboard/"


# Django sites framework
# https://docs.djangoproject.com/en/5.2/ref/contrib/sites/

SITE_ID = 1
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "localhost:8000")
SITE_NAME = os.environ.get("SITE_NAME", SITE_DOMAIN).strip() or SITE_DOMAIN


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', 'English'),
    ('ar', 'Arabic'),
]

LOCALE_PATHS = [SOURCE_DIR / 'locale']

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# Keep the source directory shared by every environment so collectstatic can
# discover the vendored Tabler build in production as well as development.
STATIC_URL = '/static/'
STATICFILES_DIRS = [SOURCE_DIR / 'static']

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Logging
# https://docs.djangoproject.com/en/4.2/topics/logging/#logging
# https://docs.djangoproject.com/en/4.2/ref/settings/#logging

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#         "default": {
#             "format": '%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
#             "datefmt": '%Y-%m-%d %H:%M:%S'
#         },
#     },
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'INFO',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': Path.joinpath(BASE_DIR, 'logs/debug.log'),
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'filters': ['special']
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['console', 'mail_admins'],
#             'level': 'ERROR',
#             "level": "WARNING",
#             'propagate': False,
#         },
#         "django.security": {
#             "handlers": ["console"],
#             "level": "WARNING",
#             "propagate": False,
#         },
#         "django.db.backends": {
#             "handlers": ["console"],
#             "level": "WARNING",
#             "propagate": False,
#         },
#         'django.contrib.admin': {
#             'handlers': ['console', 'admin_security'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#         "django.server": {
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": False,
#         }
#     }
# }




# DJANGO HELPDESK
# https://django-helpdesk.readthedocs.io/en/latest/configuration.html

HELPDESK_TEAMS_MODE_ENABLED = False
HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE = False
HELPDESK_NAVIGATION_ENABLED = False
HELPDESK_SUBMIT_A_TICKET_PUBLIC = True
HELPDESK_VIEW_A_TICKET_PUBLIC = False
HELPDESK_STAFF_ONLY_TICKET_OWNERS = True
HELPDESK_STAFF_ONLY_TICKET_CC = True
HELPDESK_CREATE_TICKET_HIDE_ASSIGNED_TO = True
HELPDESK_TICKETS_TIMELINE_ENABLED = False
HELPDESK_API_ENABLED = False
HELPDESK_DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL
HELPDESK_USE_HTTPS_IN_EMAIL_LINK = True
HELPDESK_PUBLIC_SUBMISSION_RATE_LIMIT = int(os.environ.get("HELPDESK_PUBLIC_SUBMISSION_RATE_LIMIT", "10"))
HELPDESK_PUBLIC_SUBMISSION_RATE_WINDOW = int(os.environ.get("HELPDESK_PUBLIC_SUBMISSION_RATE_WINDOW", "60"))
HELPDESK_ENABLE_ATTACHMENTS = False























# Maintenance mode
# Toggle at runtime with: python manage.py maintenance_mode <on|off>

MAINTENANCE_MODE = None
MAINTENANCE_MODE_STATE_BACKEND = ("maintenance_mode.backends.CacheBackend")
MAINTENANCE_MODE_CACHE_BACKEND = "maintenance_mode"
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_IGNORE_TESTS = True
MAINTENANCE_MODE_RETRY_AFTER = 900






