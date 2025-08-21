"""
Backend Server Startup
=====================

Server startup script untuk RAG Multi-Strategy Backend
Menjalankan FastAPI server dengan Uvicorn
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.main import app
from src.utils.logger import get_logger

logger = get_logger("BackendServer")

def main():
    """Main function untuk menjalankan backend server"""

    # Configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    logger.info(f"Starting RAG Multi-Strategy Backend Server...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Workers: {workers}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Log Level: {log_level}")

    try:
        # Run server
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            workers=workers if not reload else 1,  # Workers > 1 doesn't work with reload
            reload=reload,
            log_level=log_level,
            access_log=True,
            reload_dirs=["src"] if reload else None
        )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server startup error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
