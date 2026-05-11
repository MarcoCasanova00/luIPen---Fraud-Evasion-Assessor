#!/bin/bash

echo "Starting Fraud Evasion Assessor Backend..."

if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

if [ -f ".env" ]; then
    echo "Loading environment from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found"
fi

export FLASK_ENV=${FLASK_ENV:-development}
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Running backend on port ${PORT:-5000}"
echo "Flask environment: $FLASK_ENV"

cd backend
python wsgi.py