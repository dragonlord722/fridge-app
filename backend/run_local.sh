#!/bin/bash
export $(grep -v '^#' .env | xargs)
echo "🚀 Starting Backend..."
# Force the use of the current python3 environment
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload