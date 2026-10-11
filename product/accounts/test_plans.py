from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from plans.models import Plan, UserPlan


class PlanIntegrationTests(TestCase):
    def test_new_users_receive_default_plan_and_pricing_renders(self):
        plan = Plan.objects.create(name="Starter", default=True, available=True)
        user = get_user_model().objects.create_user("plan-user")
        self.assertEqual(UserPlan.objects.get(user=user).plan, plan)
        self.assertContains(self.client.get(reverse("pricing")), "Starter")
        self.assertEqual(self.client.get(reverse("current_plan")).status_code, 302)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("current_plan")).status_code, 200)
