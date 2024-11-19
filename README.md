# Web_App_React_Django

## to build docker image

- docker build .
- docker-compose build

## running flake8

- docker compose run --rm app sh -c "flake8"

## running test

- docker-compose run --rm app sh -c "python manage.py test"

## create django project

- docker-compose run --rm app sh -c "django-admin startproject app ."

## command to create a new app

- docker-compose run --rm app sh -c "python manage.py startapp core"

## command to start django service

- docker-compose up

## to stop docker container

- docker-compose down

## test framework

- tests.py or tests/test\_[name] and only one we can use

## Migrations

- to migrate ensure app is enabled in settings.py

- command to make migrations

```
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

- to apply migrations to DB

```
docker-compose run --rm app sh -c "python manage.py migrate"
```

## Customize User Model

- create model
  - base from AbstractBaseUSer and PermissionsMixin
  - AbstractBaseUSer provides all features for authentications
  - PermissionsMixin support for Django permission system, moreover it includes fields and methods
- Create custom manager
  - used for CLI integration
  - used for managing objects
  - any custom logic can be added here like hash password
  - `BaseUserManager` is the base class for manager
- Set AUTH_USER_MODEL in setting.py
- Create and Run migrations
- create custom model before running migrations

> while doing python manage.py migrate command if we get `django.db.migrations.exceptions.InconsistentMigrationHistory` error than you find a db by the name `web_app_react_django_dev-db-data`. we need to remove this `docker volume rm web_app_react_django_dev-db-data` and if you get `volume is in use` error than `docker-compose down` and run again `docker volume rm web_app_react_django_dev-db-data`

## create superuser via CLI

- `docker-compose run --rm app sh -c "python manage.py createsuperuser"`

### Comparison: When to Use Which View?

| **Use Case**                                | **Recommended View**                           | **Explanation**                                                                                                            | **Example Scenario**                                                                                                  |
| ------------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Full control over HTTP methods**          | `APIView`                                      | Provides complete flexibility to define custom logic for each HTTP method (`GET`, `POST`, `PUT`, `DELETE`, etc.).          | A custom endpoint that performs an action like sending an email or calculating metrics, unrelated to CRUD operations. |
| **CRUD operations with minimal code**       | `ModelViewSet`                                 | Auto-generates endpoints for all CRUD operations. Simplifies implementation by bundling standard behaviors.                | A product management API allowing `list`, `retrieve`, `create`, `update`, and `delete` for a Product model.           |
| **CRUD but with custom endpoints**          | `ViewSet` + Custom Methods                     | Provides flexibility to define additional custom actions (`@action`, `@detail_route`) alongside standard CRUD operations.  | Adding an extra `send_report` action in a User API, while still allowing CRUD functionality for User records.         |
| **List or Retrieve only**                   | `ReadOnlyModelViewSet`                         | Supports only `GET` operations for listing (`list`) or retrieving (`retrieve`) data. Does not allow data modification.     | A public API showing product listings or read-only data like blog posts or static information.                        |
| **Single behavior like list or create**     | Generic Views (`ListAPIView`, `CreateAPIView`) | Streamlines implementation when only one action is required, such as listing or creating resources.                        | An API that only allows listing all blog posts (`ListAPIView`) or creating new users (`CreateAPIView`).               |
| **Custom combinations of behaviors**        | `APIView` + Mixins                             | Combines specific actions (e.g., listing and creating but not deleting) without relying on predefined `ViewSet` behaviors. | An API allowing users to list and add tasks, but not update or delete them.                                           |
| **Custom functionality without CRUD focus** | `APIView`                                      | Best for highly customized APIs that do not fit into the CRUD paradigm, where logic deviates from resource management.     | An authentication API for login/logout or a reporting API generating custom analytics.                                |

> `Generic Views`: More suited for APIs focused on one or two operations. \
> `ViewSet`: More powerful when you need both CRUD and custom actions.

- `ViewSet`: In `ViewSet` for `ModelViewSet` we do not have to manually define separate views for each type of HTTP request. Instead `ModelViewSet` automatically create the endpoints for CRUD operations.

  - it means with a single endpoint like `/recipe/` it can handle all the request. if its a `GET` request it automatically fecthes the list using the same view as of `POST`.
  - `GET`->`list()`
  - `POST`->`create()`
  - `GET` with `id`-> `retrieve()`
  - `PUT/PATCH`-> `update()` or `partial_update()`
  - `DELETE`->`destroy()`

  - default methods provides are:

    | **Method**        | **Standard Action**        | **Purpose**                          |
    | ----------------- | -------------------------- | ------------------------------------ |
    | `get_queryset`    | `list`, `retrieve`         | Define which objects are retrieved.  |
    | `perform_create`  | `create`                   | Customize the creation of an object. |
    | `perform_update`  | `update`, `partial_update` | Customize updates.                   |
    | `perform_destroy` | `destroy`                  | Customize the deletion of an object. |

- `generic` views: if we create views using generic views We have to manually define a separate views for each operations.

  - `GET`->`ListAPIView`
  - `POST`->`CreateAPIView`
  - `GET` with `id`-> `RetrieveAPIView`
  - `PUT/PATCH`->`UpdateAPIView` or `PartialUpdateAPIView`
  - `DELETE`-> `DestroyAPIView`

example:

```
urlpatterns = [
  path("recipes/", views.ListRecipeView.as_view(), name="recipe-list"),
  path("recipes/create/", views.CreateRecipeView.as_view(), name="recipe-create"),
  path("recipes/<int:pk>/", views.RecipeDetailView.as_view(), name="recipe-detail"),
  path("recipes/<int:pk>/update/", views.UpdateRecipeView.as_view(), name="recipe-update"),
  path("recipes/<int:pk>/delete/", views.DeleteRecipeView.as_view(), name="recipe-delete"),
]
```

## Django Admin

- to customize the django admin we need to create class based off `ModelAdmin` or `UserAdmin`
- we can add
  - `ordering`: changes the order the item appears
  - `list_display`: fields to appear in list
  - `fieldset`: control the layout of page
  - `readonly_fields`: fields that cannot be changed
  - `add_fieldsets`: fields displayed only in add page

## User profile endpoints

- `user/create/`
  - POST - Register a new user
- `user/token/`
  - POST-create new token
- `user/me/`
  - PUT/PATCH - Update profile
  - GET-View Profile

> `Public Test` are unauthenticated request
> `Private Test` are authenticated request

> `Token`: Token [token]

## Recipe API

- Create
  - `/recipes/`: POST
- List
  - `/recipes/`: GET
- View details
  - `/recipes/<id>`: GET
- update
  - `/recipes/<id>`: PUT/PATCH
- Delete
  - `/recipes/<id>`: DELETE

## Tags API

- `/recipe/tags/`:
  - `GET`
  - `POST`
  - `PUT/PATCH`
  - `DELETE`
