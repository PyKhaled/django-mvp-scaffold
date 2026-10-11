from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(AUTHENTICATION_RATE_LIMIT="2/m")
class AuthenticationRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_login_and_reset_limit_posts_but_allow_gets(self):
        for name in ("login", "password_reset"):
            cache.clear()
            for _ in range(2):
                self.assertEqual(self.client.post(reverse(name), {}).status_code, 200)
            response = self.client.post(reverse(name), {})
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response["Retry-After"], "60")
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
            self.assertEqual(self.client.post(reverse(name), {}, REMOTE_ADDR="192.0.2.2").status_code, 200)
