from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class WelcomeEmailMessage(EmailMessage):
    def __init__(self, user):
        subject = "Welcome to Our Platform 🎉"
        body = render_to_string("registration/welcome_email.txt", {
            "username": user.username,
            "email": user.email or "No email provided",
            "joined_at": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
        })
        recipient_list = [user.email]

        super().__init__(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=recipient_list)
