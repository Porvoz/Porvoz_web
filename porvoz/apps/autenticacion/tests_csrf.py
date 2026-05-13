"""CSRF regression tests for auth password flows."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class PasswordCsrfFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="csrf_user",
            email="csrf_user@test.com",
            password="OldPass123",
        )

    def test_reset_password_post_accepts_matching_csrf_token(self):
        client = Client(enforce_csrf_checks=True)

        get_response = client.get(reverse("reset_password"))
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("csrftoken", get_response.cookies)

        csrf_token = get_response.cookies["csrftoken"].value
        post_response = client.post(
            reverse("reset_password"),
            {
                "email": "csrf_user@test.com",
                "csrfmiddlewaretoken": csrf_token,
            },
        )

        # Django PasswordResetView redirects to done page on success.
        self.assertEqual(post_response.status_code, 302)
        self.assertIn(reverse("password_reset_done"), post_response.url)

    def test_change_password_post_accepts_matching_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username="csrf_user", password="OldPass123")

        get_response = client.get(reverse("change_password"))
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("csrftoken", get_response.cookies)

        csrf_token = get_response.cookies["csrftoken"].value
        post_response = client.post(
            reverse("change_password"),
            {
                "old_password": "OldPass123",
                "new_password": "NewPass456",
                "confirm_password": "NewPass456",
                "csrfmiddlewaretoken": csrf_token,
            },
        )

        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, reverse("login"))
