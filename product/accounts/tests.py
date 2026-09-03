import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core import mail
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.template.loader import get_template
from django.test import Client, RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from helpdesk import settings as helpdesk_settings
from helpdesk.models import FollowUp, Queue, Ticket

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

    def test_account_pages_redirect_anonymous_users_to_login(self):
        protected_urls = [
            reverse("profile"),
            reverse("settings:profile"),
            reverse("settings:change_password"),
            reverse("settings:appearance"),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

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

    def test_invalid_profile_settings_do_not_change_the_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("settings:profile"),
            {
                "first_name": "Changed",
                "last_name": "Name",
                "email": "not-an-email-address",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "")
        self.assertEqual(self.user.last_name, "")
        self.assertEqual(self.user.email, "")

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

    def test_login_without_remember_me_expires_at_browser_close(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": "test-pass-123",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_logout_post_ends_the_authenticated_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertIn(response.status_code, {200, 302})
        self.assertNotIn("_auth_user_id", self.client.session)

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

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
    )
    def test_new_customer_receives_a_welcome_email(self):
        mail.outbox.clear()

        with self.captureOnCommitCallbacks(execute=True):
            User.objects.create_user(
                username="new-customer",
                email="new-customer@example.com",
                password="test-pass-123",
            )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new-customer@example.com"])
        self.assertIn("Welcome", mail.outbox[0].subject)
        self.assertIn("new-customer", mail.outbox[0].body)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
    )
    def test_staff_accounts_do_not_receive_customer_welcome_email(self):
        mail.outbox.clear()

        User.objects.create_user(
            username="support-agent",
            email="support-agent@example.com",
            password="test-pass-123",
            is_staff=True,
        )

        self.assertEqual(mail.outbox, [])


