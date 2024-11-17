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

## URLS

- `app_name` : It means when referring to urls in this user app, we can use this namespace to avoid conflicts between different apps in the project

- `create/`: This URL maps the `POST` request for create user to the `CreateUserView`.

- `token/`: This maps `POST` request for generating an authentication token to the `CreateTokenView`.

- `me/`: this request maps the authenticated user to `ManageUserView`. It allows `GET`, `PUT` and `Patch` request because of `RetrieveUpdateAPIView`.

- `as_view`: This method is called on class-based view to create an instance of the view.
  - when we define a class-based view in django, we don't call the class directly like a function, instead use as_view() to instantiate the view.
