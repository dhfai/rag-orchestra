# RAG Orchestra Run Script (PowerShell)
# =====================================

Write-Host "Starting RAG Orchestra System..." -ForegroundColor Green

# Check if virtual environment exists and activate it
if (Test-Path ".myenv") {
    Write-Host "Activating virtual environment (.myenv)..." -ForegroundColor Yellow
    & .\.myenv\Scripts\Activate.ps1
} elseif (Test-Path "venv") {
    Write-Host "Activating virtual environment (venv)..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "No virtual environment found. Using system Python..." -ForegroundColor Yellow
}

# Check Python and dependencies
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Run setup if needed
if (-not (Test-Path ".env")) {
    Write-Host "Running initial setup..." -ForegroundColor Yellow
    python setup.py
}

# Choose run mode
Write-Host "Select run mode:" -ForegroundColor Cyan
Write-Host "1. WebSocket Server (Real-time API)"
Write-Host "2. Interactive System"
Write-Host "3. Demo Mode"

$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host "Starting WebSocket Server..." -ForegroundColor Green
        Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "WebSocket Client: http://localhost:8000/client" -ForegroundColor Cyan
        Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
        uvicorn main_websocket_app:app --host 0.0.0.0 --port 8000 --reload
    }
    "2" {
        Write-Host "Starting Interactive System..." -ForegroundColor Green
        python main_system.py
    }
    "3" {
        Write-Host "Running Demo..." -ForegroundColor Green
        python -c "import asyncio; from main_system import RAGOrchestraSystem; asyncio.run(RAGOrchestraSystem().run_demo())"
    }
    default {
        Write-Host "Invalid choice. Starting WebSocket Server..." -ForegroundColor Yellow
        uvicorn main_websocket_app:app --host 0.0.0.0 --port 8000 --reload
    }
}
