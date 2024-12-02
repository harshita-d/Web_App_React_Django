"""
Serializers for Recipe API
"""

from rest_framework import serializers
from core.models import CreateRecipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient Serializer"""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe API"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = CreateRecipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags", "ingredients"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context["request"].user
        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_object)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context["request"].user
        for ing in ingredients:
            ingredient_object, created = Ingredient.objects.get_or_create(
                user=auth_user, **ing
            )
            recipe.ingredients.add(ingredient_object)

    def create(self, validated_data):
        """create recipe with tags"""
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe = CreateRecipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """update the recipe with tags"""

        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attrs, value in validated_data.items():
            setattr(instance, attrs, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to recipe"""

    class Meta:
        model = CreateRecipe
        fields = ["id", "image"]
        read_only = ["id"]
        extra_kwargs = {"image": {"required": "True"}}
