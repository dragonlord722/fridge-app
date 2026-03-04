#!/bin/bash
echo "🧪 Running Full Stack Test Suite..."

# Set paths so pytest can find your modules
export PYTHONPATH=$(pwd)/backend:$(pwd)/frontend

# Run tests and capture the exit code
python3 -m pytest backend/backend_tests frontend/frontend_tests

if [ $? -eq 0 ]; then
    echo "✅ All tests passed! Proceeding with push..."
else
    echo "❌ Tests failed. Fix errors before pushing."
    exit 1
fi