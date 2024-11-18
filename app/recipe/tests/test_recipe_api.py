"""Test Recipe API"""

from decimal import Decimal
from core.models import CreateRecipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def details_url(recipe_id):
    """create and return recipe detail url"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """Create and Return a sample Recipe"""

    defaults = {
        "title": "Sample Recipe Title",
        "time_minutes": 22,
        "price": Decimal("5.54"),
        "description": "Sample Description",
        "link": "http://example.com",
    }

    defaults.update(params)

    recipe = CreateRecipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com", password="testpass")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test to retrieve recipe"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = CreateRecipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""

        other_user = create_user(email="otheruser@example.com", password="testpass1")

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)  # calling api from authenticated user

        recipe = CreateRecipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """test  get recipe detail"""

        recipe = create_recipe(user=self.user)

        url = details_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """test to create a recipe"""
        payload = {
            "title": "Sample Recipe",
            "time_minutes": 30,
            "price": Decimal("5.54"),
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = CreateRecipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Testing the partial update"""
        original_link = "http://test@example.com/test.pdf"
        defaults = create_recipe(
            user=self.user,
            title="Sample Recipe",
            link=original_link,
        )

        url = details_url(defaults.id)
        payload = {"title": "New title"}
        recipe = self.client.patch(url, payload)

        self.assertEqual(recipe.status_code, status.HTTP_200_OK)
        defaults.refresh_from_db()
        self.assertEqual(defaults.title, payload["title"])
        self.assertEqual(defaults.user, self.user)
        self.assertEqual(defaults.link, original_link)

    def test_full_update(self):
        """Test full update of recipe"""

        default = create_recipe(
            user=self.user,
            title="Sample recipe",
            time_minutes=3,
            price=Decimal("2.22"),
        )

        payload = {
            "title": "New recipe",
            "time_minutes": 5,
            "price": Decimal("3.22"),
            "description": "Changed the payload",
            "link": "http://sample.com",
        }

        url = details_url(default.id)
        recipe = self.client.put(url, payload)

        self.assertEqual(recipe.status_code, status.HTTP_200_OK)
        default.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(default, k), v)
        self.assertEqual(default.user, self.user)

    def test_update_user_return_error(self):
        """Test the updating user while updating recipe will throw an error"""
        default = create_recipe(user=self.user)
        new_user = create_user(email="new@exqample.com", password="newpass123")

        url = details_url(default.id)
        payload = {"user": new_user.id}
        recipe = self.client.patch(url, payload)

        default.refresh_from_db()
        self.assertEqual(default.user, self.user)

    def test_delete_recipe(self):
        """test the delete recipe"""
        default = create_recipe(user=self.user)
        url = details_url(default.id)
        recipe = self.client.delete(url)

        self.assertEqual(recipe.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CreateRecipe.objects.filter(id=default.id).exists())

    def test_delete_other_user_recipe_error(self):
        """test to delete other user recipe error"""
        new_user = create_user(email="new@example.com", password="testpass123")
        recipe = create_recipe(user=new_user)
        url = details_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(CreateRecipe.objects.filter(id=recipe.id).exists())
