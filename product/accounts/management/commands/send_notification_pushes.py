"""Deliver generic browser alerts without exposing ticket or account details."""
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from pywebpush import WebPushException, webpush
from requests.exceptions import RequestException

from product.accounts.models import NotificationPreference, NotificationPush, WebPushSubscription
from product.accounts.web_push import configured, validate_subscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deliver pending web pushes; run once per minute.'

    def handle(self, *args, **options):
        if not configured():
            raise CommandError('Configure WEB_PUSH_PUBLIC_KEY, WEB_PUSH_PRIVATE_KEY and WEB_PUSH_SUBJECT.')
        sent = 0
        pending = NotificationPush.objects.filter(sent_at__isnull=True, cancelled_at__isnull=True)
        for pk in pending.values_list('pk', flat=True).iterator():
            with transaction.atomic():
                row = pending.select_for_update().select_related('user').filter(pk=pk).first()
                if not row:
                    continue
                enabled = NotificationPreference.objects.filter(user=row.user, kind=row.kind, web_push=True).exists()
                if not row.user.is_active or not enabled or row.created_at < timezone.now() - timedelta(days=1):
                    row.cancelled_at = timezone.now()
                    row.save(update_fields=['cancelled_at'])
                    continue
                failed = False
                for sub in WebPushSubscription.objects.filter(user=row.user):
                    try:
                        validate_subscription({'endpoint': sub.endpoint, 'keys': sub.keys})
                    except (ValueError, KeyError, TypeError, AttributeError):
                        sub.delete()
                        continue
                    try:
                        webpush(
                            subscription_info={'endpoint': sub.endpoint, 'keys': sub.keys},
                            data=json.dumps({'title': settings.SITE_NAME, 'body': 'You have a new update.', 'url': '/notifications/'}),
                            vapid_private_key=settings.WEB_PUSH_PRIVATE_KEY,
                            vapid_claims={'sub': settings.WEB_PUSH_SUBJECT},
                            timeout=10, ttl=3600,
                        )
                    except WebPushException as error:
                        if error.response is not None and error.response.status_code in (404, 410):
                            sub.delete()
                        else:
                            failed = True
                            logger.warning('Web push delivery failed for subscription %s', sub.pk)
                    except (RequestException, ValueError, OSError):
                        failed = True
                        logger.warning('Web push delivery failed for subscription %s', sub.pk)
                if not failed:
                    row.sent_at = timezone.now()
                    row.save(update_fields=['sent_at'])
                    sent += 1
        self.stdout.write(f'Delivered {sent} queued push update(s).')
