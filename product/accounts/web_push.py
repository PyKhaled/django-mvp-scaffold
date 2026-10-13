"""Validate browser subscriptions before any outbound delivery."""
import base64
from urllib.parse import urlsplit

from django.conf import settings


def configured():
    return bool(settings.WEB_PUSH_PUBLIC_KEY and settings.WEB_PUSH_PRIVATE_KEY and settings.WEB_PUSH_SUBJECT)


def validate_subscription(data):
    endpoint = data['endpoint']
    url = urlsplit(endpoint)
    # Exact configured provider hosts prevent subscriptions becoming an SSRF proxy.
    if (url.scheme != 'https' or url.hostname not in settings.WEB_PUSH_ALLOWED_HOSTS
            or url.port not in (None, 443) or url.username or url.password or url.fragment
            or len(endpoint) > 2048):
        raise ValueError('Unsupported push provider.')
    keys = data['keys']
    for key, size in [('p256dh', 65), ('auth', 16)]:
        value = keys[key]
        decoded = base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)
        if len(decoded) != size or (key == 'p256dh' and decoded[0] != 4):
            raise ValueError('Invalid subscription key.')
    return endpoint, {key: keys[key] for key in ('p256dh', 'auth')}
