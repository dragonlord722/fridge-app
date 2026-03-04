#!/bin/bash

# This "trap" ensures that if you kill this script, 
# it also kills the backend and frontend background processes.
trap "kill 0" EXIT

echo "🚀 Starting Full Stack Environment..."

# Run backend and frontend in the background
(cd backend && ./run_local.sh) & 
(cd frontend && ./run_local.sh) &

# Wait for both processes to keep the terminal open
wait