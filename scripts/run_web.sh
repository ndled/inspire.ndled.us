#!/bin/sh
su -m app -c "gunicorn --bind 0.0.0.0:5000 wsgi:app"