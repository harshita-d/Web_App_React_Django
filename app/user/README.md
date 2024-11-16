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
