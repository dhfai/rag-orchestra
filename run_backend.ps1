# Backend Setup and Run Script
# ============================

param(
    [string]$Action = "run",
    [switch]$Help
)

function Show-Help {
    Write-Host "RAG Multi-Strategy Backend - Setup and Run Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\run_backend.ps1 [ACTION] [OPTIONS]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  setup     - Install dependencies and setup environment"
    Write-Host "  run       - Run the backend server (default)"
    Write-Host "  dev       - Run in development mode with reload"
    Write-Host "  install   - Install Python packages only"
    Write-Host "  check     - Check environment and dependencies"
    Write-Host "  clean     - Clean cache and temporary files"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -Help     - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Magenta
    Write-Host "  .\run_backend.ps1 setup"
    Write-Host "  .\run_backend.ps1 run"
    Write-Host "  .\run_backend.ps1 dev"
    Write-Host ""
}

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ Python not found. Please install Python 3.13+ first." -ForegroundColor Red
        return $false
    }
    return $false
}

function Test-RequirementsFile {
    if (Test-Path "requirements.txt") {
        Write-Host "✓ requirements.txt found" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ requirements.txt not found" -ForegroundColor Red
        return $false
    }
}

function Install-Dependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

    if (-not (Test-RequirementsFile)) {
        Write-Host "Creating requirements.txt..." -ForegroundColor Yellow

        $requirements = @(
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.5.0",
            "websockets>=12.0",
            "python-multipart>=0.0.6",
            "python-dotenv>=1.0.0",
            "rich>=13.7.0",
            "colorama>=0.4.6",
            "httpx>=0.25.2",
            "asyncio-mqtt>=0.16.1",
            "redis>=5.0.1",
            "celery>=5.3.4",
            "sqlalchemy>=2.0.23",
            "alembic>=1.13.1",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-multipart>=0.0.6",
            "aiofiles>=23.2.1"
        )

        $requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
        Write-Host "✓ requirements.txt created" -ForegroundColor Green
    }

    try {
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Failed to install dependencies: $_" -ForegroundColor Red
        return $false
    }
}

function Setup-Environment {
    Write-Host "Setting up environment..." -ForegroundColor Yellow

    # Create directories
    $directories = @("logs", "uploads", "temp", "data")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✓ Created directory: $dir" -ForegroundColor Green
        }
    }

    # Create .env file if not exists
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
        } else {
            Write-Host "⚠ .env.example not found, you may need to create .env manually" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ .env file already exists" -ForegroundColor Green
    }

    Write-Host "✓ Environment setup completed" -ForegroundColor Green
}

function Initialize-Database {
    Write-Host "Initializing database..." -ForegroundColor Yellow

    try {
        # Test database connections
        python init_database.py --test
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Database connection test passed" -ForegroundColor Green

            # Create database tables
            python init_database.py --create
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Database tables created successfully" -ForegroundColor Green
                return $true
            } else {
                Write-Host "✗ Failed to create database tables" -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "✗ Database connection test failed" -ForegroundColor Red
            Write-Host "Please check your database configuration in .env file" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "✗ Database initialization error: $_" -ForegroundColor Red
        return $false
    }
}function Test-Environment {
    Write-Host "Checking environment..." -ForegroundColor Yellow

    $allGood = $true

    # Check Python
    if (-not (Test-PythonInstalled)) {
        $allGood = $false
    }

    # Check requirements.txt
    if (-not (Test-RequirementsFile)) {
        $allGood = $false
    }

    # Check directories
    $directories = @("src", "src/api", "src/core", "src/orchestrator", "src/rag", "src/services", "src/schemas", "src/websocket", "src/utils")
    foreach ($dir in $directories) {
        if (Test-Path $dir) {
            Write-Host "✓ Directory exists: $dir" -ForegroundColor Green
        } else {
            Write-Host "✗ Directory missing: $dir" -ForegroundColor Red
            $allGood = $false
        }
    }

    # Check main files
    $files = @("src/api/main.py", "run_backend.py")
    foreach ($file in $files) {
        if (Test-Path $file) {
            Write-Host "✓ File exists: $file" -ForegroundColor Green
        } else {
            Write-Host "✗ File missing: $file" -ForegroundColor Red
            $allGood = $false
        }
    }

    if ($allGood) {
        Write-Host "✓ Environment check passed" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ Environment check failed" -ForegroundColor Red
        return $false
    }
}

