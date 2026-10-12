"""Keep background notification requests out of the development toolbar history."""
from django.urls import reverse


def show_toolbar(request):
    from debug_toolbar.middleware import show_toolbar as default_show_toolbar

    if request.path_info == reverse("notification_preview"):
        return False
    return default_show_toolbar(request)
