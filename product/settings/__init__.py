import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")

if DJANGO_ENV == 'development':
    from .development import *
elif DJANGO_ENV == 'production':
    from .production import *
else:
    raise RuntimeError(
        f"Unsupported DJANGO_ENV {DJANGO_ENV!r}; expected 'development' or 'production'"
    )
