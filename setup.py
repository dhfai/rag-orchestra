"""
RAG Orchestra Setup Script
=========================

Script untuk setup dan konfigurasi sistem RAG Orchestra.
Menginstall dependencies, setup database, dan konfigurasi environment.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
from typing import Dict, Any, Optional

def run_command(command: str, description: str = "") -> bool:
    """Run command dengan error handling"""
    if description:
        print(f"\n🔧 {description}")

    print(f"Running: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(result.stdout)

        print("✅ Success")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_python_version():
    """Check Python version requirement"""
    print("\n🐍 Checking Python version...")

    version = sys.version_info
    min_version = (3, 8)

    if version >= min_version:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not supported. Minimum required: {min_version[0]}.{min_version[1]}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")

    # Update pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Updating pip"):
        return False

    # Install requirements
    requirements_files = [
        "requirements_updated.txt",
        "requirements.txt"
    ]

    for req_file in requirements_files:
        if Path(req_file).exists():
            if run_command(f"{sys.executable} -m pip install -r {req_file}", f"Installing from {req_file}"):
                return True

    # Fallback: install essential packages manually
    print("⚠️ Requirements file not found, installing essential packages...")

    essential_packages = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "websockets>=12.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "chromadb>=0.4.18",
        "sentence-transformers>=2.2.2",
        "google-generativeai>=0.3.2",
        "openai>=1.3.0",
        "duckduckgo-search>=3.9.6",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "rich>=13.7.0"
    ]

    for package in essential_packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing...")

    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directory structure...")

    directories = [
        "data/cp",
        "data/atp",
        "data/modul_ajar",
        "vector_db",
        "logs",
        "config",
        "uploads",
        "outputs"
    ]

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
        else:
            print(f"📁 Exists: {directory}")

    return True

def create_env_file():
    """Create .env file template"""
    print("\n🔧 Creating environment configuration...")

    env_file = Path(".env")

    if env_file.exists():
        print("📄 .env file already exists")
        return True

    env_template = """# RAG Orchestra Environment Configuration
# =======================================

# LLM API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=rag_orchestra

MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=rag_orchestra

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Vector Database
CHROMA_PERSIST_DIRECTORY=./vector_db

# Application Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true
"""

    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)

        print("✅ Created .env file template")
        print("⚠️  Please edit .env file and add your API keys")
        return True

    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_config_files():
    """Create configuration files"""
    print("\n📝 Creating configuration files...")

    # Create logging config
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard"
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": "logs/rag_orchestra.log",
                "formatter": "detailed"
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }

    try:
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        with open(config_dir / "logging_config.json", 'w', encoding='utf-8') as f:
            json.dump(logging_config, f, indent=2)

        print("✅ Created logging configuration")

        # Create orchestrator config
        orchestrator_config = {
            "thresholds": {
                "simple_rag": 0.85,
                "advanced_rag": 0.6,
                "graph_rag": 0.5,
                "overall_confidence": 0.8
            },
            "weights": {
                "template_matching": {
                    "lambda_1": 0.8,
                    "lambda_2": 0.2
                },
                "advanced_rag": {
                    "alpha_1": 0.3,
                    "alpha_2": 0.25,
                    "alpha_3": 0.25,
                    "alpha_4": 0.2
                },
                "graph_rag": {
                    "beta_1": 0.4,
                    "beta_2": 0.4,
                    "beta_3": 0.2
                }
            }
        }

        with open(config_dir / "orchestrator_config.json", 'w', encoding='utf-8') as f:
            json.dump(orchestrator_config, f, indent=2)

        print("✅ Created orchestrator configuration")
        return True

    except Exception as e:
        print(f"❌ Failed to create config files: {e}")
        return False

def create_run_scripts():
    """Create run scripts for different platforms"""
    print("\n🚀 Creating run scripts...")

    # Windows PowerShell script
    ps1_script = """# RAG Orchestra Run Script (PowerShell)
# =====================================

Write-Host "Starting RAG Orchestra System..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\\venv\\Scripts\\Activate.ps1
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
        python main_websocket_app.py
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
        python main_websocket_app.py
    }
}
"""

    # Bash script for Linux/Mac
    bash_script = """#!/bin/bash
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
"""

    try:
        # Create PowerShell script
        with open("run.ps1", 'w', encoding='utf-8') as f:
            f.write(ps1_script)
        print("✅ Created run.ps1 (Windows PowerShell)")

        # Create Bash script
        with open("run.sh", 'w', encoding='utf-8') as f:
            f.write(bash_script)

        # Make bash script executable
        if os.name != 'nt':  # Not Windows
            os.chmod("run.sh", 0o755)

        print("✅ Created run.sh (Linux/Mac)")
        return True

    except Exception as e:
        print(f"❌ Failed to create run scripts: {e}")
        return False

def create_readme():
    """Create README with setup and usage instructions"""
    print("\n📖 Creating README...")

    readme_content = """# RAG Orchestra - Orchestrated RAG Modul Ajar Digital

## 📋 Overview

Sistem **Orchestrated RAG (Retrieval-Augmented Generation)** untuk pembuatan modul ajar digital dengan pendekatan multi-strategy dan real-time interaction.

## 🏗️ Architecture

Sistem menggunakan pendekatan **Orchestrated RAG** dengan komponen:

1. **Main Orchestrator** - Pengendali proses utama dengan scoring system
2. **Prompt Builder Agent** - Memastikan input lengkap (Complete Input)
3. **Multi-Strategy RAG Components**:
   - Simple RAG (template matching ≥ 0.85)
   - Advanced RAG (complex queries ≥ 0.6)
   - Graph RAG (relational patterns ≥ 0.5)
   - Adaptive RAG (fallback strategy)
