# RAG Multi-Strategy System Setup Script
# PowerShell script untuk Windows

Write-Host "🎓 RAG Multi-Strategy System Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check Python installation
Write-Host "`n📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host "`n📦 Checking pip installation..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ Pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Pip not found. Please install pip first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📥 Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup environment file
Write-Host "`n⚙️ Setting up environment..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Environment file created from template" -ForegroundColor Green
        Write-Host "📝 Please edit .env file with your configuration" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ .env.example not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Environment file already exists" -ForegroundColor Green
}

# Create logs directory
Write-Host "`n📁 Creating directories..." -ForegroundColor Yellow
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Name "logs"
    Write-Host "✅ Logs directory created" -ForegroundColor Green
} else {
    Write-Host "✅ Logs directory already exists" -ForegroundColor Green
}

if (!(Test-Path "vector_db")) {
    New-Item -ItemType Directory -Name "vector_db"
    Write-Host "✅ Vector DB directory created" -ForegroundColor Green
} else {
    Write-Host "✅ Vector DB directory already exists" -ForegroundColor Green
}

# Check data directory
Write-Host "`n📚 Checking data directory..." -ForegroundColor Yellow
if (Test-Path "data") {
    Write-Host "✅ Data directory found" -ForegroundColor Green
    $cpCount = (Get-ChildItem "data/cp" -ErrorAction SilentlyContinue | Measure-Object).Count
    $atpCount = (Get-ChildItem "data/atp" -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "📊 CP documents: $cpCount" -ForegroundColor Cyan
    Write-Host "📊 ATP documents: $atpCount" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Data directory not found. Some features may be limited." -ForegroundColor Yellow
}

Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "`n🚀 To run the application:" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor White
Write-Host "`n📖 For more information, check README.md" -ForegroundColor Cyan
