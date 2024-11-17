# Recipe

## Model

- `ForiegnKey`: it links each recipe to a user, referencing the user model defined. WHen a user is deleted, all their recipes will also be deleted as well vie `models.CASCADE`.

- `__str__`: this method ensures that the string representation of the recipe instance returns its title.

## Serializer

- `RecipeSerializer` defines the fields of the `CreateRecipe` model that should be included in the serialized data.
- `RecipeDetailSerializer` extends `RecipeSerializer` and adds description field to the serialized data. This Serializer is used when showing detailed information about the recipe

## views

-
