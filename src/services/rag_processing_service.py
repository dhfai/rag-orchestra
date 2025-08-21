"""
RAG Processing Service
=====================

Service untuk mengintegrasikan orchestrator dengan backend API
Menangani alur processing dari user input hingga final result
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from ..orchestrator.main_orchestrator import MainOrchestrator
from ..orchestrator.cp_atp_orchestrator import CPATPOrchestrator
from ..core.models import UserInput, ValidationResult, FinalInput
from ..schemas.api_schemas import (
    UserInputRequest, ValidationRequest, CPATPResponse,
    FinalInputResponse, TaskAnalysisResponse, RAGStrategyEnum
)
from ..services.session_manager import SessionManager, SessionState, SessionStatusEnum
from ..utils.logger import get_logger

logger = get_logger("RAGProcessingService")

class RAGProcessingService:
    """
    Service untuk mengelola alur processing RAG Multi-Strategy
    """

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.main_orchestrator = MainOrchestrator()
        self.cp_atp_orchestrator = CPATPOrchestrator()

        # Processing queues and limits
        self.max_concurrent_processing = 5
        self.current_processing: Dict[str, asyncio.Task] = {}

        logger.info("RAG Processing Service initialized")

    async def start_processing(self, session_id: str) -> bool:
        """
        Start processing untuk session

        Args:
            session_id: ID session untuk diproses

        Returns:
            bool: True jika processing dimulai, False jika gagal
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False

        if not session.user_input:
            logger.error(f"No user input for session: {session_id}")
            return False

        # Check concurrent processing limit
        if len(self.current_processing) >= self.max_concurrent_processing:
            logger.warning(f"Max concurrent processing reached, queuing session: {session_id}")
            session.update_status(SessionStatusEnum.PROCESSING, "Queued for processing", 5.0)
            return await self._queue_processing(session_id)

        # Start processing task
        task = asyncio.create_task(self._process_session(session_id))
        self.current_processing[session_id] = task

        logger.info(f"Processing started for session: {session_id}")
        return True

    async def _queue_processing(self, session_id: str) -> bool:
        """Queue processing untuk session (untuk future implementation)"""
        # Untuk saat ini, langsung return True
        # Implementasi queue bisa ditambahkan dengan Redis atau sistem queue lainnya
        return True

    async def _process_session(self, session_id: str):
        """
        Main processing function untuk session
        Mengikuti alur flowchart yang sudah didefinisikan
        """
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                logger.error(f"Session not found during processing: {session_id}")
                return

            session.processing_start_time = datetime.now()
            session.update_status(SessionStatusEnum.PROCESSING, "Starting task analysis", 10.0)

            # Step 1: Task Analysis & Strategy Selection
            await self._send_websocket_update(session_id, "status_update", {
                "message": "Menganalisis kompleksitas tugas...",
                "step": "task_analysis"
            })

            task_analysis = await self._perform_task_analysis(session)
            self.session_manager.set_task_analysis(session_id, task_analysis)

            # Step 2: Check if CP/ATP generation needed
            if session.user_input.has_cp_atp():
                logger.info(f"CP/ATP already provided for session: {session_id}")
                await self._process_with_existing_cp_atp(session_id)
            else:
                logger.info(f"CP/ATP generation needed for session: {session_id}")
                await self._process_with_cp_atp_generation(session_id)

        except Exception as e:
            logger.error(f"Error processing session {session_id}: {str(e)}")
            await self._handle_processing_error(session_id, str(e))
        finally:
            # Remove from current processing
            if session_id in self.current_processing:
                del self.current_processing[session_id]

    async def _perform_task_analysis(self, session: SessionState) -> Dict[str, Any]:
        """Perform task analysis menggunakan main orchestrator"""

        # Simulate task analysis process
        await asyncio.sleep(1)  # Simulate processing time

        analysis_result = await self.main_orchestrator._analyze_task(session.user_input)

        # Convert to dict for API response
        task_analysis = {
            "complexity_level": analysis_result.complexity_level,
            "missing_components": analysis_result.missing_components,
            "required_rag_strategy": analysis_result.required_rag_strategy.value,
            "estimated_processing_time": analysis_result.estimated_processing_time,
            "confidence_score": analysis_result.confidence_score
        }

        logger.info(f"Task analysis completed: {task_analysis['complexity_level']} complexity")
        return task_analysis

    async def _process_with_existing_cp_atp(self, session_id: str):
        """Process session yang sudah memiliki CP/ATP"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return

        session.update_status(SessionStatusEnum.PROCESSING, "Processing with existing CP/ATP", 60.0)

        # Create final input directly
        await self._create_final_input(session_id)

    async def _process_with_cp_atp_generation(self, session_id: str):
        """Process session yang memerlukan CP/ATP generation"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return

        session.update_status(SessionStatusEnum.CP_ATP_GENERATION, "Generating CP/ATP", 30.0)

        # Generate CP/ATP
        await self._send_websocket_update(session_id, "status_update", {
            "message": "Memulai generasi CP dan ATP...",
            "step": "cp_atp_generation"
        })

        cp_atp_result = await self._generate_cp_atp(session)

        # Send CP/ATP to user for validation
        await self._send_cp_atp_for_validation(session_id, cp_atp_result)

        # Wait for user validation (akan ditangani via WebSocket/API endpoint)
        session.update_status(SessionStatusEnum.USER_VALIDATION, "Waiting for user validation", 65.0)

    async def _generate_cp_atp(self, session: SessionState) -> CPATPResponse:
        """Generate CP/ATP menggunakan orchestrator"""

        if not session.task_analysis:
            raise Exception("Task analysis not completed")

        # Get strategy from task analysis
        strategy_name = session.task_analysis["required_rag_strategy"]
        strategy_enum = RAGStrategyEnum(strategy_name)

        # Convert RAGStrategyEnum to RAGStrategy for orchestrator
        from ..core.models import RAGStrategy
        if strategy_enum == RAGStrategyEnum.SIMPLE:
            strategy = RAGStrategy.SIMPLE
        elif strategy_enum == RAGStrategyEnum.ADVANCED:
            strategy = RAGStrategy.ADVANCED
        elif strategy_enum == RAGStrategyEnum.GRAPH:
            strategy = RAGStrategy.GRAPH
        else:
            raise ValueError(f"Unknown strategy: {strategy_enum}")

        # Generate using CP/ATP orchestrator
        cp_atp_result = await self.cp_atp_orchestrator.generate_cp_atp(
            session.user_input,
            strategy
        )

        # Convert to API response format
        response = CPATPResponse(
            cp_content=cp_atp_result.cp_content,
            atp_content=cp_atp_result.atp_content,
            generation_strategy=cp_atp_result.generation_strategy,
            confidence_score=cp_atp_result.confidence_score,
            sources_used=cp_atp_result.sources_used,
            generation_metadata={
                "strategy_used": strategy.value,
                "processing_time": datetime.now().isoformat(),
                "session_id": session.session_id
            }
        )

        logger.success(f"CP/ATP generated for session: {session.session_id}")
        return response

    async def _send_cp_atp_for_validation(self, session_id: str, cp_atp_result: CPATPResponse):
        """Send CP/ATP result ke user untuk validasi"""

        # Store CP/ATP result in session
        self.session_manager.set_cp_atp_result(session_id, cp_atp_result)

        # Send via WebSocket
        await self._send_websocket_update(session_id, "cp_atp_generated", {
            "cp_content": cp_atp_result.cp_content,
            "atp_content": cp_atp_result.atp_content,
            "confidence_score": cp_atp_result.confidence_score,
            "sources_used": cp_atp_result.sources_used,
            "message": "CP dan ATP telah dihasilkan. Silakan review dan berikan validasi."
        })

    async def handle_user_validation(self, session_id: str, validation: ValidationRequest) -> bool:
        """
        Handle user validation untuk CP/ATP

        Args:
            session_id: ID session
            validation: Validation request dari user

        Returns:
            bool: True jika berhasil diproses
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False

        # Add validation to session
        self.session_manager.add_validation_result(session_id, validation)

        if validation.is_approved:
            logger.info(f"CP/ATP approved for session: {session_id}")
            await self._send_websocket_update(session_id, "status_update", {
                "message": "CP/ATP disetujui. Membuat final input...",
                "step": "creating_final_input"
            })

            # Create final input
            await self._create_final_input(session_id)
        else:
            logger.info(f"CP/ATP rejected for session: {session_id}, starting refinement")
            await self._send_websocket_update(session_id, "status_update", {
                "message": "Memproses feedback dan melakukan perbaikan...",
                "step": "refinement"
            })

            # Start refinement process
            await self._start_refinement_process(session_id, validation)

        return True

    async def _start_refinement_process(self, session_id: str, validation: ValidationRequest):
        """Start refinement process berdasarkan user feedback"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return

        session.update_status(SessionStatusEnum.REFINEMENT, "Processing refinement", 45.0)

        try:
            # Get original CP/ATP result
            original_result = session.cp_atp_result
            if not original_result:
                raise Exception("No original CP/ATP result found")

            # Perform refinement
            refined_result = await self._refine_cp_atp(session, validation, original_result)

            # Send refined result for validation
            await self._send_cp_atp_for_validation(session_id, refined_result)

        except Exception as e:
            logger.error(f"Error in refinement process: {str(e)}")
            await self._handle_processing_error(session_id, f"Refinement error: {str(e)}")

    async def _refine_cp_atp(
        self,
        session: SessionState,
        validation: ValidationRequest,
        original_result: CPATPResponse
    ) -> CPATPResponse:
        """Refine CP/ATP based on user feedback"""

        feedback = validation.feedback or ""

        # Use CP/ATP orchestrator for refinement
        # Convert back to core model format for orchestrator
        from ..core.models import CPATPResult, RAGStrategy

        original_core_result = CPATPResult(
            cp_content=original_result.cp_content,
            atp_content=original_result.atp_content,
            generation_strategy=RAGStrategy(original_result.generation_strategy),
            confidence_score=original_result.confidence_score,
            sources_used=original_result.sources_used
        )

        # Perform refinement
        refined_result = await self.cp_atp_orchestrator.refine_cp_atp(
            original_core_result,
            feedback,
            session.user_input
        )

        # Convert back to API response format
        refined_response = CPATPResponse(
            cp_content=refined_result.cp_content,
            atp_content=refined_result.atp_content,
            generation_strategy=refined_result.generation_strategy,
            confidence_score=refined_result.confidence_score,
            sources_used=refined_result.sources_used,
            generation_metadata={
                "strategy_used": refined_result.generation_strategy.value,
                "refinement_iteration": len(session.validation_history),
                "processing_time": datetime.now().isoformat(),
                "session_id": session.session_id
            }
        )

        logger.success(f"CP/ATP refined for session: {session.session_id}")
        return refined_response

    async def _create_final_input(self, session_id: str):
        """Create final input untuk session"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return

        session.update_status(SessionStatusEnum.PROCESSING, "Creating final input", 90.0)

        try:
            # Get CP/ATP content
            if session.cp_atp_result:
                cp_content = session.cp_atp_result.cp_content
                atp_content = session.cp_atp_result.atp_content
            else:
                # Use provided CP/ATP
                cp_content = session.user_input.cp or ""
                atp_content = session.user_input.atp or ""

            # Create processing metadata
            processing_metadata = {
                "complexity_level": session.task_analysis.get("complexity_level", "unknown") if session.task_analysis else "unknown",
                "rag_strategy_used": session.task_analysis.get("required_rag_strategy", "simple") if session.task_analysis else "simple",
                "validation_iterations": len(session.validation_history),
                "confidence_score": session.cp_atp_result.confidence_score if session.cp_atp_result else 1.0,
                "processing_start_time": session.processing_start_time.isoformat() if session.processing_start_time else None,
                "processing_completion_time": datetime.now().isoformat(),
                "session_id": session_id
            }

            # Create FinalInput object
            final_input = FinalInput(
                user_input=session.user_input,
                cp_content=cp_content,
                atp_content=atp_content,
                processing_metadata=processing_metadata,
                validation_history=session.validation_history
            )

            # Store in session
            self.session_manager.set_final_input(session_id, final_input)

            # Send final result via WebSocket
            await self._send_final_result(session_id, final_input)

            logger.success(f"Final input created for session: {session_id}")

        except Exception as e:
            logger.error(f"Error creating final input: {str(e)}")
            await self._handle_processing_error(session_id, f"Final input creation error: {str(e)}")

    async def _send_final_result(self, session_id: str, final_input: FinalInput):
        """Send final result ke user"""

        # Create API response
        final_response = FinalInputResponse(
            session_id=session_id,
            user_input=UserInputRequest(
                nama_guru=final_input.user_input.nama_guru,
                nama_sekolah=final_input.user_input.nama_sekolah,
                mata_pelajaran=final_input.user_input.mata_pelajaran,
                topik=final_input.user_input.topik,
                sub_topik=final_input.user_input.sub_topik,
                kelas=final_input.user_input.kelas,
                alokasi_waktu=final_input.user_input.alokasi_waktu,
                model_llm=final_input.user_input.model_llm,
                cp=final_input.user_input.cp,
                atp=final_input.user_input.atp
            ),
            cp_content=final_input.cp_content,
            atp_content=final_input.atp_content,
            processing_metadata=final_input.processing_metadata,
            validation_history=[
                {
                    "is_approved": v.is_approved,
                    "feedback": v.feedback,
                    "requested_changes": v.requested_changes
                } for v in final_input.validation_history
            ],
            completed_at=datetime.now().isoformat()
        )

        # Send via WebSocket
        await self._send_websocket_update(session_id, "final_result", {
            "message": "Proses selesai! Final input telah dibuat.",
            "final_input": final_response.dict(),
            "status": "completed"
        })

    async def _handle_processing_error(self, session_id: str, error_message: str):
        """Handle processing error"""
        session = self.session_manager.get_session(session_id)
        if session:
            session.update_status(SessionStatusEnum.ERROR, f"Error: {error_message}", session.progress_percentage)
            session.error_count += 1
            session.last_error = error_message

        # Send error via WebSocket
        await self._send_websocket_update(session_id, "error", {
            "error_message": error_message,
            "error_code": "PROCESSING_ERROR",
            "timestamp": datetime.now().isoformat()
        })

        logger.error(f"Processing error for session {session_id}: {error_message}")

    async def _send_websocket_update(self, session_id: str, message_type: str, data: Dict[str, Any]):
        """Send WebSocket update ke session"""
        message = {
            "type": message_type,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        await self.session_manager.broadcast_to_session(session_id, message)

    # === Public Methods ===

    def get_processing_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current processing status"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return None

        is_processing = session_id in self.current_processing

        return {
            "session_id": session_id,
            "status": session.status.value,
            "current_step": session.current_step,
            "progress_percentage": session.progress_percentage,
            "is_processing": is_processing,
            "validation_count": len(session.validation_history),
            "error_count": session.error_count,
            "last_error": session.last_error
        }

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "max_concurrent_processing": self.max_concurrent_processing,
            "current_processing_count": len(self.current_processing),
            "current_processing_sessions": list(self.current_processing.keys()),
            "service_status": "running"
        }

    async def cancel_processing(self, session_id: str) -> bool:
        """Cancel processing untuk session"""
        if session_id not in self.current_processing:
            return False

        task = self.current_processing[session_id]
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Update session status
        session = self.session_manager.get_session(session_id)
        if session:
            session.update_status(SessionStatusEnum.ERROR, "Processing cancelled", session.progress_percentage)

        logger.info(f"Processing cancelled for session: {session_id}")
        return True

    async def shutdown(self):
        """Shutdown processing service"""
        # Cancel all running tasks
        for session_id, task in self.current_processing.items():
            task.cancel()

        # Wait for all tasks to complete
        if self.current_processing:
            await asyncio.gather(*self.current_processing.values(), return_exceptions=True)

        logger.info("RAG Processing Service shutdown completed")
