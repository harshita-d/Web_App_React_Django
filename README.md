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

## command to start django service
- docker-compose up