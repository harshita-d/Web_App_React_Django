from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


def create_user(email="test@example.com", password="testpass"):
    """create user model"""

    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )


class PublicIngredientsAPI(TestCase):
    """testing public authentication for url"""

    def setUp(self):
        self.client = APIClient()

    def test_API_authorization(self):
        """check the api requires authentication"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class privateIngredientsAPI(TestCase):
    """test authorized api"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """testing ingredients listing api"""

        Ingredient.objects.create(user=self.user, name="Ingredients1")
        Ingredient.objects.create(user=self.user, name="Ingredients2")

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """testing that ingredients are user associated"""

        new_user = create_user(email="new@example.com")
        Ingredient.objects.create(user=new_user, name="Ingredients_new")
        user_ing = Ingredient.objects.create(user=self.user, name="Ingredient")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        print("---------", res.data)
        print("============", user_ing)
        self.assertEqual(res.data[0]["name"], user_ing.name)
        self.assertEqual(res.data[0]["id"], user_ing.id)
