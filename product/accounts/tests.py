from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from product.accounts.models import UserInformation


User = get_user_model()


class AccountsTests(TestCase):
    def setUp(self):
        self.user = User(username="creative-operator", email="")
        self.user.set_password("test-pass-123")
        self.user.save()

    def test_user_information_can_be_created(self):
        information = UserInformation.objects.create(
            user=self.user,
            notes="Prefers concise creative briefs.",
        )

        self.assertEqual(information.user, self.user)
        self.assertEqual(str(information), "creative-operator Information")

    def test_login_uses_tabler_shell(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "css/tabler.min.css")
        self.assertContains(response, "CreativeBatch")

    def test_landing_page_uses_creativebatch_tabler_ui(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Creator production without the chaos.")
        self.assertContains(response, "css/tabler.min.css")
        self.assertContains(response, "css/app.css")

    def test_profile_uses_shared_shell(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "creative-operator")
        self.assertContains(response, "css/app.css")
