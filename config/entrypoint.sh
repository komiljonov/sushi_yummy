#!/bin/sh



echo "Apply database migrations"
python manage.py migrate


echo "Create Super User"
python manage.py createsuperuser --noinput --email="komiljonovshukurullokh@gmail.com"

exec "$@"
