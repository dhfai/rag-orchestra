"""
Real-time RAG Orchestra WebSocket Application
============================================

Aplikasi WebSocket untuk interaksi real-time dengan sistem Orchestrated RAG.
Mengimplementasikan komunikasi dinamis antara user dan sistem.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.core.models import UserInput, CompleteInput, LLMModel
from src.orchestrator.enhanced_main_orchestrator import get_enhanced_main_orchestrator
from src.utils.logger import get_logger

logger = get_logger("WebSocketApp")

# FastAPI app
app = FastAPI(
    title="RAG Orchestra Real-time API",
    description="Real-time Orchestrated RAG dengan WebSocket",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    """Manager untuk WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect WebSocket untuk session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_sessions[session_id] = {
            "connected_at": datetime.now().isoformat(),
            "status": "connected",
            "current_process": None
        }
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        """Disconnect WebSocket"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message ke specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {str(e)}")
                self.disconnect(session_id)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message ke semua connections"""
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)

# Global connection manager
manager = ConnectionManager()

# Global orchestrator
orchestrator = get_enhanced_main_orchestrator()

# Request/Response models
class ProcessingRequest(BaseModel):
    """Request untuk memulai processing"""
    nama_guru: str
    nama_sekolah: str
    mata_pelajaran: str
    kelas: str
    fase: str
    topik: str
    sub_topik: str
    alokasi_waktu: str
    llm_model_choice: str = "gemini"
    cp: Optional[str] = None
    atp: Optional[str] = None

class SessionStatus(BaseModel):
    """Status session"""
    session_id: str
    status: str
    current_process: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None

# WebSocket message handler
async def handle_websocket_message(websocket: WebSocket, session_id: str, message: Dict[str, Any]):
    """Handle incoming WebSocket messages"""
    try:
        message_type = message.get("type", "")
        data = message.get("data", {})

        if message_type == "start_processing":
            await start_processing(websocket, session_id, data)
        elif message_type == "ping":
            await send_websocket_response(websocket, "pong", {"timestamp": datetime.now().isoformat()})
        elif message_type == "get_status":
            await send_session_status(websocket, session_id)
        elif message_type == "cancel_processing":
            await cancel_processing(websocket, session_id)
        elif message_type == "approve_validation":
            await approve_validation(websocket, session_id, data)
        elif message_type == "regenerate_content":
            await regenerate_content(websocket, session_id, data)
        elif message_type == "cancel_validation":
            await cancel_validation(websocket, session_id)
        else:
            await send_websocket_response(websocket, "error", {"message": f"Unknown message type: {message_type}"})

    except Exception as e:
        logger.error(f"Error handling WebSocket message: {str(e)}")
        await send_websocket_response(websocket, "error", {"message": str(e)})

