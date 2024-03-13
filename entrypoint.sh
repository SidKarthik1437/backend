#!/bin/sh

python manage.py makemigrations
python manage.py migrate --no-input
# python manage.py runserver 0.0.0.0:8000

gunicorn --workers=3 --bind 0.0.0.0:8000 nexa.wsgi:application
