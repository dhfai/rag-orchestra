#!/bin/bash
# RAG Orchestra Run Script (Bash)
# ===============================

echo "Starting RAG Orchestra System..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python and dependencies
python3 --version
if [ $? -ne 0 ]; then
    echo "Python not found! Please install Python 3.8+"
    exit 1
fi

# Run setup if needed
if [ ! -f ".env" ]; then
    echo "Running initial setup..."
    python3 setup.py
fi

# Choose run mode
echo "Select run mode:"
echo "1. WebSocket Server (Real-time API)"
echo "2. Interactive System"
echo "3. Demo Mode"

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Starting WebSocket Server..."
        python3 main_websocket_app.py
        ;;
    2)
        echo "Starting Interactive System..."
        python3 main_system.py
        ;;
    3)
        echo "Running Demo..."
        python3 -c "import asyncio; from main_system import RAGOrchestraSystem; asyncio.run(RAGOrchestraSystem().run_demo())"
        ;;
    *)
        echo "Invalid choice. Starting WebSocket Server..."
        python3 main_websocket_app.py
        ;;
esac
