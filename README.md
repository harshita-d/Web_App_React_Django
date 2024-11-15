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
