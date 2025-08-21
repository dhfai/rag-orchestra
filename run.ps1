# Quick start script untuk menjalankan aplikasi
# PowerShell script

Write-Host "🚀 Starting RAG Multi-Strategy System..." -ForegroundColor Cyan

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Check if requirements are installed
Write-Host "📋 Checking dependencies..." -ForegroundColor Yellow
$checkRequirements = pip list | Select-String "rich"
if (-not $checkRequirements) {
    Write-Host "📥 Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Run the application
Write-Host "🎓 Launching application..." -ForegroundColor Green
python main.py
