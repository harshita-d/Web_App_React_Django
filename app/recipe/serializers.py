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

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context["request"].user
        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_object)

    def create(self, validated_data):
        """create recipe with tags"""
        tags = validated_data.pop("tags", [])
        recipe = CreateRecipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """update the recipe with tags"""

        tags = validated_data.pop("tags", None)

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
        fields = RecipeSerializer.Meta.fields + ["description"]
