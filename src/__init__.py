"""
RAG Multi-Strategy Backend Package
=================================

Modular RAG Multi-Strategy system dengan real-time user interaction backend.
Menyediakan FastAPI endpoints dan WebSocket untuk komunikasi real-time.
"""

__version__ = "1.0.0"
__author__ = "RAG Multi-Strategy Team"
__email__ = "team@ragmultistrategy.com"

# Package information
__title__ = "RAG Multi-Strategy Backend"
__description__ = "Backend API untuk sistem Modular RAG Multi-Strategy dengan real-time user interaction"
__url__ = "https://github.com/ragmultistrategy/backend"
__license__ = "MIT"

# Export main components
from .core.models import UserInput, ValidationResult, FinalInput
from .schemas.api_schemas import (
    UserInputRequest,
    ValidationRequest,
    CPATPResponse,
    FinalInputResponse
)

__all__ = [
    "UserInput",
    "ValidationResult",
    "FinalInput",
    "UserInputRequest",
    "ValidationRequest",
    "CPATPResponse",
    "FinalInputResponse"
]
