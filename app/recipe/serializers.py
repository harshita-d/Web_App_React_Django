"""
Serializers for Recipe API
"""

from rest_framework import serializers
from core.models import CreateRecipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe API"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = CreateRecipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """create recipe with tags"""
        tags = validated_data.pop("tags", [])
        recipe = CreateRecipe.objects.create(**validated_data)
        auth_user = self.context["request"].user
        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_object)
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
