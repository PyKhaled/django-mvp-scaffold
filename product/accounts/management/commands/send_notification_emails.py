"""Deliver queued immediate emails or the previous days' daily digest."""

import logging
from collections import Counter
from types import SimpleNamespace

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from product.accounts.models import NotificationEmail, NotificationPreference
from product.accounts.notification_service import destination

logger = logging.getLogger(__name__)


def current_path(row):
    if row.ticket:
        path = destination(
            SimpleNamespace(target=row.ticket, data={"kind": row.kind}, slug=""), row.user
        )
        return path.split("#notification-", 1)[0]
    return row.path


class Command(BaseCommand):
    help = "Send pending notification emails. Use --digest once daily for updates before today."

    def add_arguments(self, parser):
        parser.add_argument("--digest", action="store_true")

    def handle(self, *args, **options):
        digest = options["digest"]
        pending = NotificationEmail.objects.filter(
            sent_at__isnull=True, cancelled_at__isnull=True, digest=digest
        )
        if digest:
            midnight = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
            pending = pending.filter(created_at__lt=midnight)
        users = list(pending.values_list("user_id", flat=True).distinct())
        sent = 0
        for user_id in users:
            with transaction.atomic():
                rows = list(
                    pending.select_for_update(of=("self",))
                    .filter(user_id=user_id)
                    .select_related("user", "ticket")
                    .order_by("pk")
                )
                if not rows:
                    continue
                user = rows[0].user
                preferences = dict(
                    NotificationPreference.objects.filter(user=user).values_list(
                        "kind", "email_mode"
                    )
                )
                mode = "digest" if digest else "immediate"
                deliverable = [
                    row
                    for row in rows
                    if preferences.get(row.kind) == mode and user.is_active and user.email
                ]
                skipped = [row.pk for row in rows if row not in deliverable]
                # Cancel queued messages when an account opts out or loses its address.
                NotificationEmail.objects.filter(pk__in=skipped).update(cancelled_at=timezone.now())
                batches = (
                    [deliverable] if digest and deliverable else [[row] for row in deliverable]
                )
                for batch in batches:
                    subject = (
                        f"{settings.SITE_NAME}: daily notification digest"
                        if digest
                        else batch[0].subject
                    )
                    counts = Counter((row.subject, current_path(row)) for row in batch)
                    lines = []
                    for (title, path), count in counts.items():
                        suffix = f" ({count} updates)" if count > 1 else ""
                        lines.append(f"{title}{suffix}\nhttps://{settings.SITE_DOMAIN}{path}")
                    body = (
                        "\n\n".join(lines)
                        + f"\n\nNotification preferences: https://{settings.SITE_DOMAIN}/accounts/settings/notifications/"
                    )
                    try:
                        delivered = send_mail(
                            subject,
                            body,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                    except Exception:
                        logger.exception("Notification email delivery failed for user %s", user_id)
                        continue
                    if delivered:
                        NotificationEmail.objects.filter(pk__in=[row.pk for row in batch]).update(
                            sent_at=timezone.now()
                        )
                        sent += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} notification email(s)."))
