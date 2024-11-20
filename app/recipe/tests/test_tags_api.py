"""Test for Tags API"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from recipe.serializers import TagSerializer
from core.models import Tag

TAG_URL = reverse("recipe:tag-list")


def create_user(email="test@example.com", password="testpass123"):
    """create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_id):
    """return detail tag url"""
    return reverse("recipe:tag-detail", args=[tag_id])


class PublicTagAPITests(TestCase):
    """test for public api"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test the api require authentication"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPI(TestCase):
    """test for private api"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_tag_list(self):
        """test the tag list success"""

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Italian")

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """test the tag is limited to user"""

        user = create_user(email="new@example.com", password="newpass")
        Tag.objects.create(user=user, name="Indian")

        tags = Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tags.name)
        self.assertEqual(res.data[0]["id"], tags.id)

    def test_update_tag(self):
        """test update and return new tag"""

        tags = Tag.objects.create(user=self.user, name="Sweet")

        payload = {"name": "Dessert"}
        url = detail_url(tags.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags.refresh_from_db()
        self.assertEqual(tags.name, payload["name"])
