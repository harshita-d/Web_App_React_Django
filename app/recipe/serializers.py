"""
Serializers for Recipe API
"""

from rest_framework import serializers
from core.models import CreateRecipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe API"""

    class Meta:
        model = CreateRecipe
        fields = ["id", "title", "time_minutes", "price", "link"]
        read_only_fields = ["id"]


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only = ["id"]
