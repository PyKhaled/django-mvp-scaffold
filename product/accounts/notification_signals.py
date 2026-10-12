"""Notify registered ticket participants and accounts changed by another user."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from helpdesk.decorators import is_helpdesk_staff
from helpdesk.models import FollowUp, Ticket
from simple_history.models import HistoricalRecords

from product.accounts.notification_service import emit

User = get_user_model()


def request_actor():
    request = getattr(HistoricalRecords.context, "request", None)
    user = getattr(request, "user", None)
    return user if user and user.is_authenticated else None


def participants(ticket, public=True):
    users = {}
    if ticket.assigned_to and is_helpdesk_staff(ticket.assigned_to):
        users[ticket.assigned_to_id] = ticket.assigned_to
    # An ambiguous shared email address must not expose ticket updates.
    if public and ticket.submitter_email:
        submitters = list(
            User.objects.filter(email__iexact=ticket.submitter_email, is_active=True)[:2]
        )
        if len(submitters) == 1:
            users[submitters[0].pk] = submitters[0]
    return users.values()


@receiver(pre_save, sender=Ticket)
def remember_ticket(sender, instance, **kwargs):
    instance._notification_previous = (
        Ticket.objects.filter(pk=instance.pk).values("assigned_to_id", "status").first()
    )


@receiver(post_save, sender=Ticket)
def ticket_changed(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    previous = getattr(instance, "_notification_previous", None)
    actor = request_actor()
    if (
        instance.assigned_to_id
        and is_helpdesk_staff(instance.assigned_to)
        and (created or previous and previous["assigned_to_id"] != instance.assigned_to_id)
    ):
        emit(
            recipient=instance.assigned_to,
            actor=actor,
            kind="assignment",
            verb=f"Ticket #{instance.pk} was assigned to you",
            target=instance,
            urgent=instance.priority <= 2,
        )
    if previous and previous["status"] != instance.status:
        for recipient in participants(instance):
            emit(
                recipient=recipient,
                actor=actor,
                kind="status",
                verb=f"Ticket #{instance.pk}: {instance.get_status_display()}",
                target=instance,
                urgent=instance.priority <= 2,
            )


@receiver(post_save, sender=FollowUp)
def ticket_reply(sender, instance, created, raw=False, **kwargs):
    if not created or raw or not instance.comment:
        return
    for recipient in participants(instance.ticket, public=instance.public):
        if (
            instance.is_from_submitter
            and recipient.email
            and recipient.email.casefold() == (instance.ticket.submitter_email or "").casefold()
        ):
            continue
        emit(
            recipient=recipient,
            actor=instance.user or request_actor(),
            kind="reply",
            verb=f"New reply on ticket #{instance.ticket_id}",
            target=instance.ticket,
            urgent=instance.ticket.priority <= 2,
        )


@receiver(pre_save, sender=User)
def remember_account(sender, instance, **kwargs):
    instance._notification_previous_account = (
        User.objects.filter(pk=instance.pk)
        .values(
            "email",
            "password",
            "is_active",
            "first_name",
            "last_name",
        )
        .first()
    )


@receiver(post_save, sender=User)
def account_changed(sender, instance, created, raw=False, **kwargs):
    previous = getattr(instance, "_notification_previous_account", None)
    actor = request_actor()
    if created or raw or not previous or not actor or actor.pk == instance.pk:
        return
    changed = [field for field, value in previous.items() if value != getattr(instance, field)]
    if changed:
        emit(
            recipient=instance,
            actor=actor,
            kind="account",
            verb="Your account details were changed",
            urgent=bool({"password", "email", "is_active"}.intersection(changed)),
        )
