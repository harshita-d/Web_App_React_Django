"""
Tests for Django admin modification
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Tests for Django admin"""

    def setUp(self):
        """Create User and Client"""
        # through Client class we can perform HTTP request
        # in a testing environment without needing a browser or server.
        self.client = Client()

        user = get_user_model()

        # creating a superuser
        self.admin_user = user.objects.create_superuser(
            email="admin@example.com", password="pass123"
        )

        # create user
        self.user = user.objects.create_user(
            email="user@example.com", password="pass123", name="Test User"
        )

    def test_admin_page_access(self):
        """testing accessing admin page"""

        # Login into admin as superuser
        self.client.force_login(self.admin_user)

        # Access Admin Page
        response = self.client.get("/admin/")

        # checking the status
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        """test that users are listed on that page"""

        # to access changelist of user {app_label}_{model_name}_{changelist}
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
