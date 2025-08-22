"""
RAG Orchestra System Initializer
===============================

Script untuk menginisialisasi dan menjalankan sistem RAG Orchestra
dengan semua komponen yang diperlukan.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.core.models import UserInput, LLMModel
    from src.orchestrator.enhanced_main_orchestrator import get_enhanced_main_orchestrator
    from src.services.llm_service import get_llm_service
    from src.services.vector_db_service import get_vector_db_service
    from src.services.online_search_service import get_online_search_service
    from src.utils.logger import get_logger
    from src.core.prompt_builder_agent import PromptBuilderAgent
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)

logger = get_logger("SystemInitializer")

class RAGOrchestraSystem:
    """
    Main system class untuk RAG Orchestra
    """

    def __init__(self):
        self.orchestrator = None
        self.llm_service = None
        self.vector_db_service = None
        self.online_search_service = None
        self.prompt_builder = None

        self.initialized = False

    async def initialize(self):
        """Initialize semua komponen sistem"""
        try:
            logger.info("Initializing RAG Orchestra System...")

            # Initialize services
            logger.info("Initializing LLM Service...")
            self.llm_service = get_llm_service()

            logger.info("Initializing Vector DB Service...")
            self.vector_db_service = get_vector_db_service(self.llm_service)

            logger.info("Initializing Online Search Service...")
            self.online_search_service = get_online_search_service()

            logger.info("Initializing Enhanced Main Orchestrator...")
            self.orchestrator = get_enhanced_main_orchestrator()

            logger.info("Initializing Prompt Builder Agent...")
            self.prompt_builder = PromptBuilderAgent(
                self.llm_service,
                self.vector_db_service
            )

            # Check system health
            await self._health_check()

            self.initialized = True
            logger.success("RAG Orchestra System initialized successfully!")

        except Exception as e:
            logger.error(f"Failed to initialize system: {str(e)}")
            raise

    async def _health_check(self):
        """Perform health check untuk semua services"""
        logger.info("Performing system health check...")

        health_results = {}

        # Check LLM Service
        try:
            llm_health = await self.llm_service.health_check()
            health_results["llm_service"] = llm_health
            logger.info(f"LLM Service health: {llm_health}")
        except Exception as e:
            health_results["llm_service"] = {"error": str(e)}
            logger.warning(f"LLM Service health check failed: {str(e)}")

        # Check Vector DB Service
        try:
            vector_stats = await self.vector_db_service.get_collection_stats()
            health_results["vector_db_service"] = vector_stats
            logger.info(f"Vector DB stats: {vector_stats}")
        except Exception as e:
            health_results["vector_db_service"] = {"error": str(e)}
            logger.warning(f"Vector DB health check failed: {str(e)}")

        # Check Online Search Service
        try:
            search_health = await self.online_search_service.health_check()
            health_results["online_search_service"] = search_health
            logger.info(f"Online Search health: {search_health}")
        except Exception as e:
            health_results["online_search_service"] = {"error": str(e)}
            logger.warning(f"Online Search health check failed: {str(e)}")

        return health_results

    async def run_demo(self):
        """Run demo dari sistem untuk testing"""
        if not self.initialized:
            await self.initialize()

        logger.info("Running RAG Orchestra Demo...")

        # Demo input
        demo_input = UserInput(
            nama_guru="Budi Santoso",
            nama_sekolah="SDN 1 Jakarta",
            mata_pelajaran="Matematika",
            kelas="3",
            fase="B",
            topik="Penjumlahan",
            sub_topik="Penjumlahan bilangan 1-100",
            alokasi_waktu="2 x 35 menit",
            model_llm=LLMModel.GEMINI_1_5_FLASH,
            cp=None,  # Will be generated
            atp=None  # Will be generated
        )

        logger.info("Demo Input:")
        logger.info(f"  Mata Pelajaran: {demo_input.mata_pelajaran}")
        logger.info(f"  Kelas: {demo_input.kelas}")
        logger.info(f"  Topik: {demo_input.topik}")
        logger.info(f"  Sub Topik: {demo_input.sub_topik}")

        # Callback untuk tracking progress
        async def demo_callback(event_type: str, data: Dict[str, Any]):
            logger.info(f"[DEMO] {event_type}: {data.get('message', '')}")

        try:
            # Process dengan orchestrator
            complete_input = await self.orchestrator.orchestrate_complete_input(
                user_input=demo_input,
                callback_func=demo_callback
            )

            # Display results
            logger.success("Demo completed successfully!")
            logger.info("=== COMPLETE INPUT RESULT ===")

            result_json = complete_input.to_json_standard()

            # Pretty print hasil
            import json
            print("\n" + "="*80)
            print("COMPLETE INPUT JSON STANDARD FORMAT")
            print("="*80)
            print(json.dumps(result_json, indent=2, ensure_ascii=False))
            print("="*80)

            return complete_input

        except Exception as e:
            logger.error(f"Demo failed: {str(e)}")
            raise

    async def run_interactive_mode(self):
        """Run interactive mode untuk user input"""
        if not self.initialized:
            await self.initialize()

        logger.info("Starting Interactive Mode...")
        print("\n" + "="*60)
        print("RAG ORCHESTRA - INTERACTIVE MODE")
        print("="*60)
        print("Masukkan data untuk generate Complete Input:")
        print()

        try:
            # Collect user input
            nama_guru = input("Nama Guru: ")
            nama_sekolah = input("Nama Sekolah: ")
            mata_pelajaran = input("Mata Pelajaran: ")
            kelas = input("Kelas: ")
            fase = input("Fase (A/B/C): ")
            topik = input("Topik: ")
            sub_topik = input("Sub Topik: ")
            alokasi_waktu = input("Alokasi Waktu: ")

            print("\nPilih LLM Model:")
            print("1. Gemini 1.5 Flash")
            print("2. Gemini 1.5 Pro")
            print("3. GPT-4")
            print("4. GPT-3.5 Turbo")

            llm_choice = input("Pilihan (1-4): ")
            llm_mapping = {
                "1": LLMModel.GEMINI_1_5_FLASH,
                "2": LLMModel.GEMINI_1_5_PRO,
                "3": LLMModel.GPT_4,
                "4": LLMModel.GPT_3_5_TURBO
            }
            model_llm = llm_mapping.get(llm_choice, LLMModel.GEMINI_1_5_FLASH)

            # Optional CP/ATP input
            print("\nApakah Anda sudah memiliki CP dan ATP? (y/n)")
            has_cp_atp = input().lower() == 'y'

            cp = None
            atp = None
            if has_cp_atp:
                print("\nMasukkan CP (Capaian Pembelajaran):")
                cp = input()
                print("\nMasukkan ATP (Alur Tujuan Pembelajaran):")
                atp = input()

            # Create UserInput
            user_input = UserInput(
                nama_guru=nama_guru,
                nama_sekolah=nama_sekolah,
                mata_pelajaran=mata_pelajaran,
                kelas=kelas,
                fase=fase,
                topik=topik,
                sub_topik=sub_topik,
                alokasi_waktu=alokasi_waktu,
                model_llm=model_llm,
                cp=cp,
                atp=atp
            )

            print("\n" + "="*60)
            print("MEMPROSES...")
            print("="*60)

            # Progress callback
            async def interactive_callback(event_type: str, data: Dict[str, Any]):
                message = data.get('message', '')
                if message:
                    print(f"[{event_type.upper()}] {message}")

            # Process
            complete_input = await self.orchestrator.orchestrate_complete_input(
                user_input=user_input,
                callback_func=interactive_callback
            )

            # Display results
            print("\n" + "="*60)
            print("HASIL COMPLETE INPUT")
            print("="*60)

            result_json = complete_input.to_json_standard()

            import json
            print(json.dumps(result_json, indent=2, ensure_ascii=False))

            # Ask to save results
            print("\n" + "="*60)
            save_choice = input("Simpan hasil ke file? (y/n): ")
            if save_choice.lower() == 'y':
                filename = f"complete_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, indent=2, ensure_ascii=False)
                print(f"Hasil disimpan ke: {filename}")

            return complete_input

        except KeyboardInterrupt:
            print("\n\nInteractive mode dibatalkan.")
            return None
        except Exception as e:
            logger.error(f"Error in interactive mode: {str(e)}")
            print(f"\nError: {str(e)}")
            return None

async def main():
    """Main function"""
    system = RAGOrchestraSystem()

    print("RAG Orchestra System")
    print("===================")
    print("1. Run Demo")
    print("2. Run Interactive Mode")
    print("3. Initialize Only")
    print("4. Exit")

    try:
        choice = input("\nPilih mode (1-4): ")

        if choice == "1":
            await system.run_demo()
        elif choice == "2":
            await system.run_interactive_mode()
        elif choice == "3":
            await system.initialize()
            print("System initialized successfully!")
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice.")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import datetime

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan.")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)
