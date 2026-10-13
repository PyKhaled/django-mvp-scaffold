import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from product.accounts.models import WebPushSubscription
from product.accounts.web_push import configured, validate_subscription


@require_GET
@never_cache
def service_worker(request):
    source = Path(settings.BASE_DIR) / 'product/static/js/push-worker.js'
    return HttpResponse(source.read_text(), content_type='application/javascript', headers={'Service-Worker-Allowed': '/'})


@login_required
@require_GET
@never_cache
def configuration(request):
    return JsonResponse({'public_key': settings.WEB_PUSH_PUBLIC_KEY if configured() else ''})


@login_required
@require_POST
@never_cache
def subscription(request):
    try:
        if len(request.body) > 4096:
            raise ValueError('Subscription too large.')
        data = json.loads(request.body)
        if data.get('remove'):
            WebPushSubscription.objects.filter(user=request.user, endpoint=data['endpoint']).delete()
            return JsonResponse({'ok': True})
        if not configured():
            return JsonResponse({'error': 'Browser notifications are not configured.'}, status=503)
        endpoint, keys = validate_subscription(data)
        # A shared browser can change accounts; move its single subscription to the current user.
        WebPushSubscription.objects.update_or_create(endpoint=endpoint, defaults={'user': request.user, 'keys': keys})
    except (ValueError, KeyError, TypeError, AttributeError):
        return JsonResponse({'error': 'Invalid browser subscription.'}, status=400)
    return JsonResponse({'ok': True})
