#!/bin/bash

echo "Building frontend demo..."
echo "Copying frontend-demo to docs/ directory..."

if [ -d "frontend-demo/build" ]; then
    cp -r frontend-demo/build/* docs/
    echo "Built files copied successfully"
else
    echo "No build directory found, using src files"
    if [ -d "frontend-demo/src" ]; then
        cp frontend-demo/src/*.html docs/index.html 2>/dev/null || true
        echo "Source files copied"
    fi
fi

cp shared/rules/*.json docs/assets/data/ 2>/dev/null || true

echo "Build complete! Static demo ready for GitHub Pages deployment."
echo "Documentation available at docs/index.html"