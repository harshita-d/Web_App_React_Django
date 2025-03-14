"""View for Recipe API"""

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from recipe import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import CreateRecipe, Tag, Ingredient
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma separated list of tag IDs to filter ",
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma separated list of ingredients IDs to filter",
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = CreateRecipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_int(self, qs):
        """convert a list of strings to integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        if tags:
            tag_id = self._params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tag_id)
        if ingredients:
            ing_id = self._params_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ing_id)
        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """Return the serializer class for particular request"""

        if self.action == "list":
            return serializers.RecipeSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Filter by items assigned to recipes",
            )
        ]
    )
)
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
        """filter queryset to authenticated user"""
        assigned_only = bool(int(self.request.query_params.get("assigned_only", 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(createrecipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by("-name").distinct()


class TagViewSet(BaseRecipeAttrViewset):
    """View to return tags"""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(BaseRecipeAttrViewset):
    """View for Ingredients"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
