"""
Prompt Builder Agent
===================

Agent yang bertugas memastikan input awal user menjadi Complete Input.
Mengecek kelengkapan input dan melakukan generasi CP/ATP jika diperlukan.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

from ..core.models import (
    UserInput, CompleteInput, ValidationResult,
    CPATPResult, RAGStrategy, PromptBuilderStatus
)
from ..utils.logger import get_logger
from ..services.llm_service import LLMService
from ..services.vector_db_service import VectorDBService
from ..services.online_search_service import OnlineSearchService

logger = get_logger("PromptBuilderAgent")

class InputCompleteness(Enum):
    """Status kelengkapan input"""
    COMPLETE = "complete"
    MISSING_CP_ATP = "missing_cp_atp"
    MISSING_BASIC_INFO = "missing_basic_info"
    PARTIALLY_COMPLETE = "partially_complete"

class PromptBuilderAgent:
    """
    Agent untuk membangun Complete Input dari user input.

    Fungsi utama:
    1. Mengecek kelengkapan input
    2. Generate CP/ATP jika diperlukan
    3. Validasi dengan user
    4. Menghasilkan Complete Input dalam format JSON standar
    """

    def __init__(self, llm_service: LLMService, vector_db_service: VectorDBService):
        self.llm_service = llm_service
        self.vector_db_service = vector_db_service
        self.online_search_service = OnlineSearchService()

        # Required fields untuk Complete Input
        self.required_fields = [
            'nama_guru', 'nama_sekolah', 'mata_pelajaran',
            'kelas', 'fase', 'topik', 'sub_topik', 'alokasi_waktu'
        ]

        # Optional fields yang akan digenerate jika tidak ada
        self.optional_fields = ['cp', 'atp']

        logger.info("Prompt Builder Agent initialized")

    async def build_complete_input(
        self,
        user_input: UserInput,
        llm_model_choice: str = "gemini",
        callback_func: Optional[callable] = None
    ) -> CompleteInput:
        """
        Main function untuk membangun Complete Input

        Args:
            user_input: Input awal dari user
            llm_model_choice: Model LLM yang dipilih (gemini/openai)
            callback_func: Callback untuk komunikasi real-time dengan user

        Returns:
            CompleteInput: Input yang sudah lengkap dan siap diproses
        """
        logger.info("Starting Complete Input building process")

        try:
            # Step 1: Check input completeness
            completeness_status = await self._check_input_completeness(user_input)
            await self._notify_callback(callback_func, "input_analysis", {
                "status": completeness_status.value,
                "message": "Analyzing input completeness..."
            })

            # Step 2: Handle missing information
            if completeness_status == InputCompleteness.MISSING_BASIC_INFO:
                # Request additional info from user
                missing_fields = self._get_missing_fields(user_input)
                await self._notify_callback(callback_func, "missing_info", {
                    "missing_fields": missing_fields,
                    "message": "Please provide missing information"
                })
                raise ValueError(f"Missing required fields: {missing_fields}")

            # Step 3: Generate CP/ATP if needed
            cp_content = user_input.cp
            atp_content = user_input.atp

            if completeness_status in [InputCompleteness.MISSING_CP_ATP, InputCompleteness.PARTIALLY_COMPLETE]:
                await self._notify_callback(callback_func, "generating_cp_atp", {
                    "message": "Generating CP/ATP content..."
                })

                cp_content, atp_content = await self._generate_cp_atp(
                    user_input, llm_model_choice, callback_func
                )

            # Step 4: Create Complete Input
            complete_input = CompleteInput(
                # Basic Info
                nama_guru=user_input.nama_guru,
                nama_sekolah=user_input.nama_sekolah,
                mata_pelajaran=user_input.mata_pelajaran,
                kelas=user_input.kelas,
                fase=user_input.fase,
                topik=user_input.topik,
                sub_topik=user_input.sub_topik,
                alokasi_waktu=user_input.alokasi_waktu,

                # Generated/Provided Content
                cp=cp_content,
                atp=atp_content,

                # Model choice
                llm_model_choice=llm_model_choice,

                # Metadata
                timestamp=datetime.now().isoformat(),
                status=PromptBuilderStatus.COMPLETE,
                processing_metadata={
                    "completeness_status": completeness_status.value,
                    "generation_required": completeness_status != InputCompleteness.COMPLETE,
                    "model_used": llm_model_choice
                }
            )

            await self._notify_callback(callback_func, "complete_input_ready", {
                "message": "Complete Input successfully created",
                "complete_input": complete_input.to_dict()
            })

            logger.success("Complete Input building process completed")
            return complete_input

        except Exception as e:
            logger.error(f"Error in building complete input: {str(e)}")
            await self._notify_callback(callback_func, "error", {
                "message": f"Error: {str(e)}"
            })
            raise

    async def _check_input_completeness(self, user_input: UserInput) -> InputCompleteness:
        """
        Mengecek kelengkapan input dari user

        Args:
            user_input: Input dari user

        Returns:
            InputCompleteness: Status kelengkapan
        """
        logger.debug("Checking input completeness")

        # Check basic required fields
        missing_basic = self._get_missing_fields(user_input)
        if missing_basic:
            logger.warning(f"Missing basic fields: {missing_basic}")
            return InputCompleteness.MISSING_BASIC_INFO

        # Check CP/ATP availability
        has_cp = user_input.cp and len(user_input.cp.strip()) > 0
        has_atp = user_input.atp and len(user_input.atp.strip()) > 0

        if not has_cp and not has_atp:
            logger.info("CP and ATP not provided, generation required")
            return InputCompleteness.MISSING_CP_ATP
        elif not has_cp or not has_atp:
            logger.info("Partial CP/ATP provided, completing missing part")
            return InputCompleteness.PARTIALLY_COMPLETE
        else:
            logger.info("Input is complete")
            return InputCompleteness.COMPLETE

    def _get_missing_fields(self, user_input: UserInput) -> List[str]:
        """
        Mendapatkan daftar field yang hilang

        Args:
            user_input: Input dari user

        Returns:
            List[str]: Daftar field yang hilang
        """
        missing = []
        input_dict = user_input.to_dict()

        for field in self.required_fields:
            value = input_dict.get(field)
            if not value or (isinstance(value, str) and len(value.strip()) == 0):
                missing.append(field)

        return missing

    async def _generate_cp_atp(
        self,
        user_input: UserInput,
        llm_model_choice: str,
        callback_func: Optional[callable] = None
    ) -> tuple[str, str]:
        """
        Generate CP dan ATP menggunakan RAG dan LLM

        Args:
            user_input: Input dari user
            llm_model_choice: Model LLM yang dipilih
            callback_func: Callback untuk update real-time

        Returns:
            tuple[str, str]: CP content dan ATP content
        """
        logger.info("Starting CP/ATP generation")

        try:
            # Step 1: Search relevant documents
            await self._notify_callback(callback_func, "searching_documents", {
                "message": "Searching for relevant CP/ATP documents..."
            })

            cp_documents = await self._search_relevant_documents(
                user_input, "cp", callback_func
            )
            atp_documents = await self._search_relevant_documents(
                user_input, "atp", callback_func
            )

            # Step 2: Generate CP
            cp_content = ""
            if not user_input.cp or len(user_input.cp.strip()) == 0:
                await self._notify_callback(callback_func, "generating_cp", {
                    "message": "Generating CP content..."
                })
                cp_content = await self._generate_cp(
                    user_input, cp_documents, llm_model_choice
                )
            else:
                cp_content = user_input.cp

            # Step 3: Generate ATP
            atp_content = ""
            if not user_input.atp or len(user_input.atp.strip()) == 0:
                await self._notify_callback(callback_func, "generating_atp", {
                    "message": "Generating ATP content..."
                })
                atp_content = await self._generate_atp(
                    user_input, atp_documents, llm_model_choice, cp_content
                )
            else:
                atp_content = user_input.atp

            logger.success("CP/ATP generation completed")
            return cp_content, atp_content

        except Exception as e:
            logger.error(f"Error generating CP/ATP: {str(e)}")
            raise

    async def _search_relevant_documents(
        self,
        user_input: UserInput,
        doc_type: str,
        callback_func: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Search dokumen yang relevan dari vector DB dan online jika perlu

        Args:
            user_input: Input dari user
            doc_type: Type dokumen ("cp" atau "atp")
            callback_func: Callback untuk update

        Returns:
            List[Dict]: Dokumen yang relevan
        """
        # Create search query
        search_query = f"{user_input.mata_pelajaran} {user_input.kelas} {user_input.fase} {user_input.topik}"

        # Search in vector DB first
        vector_results = await self.vector_db_service.search_documents(
            query=search_query,
            doc_type=doc_type,
            top_k=5
        )

        # If insufficient results, search online
        if len(vector_results) < 3:
            await self._notify_callback(callback_func, "searching_online", {
                "message": f"Searching online for additional {doc_type.upper()} references..."
            })

            online_query = f"{doc_type.upper()} {user_input.mata_pelajaran} kelas {user_input.kelas} {user_input.topik}"
            online_results = await self.online_search_service.search(online_query, max_results=3)

            # Combine results
            vector_results.extend(online_results)

        return vector_results

    async def _generate_cp(
        self,
        user_input: UserInput,
        documents: List[Dict[str, Any]],
        llm_model: str
    ) -> str:
        """
        Generate Capaian Pembelajaran (CP) menggunakan LLM

        Args:
            user_input: Input dari user
            documents: Dokumen referensi
            llm_model: Model LLM yang digunakan

        Returns:
            str: CP content yang dihasilkan
        """
        # Build context from documents
        context = "\n".join([doc.get("content", "") for doc in documents[:3]])

        prompt = f"""
Sebagai ahli kurikulum, buatlah Capaian Pembelajaran (CP) untuk:

Mata Pelajaran: {user_input.mata_pelajaran}
Kelas: {user_input.kelas}
Fase: {user_input.fase}
Topik: {user_input.topik}
Sub Topik: {user_input.sub_topik}

Referensi dokumen:
{context}

Buatlah CP yang:
1. Sesuai dengan kurikulum merdeka
2. Menggunakan kata kerja operasional yang tepat
3. Mencakup domain kognitif, afektif, dan psikomotorik
4. Spesifik untuk topik yang diminta
5. Sesuai dengan tingkat perkembangan siswa

CP:
"""

        response = await self.llm_service.generate_text(
            prompt=prompt,
            model=llm_model,
            max_tokens=1000
        )

        return response.strip()

    async def _generate_atp(
        self,
        user_input: UserInput,
        documents: List[Dict[str, Any]],
        llm_model: str,
        cp_content: str
    ) -> str:
        """
        Generate Alur Tujuan Pembelajaran (ATP) menggunakan LLM

        Args:
            user_input: Input dari user
            documents: Dokumen referensi
            llm_model: Model LLM yang digunakan
            cp_content: CP yang sudah dihasilkan

        Returns:
            str: ATP content yang dihasilkan
        """
        # Build context from documents
        context = "\n".join([doc.get("content", "") for doc in documents[:3]])

        prompt = f"""
Sebagai ahli kurikulum, buatlah Alur Tujuan Pembelajaran (ATP) untuk:

Mata Pelajaran: {user_input.mata_pelajaran}
Kelas: {user_input.kelas}
Fase: {user_input.fase}
Topik: {user_input.topik}
Sub Topik: {user_input.sub_topik}
Alokasi Waktu: {user_input.alokasi_waktu}

Capaian Pembelajaran (CP):
{cp_content}

Referensi dokumen:
{context}

Buatlah ATP yang:
1. Menguraikan CP menjadi tujuan pembelajaran yang terstruktur
2. Mengurutkan dari yang sederhana ke kompleks
3. Dapat dicapai dalam alokasi waktu yang tersedia
4. Menggunakan kata kerja operasional yang measurable
5. Sesuai dengan karakteristik siswa kelas {user_input.kelas}

ATP:
"""

        response = await self.llm_service.generate_text(
            prompt=prompt,
            model=llm_model,
            max_tokens=1500
        )

        return response.strip()

    async def _notify_callback(
        self,
        callback_func: Optional[callable],
        event_type: str,
        data: Dict[str, Any]
    ):
        """
        Notify callback function untuk real-time updates

        Args:
            callback_func: Callback function
            event_type: Jenis event
            data: Data yang dikirim
        """
        if callback_func:
            try:
                await callback_func(event_type, data)
            except Exception as e:
                logger.warning(f"Callback notification failed: {str(e)}")

    def validate_complete_input(self, complete_input: CompleteInput) -> ValidationResult:
        """
        Validasi Complete Input yang telah dibuat

        Args:
            complete_input: Complete Input yang akan divalidasi

        Returns:
            ValidationResult: Hasil validasi
        """
        logger.debug("Validating complete input")

        errors = []
        warnings = []

        # Check required fields
        if not complete_input.nama_guru:
            errors.append("Nama guru tidak boleh kosong")

        if not complete_input.mata_pelajaran:
            errors.append("Mata pelajaran tidak boleh kosong")

        if not complete_input.cp or len(complete_input.cp.strip()) == 0:
            errors.append("CP tidak boleh kosong")

        if not complete_input.atp or len(complete_input.atp.strip()) == 0:
            errors.append("ATP tidak boleh kosong")

        # Check content quality
        if len(complete_input.cp) < 100:
            warnings.append("CP mungkin terlalu singkat")

        if len(complete_input.atp) < 150:
            warnings.append("ATP mungkin terlalu singkat")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            validation_score=1.0 if is_valid else 0.0
        )
