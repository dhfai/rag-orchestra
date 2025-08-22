import os
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """
    Configuration class untuk RAG Orchestra System
    Updated sesuai instruksi Orchestrated RAG terbaru
    """

    # Database Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "rag_orchestra")

    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "rag_orchestra")

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # Vector Database
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./vector_db")

    # LLM Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Default LLM Models
    DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-1.5-flash")
    DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4")

    # Application Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Data Paths
    DATA_CP_PATH = os.getenv("DATA_CP_PATH", "data/cp")
    DATA_ATP_PATH = os.getenv("DATA_ATP_PATH", "data/atp")
    DATA_MODUL_AJAR_PATH = os.getenv("DATA_MODUL_AJAR_PATH", "data/modul_ajar")

    # Upload & Output Paths
    UPLOAD_PATH = os.getenv("UPLOAD_PATH", "uploads")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "outputs")

    # WebSocket Configuration
    WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8000"))

    # Orchestrator Configuration
    # Thresholds berdasarkan pilot test dan literatur
    ORCHESTRATOR_THRESHOLDS = {
        "simple_rag": float(os.getenv("SIMPLE_RAG_THRESHOLD", "0.85")),
        "advanced_rag": float(os.getenv("ADVANCED_RAG_THRESHOLD", "0.6")),
        "graph_rag": float(os.getenv("GRAPH_RAG_THRESHOLD", "0.5")),
        "overall_confidence": float(os.getenv("OVERALL_CONFIDENCE_THRESHOLD", "0.8"))
    }

    # Weights untuk scoring calculations
    ORCHESTRATOR_WEIGHTS = {
        "template_matching": {
            "lambda_1": float(os.getenv("TEMPLATE_LAMBDA_1", "0.8")),
            "lambda_2": float(os.getenv("TEMPLATE_LAMBDA_2", "0.2"))
        },
        "advanced_rag": {
            "alpha_1": float(os.getenv("ADVANCED_ALPHA_1", "0.3")),
            "alpha_2": float(os.getenv("ADVANCED_ALPHA_2", "0.25")),
            "alpha_3": float(os.getenv("ADVANCED_ALPHA_3", "0.25")),
            "alpha_4": float(os.getenv("ADVANCED_ALPHA_4", "0.2"))
        },
        "graph_rag": {
            "beta_1": float(os.getenv("GRAPH_BETA_1", "0.4")),
            "beta_2": float(os.getenv("GRAPH_BETA_2", "0.4")),
            "beta_3": float(os.getenv("GRAPH_BETA_3", "0.2"))
        }
    }

    # Online Search Configuration
    SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "5"))
    SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "10"))
    SEARCH_RETRIES = int(os.getenv("SEARCH_RETRIES", "3"))

    # Content Processing
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "3000"))
    MIN_CP_LENGTH = int(os.getenv("MIN_CP_LENGTH", "100"))
    MIN_ATP_LENGTH = int(os.getenv("MIN_ATP_LENGTH", "150"))

    @classmethod
    def ensure_directories(cls):
        """Ensure semua directory yang diperlukan ada"""
        directories = [
            cls.DATA_CP_PATH,
            cls.DATA_ATP_PATH,
            cls.DATA_MODUL_AJAR_PATH,
            cls.CHROMA_PERSIST_DIRECTORY,
            cls.UPLOAD_PATH,
            cls.OUTPUT_PATH,
            "logs"
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration"""
        validation_results = {}

        # Check required API keys
        validation_results["has_gemini_key"] = bool(cls.GEMINI_API_KEY)
        validation_results["has_openai_key"] = bool(cls.OPENAI_API_KEY)
        validation_results["has_any_llm_key"] = validation_results["has_gemini_key"] or validation_results["has_openai_key"]

        # Check directory access
        try:
            cls.ensure_directories()
            validation_results["directories_accessible"] = True
        except Exception:
            validation_results["directories_accessible"] = False

        # Check threshold values
        thresholds_valid = all(
            0.0 <= threshold <= 1.0
            for threshold in cls.ORCHESTRATOR_THRESHOLDS.values()
        )
        validation_results["thresholds_valid"] = thresholds_valid

        return validation_results

    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "llm_models": {
                "gemini_available": bool(cls.GEMINI_API_KEY),
                "openai_available": bool(cls.OPENAI_API_KEY),
                "default_gemini": cls.DEFAULT_GEMINI_MODEL,
                "default_openai": cls.DEFAULT_OPENAI_MODEL
            },
            "thresholds": cls.ORCHESTRATOR_THRESHOLDS,
            "websocket": {
                "host": cls.WEBSOCKET_HOST,
                "port": cls.WEBSOCKET_PORT
            },
            "data_paths": {
                "cp": cls.DATA_CP_PATH,
                "atp": cls.DATA_ATP_PATH,
                "modul_ajar": cls.DATA_MODUL_AJAR_PATH,
                "vector_db": cls.CHROMA_PERSIST_DIRECTORY
            }
        }
