from django.urls import path, include
from recipe import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("recipes", views.RecipeViewSet, basename="recipe")
router.register("tags", views.TagViewSet, basename="tag")
router.register("ingredients", views.IngredientsViewSet, basename="ingredient")
app_name = "recipe"

urlpatterns = [path("", include(router.urls))]
