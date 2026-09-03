import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import Site
from django.db import transaction
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from product.accounts.emails import WelcomeEmailMessage

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send a welcome email to the user after account creation.
    """
    if created and instance.email and not instance.is_staff:
        if getattr(instance, "_skip_welcome_email", False):
            return

        def deliver_welcome_email():
            try:
                WelcomeEmailMessage(instance).send(fail_silently=False)
            except Exception:
                logger.exception("Could not send welcome email for user %s", instance.pk)
            else:
                logger.info("Welcome email sent for user %s", instance.pk)

        transaction.on_commit(deliver_welcome_email)


@receiver(post_migrate, dispatch_uid="accounts.configure_site")
def configure_site(sender, **kwargs):
    if sender.label != "accounts":
        return

    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": settings.SITE_DOMAIN, "name": settings.SITE_NAME},
    )


@receiver(user_logged_in, sender=User)
def remember_me_handler(sender, request, user, **kwargs):
    remember = request.POST.get("remember_me")
    if remember:
        request.session.set_expiry(60 * 60 * 24 * 14)  # 14 days
    else:
        request.session.set_expiry(0)
