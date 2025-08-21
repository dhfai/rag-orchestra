"""
FastAPI Application
==================

Main FastAPI application untuk RAG Multi-Strategy Backend
Menyediakan REST API endpoints dan WebSocket untuk real-time interaction
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime

from ..schemas.api_schemas import (
    UserInputRequest, ValidationRequest, CPATPResponse,
    FinalInputResponse, TaskAnalysisResponse, WebSocketMessage,
    SessionCreateResponse, SessionStatusResponse, ConfigRequest
)
from ..services.session_manager import SessionManager, SessionStatusEnum, get_session_manager
from ..services.rag_processing_service import RAGProcessingService
from ..core.models import UserInput, ValidationResult
from ..utils.logger import get_logger

logger = get_logger("FastAPI-App")

# Global service instances
session_manager: Optional[SessionManager] = None
processing_service: Optional[RAGProcessingService] = None
websocket_connections: Dict[str, List[WebSocket]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global session_manager, processing_service

    # Startup
    logger.info("Starting RAG Multi-Strategy Backend...")

    # Initialize services
    session_manager = SessionManager()
    await session_manager.initialize_async_components()
    processing_service = RAGProcessingService(session_manager)

    # Configure session manager WebSocket broadcast
    session_manager.set_websocket_broadcast_callback(broadcast_to_websockets)

    logger.success("Backend services initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down RAG Multi-Strategy Backend...")
    if processing_service:
        await processing_service.shutdown()
    if session_manager:
        await session_manager.cleanup()
    logger.info("Backend shutdown completed")

# Create FastAPI app
app = FastAPI(
    title="RAG Multi-Strategy Backend",
    description="Backend API untuk sistem Modular RAG Multi-Strategy dengan real-time user interaction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Dependency Functions ===

def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    return session_manager

def get_processing_service() -> RAGProcessingService:
    """Get processing service instance"""
    if processing_service is None:
        raise HTTPException(status_code=500, detail="Processing service not initialized")
    return processing_service

# === WebSocket Management ===

async def broadcast_to_websockets(session_id: str, message: Dict[str, Any]):
    """Broadcast message to all WebSocket connections for a session"""
    if session_id not in websocket_connections:
        return

    connections = websocket_connections[session_id].copy()
    message_json = json.dumps(message)

    for websocket in connections:
        try:
            await websocket.send_text(message_json)
        except Exception as e:
            logger.warning(f"Failed to send WebSocket message: {str(e)}")
            # Remove dead connection
            if websocket in websocket_connections[session_id]:
                websocket_connections[session_id].remove(websocket)

def add_websocket_connection(session_id: str, websocket: WebSocket):
    """Add WebSocket connection to session"""
    if session_id not in websocket_connections:
        websocket_connections[session_id] = []
    websocket_connections[session_id].append(websocket)

def remove_websocket_connection(session_id: str, websocket: WebSocket):
    """Remove WebSocket connection from session"""
    if session_id in websocket_connections:
        if websocket in websocket_connections[session_id]:
            websocket_connections[session_id].remove(websocket)
        if not websocket_connections[session_id]:
            del websocket_connections[session_id]

# === REST API Endpoints ===

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "RAG Multi-Strategy Backend API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "websocket": "/ws/{session_id}",
            "sessions": "/api/sessions",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check(
    session_mgr: SessionManager = Depends(get_session_manager),
    proc_service: RAGProcessingService = Depends(get_processing_service)
):
    """Health check endpoint"""
    service_stats = proc_service.get_service_stats()
    session_stats = session_mgr.get_stats()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "session_manager": {
                "status": "running",
                "stats": session_stats
            },
            "processing_service": {
                "status": "running",
                "stats": service_stats
            }
        },
        "websocket_connections": len(websocket_connections)
    }

@app.post("/api/sessions", response_model=SessionCreateResponse)
async def create_session(
    config: Optional[ConfigRequest] = None,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Create new session"""
    try:
        # Extract user_id from config if available, otherwise use None
        user_id = None
        session_config = {}

        if config:
            session_config = config.dict()
            # Check if there's a user_id in user_preferences
            user_id = config.user_preferences.get("user_id") if config.user_preferences else None

        session_id = await session_mgr.create_session(user_id)
        session = session_mgr.get_session(session_id)

        logger.info(f"New session created: {session_id}")

        return SessionCreateResponse(
            session_id=session.session_id,
            status=session.status,
            created_at=session.created_at.isoformat(),
            config=session_config
        )
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager),
    proc_service: RAGProcessingService = Depends(get_processing_service)
):
    """Get session status"""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    processing_status = proc_service.get_processing_status(session_id)

    return SessionStatusResponse(
        session_id=session_id,
        status=session.status,
        current_step=session.current_step,
        progress_percentage=session.progress_percentage,
        created_at=session.created_at.isoformat(),
        last_activity=session.updated_at.isoformat(),
        processing_status=processing_status,
        has_user_input=session.user_input is not None,
        has_cp_atp_result=session.cp_atp_result is not None,
        has_final_input=session.final_input is not None,
        validation_count=len(session.validation_history),
        error_count=session.error_count,
        last_error=session.last_error
    )

