# Recipe

## Model

- `ForiegnKey`: it links each recipe to a user, referencing the user model defined. WHen a user is deleted, all their recipes will also be deleted as well vie `models.CASCADE`.

- `__str__`: this method ensures that the string representation of the recipe instance returns its title.

## Serializer

- `RecipeSerializer` defines the fields of the `CreateRecipe` model that should be included in the serialized data.
- `RecipeDetailSerializer` extends `RecipeSerializer` and adds description field to the serialized data. This Serializer is used when showing detailed information about the recipe

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

## URLS

- `DefaultRouter` is special class provided by DRF that automatically creates routes for CURD operations for the viewset you register with. with this we do not have to manually define paths for these operations.With default router `recipe` will be the base URL prefix for this viewset.

  - if we choose not to use default router than we need to specify all the routes path starting with `/recipe/` like `/recipe/` and `/recipe/<int:pk>` in path.

- `router.register()` this registers the viewset and assign a base name for the URL.

`basename='recipe'` argument is used to define a common base name for all the URLs generated by the router for the RecipeViewSet
