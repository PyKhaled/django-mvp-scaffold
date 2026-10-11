from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit


def authentication_rate_limit(view):
    """Limit POST attempts per peer IP, including unsuccessful submissions."""
    @wraps(view)
    def guarded(request, *args, **kwargs):
        if getattr(request, "limited", False):
            response = HttpResponse("Too many attempts. Try again later.", status=429)
            response["Retry-After"] = "60"
            return response
        return view(request, *args, **kwargs)

    return ratelimit(
        key="ip", rate=lambda group, request: settings.AUTHENTICATION_RATE_LIMIT, method="POST", block=False,
    )(guarded)
