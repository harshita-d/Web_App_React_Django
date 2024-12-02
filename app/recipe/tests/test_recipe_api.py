"""Test Recipe API"""

from decimal import Decimal
import tempfile
import os
from PIL import Image
from core.models import CreateRecipe, Tag, Ingredient
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


def image_upload_url(recipe_id):
    """Create and return an image upload URL"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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
        self.client.patch(url, payload)

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

    def test_create_recipe_with_new_tags(self):
        """test create recipe with new tags"""

        payload = {
            "title": "New recipe",
            "time_minutes": 5,
            "price": Decimal("3.22"),
            "description": "Changed the payload",
            "link": "http://sample.com",
            "tags": [{"name": "Breakfast"}, {"name": "Dinner"}],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = CreateRecipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipes[0].tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipes[0].tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_for_existing_tags(self):
        """test Create recipes with existing tags"""

        tag = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "New recipe",
            "time_minutes": 5,
            "price": Decimal("3.22"),
            "description": "Changed the payload",
            "link": "http://sample.com",
            "tags": [{"name": "Indian"}, {"name": "Dinner"}],
        }
        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = CreateRecipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        self.assertEqual(recipe[0].tags.count(), 2)
        self.assertIn(tag, recipe[0].tags.all())
        for tag in payload["tags"]:
            exists = recipe[0].tags.filter(name=tag["name"], user=self.user).exists()

        self.assertTrue(exists)

    def test_create_tag_on_recipe_update(self):
        """test creation of tag on recipe update"""

        recipe = create_recipe(user=self.user)

        payload = {"tags": [{"name": "Dinner"}]}
        url = details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tags = Tag.objects.get(user=self.user, name="Dinner")
        self.assertIn(new_tags, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """test to update recipe already have a tag"""

        tag_dinner = Tag.objects.create(user=self.user, name="Dinner")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_dinner)

        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {"tags": [{"name": "Lunch"}]}
        url = details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_dinner, recipe.tags.all())

    def test_clear_recipe_tag(self):
        """test clear recipe tag"""
        tag = Tag.objects.create(user=self.user, name="Dinner")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {"tags": []}
        url = details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_ingredient(self):
        """testing creation of ingredients through recipe"""

        payload = {
            "title": "New recipe",
            "time_minutes": 5,
            "price": Decimal("3.22"),
            "description": "Changed the payload",
            "link": "http://sample.com",
            "ingredients": [{"name": "Pepper"}],
        }

        ingredient = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(ingredient.status_code, status.HTTP_201_CREATED)
        res = CreateRecipe.objects.filter(user=self.user)
        self.assertEqual(res.count(), 1)
        recipe = res[0]
        self.assertEqual(recipe.ingredients.count(), 1)
        for value in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                user=self.user, name=value["name"]
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """test create recipe with existing ingredient"""

        ingredients = Ingredient.objects.create(user=self.user, name="Pepper")
        payload = {
            "title": "New recipe",
            "time_minutes": 5,
            "price": Decimal("3.22"),
            "description": "Changed the payload",
            "link": "http://sample.com",
            "ingredients": [{"name": "Pepper"}],
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = CreateRecipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertIn(ingredients, recipe.ingredients.all())
        for value in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                user=self.user, name=value["name"]
            ).exists()
            self.assertTrue(exists)

    def test_update_ingredients_recipe(self):
        """test updating a ingredients in recipe"""

        recipe = create_recipe(user=self.user)

        payload = {"ingredients": [{"name": "Pepper"}]}

        url = details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient = Ingredient.objects.get(user=self.user, name="Pepper")
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_update_recipe_assigned_ingredients(self):
        """assign a new ingredient to a recipe with existing ingredient value"""

        ingredient1 = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        payload = {"ingredients": [{"name": "Chili"}]}
        url = details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient2 = Ingredient.objects.get(user=self.user, name="Chili")
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """test clearing the recipe ingredients"""

        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {"ingredients": []}
        url = details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """test filtering recipes by tags"""
        r1 = create_recipe(user=self.user, title="test1")
        r2 = create_recipe(user=self.user, title="test2")
        tag1 = Tag.objects.create(user=self.user, name="Pepper")
        tag2 = Tag.objects.create(user=self.user, name="Salt")
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title="test3")

        params = {"tags": f"{tag1.id}, {tag2.id}"}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        """test filtering recipes by ingredients"""
        r1 = create_recipe(user=self.user, title="test1")
        r2 = create_recipe(user=self.user, title="test2")
        ing1 = Ingredient.objects.create(user=self.user, name="Pepper")
        ing2 = Ingredient.objects.create(user=self.user, name="Salt")
        r1.ingredients.add(ing1)
        r2.ingredients.add(ing2)
        r3 = create_recipe(user=self.user, title="test3")

        params = {"ingredients": f"{ing1.id}, {ing2.id}"}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com", password="testpass")
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe"""

        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            """
            The tempfile module is part of Python’s standard library.
            Creates a temporary file that exists only within the scope of
            the with block. Using tempfile.NamedTemporaryFile is ideal for testing
            scenarios like file uploads because:
            It avoids creating permanent files that you must manually delete.
            """
            img = Image.new("RGB", (10, 10))
            # creates a 10x10 pixel blank image in RGB format using pillow library

            img.save(image_file, format="JPEG")
            # saves the created image to a temporary file in JPEG format

            image_file.seek(0)
            # resets the file pointer to the beginning so that
            # file can be read during the upload.
            """
            When you write data to a file, the file pointer moves
            to the end of the written data. For example:
            After calling img.save(image_file, format='JPEG'),
            the file pointer is positioned at the end of the file.
            If you try to read the file or pass it to an upload function,
            it might behave incorrectly or return no data because the
            pointer is not at the start.
            """

            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")
            # multipart ensures the request is encoded as a multipart form data,
            # which is required for file uploads

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
        # Checks that the image file physically exists on the server at the
        # expected path (self.recipe.image.path).

    def test_upload_image_bad_request(self):
        """test if the image upload fails"""
        url = image_upload_url(self.recipe.id)
        payload = {"image": "string"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
