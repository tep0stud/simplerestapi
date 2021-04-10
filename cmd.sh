#!/bin/bash
set -e
ls /app
if [ "$ENV" = 'DEV' ]; then
    echo "Running Development Server"
    exec python users.py
elif [ "$ENV" = 'UNIT' ]; then
    echo "Running Unit Tests"
    exec python tests.py
else
    echo "Running Production Server"
    exec uwsgi --http 0.0.0.0:9090 --wsgi-file /app/users.py --callable app --stats 0.0.0.0:9191
fi