@app.post("/api/sessions/{session_id}/input")
async def submit_user_input(
    session_id: str,
    user_input: UserInputRequest,
    session_mgr: SessionManager = Depends(get_session_manager),
    proc_service: RAGProcessingService = Depends(get_processing_service)
):
    """Submit user input and start processing"""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Convert to core model
        core_user_input = UserInput(
            nama_guru=user_input.nama_guru,
            nama_sekolah=user_input.nama_sekolah,
            mata_pelajaran=user_input.mata_pelajaran,
            topik=user_input.topik,
            sub_topik=user_input.sub_topik,
            kelas=user_input.kelas,
            alokasi_waktu=user_input.alokasi_waktu,
            model_llm=user_input.model_llm,
            cp=user_input.cp,
            atp=user_input.atp
        )

        # Set user input
        session_mgr.set_user_input(session_id, core_user_input)

        # Start processing
        processing_started = await proc_service.start_processing(session_id)

        if not processing_started:
            raise HTTPException(status_code=500, detail="Failed to start processing")

        logger.info(f"User input submitted and processing started for session: {session_id}")

        return {
            "message": "User input received and processing started",
            "session_id": session_id,
            "status": "processing_started",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error submitting user input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process user input: {str(e)}")

@app.post("/api/sessions/{session_id}/validate")
async def submit_validation(
    session_id: str,
    validation: ValidationRequest,
    session_mgr: SessionManager = Depends(get_session_manager),
    proc_service: RAGProcessingService = Depends(get_processing_service)
):
    """Submit validation for CP/ATP"""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatusEnum.USER_VALIDATION:
        raise HTTPException(
            status_code=400,
            detail=f"Session not in validation state. Current status: {session.status.value}"
        )

    try:
        # Handle validation
        validation_handled = await proc_service.handle_user_validation(session_id, validation)

        if not validation_handled:
            raise HTTPException(status_code=500, detail="Failed to handle validation")

        logger.info(f"Validation submitted for session: {session_id}, approved: {validation.is_approved}")

        return {
            "message": "Validation received and processed",
            "session_id": session_id,
            "validation_approved": validation.is_approved,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error submitting validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process validation: {str(e)}")

@app.get("/api/sessions/{session_id}/preview")
async def get_cp_atp_preview(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Get CP/ATP preview for validation - shows current generated content"""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.cp_atp_result:
        raise HTTPException(status_code=404, detail="CP/ATP result not yet available")

    # Return preview of generated CP/ATP
    return {
        "session_id": session_id,
        "status": session.status.value,
        "preview": {
            "generated_cp": session.cp_atp_result.cp_content,
            "generated_atp": session.cp_atp_result.atp_content,
            "generation_strategy": session.cp_atp_result.generation_strategy,
            "confidence_score": session.cp_atp_result.confidence_score,
            "sources_used": session.cp_atp_result.sources_used,
            "generation_metadata": session.cp_atp_result.generation_metadata
        },
        "user_input": {
            "nama_guru": session.user_input.nama_guru,
            "nama_sekolah": session.user_input.nama_sekolah,
            "mata_pelajaran": session.user_input.mata_pelajaran,
            "topik": session.user_input.topik,
            "sub_topik": session.user_input.sub_topik,
            "kelas": session.user_input.kelas,
            "alokasi_waktu": session.user_input.alokasi_waktu
        },
        "instructions": "Review the generated CP/ATP above. Use POST /api/sessions/{session_id}/validate to approve or request changes.",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sessions/{session_id}/result")
async def get_final_result(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Get final result for session"""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.final_input:
        raise HTTPException(status_code=404, detail="Final result not yet available")

    # Create response
    final_response = FinalInputResponse(
        session_id=session_id,
        user_input=UserInputRequest(
            nama_guru=session.final_input.user_input.nama_guru,
            nama_sekolah=session.final_input.user_input.nama_sekolah,
            mata_pelajaran=session.final_input.user_input.mata_pelajaran,
            topik=session.final_input.user_input.topik,
            sub_topik=session.final_input.user_input.sub_topik,
            kelas=session.final_input.user_input.kelas,
            alokasi_waktu=session.final_input.user_input.alokasi_waktu,
            model_llm=session.final_input.user_input.model_llm,
            cp=session.final_input.user_input.cp,
            atp=session.final_input.user_input.atp
        ),
        cp_content=session.final_input.cp_content,
        atp_content=session.final_input.atp_content,
        processing_metadata=session.final_input.processing_metadata,
        validation_history=[
            {
                "is_approved": v.is_approved,
                "feedback": v.feedback,
                "requested_changes": v.requested_changes
            } for v in session.final_input.validation_history
        ],
        completed_at=datetime.now().isoformat()
    )

    return final_response

@app.delete("/api/sessions/{session_id}")
async def delete_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager),
    proc_service: RAGProcessingService = Depends(get_processing_service)
):
    """Delete session"""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Cancel processing if running
        await proc_service.cancel_processing(session_id)

        # Remove session
        removed = session_mgr.remove_session(session_id)

        # Close WebSocket connections
        if session_id in websocket_connections:
            connections = websocket_connections[session_id].copy()
            for websocket in connections:
                try:
                    await websocket.close()
                except Exception:
                    pass
            del websocket_connections[session_id]

        if not removed:
            raise HTTPException(status_code=500, detail="Failed to remove session")

        logger.info(f"Session deleted: {session_id}")

        return {
            "message": "Session deleted successfully",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.get("/api/sessions")
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """List all sessions"""
    sessions = session_mgr.list_sessions(limit=limit, offset=offset)

    return {
        "sessions": [
            {
                "session_id": session.session_id,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.updated_at.isoformat(),
                "progress_percentage": session.progress_percentage,
                "has_user_input": session.user_input is not None,
                "has_final_input": session.final_input is not None
            } for session in sessions
        ],
        "total_count": len(sessions),
        "limit": limit,
        "offset": offset
    }

# === WebSocket Endpoint ===

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint untuk real-time communication"""
    await websocket.accept()

    # Verify session exists
    if session_manager is None:
        await websocket.close(code=1011, reason="Service not available")
        return

    session = session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return

    # Add connection
    add_websocket_connection(session_id, websocket)
    logger.info(f"WebSocket connected for session: {session_id}")

    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "status": session.status.value,
            "timestamp": datetime.now().isoformat()
        }))

        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Handle different message types
                await handle_websocket_message(session_id, message_data, websocket)

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error_message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error_message": f"Message handling error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
    finally:
        # Remove connection
        remove_websocket_connection(session_id, websocket)

async def handle_websocket_message(session_id: str, message_data: Dict[str, Any], websocket: WebSocket):
    """Handle incoming WebSocket message"""
    message_type = message_data.get("type")

    if message_type == "ping":
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))

    elif message_type == "get_status":
        if processing_service:
            status = processing_service.get_processing_status(session_id)
            await websocket.send_text(json.dumps({
                "type": "status_response",
                "data": status,
                "timestamp": datetime.now().isoformat()
            }))

    else:
        await websocket.send_text(json.dumps({
            "type": "unknown_message_type",
            "received_type": message_type,
            "timestamp": datetime.now().isoformat()
        }))

# === Error Handlers ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )
