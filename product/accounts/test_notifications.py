from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from helpdesk.models import FollowUp, Queue, Ticket
from notifications.signals import notify

from product.accounts.models import NotificationEmail, NotificationPreference
from product.accounts.notification_service import emit

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class NotificationWorkflowTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="customer", email="customer@example.com")
        self.staff = User.objects.create_user(
            username="agent", email="agent@example.com", is_staff=True
        )
        self.other = User.objects.create_user(username="other", email="other@example.com")
        self.queue = Queue.objects.create(title="Support", slug="support")
        self.ticket = Ticket.objects.create(
            queue=self.queue,
            title="Question",
            submitter_email=self.customer.email,
            assigned_to=self.staff,
            priority=3,
        )
        self.staff.notifications.all().delete()
        self.client.force_login(self.customer)

    def test_public_reply_notifies_customer_but_not_actor(self):
        FollowUp.objects.create(ticket=self.ticket, user=self.staff, public=True, comment="Reply")
        self.assertEqual(self.customer.notifications.count(), 1)
        self.assertEqual(self.staff.notifications.count(), 0)
        self.assertEqual(self.customer.notifications.first().data["kind"], "reply")

    def test_private_reply_never_notifies_submitter(self):
        FollowUp.objects.create(
            ticket=self.ticket, user=self.other, public=False, comment="Private"
        )
        self.assertEqual(self.customer.notifications.count(), 0)
        self.assertEqual(self.staff.notifications.count(), 1)

    def test_inbound_email_reply_does_not_notify_its_submitter(self):
        FollowUp.objects.create(
            ticket=self.ticket,
            public=True,
            comment="Email reply",
            message_id="incoming@example.com",
        )
        self.assertEqual(self.customer.notifications.count(), 0)
        self.assertEqual(self.staff.notifications.count(), 1)

    def test_self_reply_does_not_notify_customer(self):
        FollowUp.objects.create(
            ticket=self.ticket, user=self.customer, public=True, comment="My question"
        )
        self.assertEqual(self.customer.notifications.count(), 0)
        self.assertEqual(self.staff.notifications.count(), 1)

    def test_assignment_and_status_changes_generate_events(self):
        self.ticket.assigned_to = self.other
        self.other.is_staff = True
        self.other.save()
        with patch("product.accounts.notification_signals.request_actor", return_value=self.staff):
            self.ticket.save()
            self.ticket.status = Ticket.CLOSED_STATUS
            self.ticket.save()
        self.assertEqual(self.other.notifications.filter(data__kind="assignment").count(), 1)
        self.assertEqual(self.customer.notifications.filter(data__kind="status").count(), 1)

    def test_account_changes_by_other_user_are_important(self):
        with patch("product.accounts.notification_signals.request_actor", return_value=self.staff):
            self.customer.email = "updated@example.com"
            self.customer.save()
        notice = self.customer.notifications.get()
        self.assertEqual(notice.data["kind"], "account")
        self.assertEqual(notice.level, "warning")
        response = self.client.post(reverse("notification_open", args=[notice.slug]))
        self.assertRedirects(response, reverse("settings:profile"))

    def test_own_account_changes_are_suppressed(self):
        with patch(
            "product.accounts.notification_signals.request_actor", return_value=self.customer
        ):
            self.customer.first_name = "New"
            self.customer.save()
        self.assertEqual(self.customer.notifications.count(), 0)

    def test_grouping_only_combines_recent_unread_events_for_same_target(self):
        for _ in range(3):
            emit(
                recipient=self.customer,
                actor=self.staff,
                kind="reply",
                verb="New reply",
                target=self.ticket,
            )
        notice = self.customer.notifications.get()
        self.assertEqual(notice.data["count"], 3)
        notice.mark_as_read()
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="New reply",
            target=self.ticket,
        )
        self.assertEqual(self.customer.notifications.count(), 2)
        unread = self.customer.notifications.unread().get()
        unread.timestamp = timezone.now() - timedelta(hours=2)
        unread.save()
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="New reply",
            target=self.ticket,
        )
        self.assertEqual(self.customer.notifications.count(), 3)

    def test_open_is_post_only_marks_read_and_uses_secure_ticket_destination(self):
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        notice = self.customer.notifications.get()
        url = reverse("notification_open", args=[notice.slug])
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)
        self.assertIn(reverse("helpdesk:public_view"), response.url)
        self.assertIn("key=" + self.ticket.secret_key, response.url)
        notice.refresh_from_db()
        self.assertFalse(notice.unread)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.customer)
        self.assertEqual(csrf_client.post(url).status_code, 403)

    def test_staff_open_uses_staff_ticket_page(self):
        emit(
            recipient=self.staff,
            actor=self.customer,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        self.client.force_login(self.staff)
        notice = self.staff.notifications.get()
        self.assertEqual(
            self.client.post(reverse("notification_open", args=[notice.slug])).url,
            reverse("helpdesk:view", args=[self.ticket.pk]),
        )

    def test_open_rejects_other_users_notice_and_has_safe_fallback(self):
        notify.send(self.staff, recipient=self.other, verb="Other update")
        foreign = self.other.notifications.get()
        self.assertEqual(
            self.client.post(reverse("notification_open", args=[foreign.slug])).status_code, 404
        )
        notify.send(self.staff, recipient=self.customer, verb="Generic update")
        notice = self.customer.notifications.get()
        response = self.client.post(reverse("notification_open", args=[notice.slug]))
        self.assertEqual(
            response.url, reverse("notifications:all") + f"#notification-{notice.slug}"
        )

    def test_ticket_destination_does_not_expose_secret_after_email_change(self):
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        notice = self.customer.notifications.get()
        self.customer.email = "changed@example.com"
        self.customer.save()
        response = self.client.post(reverse("notification_open", args=[notice.slug]))
        self.assertNotIn("key=", response.url)

    def test_preview_is_private_and_limits_latest_ten(self):
        for index in range(12):
            notify.send(self.staff, recipient=self.customer, verb=f"Update {index}")
        notify.send(self.staff, recipient=self.other, verb="Other user secret")
        response = self.client.get(reverse("notification_preview"))
        data = response.json()
        self.assertEqual(data["unread_count"], 12)
        self.assertEqual(data["html"].count('class="notification-preview-item"'), 10)
        self.assertNotIn("Other user secret", data["html"])
        self.assertIn("no-store", response["Cache-Control"])
        self.client.logout()
        self.assertEqual(self.client.get(reverse("notification_preview")).status_code, 302)

    def test_preview_escapes_notification_content(self):
        notify.send(self.staff, recipient=self.customer, verb='<script>alert("x")</script>')
        html = self.client.get(reverse("notification_preview")).json()["html"]
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    @override_settings(DEBUG=True, INTERNAL_IPS=["127.0.0.1"])
    def test_preview_does_not_trigger_debug_toolbar_history_requests(self):
        from product.debug_toolbar_config import show_toolbar

        response = self.client.get(reverse("notification_preview"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("djdt-request-id", response.headers)
        request = RequestFactory().get(reverse("profile"))
        self.assertTrue(show_toolbar(request))
        with override_settings(DEBUG=False):
            self.assertFalse(show_toolbar(request))

    def test_preferences_are_account_scoped_and_control_delivery(self):
        data = {f"email_{kind}": "off" for kind, _ in NotificationPreference.Kind.choices}
        data["email_reply"] = "immediate"
        response = self.client.post(reverse("settings:notifications"), data)
        self.assertRedirects(response, reverse("settings:notifications"))
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Email only",
            target=self.ticket,
        )
        self.assertEqual(self.customer.notifications.count(), 0)
        self.assertEqual(NotificationEmail.objects.filter(user=self.customer).count(), 1)
        self.assertEqual(NotificationPreference.objects.filter(user=self.other).count(), 0)
        data["email_reply"] = "invalid"
        self.assertEqual(self.client.post(reverse("settings:notifications"), data).status_code, 400)

    def test_defaults_are_in_app_without_email(self):
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        self.assertEqual(self.customer.notifications.count(), 1)
        self.assertEqual(NotificationEmail.objects.count(), 0)

    def test_immediate_delivery_and_retry(self):
        NotificationPreference.objects.create(
            user=self.customer, kind="reply", email_mode="immediate"
        )
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        with (
            patch(
                "product.accounts.management.commands.send_notification_emails.send_mail",
                side_effect=OSError("offline"),
            ),
            self.assertLogs(
                "product.accounts.management.commands.send_notification_emails", level="ERROR"
            ),
        ):
            call_command("send_notification_emails")
        self.assertIsNone(NotificationEmail.objects.get().sent_at)
        call_command("send_notification_emails")
        call_command("send_notification_emails")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIsNotNone(NotificationEmail.objects.get().sent_at)

    def test_digest_groups_previous_days_updates_and_is_not_resent(self):
        NotificationPreference.objects.create(user=self.customer, kind="reply", email_mode="digest")
        for _ in range(2):
            emit(
                recipient=self.customer,
                actor=self.staff,
                kind="reply",
                verb="Reply",
                target=self.ticket,
            )
        NotificationEmail.objects.update(created_at=timezone.now() - timedelta(days=1))
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Today",
            target=self.ticket,
        )
        call_command("send_notification_emails", digest=True)
        call_command("send_notification_emails", digest=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("(2 updates)", mail.outbox[0].body)
        self.assertNotIn("Today", mail.outbox[0].body)
        self.assertEqual(NotificationEmail.objects.filter(sent_at__isnull=True).count(), 1)

    def test_email_opt_out_cancels_pending_delivery(self):
        preference = NotificationPreference.objects.create(
            user=self.customer, kind="reply", email_mode="immediate"
        )
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        preference.email_mode = "off"
        preference.save()
        call_command("send_notification_emails")
        self.assertEqual(len(mail.outbox), 0)
        queued = NotificationEmail.objects.get()
        self.assertIsNone(queued.sent_at)
        self.assertIsNotNone(queued.cancelled_at)

    def test_email_destination_is_rechecked_at_delivery(self):
        NotificationPreference.objects.create(
            user=self.customer, kind="reply", email_mode="immediate"
        )
        emit(
            recipient=self.customer,
            actor=self.staff,
            kind="reply",
            verb="Reply",
            target=self.ticket,
        )
        self.customer.email = "new@example.com"
        self.customer.save()
        call_command("send_notification_emails")
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])
        self.assertNotIn("key=", mail.outbox[0].body)

    def test_shared_email_does_not_receive_submitter_updates(self):
        self.other.email = self.customer.email
        self.other.save()
        FollowUp.objects.create(ticket=self.ticket, user=self.staff, public=True, comment="Reply")
        self.assertEqual(self.customer.notifications.count(), 0)
        self.assertEqual(self.other.notifications.count(), 0)
