#!/bin/sh

flask db upgrade

exec gunicorn \
    --reload \
    --bind 0.0.0.0:80 \
    --access-logfile - \
    --error-logfile - \
    "app:create_app()"