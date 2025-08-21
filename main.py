"""
RAG Multi-Strategy System - Main Application
===========================================

Sistem Pembuat Modul Ajar dengan Multiple RAG Strategy
Mengikuti flowchart yang telah didefinisikan dalam prompt_builder1.md

Author: AI Assistant
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.user_interface import UserInterface
from src.core.models import UserInput, ValidationResult
from src.orchestrator.main_orchestrator import MainOrchestrator
from src.utils.logger import get_logger

logger = get_logger("MainApplication")

class RAGMultiStrategyApp:
    """
    Main application class untuk RAG Multi-Strategy System

    Mengatur alur dari input user sampai final input sesuai flowchart:
    1. Start
    2. User Input
    3. Main Orchestrator (Task Analysis & Strategy Selection)
    4. CP/ATP Generation (jika diperlukan)
    5. User Validation CP/ATP
    6. Retrieve RAG Refinement Strategy (jika diperlukan)
    7. Final Input Display
    """

    def __init__(self):
        self.ui = UserInterface()
        self.main_orchestrator = MainOrchestrator()
        logger.info("RAG Multi-Strategy System initialized")

    async def run(self):
        """
        Main entry point untuk menjalankan aplikasi
        Mengikuti alur flowchart yang telah didefinisikan
        """
        try:
            # Display welcome banner
            self.ui.welcome_banner()
            logger.step("Application Start", "Memulai sistem RAG Multi-Strategy")

            # Step 1: Collect User Input
            user_input = await self._collect_user_input()

            # Step 2: Process through Main Orchestrator
            final_input = await self._process_with_orchestrator(user_input)

            # Step 3: Display Final Input (End point untuk fase ini)
            await self._display_final_result(final_input)

            logger.success("Sistem berhasil menyelesaikan proses hingga Final Input")

        except KeyboardInterrupt:
            logger.warning("Aplikasi dihentikan oleh user")
            if self.ui.confirm_exit():
                logger.info("Aplikasi ditutup")
                return
            else:
                await self.run()  # Restart application

        except Exception as e:
            logger.error(f"Error dalam aplikasi: {str(e)}")
            self.ui.show_error(f"Terjadi kesalahan: {str(e)}")
            raise

    async def _collect_user_input(self) -> UserInput:
        """
        Step 1: Mengumpulkan input dari user
        Sesuai dengan titik 'User Input' dalam flowchart
        """
        logger.step("User Input Collection", "Mengumpulkan data input dari pengguna")

        try:
            # Collect input through interactive UI
            user_input = self.ui.collect_user_input()

            # Display summary for confirmation
            self.ui.display_input_summary(user_input)

            # Log the collected input
            logger.user_interaction(f"Input collected: {user_input.mata_pelajaran} - {user_input.topik}")

            return user_input

        except Exception as e:
            logger.error(f"Error collecting user input: {str(e)}")
            self.ui.show_error("Gagal mengumpulkan input pengguna")
            raise

    async def _process_with_orchestrator(self, user_input: UserInput):
        """
        Step 2-6: Process melalui Main Orchestrator
        Meliputi:
        - Main Orchestrator (Task Analysis & Strategy Selection)
        - CP/ATP Generation (jika diperlukan)
        - User Validation CP/ATP
        - Retrieve RAG Refinement Strategy (jika diperlukan)
        """
        logger.step("Orchestrator Processing", "Memproses melalui Main Orchestrator")

        try:
            # Check if CP/ATP generation is needed
            if user_input.has_cp_atp():
                logger.orchestrator_log("CP/ATP sudah tersedia, skip generation", "Main")
                # Directly create final input without CP/ATP generation
                final_input = await self.main_orchestrator.process_request(user_input)
            else:
                logger.orchestrator_log("CP/ATP tidak tersedia, memulai generation process", "Main")

                # Process through CP/ATP generation with user validation loop
                final_input = await self._handle_cp_atp_generation_flow(user_input)

            return final_input

        except Exception as e:
            logger.error(f"Error in orchestrator processing: {str(e)}")
            self.ui.show_error("Gagal memproses melalui orchestrator")
            raise

    async def _handle_cp_atp_generation_flow(self, user_input: UserInput):
        """
        Handle CP/ATP generation flow dengan user validation loop
        Mengikuti alur flowchart untuk CP/ATP generation dan validation
        """
        logger.step("CP/ATP Generation Flow", "Memulai alur generation dan validasi CP/ATP")

        max_iterations = 3
        current_iteration = 0

        while current_iteration < max_iterations:
            current_iteration += 1
            logger.orchestrator_log(f"CP/ATP Generation Iteration {current_iteration}", "Main")

            # Step 4: Generate CP/ATP
            cp_atp_result = await self._generate_cp_atp(user_input)

            # Display generated CP/ATP to user
            self.ui.display_generated_cp_atp(
                cp_atp_result.cp_content,
                cp_atp_result.atp_content
            )

            # Step 5: User Validation CP/ATP
            validation_result = await self._get_user_validation()

            if validation_result.is_approved:
                logger.success("CP/ATP disetujui oleh user")
                # Create final input dengan approved CP/ATP
                return await self._create_final_input_with_cp_atp(
                    user_input, cp_atp_result, [validation_result]
                )

            # Step 6: Retrieve RAG Refinement Strategy
            if current_iteration < max_iterations:
                logger.orchestrator_log("CP/ATP tidak disetujui, melakukan refinement", "Main")
                await self._show_refinement_process()

                # Refine strategy based on feedback
                # (Integration dengan CP/ATP Orchestrator untuk refinement)
                user_input = await self._refine_based_on_feedback(user_input, validation_result)
            else:
                logger.warning("Maximum iterations reached untuk CP/ATP generation")
                # Gunakan hasil terakhir
                return await self._create_final_input_with_cp_atp(
                    user_input, cp_atp_result, [validation_result]
                )

        # Fallback - shouldn't reach here
        raise Exception("Failed to generate acceptable CP/ATP after maximum iterations")

    async def _generate_cp_atp(self, user_input: UserInput):
        """Generate CP/ATP menggunakan orchestrator"""

        # Show progress to user
        self.ui.show_cp_atp_generation_progress()

        # Process through Main Orchestrator
        final_input = await self.main_orchestrator.process_request(user_input)

        # Extract CP/ATP from final input (simulate CP/ATP result)
        from src.core.models import CPATPResult, RAGStrategy

        cp_atp_result = CPATPResult(
            cp_content=final_input.cp_content,
            atp_content=final_input.atp_content,
            generation_strategy=RAGStrategy.SIMPLE,  # This would be determined by orchestrator
            confidence_score=0.85,
            sources_used=["Simulated sources"]
        )

        return cp_atp_result

    async def _get_user_validation(self) -> ValidationResult:
        """Get user validation untuk CP/ATP yang dihasilkan"""

        logger.step("User Validation", "Meminta validasi user untuk CP/ATP")

        # Get validation through UI
        validation_result = self.ui.get_user_validation()

        logger.user_interaction(
            f"Validation: {'Approved' if validation_result.is_approved else 'Rejected'}"
        )

        return validation_result

    async def _show_refinement_process(self):
        """Show refinement process kepada user"""

        logger.step("Refinement Process", "Menampilkan proses refinement")
        self.ui.show_refinement_progress()

    async def _refine_based_on_feedback(self, user_input: UserInput, validation_result: ValidationResult) -> UserInput:
        """
        Refine user input based on feedback
        Dalam implementasi nyata, ini akan mengintegrasikan dengan CP/ATP Orchestrator
        """

        logger.orchestrator_log("Analyzing feedback untuk refinement", "CP/ATP")

        # Simulate refinement process
        # Dalam implementasi nyata, ini akan menggunakan feedback untuk adjust strategy

        return user_input  # For now, return original input

    async def _create_final_input_with_cp_atp(self, user_input: UserInput, cp_atp_result, validation_history):
        """Create final input dengan CP/ATP yang sudah divalidasi"""

        from src.core.models import FinalInput

        processing_metadata = {
            "strategy_used": cp_atp_result.generation_strategy.value,
            "confidence_score": cp_atp_result.confidence_score,
            "sources_used": cp_atp_result.sources_used,
            "validation_iterations": len(validation_history),
            "timestamp": "2024-08-20 12:00:00"  # Would be actual timestamp
        }

        final_input = FinalInput(
            user_input=user_input,
            cp_content=cp_atp_result.cp_content,
            atp_content=cp_atp_result.atp_content,
            processing_metadata=processing_metadata,
            validation_history=validation_history
        )

        return final_input

    async def _display_final_result(self, final_input):
        """
        Step 7: Display Final Input
        Ini adalah endpoint untuk fase pertama sistem sesuai requirement
        """
        logger.step("Final Input Display", "Menampilkan hasil final untuk tahap selanjutnya")

        try:
            # Display final input melalui UI
            self.ui.display_final_input(final_input)

            # Log completion
            logger.success("Final Input berhasil ditampilkan")
            logger.info("Sistem siap untuk tahap selanjutnya (modul ajar generation)")

            # Save final input untuk tahap selanjutnya (optional)
            await self._save_final_input_for_next_stage(final_input)

        except Exception as e:
            logger.error(f"Error displaying final result: {str(e)}")
            self.ui.show_error("Gagal menampilkan hasil final")
            raise

    async def _save_final_input_for_next_stage(self, final_input):
        """
        Save final input untuk tahap selanjutnya
        (Tahap modul ajar generation yang akan dikembangkan kemudian)
        """
        try:
            # Convert to dict for saving
            final_input_dict = final_input.to_dict()

            # Log untuk development tracking
            logger.info("Final input ready untuk tahap modul ajar generation")
            logger.debug(f"Final input contains: CP ({len(final_input.cp_content)} chars), ATP ({len(final_input.atp_content)} chars)")

            # Dalam implementasi nyata, ini bisa save ke database atau file
            # untuk digunakan di tahap selanjutnya

        except Exception as e:
            logger.warning(f"Failed to save final input for next stage: {str(e)}")
            # Non-critical error, tidak perlu stop aplikasi

    def get_system_status(self) -> dict:
        """Get current system status untuk monitoring"""
        return {
            "status": "ready",
            "version": "1.0.0",
            "components": {
                "user_interface": "initialized",
                "main_orchestrator": "ready",
                "cp_atp_orchestrator": "ready",
                "rag_strategies": ["simple", "advanced", "graph"]
            },
            "current_stage": "final_input_display"
        }


async def main():
    """
    Main function untuk menjalankan aplikasi RAG Multi-Strategy
    """

    # Initialize and run application
    app = RAGMultiStrategyApp()

    try:
        await app.run()
    except Exception as e:
        logger.critical(f"Critical error in main application: {str(e)}")
        print(f"\n❌ Critical Error: {str(e)}")
        print("Please check the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    """
    Entry point untuk aplikasi

    Usage:
        python main.py
    """

    # Setup logging
    logger.info("Starting RAG Multi-Strategy System")

    try:
        # Run the async application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        print("\n👋 Terima kasih telah menggunakan RAG Multi-Strategy System!")
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        print(f"\n💥 Failed to start: {str(e)}")
        sys.exit(1)
