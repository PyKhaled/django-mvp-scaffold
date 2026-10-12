"""Account-scoped notification generation and destination resolution."""

from datetime import timedelta
from urllib.parse import urlencode

from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from helpdesk.decorators import is_helpdesk_staff
from helpdesk.models import Ticket
from notifications.helpers import invalidate_unread_count_cache
from notifications.signals import notify

from product.accounts.models import NotificationEmail, NotificationPreference


def destination(notice, user):
    ticket = notice.target
    if isinstance(ticket, Ticket):
        if is_helpdesk_staff(user):
            return reverse("helpdesk:view", args=[ticket.pk])
        if (
            user.email
            and ticket.submitter_email
            and ticket.submitter_email.casefold() == user.email.casefold()
            and ticket.secret_key
        ):
            return (
                reverse("helpdesk:public_view")
                + "?"
                + urlencode(
                    {
                        "ticket": ticket.ticket_for_url,
                        "email": ticket.submitter_email,
                        "key": ticket.secret_key,
                    }
                )
            )
    if (notice.data or {}).get("kind") == "account":
        return reverse("settings:profile")
    return reverse("notifications:all") + f"#notification-{notice.slug}"


def emit(*, recipient, actor, kind, verb, target=None, urgent=False):
    """Group repeated unread events for one target; email is explicitly opt-in."""
    if not recipient.is_active or (
        actor and actor.pk == recipient.pk and type(actor) is type(recipient)
    ):
        return
    with transaction.atomic():
        preference, _ = NotificationPreference.objects.get_or_create(user=recipient, kind=kind)
        # Serialize emissions for the same account/category on supported databases.
        preference = NotificationPreference.objects.select_for_update().get(pk=preference.pk)
        if preference.in_app:
            recent = (
                recipient.notifications.unread()
                .filter(
                    timestamp__gte=timezone.now() - timedelta(hours=1),
                    data__kind=kind,
                    data__group=str(getattr(target, "pk", "account")),
                )
                .first()
            )
            if recent:
                recent.data = {**recent.data, "count": recent.data.get("count", 1) + 1}
                recent.timestamp = timezone.now()
                recent.verb = verb
                recent.level = "warning" if urgent else recent.level
                recent.save(update_fields=["data", "timestamp", "verb", "level"])
            else:
                notify.send(
                    actor or target or recipient,
                    recipient=recipient,
                    verb=verb,
                    target=target,
                    public=False,
                    level="warning" if urgent else "info",
                    kind=kind,
                    group=str(getattr(target, "pk", "account")),
                    count=1,
                )
            invalidate_unread_count_cache(recipient)
        if preference.email_mode != NotificationPreference.EmailMode.OFF and recipient.email:
            NotificationEmail.objects.create(
                user=recipient,
                kind=kind,
                subject=verb,
                ticket=target if isinstance(target, Ticket) else None,
                path=reverse("settings:profile")
                if kind == "account"
                else reverse("notifications:all"),
                digest=preference.email_mode == NotificationPreference.EmailMode.DIGEST,
            )
