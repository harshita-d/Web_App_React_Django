# User Authentication System

## Overview

- Custom user authentication is implemented using `DRF`

## Models

- `AbstractBaseUser`: It provide authentication features like password hashing etc.

- `PermissionMixin`: add fields and methods to handle user permissions like is_staff etc..

- here we are customizing `email` and `password` as the fields instead of `username` and `password`

- `UserManager`: Custom manager to create users and superusers with inbuilt functions `create_user` and `create_superuser`.

  - `normalize_email(email)`: it is provided by `BaseUserManager` which converts into lowerCase

  - `set_password`: This is a part of `AbstractBaseUser` class which hashes password.

  - `save()`: this is built in method in models that saves the object to the database.

- `User`: here the primary identifier is `email` instead of `username`.

  - `is_staff`: it indicates whether the user has staff(admin) access or not.

  - `USERNAME_FIELD`: this is a built-in field in `AbstractBaseUser` tha tells django to use the `email` field as unique identifier instead of default `username`.

## Serializers

- Serializers in `DRF` are used to convert complex data types like Django Models into JSON or vice versa

- `UserSerializers`: This serializers converts the `User` model data into JSON and validates the input data as per mentioned in models when creating or updating the user

  - `Create`: this is a in-built method responsible for creating a new user with an encrypted password. It calls `create_user` from `UserManager` to create user.

  - `Update`: It is used to update the data. if password is also updated than it explicitly hashes the password using `set_password` and than save it.

    - `super().update()`: this calls the parent `ModelSerializer`'s `update()` method to update the other fields

- `AuthTokenSerializer`: This serializer checks whether the provided email and password are correct.

  - `validate`: this method is responsible for authenticating the user based on the provided credentials. It uses Django `authenticate()` function to check if the credentials are valid or not. `attrs['user']` this adds the authenticated user object to the attrs dictionary, which can be used in the views.

## views

- Views in DRF are used to handle HTTP request(GET, POST, PUT, PATCH, DELETE) and return appropriate responses.

- In DRF views know how to habdle `GET`,`POST` and other HTTP methods because fo the predefined logic in the base view classes provided by the DRF.

- DRF provides base view classes like `ModelViewSet`, `APIViewSet` and `generic` views that defines how to handle different HTTP method. These base classes internally map HTTP methods to specific class method.

```
GET → retrieve() or list()
POST → create()
PUT → update()
PATCH → partial_update()
DELETE → destroy()
```

- `CreateUserView`: it handles user creation.

  - It inherit `CreateAPIView` as a base class.
  - It is specifically used for handling `POSt` request.
  - Automatically maps HTTP POST request to the `create()` method of serializer.
  - In serializer the data is validated.
  - if the data is valid then new user is created with `create()` method with `201 created` as response.
  - create() method in `UserSerializer` calls the `create_user()` method of the custom user model `get_user_model()`
  - if not then serializer raise validation error `400 Bad request`

> `get_user_model()` is the utility function provided by Django. It retrieves the user model that is currently being used in th project. in setting.py `AUTH_USER_MODEL = [path to user_model]`

- `CreateTokenView` : This view is responsible for creating a token for the user.

  - It inherits from `ObtainAuthToken` provided by DRF to handle token generation.
  - `ObtainAuthToken` validates user credentials
  - `AuthTokenSerializer` validates the data
  - return token if valid data else raise error
  - `renderer_classes`: this ensures that the token response is returned in the desired format. `api_settings.DEFAULT_RENDERER_CLASSES` typically includes formats like JSON and Browsable API
  - it is better to use `ObtainAuthToken` rather than writing our own token generation logic as it provides a built-in, reliable, secure mechanism for token based auth.

- `ManageUserView`: This view handles the retrieval and update of the authenticated single user's data.

  - `RetrieveUpdateAPIView` allows `GET`, `PUT` and `PATCH` request.
  - `authentication_classes` this ensures that the view is accessible only to users authenticated via token-based authentication.
  - `permission_classes` this restricts access to the view to only authenticated users. Otherwise i will throw `401` error.
  - `get_object()` specifies which user object should be retrieved or updated. `self.request.user` ensures that the view only interacts with the current user's data.

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
