from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

User = get_user_model()


class GenderChoices(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'


class NationalityChoices(models.TextChoices):
    EGYPT = "EG", "Egypt"
    USA = "US", "United States"
    UK = "GB", "United Kingdom"
    OTHER = "OT", "Other"


class UserInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notes = models.TextField('Notes', blank=True, help_text='Additional notes about the user.', default='')
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username} Information"


class NotificationPreference(models.Model):
    class Kind(models.TextChoices):
        REPLY = "reply", "Ticket replies"
        ASSIGNMENT = "assignment", "Ticket assignments"
        STATUS = "status", "Ticket status changes"
        ACCOUNT = "account", "Account changes"

    class EmailMode(models.TextChoices):
        OFF = "off", "Off"
        IMMEDIATE = "immediate", "Immediate"
        DIGEST = "digest", "Daily digest"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=16, choices=Kind.choices)
    in_app = models.BooleanField(default=True)
    web_push = models.BooleanField(default=False)
    email_mode = models.CharField(max_length=16, choices=EmailMode.choices, default=EmailMode.OFF)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "kind"], name="unique_notification_preference")]


class NotificationEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey("helpdesk.Ticket", on_delete=models.SET_NULL, null=True, blank=True)
    kind = models.CharField(max_length=16, choices=NotificationPreference.Kind.choices)
    subject = models.CharField(max_length=255)
    path = models.TextField()
    digest = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


class WebPushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.URLField(max_length=2048, unique=True)
    keys = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationPush(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=16, choices=NotificationPreference.Kind.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
