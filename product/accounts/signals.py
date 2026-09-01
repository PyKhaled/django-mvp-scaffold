import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
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
        email_message = WelcomeEmailMessage(instance)
        email_message.send(fail_silently=True)
        print(f"📧 Welcome email sent to {instance.email}")

@receiver(user_logged_in, sender=User)
def remember_me_handler(sender, request, user, **kwargs):
    remember = request.POST.get("remember_me")
    if remember:
        request.session.set_expiry(60 * 60 * 24 * 14)  # 14 days
    else:
        request.session.set_expiry(0)
