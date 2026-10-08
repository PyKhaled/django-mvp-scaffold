from django.conf import settings


def identity(request):
    """Expose the configured display name to every request-rendered template."""
    return {"product_name": settings.SITE_NAME}
