#!/bin/bash

# Character Replacement MVP - Quick Start Script
# This script sets up and runs both backend and frontend

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting Character Replacement MVP..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Setup Backend
echo ""
echo "📦 Setting up backend..."
cd "$PROJECT_ROOT/backend"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "❗ ВАЖНО: Отредактируйте backend/.env и добавьте Cloudinary credentials"
    echo "   Получить на: https://cloudinary.com/console"
    echo ""
    read -p "Нажмите Enter когда заполните .env файл..."
fi

# Start backend in background
echo ""
echo "🔧 Starting backend on http://localhost:8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Backend failed to start. Check backend.log for errors."
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Start frontend
echo ""
echo "🌐 Starting frontend on http://localhost:3000..."
cd "$PROJECT_ROOT/frontend"
python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 2

echo ""
echo "✅ All services are running!"
echo ""
echo "📱 Open in browser: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop all services..."

# Save PIDs for cleanup
echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"
echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend.pid"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."

    if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/.backend.pid")
        kill $BACKEND_PID 2>/dev/null || true
        rm "$PROJECT_ROOT/.backend.pid"
    fi

    if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend.pid")
        kill $FRONTEND_PID 2>/dev/null || true
        rm "$PROJECT_ROOT/.frontend.pid"
    fi

    echo "✅ All services stopped"
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Keep script running
wait
