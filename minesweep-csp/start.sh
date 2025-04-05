#!/bin/bash

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Starting backend server..."
python app.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Starting frontend server..."
npm run dev

cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    exit 0
}

trap cleanup SIGINT SIGTERM

wait
