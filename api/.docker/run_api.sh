#!/bin/bash

set -e

./manage.py migrate --noinput
if [ -n "$DEBUG" ]; then
  ./manage.py runserver 0.0.0.0:$PORT
else
  echo "No Prod"
  # ./manage.py collectstatic --noinput
  # gunicorn atf_eregs.wsgi:application -b 0.0.0.0:$PORT --access-logfile -
fi
