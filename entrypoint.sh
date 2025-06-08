#!/bin/bash
echo "Applying Django migrations..."
python manage.py migrate

echo "Starting Uvicorn server..."
exec uvicorn wantedlab.fastapi:app --host 0.0.0.0 --port 8000 --reload