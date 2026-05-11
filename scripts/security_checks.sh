#!/bin/bash

echo "Running backend security checks..."

echo "1. Checking Python syntax..."
python -m py_compile backend/app/__init__.py
python -m py_compile backend/app/config.py
python -m py_compile backend/app/routes/web.py
python -m py_compile backend/app/routes/api.py
python -m py_compile backend/app/services/scoring.py
python -m py_compile backend/app/services/geoip.py
python -m py_compile backend/app/services/reporting.py
python -m py_compile backend/app/services/validation.py
echo "   Python syntax OK"

echo "2. Checking for required environment variables..."
if [ -f .env ]; then
    echo "   .env file found"
else
    echo "   Warning: .env file not found. Copy .env.example to .env"
fi

echo "3. Checking static files..."
if [ -f "backend/app/static/css/style.css" ]; then
    echo "   CSS files OK"
else
    echo "   Warning: CSS files missing"
fi

if [ -f "backend/app/static/js/script.js" ]; then
    echo "   JS files OK"
else
    echo "   Warning: JS files missing"
fi

echo "4. Checking shared resources..."
if [ -d "shared/rules" ]; then
    echo "   Shared rules directory OK"
    ls shared/rules/
else
    echo "   Warning: shared/rules directory missing"
fi

echo "5. Security checks complete."
echo ""
echo "To run tests: cd backend && python -m pytest tests/"
echo "To start server: cd backend && python wsgi.py"