async def start_processing(websocket: WebSocket, session_id: str, data: Dict[str, Any]):
    """Start processing dengan real-time updates"""
    try:
        # Validate input data
        processing_request = ProcessingRequest(**data)

        # Update session status
        manager.user_sessions[session_id]["current_process"] = "orchestrated_rag"
        manager.user_sessions[session_id]["status"] = "processing"

        # Send acknowledgment as system log
        await send_system_log(websocket, "processing_started",
                             "Orchestrated RAG processing started",
                             {"session_id": session_id})

        # Convert to UserInput
        # Map string to LLMModel enum
        llm_model_mapping = {
            "gemini-1.5-flash": LLMModel.GEMINI_1_5_FLASH,
            "gemini-1.5-pro": LLMModel.GEMINI_1_5_PRO,
            "gpt-4": LLMModel.GPT_4,
            "gpt-3.5-turbo": LLMModel.GPT_3_5_TURBO,
            # Legacy support
            "gemini": LLMModel.GEMINI_1_5_FLASH,
            "openai": LLMModel.GPT_3_5_TURBO
        }

        model_llm = llm_model_mapping.get(
            processing_request.llm_model_choice,
            LLMModel.GEMINI_1_5_FLASH
        )

        user_input = UserInput(
            nama_guru=processing_request.nama_guru,
            nama_sekolah=processing_request.nama_sekolah,
            mata_pelajaran=processing_request.mata_pelajaran,
            topik=processing_request.topik,
            sub_topik=processing_request.sub_topik,
            kelas=processing_request.kelas,
            fase=processing_request.fase,
            alokasi_waktu=processing_request.alokasi_waktu,
            model_llm=model_llm,
            cp=processing_request.cp,
            atp=processing_request.atp
        )

        # Store original input for potential regeneration
        manager.user_sessions[session_id]["original_input"] = data

        # Create callback untuk real-time updates dengan separation
        async def websocket_callback(event_type: str, event_data: Dict[str, Any]):
            # Determine if this is a system log or content result
            system_log_types = [
                "task_analysis_start", "task_analysis_complete",
                "strategy_selection_start", "strategy_selection_complete",
                "orchestration_decision", "input_analysis",
                "searching_documents", "searching_online",
                "generating_cp_atp", "generating_cp", "generating_atp",
                "quality_monitoring", "re_routing", "adaptive_rag"
            ]

            content_result_types = [
                "complete_input_ready", "cp_generated", "atp_generated",
                "final_result"
            ]

            # Special handling for CP/ATP generation completion
            if event_type == "complete_input_ready" and event_data.get("complete_input"):
                complete_input = event_data["complete_input"]

                # Check if CP/ATP was generated (not provided by user)
                has_generated_content = (
                    not processing_request.cp or not processing_request.atp
                )

                if has_generated_content:
                    # Trigger validation modal
                    await send_content_result(websocket, "cp_atp_generated", {
                        "requires_validation": True,
                        "generated_cp": complete_input.get("cp", ""),
                        "generated_atp": complete_input.get("atp", ""),
                        "session_id": session_id,
                        "message": "CP/ATP generated, awaiting user validation"
                    }, stage="validation")

                    # Store generated content for validation
                    manager.user_sessions[session_id]["generated_cp"] = complete_input.get("cp", "")
                    manager.user_sessions[session_id]["generated_atp"] = complete_input.get("atp", "")
                    manager.user_sessions[session_id]["status"] = "awaiting_validation"

                    return  # Don't continue processing until validation
                else:
                    # User provided CP/ATP, continue with final result
                    await send_content_result(websocket, event_type, event_data, stage="generation")

            if event_type in system_log_types:
                # Send as system log
                message = event_data.get("message", f"{event_type} event")
                metadata = {k: v for k, v in event_data.items() if k != "message"}
                await send_system_log(websocket, event_type, message, metadata)
            elif event_type in content_result_types:
                # Send as content result
                await send_content_result(websocket, event_type, event_data, stage="generation")
            else:
                # Fallback to original method for unknown types
                await send_websocket_response(websocket, event_type, event_data)

        # Process dengan orchestrator
        complete_input = await orchestrator.orchestrate_complete_input(
            user_input=user_input,
            callback_func=websocket_callback
        )

        # Send final result as content
        await send_content_result(websocket, "final_complete_input", {
            "complete_input": complete_input.to_json_standard(),
            "processing_summary": {
                "total_time": "calculated_time",
                "quality_score": "final_quality",
                "status": "completed"
            }
        }, stage="final")

        # Update session status
        manager.user_sessions[session_id]["current_process"] = None
        manager.user_sessions[session_id]["status"] = "completed"

    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")
        await send_system_log(websocket, "processing_error",
                             f"Processing failed: {str(e)}",
                             {"error_type": type(e).__name__, "session_id": session_id})

        # Update session status
        manager.user_sessions[session_id]["current_process"] = None
        manager.user_sessions[session_id]["status"] = "error"

async def cancel_processing(websocket: WebSocket, session_id: str):
    """Cancel ongoing processing"""
    if session_id in manager.user_sessions:
        manager.user_sessions[session_id]["current_process"] = None
        manager.user_sessions[session_id]["status"] = "cancelled"

    await send_websocket_response(websocket, "processing_cancelled", {
        "message": "Processing cancelled by user"
    })

