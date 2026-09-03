from django.contrib.auth import get_user_model
from django.db import models

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

    def __str__(self):
        return f"{self.user.username} Information"
