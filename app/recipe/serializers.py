"""
Serializers for Recipe API
"""

from rest_framework import serializers
from core.models import CreateRecipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe API"""

    class Meta:
        model = CreateRecipe
        fields = ["id", "title", "time_minutes", "price", "link"]
        read_only_fields = ["id"]
