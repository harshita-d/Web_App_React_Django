"""View for Recipe API"""

from rest_framework import viewsets, mixins
from recipe import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import CreateRecipe, Tag, Ingredient


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = CreateRecipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for particular request"""

        if self.action == "list":
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewset(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """base class viewset for recipe attributes"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-name")


class TagViewSet(BaseRecipeAttrViewset):
    """View to return tags"""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(BaseRecipeAttrViewset):
    """View for Ingredients"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
