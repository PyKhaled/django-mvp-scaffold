from pathlib import Path
from django.core.management.utils import get_random_secret_key
import os

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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hijack.middleware.HijackUserMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

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

OPENAI_APPEARANCE_MODEL = os.environ.get("OPENAI_APPEARANCE_MODEL", "gpt-5")


# Maintenance mode
# Toggle at runtime with: python manage.py maintenance_mode <on|off>
MAINTENANCE_MODE = None
MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.LocalFileBackend"
MAINTENANCE_MODE_STATE_FILE_PATH = str(BASE_DIR / "maintenance_mode_state.txt")
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_IGNORE_TESTS = True
MAINTENANCE_MODE_RETRY_AFTER = 900


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
#             'handlers': ['console', 'file'],
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'django.contrib.admin': {
#             'handlers': ['console', 'admin_security'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#     }
# }

# LOGIN_REDIRECT_URL = "/dashboard/"

# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF_COOKIE_SECURE = True


SITE_ID = 1

# DJANGO HELPDESK
# Teams mode requires the optional pinax-teams integration and is not needed
# for CreativeBatch's user-based ticket assignment.
HELPDESK_TEAMS_MODE_ENABLED = False

# Customers can submit and follow their own requests, but only employees marked
# as staff in Django admin can access the operational helpdesk.
HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE = False
HELPDESK_NAVIGATION_ENABLED = False
HELPDESK_SUBMIT_A_TICKET_PUBLIC = True
HELPDESK_VIEW_A_TICKET_PUBLIC = True
HELPDESK_STAFF_ONLY_TICKET_OWNERS = True
HELPDESK_STAFF_ONLY_TICKET_CC = True
HELPDESK_CREATE_TICKET_HIDE_ASSIGNED_TO = True
HELPDESK_TICKETS_TIMELINE_ENABLED = False

# Uploaded ticket attachments must be served through an authenticated view or
# private object storage. Keep them disabled while MEDIA_URL is publicly served.
HELPDESK_ENABLE_ATTACHMENTS = False

# NEWSLETTER - Removed (unused dependency)
# https://django-newsletter.readthedocs.io/

# ADMIN SECURITY SETTINGS
# https://docs.djangoproject.com/en/5.2/ref/contrib/admin/security/
