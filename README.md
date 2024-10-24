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
- tests.py or tests/test_[name] and only one we can use