async def approve_validation(websocket: WebSocket, session_id: str, data: Dict[str, Any]):
    """Approve validated CP/ATP and continue processing"""
    try:
        validated_cp = data.get("validated_cp", "")
        validated_atp = data.get("validated_atp", "")

        # Store validated content in session
        if session_id in manager.user_sessions:
            manager.user_sessions[session_id]["validated_cp"] = validated_cp
            manager.user_sessions[session_id]["validated_atp"] = validated_atp
            manager.user_sessions[session_id]["validation_status"] = "approved"

        await send_system_log(websocket, "validation_approved",
                             "User approved CP/ATP content",
                             {"session_id": session_id})

        # Continue with final Complete Input generation
        await generate_final_complete_input(websocket, session_id)

    except Exception as e:
        logger.error(f"Error in approve_validation: {str(e)}")
        await send_system_log(websocket, "validation_error",
                             f"Error approving validation: {str(e)}",
                             {"session_id": session_id})

async def regenerate_content(websocket: WebSocket, session_id: str, data: Dict[str, Any]):
    """Regenerate CP/ATP content"""
    try:
        await send_system_log(websocket, "regenerating_content",
                             "Regenerating CP/ATP content",
                             {"session_id": session_id})

        # Get original input from session
        if session_id in manager.user_sessions:
            original_input = manager.user_sessions[session_id].get("original_input")
            if original_input:
                # Restart CP/ATP generation process
                await start_processing(websocket, session_id, original_input)
            else:
                await send_system_log(websocket, "regeneration_error",
                                     "Original input not found",
                                     {"session_id": session_id})

    except Exception as e:
        logger.error(f"Error in regenerate_content: {str(e)}")
        await send_system_log(websocket, "regeneration_error",
                             f"Error regenerating content: {str(e)}",
                             {"session_id": session_id})

async def cancel_validation(websocket: WebSocket, session_id: str):
    """Cancel validation process"""
    try:
        if session_id in manager.user_sessions:
            manager.user_sessions[session_id]["validation_status"] = "cancelled"
            manager.user_sessions[session_id]["status"] = "cancelled"

        await send_system_log(websocket, "validation_cancelled",
                             "User cancelled validation process",
                             {"session_id": session_id})

    except Exception as e:
        logger.error(f"Error in cancel_validation: {str(e)}")
        await send_system_log(websocket, "validation_error",
                             f"Error cancelling validation: {str(e)}",
                             {"session_id": session_id})

async def generate_final_complete_input(websocket: WebSocket, session_id: str):
    """Generate final Complete Input with validated CP/ATP"""
    try:
        if session_id not in manager.user_sessions:
            return

        session_data = manager.user_sessions[session_id]
        validated_cp = session_data.get("validated_cp", "")
        validated_atp = session_data.get("validated_atp", "")
        original_input = session_data.get("original_input", {})

        # Create Complete Input with validated content
        complete_input = {
            "basic_info": {
                "nama_guru": original_input.get("nama_guru", ""),
                "nama_sekolah": original_input.get("nama_sekolah", ""),
                "mata_pelajaran": original_input.get("mata_pelajaran", ""),
                "kelas": original_input.get("kelas", ""),
                "fase": original_input.get("fase", ""),
                "topik": original_input.get("topik", ""),
                "sub_topik": original_input.get("sub_topik", ""),
                "alokasi_waktu": original_input.get("alokasi_waktu", "")
            },
            "curriculum_content": {
                "cp": validated_cp,
                "atp": validated_atp
            },
            "technical_info": {
                "llm_model": original_input.get("llm_model_choice", "gemini-1.5-flash"),
                "timestamp": datetime.now().isoformat(),
                "status": "complete"
            },
            "metadata": {
                "completeness_status": "user_validated",
                "validation_approved": True,
                "model_used": original_input.get("llm_model_choice", "gemini-1.5-flash")
            }
        }

        # Send final result
        await send_content_result(websocket, "final_complete_input", {
            "complete_input": complete_input,
            "processing_summary": {
                "status": "completed_with_validation",
                "validation_method": "user_approved"
            }
        }, stage="final")

        # Update session status
        manager.user_sessions[session_id]["status"] = "completed"

    except Exception as e:
        logger.error(f"Error generating final Complete Input: {str(e)}")
        await send_system_log(websocket, "final_generation_error",
                             f"Error generating final Complete Input: {str(e)}",
                             {"session_id": session_id})