4. **Real-time WebSocket** - Komunikasi dinamis dengan user

## 🛠️ Tech Stack

- **Python 3.8+** - Core language
- **FastAPI** - RESTful API framework
- **WebSocket** - Real-time communication
- **ChromaDB** - Vector database
- **LLM APIs** - Gemini, OpenAI
- **DuckDuckGo Search** - Online content retrieval
- **MongoDB** - Document storage
- **Redis** - Caching layer

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd rag-orchestra
```

### 2. Run Setup
```bash
# Windows
python setup.py

# Linux/Mac
python3 setup.py
```

### 3. Configure Environment
Edit `.env` file and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Usage

### Option 1: WebSocket Server (Recommended)
```bash
# Windows
.\\run.ps1

# Linux/Mac
./run.sh
```

Access WebSocket client: http://localhost:8000/client

### Option 2: Interactive Mode
```bash
python main_system.py
```

### Option 3: Demo Mode
```bash
python -c "import asyncio; from main_system import RAGOrchestraSystem; asyncio.run(RAGOrchestraSystem().run_demo())"
```

## 📡 WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/your_session_id');
```

### Start Processing
```javascript
ws.send(JSON.stringify({
    type: 'start_processing',
    data: {
        nama_guru: 'Budi Santoso',
        nama_sekolah: 'SDN 1 Jakarta',
        mata_pelajaran: 'Matematika',
        kelas: '3',
        fase: 'B',
        topik: 'Penjumlahan',
        sub_topik: 'Penjumlahan 1-100',
        alokasi_waktu: '2 x 35 menit',
        llm_model_choice: 'gemini'
    }
}));
```

### Response Format
```javascript
{
    "type": "processing_complete",
    "data": {
        "complete_input": {
            "basic_info": { ... },
            "curriculum_content": {
                "cp": "Generated CP content...",
                "atp": "Generated ATP content..."
            },
            "technical_info": { ... },
            "metadata": { ... }
        }
    },
    "timestamp": "2024-08-22T10:30:00"
}
```

## 🧠 Scoring System

Sistem menggunakan scoring transparan untuk strategy selection:

### Template Matching Score
```
S_tmpl = λ₁ · μₖ + λ₂ · Δ̂
```
- μₖ = rata-rata cosine similarity top-k
- Δ̂ = margin antara dokumen teratas
- λ₁ = 0.8, λ₂ = 0.2

### Advanced RAG Score
```
S_adv = α₁L' + α₂E' + α₃D + α₄S'
```
- L' = panjang query ternormalisasi
- E' = jumlah entitas ternormalisasi
- D = document dispersion
- S' = query specificity

### Monitoring Score
```
C_overall = min(C_r, C_g)
```
- C_r = retrieval confidence
- C_g = generation confidence

## 📁 Project Structure

```
rag-orchestra/
├── src/
│   ├── core/
│   │   ├── models.py
│   │   └── prompt_builder_agent.py
│   ├── orchestrator/
│   │   └── enhanced_main_orchestrator.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── vector_db_service.py
│   │   └── online_search_service.py
│   └── utils/
├── data/
│   ├── cp/
│   ├── atp/
│   └── modul_ajar/
├── config/
├── logs/
├── main_websocket_app.py
├── main_system.py
├── setup.py
└── run.ps1 / run.sh
```

## 🔧 Configuration

### Orchestrator Thresholds
- Simple RAG: S_tmpl ≥ 0.85
- Advanced RAG: S_adv ≥ 0.6
- Graph RAG: S_graph ≥ 0.5
- Overall Confidence: C_overall ≥ 0.8

### Model Support
- **Gemini**: 1.5 Flash, 1.5 Pro
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Active Sessions
```bash
curl http://localhost:8000/sessions
```

## 🐛 Troubleshooting

### Common Issues

1. **ImportError**: Run `python setup.py` to install dependencies
2. **API Key Error**: Check `.env` file configuration
3. **WebSocket Connection Failed**: Ensure port 8000 is available
4. **Vector DB Error**: Check `vector_db/` directory permissions

### Logs
Check logs in `logs/rag_orchestra.log` for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

[License information]

## 📞 Support

For issues and questions, please check the logs and documentation first.
"""

    try:
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ Created README.md")
        return True

    except Exception as e:
        print(f"❌ Failed to create README: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 RAG Orchestra Setup")
    print("=====================")

    success_count = 0
    total_steps = 7

    # Step 1: Check Python version
    if check_python_version():
        success_count += 1

    # Step 2: Install dependencies
    if install_dependencies():
        success_count += 1

    # Step 3: Create directories
    if create_directories():
        success_count += 1

    # Step 4: Create environment file
    if create_env_file():
        success_count += 1

    # Step 5: Create config files
    if create_config_files():
        success_count += 1

    # Step 6: Create run scripts
    if create_run_scripts():
        success_count += 1

    # Step 7: Create README
    if create_readme():
        success_count += 1

    # Summary
    print(f"\n📊 Setup Summary: {success_count}/{total_steps} steps completed")

    if success_count == total_steps:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file and add your API keys")
        print("2. Run the system:")
        if os.name == 'nt':  # Windows
            print("   .\\run.ps1")
        else:
            print("   ./run.sh")
        print("3. Access WebSocket client: http://localhost:8000/client")
    else:
        print(f"\n⚠️ Setup completed with {total_steps - success_count} issues")
        print("Please review the errors above and retry.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        sys.exit(1)
