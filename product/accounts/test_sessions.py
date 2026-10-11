from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from user_sessions.models import Session


class UserSessionTests(TestCase):
    def test_sessions_are_owned_and_other_devices_can_be_revoked(self):
        user = get_user_model().objects.create_user("sessions", password="session-pass")
        self.client.force_login(user)
        other = Client()
        other.force_login(user)
        stranger = get_user_model().objects.create_user("stranger")
        stranger_client = Client()
        stranger_client.force_login(stranger)
        response = self.client.get(reverse("user_sessions:session_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 2)
        self.assertEqual(self.client.post(reverse("user_sessions:session_delete_other")).status_code, 302)
        self.assertEqual(Session.objects.filter(user=user).count(), 1)
        self.assertEqual(Session.objects.filter(user=stranger).count(), 1)
        self.assertEqual(other.get(reverse("profile")).status_code, 302)
