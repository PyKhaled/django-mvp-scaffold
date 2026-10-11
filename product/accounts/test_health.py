from unittest.mock import patch

from django.test import TransactionTestCase
from django.urls import reverse
from health_check.exceptions import ServiceUnavailable


class HealthCheckTests(TransactionTestCase):
    def test_database_and_cache_are_healthy(self):
        response = self.client.get(reverse("health_check"), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(set(response.json().values()), {"OK"})
        self.assertIn("no-cache", response["Cache-Control"])

    def test_failed_dependency_returns_server_error(self):
        with patch("health_check.checks.Cache.run", side_effect=ServiceUnavailable("offline")):
            response = self.client.get(reverse("health_check"), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 500)
