#!/bin/bash
set -e
ls /app
if [ "$ENV" = 'PROD' ]; then
    echo "Running Production Server"
    exec uwsgi --http 0.0.0.0:9090 --wsgi-file /app/SimpleAPI.py --callable app --stats 0.0.0.0:9191
elif [ "$ENV" = 'UNIT' ]; then
    echo "Running Unit Tests"
    exec python tests.py
else
    echo "Running Development Server"
    exec python SimpleAPI.py
fi