async def send_session_status(websocket: WebSocket, session_id: str):
    """Send current session status"""
    if session_id in manager.user_sessions:
        status_data = manager.user_sessions[session_id]
    else:
        status_data = {"status": "not_found"}

    await send_websocket_response(websocket, "session_status", status_data)

async def send_websocket_response(websocket: WebSocket, response_type: str, data: Dict[str, Any]):
    """Send formatted response via WebSocket"""
    response = {
        "type": response_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

    try:
        # Custom JSON serialization to handle enums
        def json_serializer(obj):
            if hasattr(obj, 'value'):  # Enum objects
                return obj.value
            if hasattr(obj, '__dict__'):  # Complex objects
                return obj.__dict__
            return str(obj)

        await websocket.send_text(json.dumps(response, default=json_serializer))
    except Exception as e:
        logger.error(f"Failed to send WebSocket response: {str(e)}")

async def send_system_log(websocket: WebSocket, log_type: str, message: str, metadata: Dict[str, Any] = None):
    """Send system log message via WebSocket"""
    response = {
        "category": "system_log",
        "type": log_type,
        "message": message,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }

    try:
        def json_serializer(obj):
            if hasattr(obj, 'value'):
                return obj.value
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)

        await websocket.send_text(json.dumps(response, default=json_serializer))
    except Exception as e:
        logger.error(f"Failed to send system log: {str(e)}")

async def send_content_result(websocket: WebSocket, result_type: str, content: Dict[str, Any], stage: str = None):
    """Send content generation result via WebSocket"""
    response = {
        "category": "content_result",
        "type": result_type,
        "stage": stage,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }

    try:
        def json_serializer(obj):
            if hasattr(obj, 'value'):
                return obj.value
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)

        await websocket.send_text(json.dumps(response, default=json_serializer))
    except Exception as e:
        logger.error(f"Failed to send content result: {str(e)}")

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Main WebSocket endpoint untuk real-time interaction"""
    await manager.connect(websocket, session_id)

    try:
        # Send welcome message
        await send_websocket_response(websocket, "connected", {
            "session_id": session_id,
            "message": "Connected to RAG Orchestra Real-time API",
            "available_commands": [
                "start_processing",
                "get_status",
                "cancel_processing",
                "ping"
            ]
        })

        # Message handling loop
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, session_id, message)
            except json.JSONDecodeError:
                await send_websocket_response(websocket, "error", {
                    "message": "Invalid JSON format"
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {str(e)}")
        manager.disconnect(session_id)

# REST API endpoints for monitoring
@app.get("/")
async def root():
    """Root endpoint dengan informasi API"""
    return {
        "name": "RAG Orchestra Real-time API",
        "version": "2.0.0",
        "description": "Real-time Orchestrated RAG dengan WebSocket",
        "websocket_endpoint": "/ws/{session_id}",
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test orchestrator
        health_status = {
            "status": "healthy",
            "services": {
                "orchestrator": "available",
                "websocket_manager": "available",
                "active_connections": len(manager.active_connections)
            },
            "timestamp": datetime.now().isoformat()
        }

        return health_status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/sessions")
async def get_active_sessions():
    """Get information tentang active sessions"""
    sessions_info = []

    for session_id, session_data in manager.user_sessions.items():
        sessions_info.append({
            "session_id": session_id,
            "status": session_data.get("status", "unknown"),
            "connected_at": session_data.get("connected_at", ""),
            "current_process": session_data.get("current_process"),
            "has_websocket": session_id in manager.active_connections
        })

    return {
        "total_sessions": len(sessions_info),
        "sessions": sessions_info
    }

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information tentang specific session"""
    if session_id not in manager.user_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = manager.user_sessions[session_id]
    session_data["has_websocket"] = session_id in manager.active_connections

    return session_data

