#!/bin/bash
# 1. Load Secrets (relative to root)
export $(grep -v '^#' backend/.env | xargs)

echo "🚀 Starting Backend from Root..."

# 2. Tell Python to treat the current directory as a source of modules
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend

# 3. Run uvicorn using the module path
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload