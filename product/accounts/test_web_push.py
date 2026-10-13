import base64
import json
from io import StringIO
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from pywebpush import WebPushException

from product.accounts.models import NotificationPreference, NotificationPush, WebPushSubscription
from product.accounts.notification_service import emit


def browser_subscription():
    return {'endpoint': 'https://fcm.googleapis.com/push/example', 'keys': {
        'p256dh': base64.urlsafe_b64encode(b'\x04' + b'a' * 64).decode().rstrip('='),
        'auth': base64.urlsafe_b64encode(b'b' * 16).decode().rstrip('='),
    }}


@override_settings(WEB_PUSH_PUBLIC_KEY='public', WEB_PUSH_PRIVATE_KEY='private', WEB_PUSH_SUBJECT='mailto:ops@example.com')
class WebPushTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='push-user')
        self.actor = get_user_model().objects.create_user(username='push-actor')
        self.client.force_login(self.user)

    def subscribe(self, data=None):
        return self.client.post(reverse('push_subscription'), json.dumps(data or browser_subscription()), content_type='application/json')

    def test_subscription_requires_authentication_and_csrf(self):
        self.assertEqual(Client().post(reverse('push_subscription')).status_code, 302)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse('push_subscription')).status_code, 403)

    def test_subscription_validation_and_owner_scoped_removal(self):
        self.assertEqual(self.subscribe().status_code, 200)
        for endpoint in ['http://fcm.googleapis.com/x', 'https://127.0.0.1/x', 'https://fcm.googleapis.com.evil.test/x', 'https://fcm.googleapis.com:8443/x']:
            self.assertEqual(self.subscribe({**browser_subscription(), 'endpoint': endpoint}).status_code, 400)
        self.assertEqual(self.subscribe({'endpoint': browser_subscription()['endpoint'], 'keys': {}}).status_code, 400)
        self.client.force_login(self.actor)
        self.subscribe({'remove': True, 'endpoint': browser_subscription()['endpoint']})
        self.assertEqual(WebPushSubscription.objects.count(), 1)
        self.client.force_login(self.user)
        self.subscribe({'remove': True, 'endpoint': browser_subscription()['endpoint']})
        self.assertFalse(WebPushSubscription.objects.exists())

    @override_settings(WEB_PUSH_PRIVATE_KEY='')
    def test_missing_credentials_disable_subscription(self):
        self.assertEqual(self.subscribe().status_code, 503)
        self.assertEqual(self.client.get(reverse('push_config')).json(), {'public_key': ''})

    def test_push_is_opt_in_independent_of_in_app(self):
        emit(recipient=self.user, actor=self.actor, kind='account', verb='Changed')
        self.assertFalse(NotificationPush.objects.exists())
        NotificationPreference.objects.filter(user=self.user).update(web_push=True, in_app=False)
        emit(recipient=self.user, actor=self.actor, kind='account', verb='Changed')
        self.assertEqual(NotificationPush.objects.count(), 1)

    @patch('product.accounts.management.commands.send_notification_pushes.webpush')
    def test_delivery_and_opt_out(self, send):
        self.subscribe()
        NotificationPreference.objects.create(user=self.user, kind='account', web_push=True)
        row = NotificationPush.objects.create(user=self.user, kind='account')
        call_command('send_notification_pushes', stdout=StringIO())
        self.assertEqual(send.call_count, 1)
        payload = json.loads(send.call_args.kwargs['data'])
        self.assertEqual(payload['url'], '/notifications/')
        self.assertNotIn(self.user.username, payload['body'])
        row.refresh_from_db()
        self.assertIsNotNone(row.sent_at)
        NotificationPreference.objects.filter(user=self.user).update(web_push=False)
        row = NotificationPush.objects.create(user=self.user, kind='account')
        call_command('send_notification_pushes', stdout=StringIO())
        row.refresh_from_db()
        self.assertIsNotNone(row.cancelled_at)
        self.assertEqual(send.call_count, 1)

    @patch('product.accounts.management.commands.send_notification_pushes.webpush')
    def test_expired_subscriptions_removed_and_transient_errors_retry(self, send):
        self.subscribe()
        NotificationPreference.objects.create(user=self.user, kind='account', web_push=True)
        row = NotificationPush.objects.create(user=self.user, kind='account')
        send.side_effect = WebPushException('temporary', response=Mock(status_code=503))
        call_command('send_notification_pushes', stdout=StringIO())
        row.refresh_from_db()
        self.assertIsNone(row.sent_at)
        self.assertTrue(WebPushSubscription.objects.exists())
        send.side_effect = WebPushException('expired', response=Mock(status_code=410))
        call_command('send_notification_pushes', stdout=StringIO())
        self.assertFalse(WebPushSubscription.objects.exists())

    def test_worker_and_preferences_render(self):
        self.assertContains(self.client.get(reverse('settings:notifications')), 'Enable this browser')
        response = self.client.get(reverse('push_worker'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/javascript')
