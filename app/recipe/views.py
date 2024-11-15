"""View for Recipe API"""

from rest_framework import viewsets
from recipe import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import CreateRecipe


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API"""

    serializer_class = serializers.RecipeSerializer
    queryset = CreateRecipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")
