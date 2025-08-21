"""
Session Manager untuk RAG Multi-Strategy System
===============================================

Mengelola session state, user interactions, dan alur processing
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from enum import Enum
import json

from ..schemas.api_schemas import (
    SessionStatusEnum, UserInputRequest, ValidationRequest,
    CPATPResponse, FinalInputResponse, ProcessingStatusResponse
)
from ..core.models import UserInput, ValidationResult, FinalInput
from ..utils.logger import get_logger

logger = get_logger("SessionManager")

class SessionState:
    """State object untuk menyimpan data session"""

    def __init__(self, session_id: str, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.status = SessionStatusEnum.CREATED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Data processing
        self.user_input: Optional[UserInput] = None
        self.task_analysis: Optional[Dict[str, Any]] = None
        self.cp_atp_result: Optional[CPATPResponse] = None
        self.validation_history: List[ValidationResult] = []
        self.final_input: Optional[FinalInput] = None

        # Processing metadata
        self.current_step = "initialized"
        self.progress_percentage = 0.0
        self.processing_start_time: Optional[datetime] = None
        self.estimated_completion_time: Optional[datetime] = None

        # Error handling
        self.error_count = 0
        self.last_error: Optional[str] = None

        # WebSocket connection
        self.websocket_connection = None

    def update_status(self, status: SessionStatusEnum, step: str = "", progress: float = 0.0):
        """Update session status"""
        self.status = status
        self.current_step = step
        self.progress_percentage = progress
        self.updated_at = datetime.now()

        logger.info(f"Session {self.session_id} status updated: {status.value} - {step}")

    def add_validation(self, validation: ValidationResult):
        """Add validation result to history"""
        self.validation_history.append(validation)
        self.updated_at = datetime.now()

    def is_expired(self, expiry_hours: int = 24) -> bool:
        """Check if session is expired"""
        expiry_time = self.created_at + timedelta(hours=expiry_hours)
        return datetime.now() > expiry_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert session state to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_step": self.current_step,
            "progress_percentage": self.progress_percentage,
            "validation_count": len(self.validation_history),
            "error_count": self.error_count,
            "has_user_input": self.user_input is not None,
            "has_cp_atp_result": self.cp_atp_result is not None,
            "has_final_input": self.final_input is not None
        }

class SessionManager:
    """
    Manager untuk mengelola session dan state management
    """

    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
        self.max_sessions_per_user = 5
        self.session_expiry_hours = 24

        # WebSocket broadcast callback
        self.websocket_broadcast_callback = None

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False

        logger.info("Session Manager initialized")

    def _start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        except RuntimeError:
            # No event loop running, will be started later
            pass

    async def initialize_async_components(self):
        """Initialize async components when event loop is available"""
        if not self._initialized:
            self._start_cleanup_task()
            self._initialized = True
            logger.info("Session Manager async components initialized")

    async def _cleanup_expired_sessions(self):
        """Background task untuk cleanup expired sessions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")

    async def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create new session

        Args:
            user_id: Optional user ID

        Returns:
            session_id: Generated session ID
        """
        # Generate unique session ID
        session_id = f"rag-{uuid.uuid4().hex[:12]}"

        # Check user session limit
        if user_id:
            user_session_count = len(self.user_sessions.get(user_id, []))
            if user_session_count >= self.max_sessions_per_user:
                # Remove oldest session
                oldest_session = self.user_sessions[user_id][0]
                await self.delete_session(oldest_session)

        # Create session state
        session_state = SessionState(session_id, user_id)
        self.sessions[session_id] = session_state

        # Track user sessions
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)

        logger.success(f"Session created: {session_id} for user: {user_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and session.is_expired(self.session_expiry_hours):
            logger.warning(f"Session {session_id} is expired")
            return None
        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        # Close WebSocket connection if exists
        if session.websocket_connection:
            try:
                await session.websocket_connection.close()
            except:
                pass

        # Remove from user sessions
        if session.user_id and session.user_id in self.user_sessions:
            if session_id in self.user_sessions[session.user_id]:
                self.user_sessions[session.user_id].remove(session_id)

            # Clean up empty user session list
            if not self.user_sessions[session.user_id]:
                del self.user_sessions[session.user_id]

        # Remove session
        del self.sessions[session_id]

        logger.info(f"Session deleted: {session_id}")
        return True

    def get_user_sessions(self, user_id: str) -> List[SessionState]:
        """Get all sessions for a user"""
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def get_active_sessions(self) -> List[SessionState]:
        """Get all active sessions"""
        active_statuses = [
            SessionStatusEnum.INPUT_COLLECTION,
            SessionStatusEnum.PROCESSING,
            SessionStatusEnum.CP_ATP_GENERATION,
            SessionStatusEnum.USER_VALIDATION,
            SessionStatusEnum.REFINEMENT
        ]

        return [
            session for session in self.sessions.values()
            if session.status in active_statuses and not session.is_expired()
        ]

    async def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired(self.session_expiry_hours)
        ]

        for session_id in expired_sessions:
            await self.delete_session(session_id)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    # === Session Data Management ===

    def set_user_input(self, session_id: str, user_input: UserInputRequest) -> bool:
        """Set user input untuk session"""
        session = self.get_session(session_id)
        if not session:
            return False

        # Convert API model to core model
        session.user_input = UserInput(
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

        session.update_status(SessionStatusEnum.INPUT_COLLECTION, "User input received", 10.0)

        logger.info(f"User input set for session {session_id}")
        return True

    def set_task_analysis(self, session_id: str, analysis: Dict[str, Any]) -> bool:
        """Set task analysis result"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.task_analysis = analysis
        session.update_status(SessionStatusEnum.PROCESSING, "Task analysis completed", 20.0)

        return True

    def set_cp_atp_result(self, session_id: str, cp_atp_result: CPATPResponse) -> bool:
        """Set CP/ATP generation result"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.cp_atp_result = cp_atp_result
        session.update_status(SessionStatusEnum.CP_ATP_GENERATION, "CP/ATP generated", 60.0)

        return True

    def add_validation_result(self, session_id: str, validation: ValidationRequest) -> bool:
        """Add validation result"""
        session = self.get_session(session_id)
        if not session:
            return False

        # Convert API model to core model
        validation_result = ValidationResult(
            is_approved=validation.is_approved,
            feedback=validation.feedback,
            requested_changes=validation.requested_changes
        )

        session.add_validation(validation_result)

        if validation.is_approved:
            session.update_status(SessionStatusEnum.USER_VALIDATION, "Validation approved", 80.0)
        else:
            session.update_status(SessionStatusEnum.REFINEMENT, "Refinement needed", 50.0)

        return True

    def set_final_input(self, session_id: str, final_input: FinalInput) -> bool:
        """Set final input result"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.final_input = final_input
        session.update_status(SessionStatusEnum.COMPLETED, "Processing completed", 100.0)

        logger.success(f"Final input set for session {session_id}")
        return True

    # === WebSocket Management ===

    def set_websocket_connection(self, session_id: str, websocket) -> bool:
        """Set WebSocket connection for session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.websocket_connection = websocket
        logger.info(f"WebSocket connection set for session {session_id}")
        return True

    def remove_websocket_connection(self, session_id: str) -> bool:
        """Remove WebSocket connection"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.websocket_connection = None
        logger.info(f"WebSocket connection removed for session {session_id}")
        return True

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Broadcast message to session's WebSocket connection"""
        session = self.get_session(session_id)
        if not session or not session.websocket_connection:
            return False

        try:
            await session.websocket_connection.send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Failed to send WebSocket message to session {session_id}: {str(e)}")
            # Remove broken connection
            session.websocket_connection = None
            return False

    def set_websocket_broadcast_callback(self, callback):
        """Set callback function for WebSocket broadcasting"""
        self.websocket_broadcast_callback = callback
        logger.info("WebSocket broadcast callback set")

    # === Status and Monitoring ===

    def get_processing_status(self, session_id: str) -> Optional[ProcessingStatusResponse]:
        """Get processing status for session"""
        session = self.get_session(session_id)
        if not session:
            return None

        # Calculate estimated remaining time
        estimated_remaining = None
        if session.processing_start_time and session.progress_percentage > 0:
            elapsed = datetime.now() - session.processing_start_time
            total_estimated = elapsed.total_seconds() / (session.progress_percentage / 100.0)
            remaining = total_estimated - elapsed.total_seconds()
            estimated_remaining = max(0, int(remaining))

        return ProcessingStatusResponse(
            session_id=session_id,
            status=session.status,
            current_step=session.current_step,
            progress_percentage=session.progress_percentage,
            estimated_remaining_time=estimated_remaining,
            last_updated=session.updated_at.isoformat()
        )

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total_sessions = len(self.sessions)
        active_sessions = len(self.get_active_sessions())
        completed_sessions = len([
            s for s in self.sessions.values()
            if s.status == SessionStatusEnum.COMPLETED
        ])
        error_sessions = len([
            s for s in self.sessions.values()
            if s.status == SessionStatusEnum.ERROR
        ])

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "error_sessions": error_sessions,
            "unique_users": len(self.user_sessions),
            "average_processing_time": self._calculate_average_processing_time(),
            "success_rate": self._calculate_success_rate()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics (alias for get_system_stats for compatibility)"""
        return self.get_system_stats()

    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[SessionState]:
        """List sessions with pagination"""
        session_list = list(self.sessions.values())
        # Sort by created_at descending (newest first)
        session_list.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        start = offset
        end = offset + limit
        return session_list[start:end]

    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time for completed sessions"""
        completed_sessions = [
            s for s in self.sessions.values()
            if s.status == SessionStatusEnum.COMPLETED and s.processing_start_time
        ]

        if not completed_sessions:
            return 0.0

        total_time = sum(
            (s.updated_at - s.processing_start_time).total_seconds()
            for s in completed_sessions
        )

        return total_time / len(completed_sessions)

    def _calculate_success_rate(self) -> float:
        """Calculate success rate"""
        if not self.sessions:
            return 0.0

        completed_count = len([
            s for s in self.sessions.values()
            if s.status == SessionStatusEnum.COMPLETED
        ])

        return (completed_count / len(self.sessions)) * 100.0

    async def shutdown(self):
        """Shutdown session manager"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all WebSocket connections
        for session in self.sessions.values():
            if session.websocket_connection:
                try:
                    await session.websocket_connection.close()
                except:
                    pass

        logger.info("Session Manager shutdown completed")

# Global session manager instance
_session_manager: Optional[SessionManager] = None

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