function Start-Backend {
    param([bool]$DevMode = $false)

    Write-Host "Starting RAG Multi-Strategy Backend..." -ForegroundColor Yellow

    if (-not (Test-Environment)) {
        Write-Host "Environment check failed. Run setup first." -ForegroundColor Red
        return
    }

    # Set environment variables for development
    if ($DevMode) {
        $env:RELOAD = "true"
        $env:LOG_LEVEL = "debug"
        Write-Host "Running in development mode with auto-reload" -ForegroundColor Cyan
    } else {
        $env:RELOAD = "false"
        $env:LOG_LEVEL = "info"
        Write-Host "Running in production mode" -ForegroundColor Cyan
    }

    # Check if port is available
    $port = $env:PORT
    if (-not $port) { $port = 8000 }

    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($connection) {
            Write-Host "⚠ Port $port is already in use. The server might already be running." -ForegroundColor Yellow
            $response = Read-Host "Do you want to continue anyway? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                return
            }
        }
    } catch {
        # Port is available
    }

    Write-Host ""
    Write-Host "Server will be available at:" -ForegroundColor Green
    Write-Host "  • Main API: http://localhost:$port" -ForegroundColor Cyan
    Write-Host "  • Documentation: http://localhost:$port/docs" -ForegroundColor Cyan
    Write-Host "  • WebSocket: ws://localhost:$port/ws/{session_id}" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""

    try {
        python run_backend.py
    } catch {
        Write-Host "Error starting backend: $_" -ForegroundColor Red
    }
}

function Clean-Cache {
    Write-Host "Cleaning cache and temporary files..." -ForegroundColor Yellow

    # Python cache
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | ForEach-Object {
        Remove-Item -Recurse -Force $_
        Write-Host "✓ Removed: $_" -ForegroundColor Green
    }

    # Temporary files
    if (Test-Path "temp") {
        Get-ChildItem -Path "temp" | Remove-Item -Recurse -Force
        Write-Host "✓ Cleaned temp directory" -ForegroundColor Green
    }

    # Log files (optional)
    $response = Read-Host "Do you want to clean log files? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        if (Test-Path "logs") {
            Get-ChildItem -Path "logs" -Name "*.log" | ForEach-Object {
                Remove-Item -Force "logs/$_"
                Write-Host "✓ Removed log: $_" -ForegroundColor Green
            }
        }
    }

    Write-Host "✓ Cache cleanup completed" -ForegroundColor Green
}

# Main script logic
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "RAG Multi-Strategy Backend - Management Script" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""

switch ($Action.ToLower()) {
    "setup" {
        Write-Host "Running full setup..." -ForegroundColor Cyan
        if (Test-PythonInstalled) {
            Setup-Environment
            Install-Dependencies

            # Initialize database
            $dbResult = Initialize-Database
            if ($dbResult) {
                Write-Host ""
                Write-Host "✓ Setup completed successfully!" -ForegroundColor Green
                Write-Host "Database tables created and ready to use." -ForegroundColor Green
                Write-Host "Run '.\run_backend.ps1 run' to start the backend server." -ForegroundColor Yellow
            } else {
                Write-Host ""
                Write-Host "⚠ Setup completed with database warnings." -ForegroundColor Yellow
                Write-Host "Please check your database configuration in .env file." -ForegroundColor Yellow
                Write-Host "You can run '.\run_backend.ps1 init-db' to retry database setup." -ForegroundColor Yellow
            }
        }
    }

    "init-db" {
        Write-Host "Initializing database..." -ForegroundColor Cyan
        Initialize-Database
    }

    "db-info" {
        Write-Host "Showing database information..." -ForegroundColor Cyan
        python init_database.py --info
    }

    "install" {
        Write-Host "Installing dependencies only..." -ForegroundColor Cyan
        if (Test-PythonInstalled) {
            Install-Dependencies
        }
    }

    "check" {
        Write-Host "Checking environment..." -ForegroundColor Cyan
        Test-Environment
    }

    "dev" {
        Write-Host "Starting development server..." -ForegroundColor Cyan
        Start-Backend -DevMode $true
    }

    "run" {
        Write-Host "Starting production server..." -ForegroundColor Cyan
        Start-Backend -DevMode $false
    }

    "clean" {
        Write-Host "Cleaning cache..." -ForegroundColor Cyan
        Clean-Cache
    }

    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Write-Host "Use -Help for available actions." -ForegroundColor Yellow
    }
}
