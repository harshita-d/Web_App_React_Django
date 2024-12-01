"""
tests for models.
"""

from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal


def create_user(email="user@example.com", password="testpass123"):
    """create and return new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """test creating a user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """test email is normalizer for new user"""
        sample_email = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_email:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """test creating a superuser"""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_recipe_details_save(self):
        """Test if the recipe details are saved."""
        user = get_user_model().objects.create_user("test@example.com", "testpass")

        res = models.CreateRecipe.objects.create(
            user=user,
            title="test recipe",
            time_minutes=5,
            price=Decimal("5.50"),
            description="simple recipe",
        )

        self.assertEqual(str(res), res.title)

    def test_create_tag(self):
        """test the creation of tags for a user"""

        user = create_user()
        tags = models.Tag.objects.create(user=user, name="tags")

        self.assertEqual(tags.name, str(tags))

    def test_create_ingredients(self):
        """test creating ingredients"""

        user = create_user()
        ing = models.Ingredient.objects.create(
            user=user,
            name="Ingredients1",
        )

        self.assertEqual(str(ing), ing.name)

    @patch("core.models.uuid.uuid4")
    # This decorator replaces the uuid4() function (normally from the uuid module)
    # with a mocked version for the duration of the test.
    # Instead of generating a random UUID, the mock returns a predefined value ('test-uuid').
    def test_recipe_file_name_uuid(self, mock_uuid):
        """test generating image path"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        # sets the mocked uuid4() function to return the string 'test-uuid'.

        file_path = models.recipe_image_file_path(None, "example.jpg")
        # Calls the function recipe_image_file_path (presumably defined in the core.models module)

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
