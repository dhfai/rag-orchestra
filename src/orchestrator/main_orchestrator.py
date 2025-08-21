from typing import Dict, Any, Optional
import asyncio
from ..core.models import (
    UserInput, TaskAnalysisResult, RAGStrategy,
    CPATPResult, ValidationResult, FinalInput
)
from ..utils.logger import get_logger
from .cp_atp_orchestrator import CPATPOrchestrator

logger = get_logger("MainOrchestrator")

class MainOrchestrator:
    """
    Main Orchestrator - Core component yang mengatur dan mengkoordinasikan seluruh proses sistem

    Fungsi utama:
    1. Task Analysis - Menganalisis kompleksitas dan kebutuhan request
    2. Strategy Selection - Memilih strategi RAG yang tepat
    3. Decision Making - Menentukan alur proses yang akan dijalankan
    4. Monitoring - Mengawasi seluruh proses dan memastikan kualitas output
    """

    def __init__(self):
        self.cp_atp_orchestrator = CPATPOrchestrator()
        logger.orchestrator_log("Main Orchestrator initialized", "Main")

    async def process_request(self, user_input: UserInput) -> FinalInput:
        """
        Main entry point untuk memproses request pengguna

        Args:
            user_input: Input dari pengguna

        Returns:
            FinalInput: Input final yang siap untuk tahap selanjutnya
        """
        logger.orchestrator_log("Starting request processing", "Main")
        logger.orchestrator_log(f"Processing: {user_input.mata_pelajaran} - {user_input.topik}", "Main")

        try:
            # Step 1: Task Analysis
            task_analysis = await self._analyze_task(user_input)
            logger.orchestrator_log(f"Task analysis completed - Complexity: {task_analysis.complexity_level}", "Main")

            # Step 2: Strategy Selection
            selected_strategy = self._select_strategy(task_analysis)
            logger.orchestrator_log(f"Strategy selected: {selected_strategy.value}", "Main")

            # Step 3: Decision Making - Check if CP/ATP generation is needed
            if user_input.has_cp_atp():
                logger.orchestrator_log("CP/ATP already provided, proceeding to final input", "Main")
                cp_content = user_input.cp
                atp_content = user_input.atp
                validation_history = []
            else:
                logger.orchestrator_log("CP/ATP not provided, initiating generation process", "Main")
                cp_content, atp_content, validation_history = await self._handle_cp_atp_generation(
                    user_input, selected_strategy
                )

            # Step 4: Create Final Input
            final_input = self._create_final_input(
                user_input, cp_content, atp_content, task_analysis, validation_history
            )

            logger.orchestrator_log("Request processing completed successfully", "Main")
            return final_input

        except Exception as e:
            logger.error(f"Error in request processing: {str(e)}")
            raise

    async def _analyze_task(self, user_input: UserInput) -> TaskAnalysisResult:
        """
        Menganalisis kompleksitas dan kebutuhan dari request

        Args:
            user_input: Input pengguna

        Returns:
            TaskAnalysisResult: Hasil analisis tugas
        """
        logger.orchestrator_log("Analyzing task complexity and requirements", "Main")

        # Analyze complexity based on various factors
        complexity_factors = {
            'topic_complexity': self._assess_topic_complexity(user_input.topik, user_input.sub_topik),
            'subject_complexity': self._assess_subject_complexity(user_input.mata_pelajaran),
            'grade_level': self._assess_grade_complexity(user_input.kelas),
            'time_allocation': self._assess_time_complexity(user_input.alokasi_waktu)
        }

        # Calculate overall complexity
        complexity_score = sum(complexity_factors.values()) / len(complexity_factors)

        if complexity_score < 0.3:
            complexity_level = "simple"
            required_strategy = RAGStrategy.SIMPLE
        elif complexity_score < 0.7:
            complexity_level = "medium"
            required_strategy = RAGStrategy.ADVANCED
        else:
            complexity_level = "complex"
            required_strategy = RAGStrategy.GRAPH

        # Identify missing components
        missing_components = []
        if not user_input.cp:
            missing_components.append("CP")
        if not user_input.atp:
            missing_components.append("ATP")

        # Estimate processing time
        base_time = 30  # base 30 seconds
        if missing_components:
            base_time += len(missing_components) * 45  # add 45 seconds per missing component

        if complexity_level == "complex":
            base_time *= 1.5
        elif complexity_level == "medium":
            base_time *= 1.2

        result = TaskAnalysisResult(
            complexity_level=complexity_level,
            missing_components=missing_components,
            required_rag_strategy=required_strategy,
            estimated_processing_time=int(base_time),
            confidence_score=0.9 - (complexity_score * 0.3)  # Higher complexity = lower confidence
        )

        logger.orchestrator_log(
            f"Task analysis result: {complexity_level} complexity, "
            f"strategy: {required_strategy.value}, "
            f"missing: {missing_components}",
            "Main"
        )

        return result

    def _assess_topic_complexity(self, topik: str, sub_topik: str) -> float:
        """Assess topic complexity based on content"""
        complex_keywords = [
            'analisis', 'sintesis', 'evaluasi', 'kritik', 'perbandingan',
            'complex', 'advanced', 'tingkat tinggi', 'mendalam'
        ]

        text = f"{topik} {sub_topik}".lower()
        complexity_score = sum(1 for keyword in complex_keywords if keyword in text)
        return min(complexity_score / len(complex_keywords), 1.0)

    def _assess_subject_complexity(self, mata_pelajaran: str) -> float:
        """Assess subject complexity"""
        complex_subjects = {
            'matematika': 0.8,
            'fisika': 0.9,
            'kimia': 0.9,
            'biologi': 0.7,
            'bahasa indonesia': 0.6,
            'bahasa inggris': 0.7,
            'ipas': 0.7,
            'ppkn': 0.5,
            'pjok': 0.4,
            'seni': 0.5
        }

        subject_lower = mata_pelajaran.lower()
        for subject, score in complex_subjects.items():
            if subject in subject_lower:
                return score
        return 0.6  # default complexity

    def _assess_grade_complexity(self, kelas: str) -> float:
        """Assess grade level complexity"""
        try:
            # Extract number from grade
            import re
            grade_num = re.findall(r'\d+', kelas)
            if grade_num:
                grade = int(grade_num[0])
                return min(grade / 12, 1.0)  # Normalize to 0-1
        except:
            pass
        return 0.5  # default

    def _assess_time_complexity(self, alokasi_waktu: str) -> float:
        """Assess time allocation complexity"""
        try:
            # Extract numbers from time allocation
            import re
            numbers = re.findall(r'\d+', alokasi_waktu)
            if numbers:
                total_minutes = sum(int(num) for num in numbers)
                # More time = potentially more complex
                return min(total_minutes / 180, 1.0)  # Normalize against 3 hours
        except:
            pass
        return 0.5  # default

    def _select_strategy(self, task_analysis: TaskAnalysisResult) -> RAGStrategy:
        """
        Memilih strategi RAG berdasarkan hasil analisis

        Args:
            task_analysis: Hasil analisis tugas

        Returns:
            RAGStrategy: Strategi yang dipilih
        """
        strategy = task_analysis.required_rag_strategy

        logger.orchestrator_log(
            f"Strategy selection based on complexity: {strategy.value}",
            "Main"
        )

        return strategy

    async def _handle_cp_atp_generation(
        self,
        user_input: UserInput,
        strategy: RAGStrategy
    ) -> tuple[str, str, list[ValidationResult]]:
        """
        Handle CP/ATP generation process with user validation loop

        Args:
            user_input: Input pengguna
            strategy: Strategi RAG yang dipilih

        Returns:
            tuple: (cp_content, atp_content, validation_history)
        """
        logger.orchestrator_log("Starting CP/ATP generation process", "Main")

        validation_history = []
        max_iterations = 3
        current_iteration = 0

        while current_iteration < max_iterations:
            current_iteration += 1
            logger.orchestrator_log(f"CP/ATP generation iteration {current_iteration}", "Main")

            # Generate CP/ATP using sub-orchestrator
            cp_atp_result = await self.cp_atp_orchestrator.generate_cp_atp(user_input, strategy)

            # Here we would normally show to user and get validation
            # For now, we'll simulate user validation
            # In actual implementation, this would be handled by the main application

            # Simulate user validation (this would be replaced with actual user interaction)
            validation_result = ValidationResult(is_approved=True)  # Simulate approval
            validation_history.append(validation_result)

            if validation_result.is_approved:
                logger.orchestrator_log("CP/ATP approved by user", "Main")
                return cp_atp_result.cp_content, cp_atp_result.atp_content, validation_history

            # If not approved, refine the strategy
            logger.orchestrator_log("CP/ATP not approved, refining strategy", "Main")
            strategy = await self._refine_strategy(strategy, validation_result)

        # If max iterations reached, return the last result
        logger.orchestrator_log("Max iterations reached, returning last result", "Main")
        return cp_atp_result.cp_content, cp_atp_result.atp_content, validation_history

    async def _refine_strategy(
        self,
        current_strategy: RAGStrategy,
        validation_result: ValidationResult
    ) -> RAGStrategy:
        """
        Refine RAG strategy based on user feedback

        Args:
            current_strategy: Current RAG strategy
            validation_result: User validation result with feedback

        Returns:
            RAGStrategy: Refined strategy
        """
        logger.orchestrator_log("Refining strategy based on user feedback", "Main")

        # Analyze feedback and adjust strategy
        if validation_result.feedback:
            feedback_lower = validation_result.feedback.lower()

            if any(word in feedback_lower for word in ['detail', 'lengkap', 'spesifik']):
                # User wants more detail, use more advanced strategy
                if current_strategy == RAGStrategy.SIMPLE:
                    return RAGStrategy.ADVANCED
                elif current_strategy == RAGStrategy.ADVANCED:
                    return RAGStrategy.GRAPH

            elif any(word in feedback_lower for word in ['sederhana', 'singkat', 'simple']):
                # User wants simpler approach
                if current_strategy == RAGStrategy.GRAPH:
                    return RAGStrategy.ADVANCED
                elif current_strategy == RAGStrategy.ADVANCED:
                    return RAGStrategy.SIMPLE

        # Default: try next strategy in sequence
        strategy_sequence = [RAGStrategy.SIMPLE, RAGStrategy.ADVANCED, RAGStrategy.GRAPH]
        current_index = strategy_sequence.index(current_strategy)
        next_index = (current_index + 1) % len(strategy_sequence)

        refined_strategy = strategy_sequence[next_index]
        logger.orchestrator_log(f"Strategy refined from {current_strategy.value} to {refined_strategy.value}", "Main")

        return refined_strategy

    def _create_final_input(
        self,
        user_input: UserInput,
        cp_content: str,
        atp_content: str,
        task_analysis: TaskAnalysisResult,
        validation_history: list[ValidationResult]
    ) -> FinalInput:
        """
        Create final input object ready for next stage

        Args:
            user_input: Original user input
            cp_content: Final CP content
            atp_content: Final ATP content
            task_analysis: Task analysis result
            validation_history: History of user validations

        Returns:
            FinalInput: Final processed input
        """
        logger.orchestrator_log("Creating final input object", "Main")

        processing_metadata = {
            "complexity_level": task_analysis.complexity_level,
            "rag_strategy_used": task_analysis.required_rag_strategy.value,
            "processing_time": task_analysis.estimated_processing_time,
            "confidence_score": task_analysis.confidence_score,
            "validation_iterations": len(validation_history),
            "timestamp": logger.logger.handlers[0].formatter.formatTime(
                logger.logger.makeRecord("", 0, "", 0, "", (), None),
                "%Y-%m-%d %H:%M:%S"
            ) if logger.logger.handlers else "Unknown"
        }

        final_input = FinalInput(
            user_input=user_input,
            cp_content=cp_content,
            atp_content=atp_content,
            processing_metadata=processing_metadata,
            validation_history=validation_history
        )

        logger.orchestrator_log("Final input created successfully", "Main")
        return final_input

    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            "orchestrator": "Main",
            "status": "ready",
            "sub_orchestrators": {
                "cp_atp": "initialized"
            }
        }
