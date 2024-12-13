# Recipe

## Model

- `ForiegnKey`: it links each recipe to a user, referencing the user model defined. WHen a user is deleted, all their recipes will also be deleted as well vie `models.CASCADE`.

- `__str__`: this method ensures that the string representation of the recipe instance returns its title.

## Serializer

- `RecipeSerializer` defines the fields of the `CreateRecipe` model that should be included in the serialized data.
- `RecipeDetailSerializer` extends `RecipeSerializer` and adds description field to the serialized data. This Serializer is used when showing detailed information about the recipe
- `TagSerializer` defines the fields og the `Tag` model.
- Many-to-many relationships are handled dynamically using methods like `recipe.tags.add()` and `instance.tags.clear()`.
- `Tags` is `ManyToManyField`. To handle this relationship django provides methods like
  - `add()`: add one or more related objects to the relationship
  - `remove()`: Remove one or more related objects from relationships
  - `clear()` : remove all related objects from the relationships
- Since the `tag` field in the `CreateRecipe` model is ManytoMany, this means it expects a list if `Tag model instances`, not raw data or dictionary.
- with `create_or_get` method if the tag with the given name and email already exist it retrieves it otherwise create a new `Tag model instance`. these instance are than added to the recipe tags using add()
- `setattr` does not support these operations. it expects a fully processed data that matches the field type.

- `serializers.ModelSerializer` directly links to the Recipe/Tag/Ingredient model in model, ensuring that the fields (id and name) are properly serialized. The serializer automatically includes all fields you specify in fields
- `serializers.Serializer` is a general-purpose serializer. It doesn’t automatically connect to any model. Although you specify `fields = ["id", "name"]` in the Meta class, serializers.Serializer does not process the `Meta` class. It simply ignores it.

  - To use `serializers.Serializer`, you would need to manually define each field and how it should behave:

  ```
  class IngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
  ```

- Custom Action Requires Manual Serializer Initialization just like image.
  - The upload_image method is a custom action defined with the @action decorator.
  - DRF does not automatically initialize a serializer for custom actions like it does for standard actions (list, retrieve, etc.).
  - In upload_image, we need to pass both the recipe instance and request.data to the serializer. This manual initialization is achieved via self.get_serializer().
- The `get_object()` method fetches the specific recipe instance from the database based on the id provided in the URL.

## views

- Views are class based views. It extends `ModelViewSet` class in DRF.

- `serializer_class` specifies the default serializer to use.

- `queryset` defines the set of `CreateRecipe` objects that the view will operate on. Here by default its fetching all objects from DB

- `authentication_class` specifies that the `TokenAuthentication` is used for authentication. it means user must send a valid token in request headers to access the api.

- `permission_class` specifies that the user must be authenticated to access the api and is done by `IsAuthenticated`.

- `get_queryset` method customize the queryset to only return recipes for the authenticated user.

- `get_serializer_class` this method allows dynamic selection of serializer class based on action. various actions are `list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`.

- `perform_create` overrides the default `perform_create` method to associate the authenticated user with newly created recipe. By default, the `save()` method only processes validated data from the request. adding the user ensures the recipe is linked to the logged in user.

| **HTTP Method**            | **Function/Action**    | **Flow**                                                                                             |
| -------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------- |
| **GET (list)**             | `get_queryset`         | - Filters the queryset to include only the recipes for the authenticated user (`self.request.user`). |
|                            | `get_serializer_class` | - Returns `RecipeSerializer` because the action is `"list"`.                                         |
|                            | `list`                 | - Handles retrieving a list of recipes.                                                              |
| **GET (retrieve)**         | `get_queryset`         | - Filters the queryset to include only the recipes for the authenticated user.                       |
|                            | `get_serializer_class` | - Returns `RecipeDetailSerializer` (the default serializer for this action).                         |
|                            | `retrieve`             | - Handles retrieving the details of a single recipe based on its ID.                                 |
| **POST (create)**          | `get_serializer_class` | - Returns `RecipeDetailSerializer` (default serializer for creation).                                |
|                            | `perform_create`       | - Creates a new `CreateRecipe` object and assigns the authenticated user (`self.request.user`).      |
|                            | `create`               | - Handles creating a new recipe and triggering `perform_create`.                                     |
| **PUT (update)**           | `get_queryset`         | - Filters the queryset to include only the recipes for the authenticated user.                       |
|                            | `get_serializer_class` | - Returns `RecipeDetailSerializer` (default serializer for update).                                  |
|                            | `update`               | - Handles updating a recipe (replaces the existing resource with a new one).                         |
| **PATCH (partial update)** | `get_queryset`         | - Filters the queryset to include only the recipes for the authenticated user.                       |
|                            | `get_serializer_class` | - Returns `RecipeDetailSerializer` (default serializer for partial updates).                         |
|                            | `partial_update`       | - Handles partially updating a recipe (only updated fields are replaced).                            |
| **DELETE (destroy)**       | `get_queryset`         | - Filters the queryset to include only the recipes for the authenticated user.                       |
|                            | `get_serializer_class` | - Returns `RecipeDetailSerializer` (same serializer for destroy action).                             |
|                            | `destroy`              | - Handles deleting a recipe from the database.                                                       |

---

- `TagViewSet`:
- Instead of manually combining multiple mixins (`ListModelMixin`, `CreateModelMixin`, `RetrieveModelMixin`, `UpdateModelMixin`, `DestroyModelMixin`), ModelViewSet bundles all these mixins into one convenient class.

  | **Use Case**                     | **Recommended Approach**           | **Reason**                                                                          |
  | -------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------- |
  | Single action (e.g., listing)    | `GenericViewSet` + Relevant Mixins | Lightweight and avoids unnecessary functionality.                                   |
  | Full CRUD functionality required | `ModelViewSet`                     | Simplifies implementation, reduces boilerplate, and provides all necessary actions. |

- `@extend_schema_view`: This decorator is used to override or extend the default schema for specific actions (e.g., list, retrieve, create) of a DRF view.

- `list=extend_schema`
  The list keyword refers to the list action of the view. This is used for GET requests to fetch multiple items

- `OpenApiParameter`
  Represents a query parameter for the API documentation.

- `enum=[0, 1]:`
  Restricts the allowed values to 0 (false) or 1 (true).

```
tags: Type: OpenApiTypes.STR (string)
      Description: A comma-separated list of tag IDs to filter the results.
ingredients:Type: OpenApiTypes.STR (string)
      Description: A comma-separated list of ingredient IDs to filter the results.
```

## URLS

- `DefaultRouter` is special class provided by DRF that automatically creates routes for CURD operations for the viewset you register with. with this we do not have to manually define paths for these operations.With default router `recipe` will be the base URL prefix for this viewset.

  - if we choose not to use default router than we need to specify all the routes path starting with `/recipe/` like `/recipe/` and `/recipe/<int:pk>` in path.

- `router.register()` this registers the viewset and assign a base name for the URL.

`basename='recipe'` argument is used to define a common base name for all the URLs generated by the router for the RecipeViewSet

`basename='tag'` argument is used to define a common base name for all the URLs generated by the router for the TagViewSet
