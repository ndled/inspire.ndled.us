#!/bin/sh
su -m app -c "gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app"