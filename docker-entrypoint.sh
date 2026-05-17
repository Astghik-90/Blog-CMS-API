#!/bin/sh
# Ensure this script uses LF line endings.
# Run DB migrations using the app factory explicitly
flask --app "app:create_app()" db upgrade

exec gunicorn \
    --reload \
    --bind 0.0.0.0:80 \
    --access-logfile - \
    --error-logfile - \
    "app:create_app()"
