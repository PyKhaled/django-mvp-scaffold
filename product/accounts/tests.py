import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.template.loader import get_template
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from helpdesk.models import FollowUp, Queue, Ticket
from helpdesk import settings as helpdesk_settings

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
        self.assertContains(response, 'name="remember_me"')

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

    def test_profile_settings_updates_the_user_with_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.get(reverse("settings:profile"))
        csrf_token = client.cookies["csrftoken"].value

        response = client.post(
            reverse("settings:profile"),
            {
                "csrfmiddlewaretoken": csrf_token,
                "first_name": "Creative",
                "last_name": "Operator",
                "email": "operator@example.com",
            },
        )

        self.assertRedirects(response, reverse("settings:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Creative")
        self.assertEqual(self.user.last_name, "Operator")
        self.assertEqual(self.user.email, "operator@example.com")

    def test_password_settings_changes_password_and_preserves_session(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.get(reverse("settings:change_password"))
        csrf_token = client.cookies["csrftoken"].value

        response = client.post(
            reverse("settings:change_password"),
            {
                "csrfmiddlewaretoken": csrf_token,
                "old_password": "test-pass-123",
                "new_password1": "new-test-pass-456",
                "new_password2": "new-test-pass-456",
            },
        )

        self.assertRedirects(response, reverse("settings:change_password"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-test-pass-456"))
        self.assertEqual(int(client.session["_auth_user_id"]), self.user.pk)

    def test_remember_me_sets_a_two_week_session(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": "test-pass-123",
                "remember_me": "1",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertGreaterEqual(self.client.session.get_expiry_age(), 1_209_000)

    def test_password_recovery_uses_the_product_template(self):
        template = get_template("registration/password_reset_form.html")

        self.assertIn("product/accounts/templates", template.origin.name)
        response = self.client.get(reverse("password_reset"))
        self.assertContains(response, "CreativeBatch")
        self.assertContains(response, "Forgot password")

    def test_appearance_save_does_not_clear_stored_preferences(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("settings:appearance"))

        self.assertEqual(
            response.content.count(b"window.localStorage.removeItem"),
            1,
        )


class HelpdeskWorkflowTests(TestCase):
    def setUp(self):
        self.queue = Queue.objects.create(
            title="General support",
            slug="general-support",
            allow_public_submission=True,
        )

    def test_public_homepage_renders_the_package_form_fields(self):
        response = self.client.get(reverse("helpdesk:home"))

        self.assertContains(response, 'name="queue"')
        self.assertContains(response, 'name="submitter_email"')
        self.assertNotContains(response, 'action="/helpdesk/"')
        self.assertContains(response, "secure ticket link")

    def test_public_ticket_submission_creates_ticket_and_returns_secure_link(self):
        response = self.client.post(
            reverse("helpdesk:submit"),
            {
                "queue": str(self.queue.pk),
                "title": "A production question",
                "body": "Please help with this workflow.",
                "submitter_email": "buyer@example.com",
                "priority": "3",
            },
        )

        ticket = Ticket.objects.get(title="A production question")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("helpdesk:public_view")))
        self.assertIn("key=", response["Location"])

    def test_ticket_requires_secret_and_hides_private_followups(self):
        ticket = Ticket.objects.create(
            title="Sensitive support request",
            queue=self.queue,
            submitter_email="buyer@example.com",
            description="Customer-visible description",
            priority="3",
            status=Ticket.OPEN_STATUS,
        )
        FollowUp.objects.create(
            ticket=ticket,
            title="Public update",
            comment="Customer-visible update",
            date=timezone.now(),
            public=True,
        )
        FollowUp.objects.create(
            ticket=ticket,
            title="Internal note",
            comment="Private staff-only note",
            date=timezone.now(),
            public=False,
        )
        query = {
            "ticket": ticket.ticket_for_url,
            "email": ticket.submitter_email,
        }

        response = self.client.get(reverse("helpdesk:public_view"), query)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(ticket.title.encode(), response.content)
        self.assertNotIn(b"Private staff-only note", response.content)

        query["key"] = "not-the-ticket-secret"
        response = self.client.get(reverse("helpdesk:public_view"), query)
        self.assertEqual(response.status_code, 403)

        query["key"] = ticket.secret_key
        response = self.client.get(reverse("helpdesk:public_view"), query)
        self.assertContains(response, ticket.title)
        self.assertContains(response, "Customer-visible update")
        self.assertNotContains(response, "Private staff-only note")

    def test_missing_secret_cannot_close_resolved_ticket(self):
        ticket = Ticket.objects.create(
            title="Resolved support request",
            queue=self.queue,
            submitter_email="buyer@example.com",
            description="Resolved",
            priority="3",
            status=Ticket.RESOLVED_STATUS,
        )

        self.client.get(
            reverse("helpdesk:public_view"),
            {
                "ticket": ticket.ticket_for_url,
                "email": ticket.submitter_email,
                "close": "1",
            },
        )

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.RESOLVED_STATUS)

    def test_missing_secret_cannot_match_a_legacy_blank_key(self):
        ticket = Ticket.objects.create(
            title="Legacy support request",
            queue=self.queue,
            submitter_email="buyer@example.com",
            description="Legacy record",
            priority="3",
            status=Ticket.OPEN_STATUS,
        )
        Ticket.objects.filter(pk=ticket.pk).update(secret_key="")

        response = self.client.get(
            reverse("helpdesk:public_view"),
            {
                "ticket": ticket.ticket_for_url,
                "email": ticket.submitter_email,
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_malformed_ticket_reference_is_rejected(self):
        response = self.client.get(
            reverse("helpdesk:public_view"),
            {
                "ticket": "not-a-number",
                "email": "buyer@example.com",
                "key": "attacker-controlled-key",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_editable_account_email_cannot_bypass_ticket_secret(self):
        user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="test-pass-123",
        )
        ticket = Ticket.objects.create(
            title="Buyer-owned request",
            queue=self.queue,
            submitter_email=user.email,
            description="Owned by the signed-in buyer",
            priority="3",
            status=Ticket.OPEN_STATUS,
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("helpdesk:public_view"),
            {
                "ticket": ticket.ticket_for_url,
                "email": user.email,
            },
        )

        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            reverse("helpdesk:public_view"),
            {
                "ticket": ticket.ticket_for_url,
                "email": user.email,
                "key": ticket.secret_key,
            },
        )
        self.assertContains(response, ticket.title)

    def test_public_ticket_route_preserves_the_package_protector(self):
        ticket = Ticket.objects.create(
            title="Protected support request",
            queue=self.queue,
            submitter_email="buyer@example.com",
            description="Protected by the configured integration hook",
            priority="3",
            status=Ticket.OPEN_STATUS,
        )

        with patch.object(
            helpdesk_settings,
            "HELPDESK_PUBLIC_VIEW_PROTECTOR",
            return_value=HttpResponseForbidden(),
        ):
            response = self.client.get(ticket.ticket_url)

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(ticket.title.encode(), response.content)

    def test_generated_ticket_url_supports_plus_address_email(self):
        ticket = Ticket.objects.create(
            title="Plus-address support request",
            queue=self.queue,
            submitter_email="buyer+tag@example.com",
            description="A valid plus-address ticket",
            priority="3",
            status=Ticket.RESOLVED_STATUS,
        )

        response = self.client.get(ticket.ticket_url)
        self.assertContains(response, ticket.title)

        response = self.client.get(f"{ticket.ticket_url}&close=1")
        self.assertEqual(response.status_code, 302)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.CLOSED_STATUS)


class ProductionSettingsTests(SimpleTestCase):
    project_root = Path(__file__).resolve().parents[2]

    def production_env(self):
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_ENV": "production",
                "SECRET_KEY": "a-production-secret-key-with-at-least-fifty-characters-123",
                "ALLOWED_HOSTS": "example.com",
                "POSTGRES_DB": "product",
                "POSTGRES_USER": "product",
                "POSTGRES_PASSWORD": "password",
                "GS_BUCKET_NAME": "product-assets",
                "EMAIL_HOST": "smtp.example.com",
            }
        )
        return env

    def run_settings_import(self, env, expression):
        return subprocess.run(
            [sys.executable, "-c", expression],
            cwd=self.project_root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_production_requires_secret_key(self):
        env = self.production_env()
        env.pop("SECRET_KEY")

        result = self.run_settings_import(env, "import product.settings")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY environment variable is required", result.stderr)

    def test_production_rejects_whitespace_only_secret_key(self):
        env = self.production_env()
        env["SECRET_KEY"] = "   "

        result = self.run_settings_import(env, "import product.settings")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY environment variable is required", result.stderr)

    def test_production_parses_typed_email_and_security_settings(self):
        env = self.production_env()
        env.update(
            {
                "EMAIL_PORT": "587",
                "EMAIL_TIMEOUT": "10.5",
                "EMAIL_USE_TLS": "true",
                "EMAIL_USE_SSL": "false",
            }
        )
        expression = (
            "from product import settings as s; "
            "assert s.EMAIL_PORT == 587; "
            "assert s.EMAIL_TIMEOUT == 10.5; "
            "assert s.EMAIL_USE_TLS is True; "
            "assert s.EMAIL_USE_SSL is False; "
            "assert s.SESSION_COOKIE_SECURE is True; "
            "assert s.CSRF_COOKIE_SECURE is True; "
            "assert s.HELPDESK_VIEW_A_TICKET_PUBLIC is False; "
            "assert s.STORAGES['default']['OPTIONS']['location'] == 'mediafiles'; "
            "assert s.STORAGES['staticfiles']['OPTIONS']['location'] == 'staticfiles'"
        )

        result = self.run_settings_import(env, expression)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_rejects_ambiguous_boolean_values(self):
        env = self.production_env()
        env["EMAIL_USE_TLS"] = "sometimes"

        result = self.run_settings_import(env, "import product.settings")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("EMAIL_USE_TLS environment variable must be a boolean", result.stderr)
