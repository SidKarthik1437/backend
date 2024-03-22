#!/bin/sh

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start the Django application
gunicorn --workers=3 --bind 0.0.0.0:8000 nexa.wsgi:application