class HelpdeskWorkflowTests(TestCase):
    def setUp(self):
        cache.clear()
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

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("helpdesk:public_view")))
        self.assertIn("key=", response["Location"])

    def test_public_ticket_submission_enforces_csrf(self):
        client = Client(enforce_csrf_checks=True)
        submission = {
            "queue": str(self.queue.pk),
            "title": "CSRF-protected question",
            "body": "This request must come from the rendered form.",
            "submitter_email": "buyer@example.com",
            "priority": "3",
        }

        response = client.post(reverse("helpdesk:submit"), submission)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Ticket.objects.filter(title=submission["title"]).exists())

        client.get(reverse("helpdesk:home"))
        submission["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
        response = client.post(reverse("helpdesk:submit"), submission)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ticket.objects.filter(title=submission["title"]).exists())

    def test_invalid_public_ticket_submission_renders_field_errors(self):
        response = self.client.post(
            reverse("helpdesk:submit"),
            {"queue": str(self.queue.pk), "priority": "3"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertEqual(Ticket.objects.count(), 0)

    def test_staff_helpdesk_pages_are_restricted_to_staff(self):
        dashboard_url = reverse("helpdesk:dashboard")

        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 302)

        customer = User.objects.create_user(
            username="customer",
            password="test-pass-123",
        )
        self.client.force_login(customer)
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 302)

        customer.is_staff = True
        customer.save(update_fields=["is_staff"])
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Helpdesk Dashboard")

    def test_staff_can_render_ticket_creation_and_detail_forms(self):
        staff_user = User.objects.create_user(
            username="support-agent",
            password="test-pass-123",
            is_staff=True,
        )
        ticket = Ticket.objects.create(
            title="Visible staff ticket",
            queue=self.queue,
            submitter_email="buyer@example.com",
            description="Staff should be able to read this request.",
            priority="3",
            status=Ticket.OPEN_STATUS,
        )
        self.client.force_login(staff_user)

        create_response = self.client.get(reverse("helpdesk:submit"))
        detail_response = self.client.get(
            reverse("helpdesk:view", kwargs={"ticket_id": ticket.pk})
        )

        self.assertEqual(create_response.status_code, 200)
        self.assertTemplateUsed(create_response, "helpdesk/create_ticket.html")
        self.assertContains(create_response, "Submit a Ticket")
        self.assertContains(create_response, 'name="title"')
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, ticket.title)
        self.assertContains(detail_response, ticket.description)

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
        self.assertEqual(response.headers["Cache-Control"], "private, no-store")
        self.assertEqual(response.headers["Referrer-Policy"], "no-referrer")

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

    def test_email_change_cannot_expose_ticket_secrets_through_package_api(self):
        user = User.objects.create_user(
            username="api-attacker",
            password="test-pass-123",
        )
        ticket = Ticket.objects.create(
            title="Private API ticket",
            queue=self.queue,
            submitter_email="victim@example.com",
            description="Must remain private",
            priority=3,
            status=Ticket.OPEN_STATUS,
        )
        self.client.force_login(user)
        self.client.post(
            reverse("settings:profile"),
            {"first_name": "", "last_name": "", "email": ticket.submitter_email},
        )

        response = self.client.get("/help/api/user_tickets/")

        self.assertEqual(response.status_code, 404)
        with self.assertRaises(NoReverseMatch):
            reverse("helpdesk:my-tickets")

    def test_staff_api_remains_available_without_the_customer_ticket_listing(self):
        staff_user = User.objects.create_user(
            username="api-support-agent",
            password="test-pass-123",
            is_staff=True,
        )
        ticket = Ticket.objects.create(
            title="Staff API ticket",
            queue=self.queue,
            submitter_email="buyer@example.com",
            description="Visible through the restricted staff API",
            priority="3",
            status=Ticket.OPEN_STATUS,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("helpdesk:ticket-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ticket.title)
        self.assertContains(response, ticket.description)

    def test_iframe_submission_requires_csrf_and_still_works_with_a_token(self):
        client = Client(enforce_csrf_checks=True)
        iframe_url = reverse("helpdesk:submit_iframe")
        submission = {
            "queue": str(self.queue.pk),
            "title": "CSRF-protected iframe ticket",
            "body": "The iframe must use a same-origin CSRF token.",
            "submitter_email": "iframe@example.com",
            "priority": "3",
        }

        response = client.post(iframe_url, submission)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Ticket.objects.filter(title=submission["title"]).exists())

        client.get(iframe_url)
        submission["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
        response = client.post(iframe_url, submission)

        self.assertRedirects(response, reverse("helpdesk:success_iframe"))
        self.assertTrue(Ticket.objects.filter(title=submission["title"]).exists())

    @override_settings(HELPDESK_PUBLIC_SUBMISSION_RATE_LIMIT=1)
    def test_public_submission_routes_share_a_rate_limit(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("helpdesk:home"))
        csrf_token = client.cookies["csrftoken"].value
        submission = {
            "csrfmiddlewaretoken": csrf_token,
            "queue": str(self.queue.pk),
            "title": "First rate-limited ticket",
            "body": "The first request is allowed.",
            "submitter_email": "rate-limit@example.com",
            "priority": "3",
        }

        first_response = client.post(reverse("helpdesk:submit"), submission)
        submission["title"] = "Homepage rate-limit bypass"
        home_response = client.post(reverse("helpdesk:home"), submission)
        submission["title"] = "Iframe rate-limit bypass"
        iframe_response = client.post(reverse("helpdesk:submit_iframe"), submission)

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(home_response.status_code, 429)
        self.assertEqual(home_response.headers["Retry-After"], "60")
        self.assertEqual(iframe_response.status_code, 429)
        self.assertEqual(iframe_response.headers["Retry-After"], "60")
        self.assertEqual(Ticket.objects.count(), 1)

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
        self.assertEqual(response.status_code, 405)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.RESOLVED_STATUS)

        client = Client(enforce_csrf_checks=True)
        query = urlencode(
            {
                "ticket": ticket.ticket_for_url,
                "email": ticket.submitter_email,
                "key": ticket.secret_key,
            }
        )
        public_url = f"{reverse('helpdesk:public_view')}?{query}"
        response = client.post(public_url, {"action": "close"})
        self.assertEqual(response.status_code, 403)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.RESOLVED_STATUS)

        client.get(public_url)
        csrf_token = client.cookies["csrftoken"].value
        response = client.post(
            public_url,
            {"action": "unsupported", "csrfmiddlewaretoken": csrf_token},
        )
        self.assertEqual(response.status_code, 400)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.RESOLVED_STATUS)

        response = client.post(
            public_url,
            {
                "action": "close",
                "csrfmiddlewaretoken": csrf_token,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Cache-Control"], "private, no-store")
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.CLOSED_STATUS)


class PlatformIntegrationTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_superuser(
            username="platform-admin",
            email="",
            password="test-pass-123",
        )

    def test_flat_page_is_public_and_included_in_the_sitemap(self):
        flat_page = FlatPage.objects.create(
            url="/terms/",
            title="Terms of service",
            content="CreativeBatch terms content",
        )
        flat_page.sites.add(Site.objects.get_current())

        page_response = self.client.get(flat_page.url)
        sitemap_response = self.client.get(reverse("sitemap"))

        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, flat_page.title)
        self.assertContains(page_response, flat_page.content)
        self.assertEqual(sitemap_response.status_code, 200)
        self.assertContains(sitemap_response, flat_page.url)

    def test_site_domain_is_configured_from_settings_after_migration(self):
        site = Site.objects.get_current()

        self.assertEqual(site.domain, settings.SITE_DOMAIN)
        self.assertEqual(site.name, settings.SITE_NAME)

    def test_admin_requires_a_staff_account(self):
        admin_url = reverse("admin:index")

        anonymous_response = self.client.get(admin_url)
        self.assertEqual(anonymous_response.status_code, 302)

        customer = User.objects.create_user(
            username="non-staff-customer",
            password="test-pass-123",
        )
        self.client.force_login(customer)
        customer_response = self.client.get(admin_url)
        self.assertEqual(customer_response.status_code, 302)

        self.client.force_login(self.staff_user)
        staff_response = self.client.get(admin_url)
        self.assertEqual(staff_response.status_code, 200)
        self.assertContains(staff_response, "Product administration")

    @override_settings(
        MAINTENANCE_MODE=True,
        MAINTENANCE_MODE_IGNORE_TESTS=False,
    )
    def test_maintenance_mode_returns_custom_503_and_retry_header(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["Retry-After"], "900")
        self.assertContains(response, "We’ll be right back.", status_code=503)

    @override_settings(
        MAINTENANCE_MODE=True,
        MAINTENANCE_MODE_IGNORE_TESTS=False,
    )
    def test_superuser_and_admin_login_bypass_maintenance_mode(self):
        admin_url = reverse("admin:index")
        anonymous_admin_response = self.client.get(admin_url)
        self.assertNotEqual(anonymous_admin_response.status_code, 503)

        self.client.force_login(self.staff_user)
        landing_response = self.client.get("/")

        self.assertEqual(landing_response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_debug_toolbar_is_available_to_loopback_requests(self):
        from debug_toolbar.middleware import show_toolbar

        request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1")

        self.assertTrue(show_toolbar(request))


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
                "DEFAULT_FROM_EMAIL": "support@example.com",
                "SITE_DOMAIN": "example.com",
                "REDIS_URL": "redis://redis:6379",
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

    def test_unknown_environment_is_rejected(self):
        env = self.production_env()
        env["DJANGO_ENV"] = "staging"

        result = self.run_settings_import(env, "import product.settings")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported DJANGO_ENV", result.stderr)

    def test_production_requires_deployment_identity_and_redis_settings(self):
        for name in ("ALLOWED_HOSTS", "DEFAULT_FROM_EMAIL", "SITE_DOMAIN", "REDIS_URL"):
            with self.subTest(name=name):
                env = self.production_env()
                env.pop(name)

                result = self.run_settings_import(env, "import product.settings")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"{name} environment variable is required", result.stderr)

    def test_production_rejects_short_secret_key(self):
        env = self.production_env()
        env["SECRET_KEY"] = "too-short"

        result = self.run_settings_import(env, "import product.settings")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY must contain at least 50 characters", result.stderr)

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
            "assert s.ALLOWED_HOSTS == ['example.com']; "
            "assert s.DEFAULT_FROM_EMAIL == 'support@example.com'; "
            "assert s.SITE_DOMAIN == 'example.com'; "
            "assert s.HELPDESK_VIEW_A_TICKET_PUBLIC is False; "
            "assert s.HELPDESK_USE_HTTPS_IN_EMAIL_LINK is True; "
            "assert s.CACHES['default']['LOCATION'] == 'redis://redis:6379/0'; "
            "assert s.CACHES['maintenance_mode']['LOCATION'] == 'redis://redis:6379/1'; "
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

    def test_entrypoint_is_fail_fast_and_non_interactive(self):
        entrypoint = self.project_root / "entrypoint.sh"
        contents = entrypoint.read_text()

        self.assertTrue(os.access(entrypoint, os.X_OK))
        self.assertTrue(contents.startswith("#!/bin/sh\nset -eu\n"))
        self.assertIn("DJANGO_ENV=${DJANGO_ENV:-production}", contents)
        self.assertIn("check --deploy", contents)
        self.assertIn("collectstatic --noinput", contents)
        self.assertIn("migrate --noinput", contents)
        self.assertNotIn("makemessages", contents)
        self.assertNotIn("createcachetable", contents)