# HTML client untuk testing (optional)
@app.get("/client", response_class=HTMLResponse)
async def websocket_client():
    """Simple HTML client untuk testing WebSocket"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>RAG Orchestra WebSocket Client</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .messages {
            height: 400px;
            border: 1px solid #ccc;
            padding: 10px;
            overflow-y: scroll;
            background-color: #f9f9f9;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .input-group { margin-bottom: 10px; }
        .input-group label { display: block; margin-bottom: 5px; }
        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 5px;
            box-sizing: border-box;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            cursor: pointer;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .status.connected { background-color: #d4edda; color: #155724; }
        .status.disconnected { background-color: #f8d7da; color: #721c24; }

        /* System Log Styling */
        .error { color: #dc3545; font-weight: bold; }
        .success { color: #28a745; font-weight: bold; }
        .info { color: #007bff; font-weight: bold; }
        .default { color: #6c757d; font-weight: bold; }

        /* Content Result Styling */
        .content-result {
            color: #fd7e14;
            font-weight: bold;
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }

        /* Modal Styling */
        .modal {
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 800px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .modal-buttons {
            text-align: center;
            margin-top: 20px;
        }
        .modal-buttons button {
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>RAG Orchestra WebSocket Client</h1>

        <div id="status" class="status disconnected">Disconnected</div>

        <div class="messages" id="messages"></div>

        <div class="input-group">
            <label>Session ID:</label>
            <input type="text" id="sessionId" placeholder="Enter session ID (auto-generated if empty)">
        </div>

        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
        <button onclick="ping()">Ping</button>

        <h3>Start Processing</h3>

        <div class="input-group">
            <label>Nama Guru:</label>
            <input type="text" id="namaGuru" value="Budi Santoso">
        </div>

        <div class="input-group">
            <label>Nama Sekolah:</label>
            <input type="text" id="namaSekolah" value="SDN 1 Jakarta">
        </div>

        <div class="input-group">
            <label>Mata Pelajaran:</label>
            <select id="mataPelajaran">
                <option>Matematika</option>
                <option>Bahasa Indonesia</option>
                <option>IPA</option>
                <option>IPS</option>
                <option>Bahasa Inggris</option>
            </select>
        </div>

        <div class="input-group">
            <label>Kelas:</label>
            <select id="kelas">
                <option>1</option>
                <option>2</option>
                <option>3</option>
                <option>4</option>
                <option>5</option>
                <option>6</option>
            </select>
        </div>

        <div class="input-group">
            <label>Fase:</label>
            <select id="fase">
                <option>A</option>
                <option>B</option>
                <option>C</option>
            </select>
        </div>

        <div class="input-group">
            <label>Topik:</label>
            <input type="text" id="topik" value="Penjumlahan">
        </div>

        <div class="input-group">
            <label>Sub Topik:</label>
            <input type="text" id="subTopik" value="Penjumlahan bilangan 1-10">
        </div>

        <div class="input-group">
            <label>Alokasi Waktu:</label>
            <input type="text" id="alokasiWaktu" value="2 x 35 menit">
        </div>

        <div class="input-group">
            <label>LLM Model:</label>
            <select id="llmModel">
                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
        </div>

        <h4>Optional: Capaian Pembelajaran & Alur Tujuan Pembelajaran</h4>
        <p><em>Kosongkan jika ingin sistem generate otomatis</em></p>

        <div class="input-group">
            <label>CP (Capaian Pembelajaran):</label>
            <textarea id="cp" rows="4" placeholder="Masukkan CP jika sudah ada, atau kosongkan untuk auto-generate"></textarea>
        </div>

        <div class="input-group">
            <label>ATP (Alur Tujuan Pembelajaran):</label>
            <textarea id="atp" rows="4" placeholder="Masukkan ATP jika sudah ada, atau kosongkan untuk auto-generate"></textarea>
        </div>

        <button onclick="startProcessing()">Start Processing</button>
        <button onclick="cancelProcessing()">Cancel Processing</button>
        <button onclick="getStatus()">Get Status</button>

        <!-- Validation Modal -->
        <div id="validationModal" class="modal" style="display: none;">
            <div class="modal-content">
                <h3>Validasi CP/ATP yang Dihasilkan</h3>
                <p>Sistem telah menghasilkan CP dan ATP. Silakan review dan edit jika diperlukan:</p>

                <div class="input-group">
                    <label>CP (Capaian Pembelajaran):</label>
                    <textarea id="validationCP" rows="6"></textarea>
                </div>

                <div class="input-group">
                    <label>ATP (Alur Tujuan Pembelajaran):</label>
                    <textarea id="validationATP" rows="6"></textarea>
                </div>

                <div class="modal-buttons">
                    <button onclick="approveValidation()">Approve & Continue</button>
                    <button onclick="regenerateContent()">Regenerate</button>
                    <button onclick="cancelValidation()">Cancel</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let sessionId = null;

        function log(message) {
            const messages = document.getElementById('messages');
            const timestamp = new Date().toLocaleTimeString();
            messages.innerHTML += `[${timestamp}] ${message}\\n`;
            messages.scrollTop = messages.scrollHeight;
        }

        function updateStatus(connected) {
            const statusEl = document.getElementById('status');
            if (connected) {
                statusEl.textContent = `Connected (Session: ${sessionId})`;
                statusEl.className = 'status connected';
            } else {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'status disconnected';
            }
        }

        function connect() {
            sessionId = document.getElementById('sessionId').value ||
                       'session_' + Math.random().toString(36).substr(2, 9);

            const wsUrl = `ws://localhost:8000/ws/${sessionId}`;
            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                log('WebSocket connected');
                updateStatus(true);
            };

            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);

                // Handle different message categories
                if (message.category === 'system_log') {
                    logSystemMessage(message);
                } else if (message.category === 'content_result') {
                    logContentResult(message);
                } else {
                    // Legacy support for old format
                    log(`Received: ${message.type} - ${JSON.stringify(message.data, null, 2)}`);
                }
            };

        function logSystemMessage(message) {
            const messages = document.getElementById('messages');
            const timestamp = new Date(message.timestamp).toLocaleTimeString();
            const logClass = getLogClass(message.type);

            messages.innerHTML += `[${timestamp}] <span class="${logClass}">SYSTEM</span> ${message.message}\\n`;

            if (Object.keys(message.metadata).length > 0) {
                messages.innerHTML += `    └─ Metadata: ${JSON.stringify(message.metadata, null, 2)}\\n`;
            }

            messages.scrollTop = messages.scrollHeight;
        }

        function logContentResult(message) {
            const messages = document.getElementById('messages');
            const timestamp = new Date(message.timestamp).toLocaleTimeString();

            messages.innerHTML += `[${timestamp}] <span class="content-result">CONTENT</span> ${message.type}\\n`;

            if (message.stage) {
                messages.innerHTML += `    └─ Stage: ${message.stage}\\n`;
            }

            // Check if this requires validation
            if (message.type === 'cp_atp_generated' && message.content.requires_validation) {
                showValidationModal(
                    message.content.generated_cp,
                    message.content.generated_atp,
                    message.content.session_id
                );
                messages.innerHTML += `    └─ ⚠️ User validation required\\n`;
            } else {
                // Format content nicely for other types
                if (message.content) {
                    const contentStr = JSON.stringify(message.content, null, 2);
                    const truncated = contentStr.length > 500 ?
                        contentStr.substring(0, 500) + '...' : contentStr;
                    messages.innerHTML += `    └─ Content: ${truncated}\\n`;
                }
            }

            messages.scrollTop = messages.scrollHeight;
        }

        function getLogClass(type) {
            if (type.includes('error')) return 'error';
            if (type.includes('complete')) return 'success';
            if (type.includes('start')) return 'info';
            return 'default';
        }

            ws.onclose = function() {
                log('WebSocket disconnected');
                updateStatus(false);
            };

            ws.onerror = function(error) {
                log(`WebSocket error: ${error}`);
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
            }
        }

        function ping() {
            if (ws) {
                ws.send(JSON.stringify({
                    type: 'ping',
                    data: {}
                }));
            }
        }

        function startProcessing() {
            if (!ws) {
                alert('Please connect first');
                return;
            }

            const data = {
                nama_guru: document.getElementById('namaGuru').value,
                nama_sekolah: document.getElementById('namaSekolah').value,
                mata_pelajaran: document.getElementById('mataPelajaran').value,
                kelas: document.getElementById('kelas').value,
                fase: document.getElementById('fase').value,
                topik: document.getElementById('topik').value,
                sub_topik: document.getElementById('subTopik').value,
                alokasi_waktu: document.getElementById('alokasiWaktu').value,
                llm_model_choice: document.getElementById('llmModel').value,
                cp: document.getElementById('cp').value || null,
                atp: document.getElementById('atp').value || null
            };

            ws.send(JSON.stringify({
                type: 'start_processing',
                data: data
            }));
        }

        function cancelProcessing() {
            if (ws) {
                ws.send(JSON.stringify({
                    type: 'cancel_processing',
                    data: {}
                }));
            }
        }

        function getStatus() {
            if (ws) {
                ws.send(JSON.stringify({
                    type: 'get_status',
                    data: {}
                }));
            }
        }

        // Global variables for validation
        let pendingValidation = null;
        let currentSessionForValidation = null;

        // Show validation modal when CP/ATP generation is complete
        function showValidationModal(cpContent, atpContent, sessionId) {
            pendingValidation = { cp: cpContent, atp: atpContent };
            currentSessionForValidation = sessionId;

            document.getElementById('validationCP').value = cpContent;
            document.getElementById('validationATP').value = atpContent;
            document.getElementById('validationModal').style.display = 'block';
        }

        // Approve validation and continue processing
        function approveValidation() {
            if (!ws || !currentSessionForValidation) return;

            const validatedCP = document.getElementById('validationCP').value;
            const validatedATP = document.getElementById('validationATP').value;

            ws.send(JSON.stringify({
                type: 'approve_validation',
                data: {
                    session_id: currentSessionForValidation,
                    validated_cp: validatedCP,
                    validated_atp: validatedATP
                }
            }));

            closeValidationModal();
        }

        // Request regeneration of CP/ATP
        function regenerateContent() {
            if (!ws || !currentSessionForValidation) return;

            ws.send(JSON.stringify({
                type: 'regenerate_content',
                data: {
                    session_id: currentSessionForValidation
                }
            }));

            closeValidationModal();
        }

        // Cancel validation process
        function cancelValidation() {
            if (!ws || !currentSessionForValidation) return;

            ws.send(JSON.stringify({
                type: 'cancel_validation',
                data: {
                    session_id: currentSessionForValidation
                }
            }));

            closeValidationModal();
        }

        // Close validation modal
        function closeValidationModal() {
            document.getElementById('validationModal').style.display = 'none';
            pendingValidation = null;
            currentSessionForValidation = null;
        }

        // Update message handling to trigger validation
        function handleValidationTrigger(message) {
            if (message.type === 'cp_atp_generated' && message.data.requires_validation) {
                showValidationModal(
                    message.data.generated_cp,
                    message.data.generated_atp,
                    message.data.session_id
                );
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting RAG Orchestra Real-time WebSocket API...")

    uvicorn.run(
        "main_websocket_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
