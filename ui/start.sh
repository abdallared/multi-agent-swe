#!/bin/bash

# AI Software Company UI - Start Script

echo "🚀 Starting AI Software Company UI..."
echo ""

# Check if Ollama is running
echo "1️⃣ Checking Ollama..."
if ! ollama list > /dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo "   Please start Ollama first: ollama serve"
    exit 1
fi
echo "✅ Ollama is running"
echo ""

# Start Backend
echo "2️⃣ Starting Backend..."
cd backend
python app.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Running on: http://localhost:8000"
echo ""

# Wait for backend to start
sleep 3

# Start Frontend
echo "3️⃣ Starting Frontend..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Running on: http://localhost:3000"
echo ""

echo "🎉 AI Software Company UI is ready!"
echo ""
echo "📝 Open your browser: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
