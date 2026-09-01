import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")

if DJANGO_ENV == 'development':
    from .development import *

if DJANGO_ENV == 'production':
    from .production import *
