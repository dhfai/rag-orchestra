from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.models import UserInput
from ..utils.logger import get_logger

logger = get_logger("RAGBase")

class BaseRAG(ABC):
    """
    Base abstract class for all RAG implementations
    """

    def __init__(self):
        self.name = self.__class__.__name__
        logger.rag_log(f"{self.name} initialized")

    @abstractmethod
    async def retrieve_documents(
        self,
        query: str,
        document_type: str = "general",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on query

        Args:
            query: Search query
            document_type: Type of document to search (cp, atp, modul_ajar)
            top_k: Number of top documents to retrieve

        Returns:
            List of retrieved documents with metadata
        """
        pass

    @abstractmethod
    async def generate_content(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate content using retrieved documents and LLM

        Args:
            query: Original query
            context_docs: Retrieved context documents
            content_type: Type of content to generate (cp, atp, etc.)
            user_input: User input data
            additional_context: Additional context for generation

        Returns:
            Generated content string
        """
        pass

    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from retrieved documents

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "Tidak ada dokumen relevan ditemukan."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            score = doc.get('score', 0.0)

            context_parts.append(f"""
            Dokumen {i} (Relevansi: {score:.2f}):
            Sumber: {source}
            Konten: {content[:500]}{'...' if len(content) > 500 else ''}
            """)

        return "\n".join(context_parts)

    def _build_prompt(
        self,
        query: str,
        context: str,
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt for LLM generation

        Args:
            query: Original query
            context: Context from retrieved documents
            content_type: Type of content to generate
            user_input: User input data
            additional_context: Additional context

        Returns:
            Formatted prompt string
        """
        base_info = f"""
        Mata Pelajaran: {user_input.mata_pelajaran}
        Kelas: {user_input.kelas}
        Topik: {user_input.topik}
        Sub Topik: {user_input.sub_topik}
        Alokasi Waktu: {user_input.alokasi_waktu}
        Nama Guru: {user_input.nama_guru}
        Nama Sekolah: {user_input.nama_sekolah}
        """

        if content_type == "cp":
            prompt = f"""
            Anda adalah ahli kurikulum yang bertugas membuat Capaian Pembelajaran (CP) berdasarkan Kurikulum Merdeka.

            Informasi Pembelajaran:
            {base_info}

            Konteks dari dokumen referensi:
            {context}

            Tugas: Buatlah Capaian Pembelajaran (CP) yang sesuai dengan informasi di atas.
            CP harus mencakup:
            1. Pengetahuan yang harus dikuasai peserta didik
            2. Keterampilan yang harus dimiliki
            3. Sikap yang harus ditunjukkan
            4. Sesuai dengan fase pembelajaran dan karakteristik peserta didik

            Format CP harus jelas, terstruktur, dan menggunakan kata kerja operasional yang tepat.
            """

        elif content_type == "atp":
            additional_cp = additional_context.get('cp_content', '') if additional_context else ''
            prompt = f"""
            Anda adalah ahli kurikulum yang bertugas membuat Alur Tujuan Pembelajaran (ATP) berdasarkan Kurikulum Merdeka.

            Informasi Pembelajaran:
            {base_info}

            Capaian Pembelajaran (CP) yang sudah ditetapkan:
            {additional_cp}

            Konteks dari dokumen referensi:
            {context}

            Tugas: Buatlah Alur Tujuan Pembelajaran (ATP) yang merinci langkah-langkah pembelajaran untuk mencapai CP di atas.
            ATP harus mencakup:
            1. Urutan tujuan pembelajaran yang logis dan sistematis
            2. Indikator pencapaian untuk setiap tujuan
            3. Estimasi waktu untuk setiap tahapan
            4. Keterkaitan antar tujuan pembelajaran

            ATP harus sesuai dengan alokasi waktu yang tersedia dan karakteristik peserta didik.
            """

        elif content_type in ["cp_refinement", "atp_refinement"]:
            original_content = additional_context.get('original_content', '') if additional_context else ''
            feedback = additional_context.get('feedback', '') if additional_context else ''

            content_name = "Capaian Pembelajaran (CP)" if "cp" in content_type else "Alur Tujuan Pembelajaran (ATP)"

            prompt = f"""
            Anda adalah ahli kurikulum yang bertugas memperbaiki {content_name} berdasarkan feedback pengguna.

            Informasi Pembelajaran:
            {base_info}

            {content_name} Original:
            {original_content}

            Feedback dari Pengguna:
            {feedback}

            Konteks tambahan dari dokumen referensi:
            {context}

            Tugas: Perbaiki {content_name} berdasarkan feedback di atas. Pastikan perbaikan:
            1. Mengatasi semua poin yang disebutkan dalam feedback
            2. Tetap sesuai dengan standar Kurikulum Merdeka
            3. Mempertahankan aspek baik dari versi original
            4. Meningkatkan kualitas dan relevansi
            """

        else:
            prompt = f"""
            Anda adalah ahli kurikulum. Berdasarkan informasi berikut:

            {base_info}

            Konteks:
            {context}

            Query: {query}

            Silakan berikan respons yang sesuai dengan kebutuhan pembelajaran.
            """

        return prompt.strip()

    async def _simulate_llm_call(self, prompt: str, model: str = "gemini-1.5-flash") -> str:
        """
        Simulate LLM API call (placeholder for actual implementation)

        Args:
            prompt: Prompt to send to LLM
            model: Model to use

        Returns:
            Generated response
        """
        # This is a placeholder - in actual implementation,
        # this would call the actual LLM API (Gemini or OpenAI)

        logger.rag_log(f"Simulating LLM call with {model}")

        # Simulate processing time
        import asyncio
        await asyncio.sleep(1)

        # Return simulated response based on content type
        if "Capaian Pembelajaran" in prompt:
            return self._generate_sample_cp()
        elif "Alur Tujuan Pembelajaran" in prompt:
            return self._generate_sample_atp()
        else:
            return "Generated content based on provided context and requirements."

    def _generate_sample_cp(self) -> str:
        """Generate sample CP content"""
        return """
        CAPAIAN PEMBELAJARAN (CP)

        Pada akhir pembelajaran, peserta didik diharapkan mampu:

        1. PENGETAHUAN
           - Memahami konsep dasar materi pembelajaran
           - Menjelaskan hubungan antar konsep yang dipelajari
           - Menganalisis karakteristik dan ciri-ciri khusus materi

        2. KETERAMPILAN
           - Mengaplikasikan konsep dalam situasi nyata
           - Melakukan praktik sesuai prosedur yang benar
           - Mempresentasikan hasil pembelajaran dengan baik

        3. SIKAP
           - Menunjukkan sikap kritis dan analitis
           - Berpartisipasi aktif dalam kegiatan pembelajaran
           - Menghargai pendapat dan karya orang lain

        CP ini dirancang sesuai dengan fase pembelajaran dan karakteristik peserta didik
        dengan memperhatikan keberagaman kemampuan dan minat.
        """

    def _generate_sample_atp(self) -> str:
        """Generate sample ATP content"""
        return """
        ALUR TUJUAN PEMBELAJARAN (ATP)

        Tujuan Pembelajaran 1: Pemahaman Konsep Dasar (2 x 45 menit)
        - Indikator: Peserta didik dapat menjelaskan konsep dasar dengan benar
        - Kegiatan: Eksplorasi konsep melalui diskusi dan demonstrasi

        Tujuan Pembelajaran 2: Analisis dan Penerapan (2 x 45 menit)
        - Indikator: Peserta didik dapat menganalisis dan menerapkan konsep
        - Kegiatan: Studi kasus dan praktik terbimbing

        Tujuan Pembelajaran 3: Evaluasi dan Refleksi (1 x 45 menit)
        - Indikator: Peserta didik dapat mengevaluasi hasil pembelajaran
        - Kegiatan: Presentasi hasil dan refleksi pembelajaran

        Penilaian:
        - Penilaian formatif: Observasi selama proses pembelajaran
        - Penilaian sumatif: Tes tertulis dan presentasi

        Keterkaitan: Setiap tujuan pembelajaran saling berkaitan dan mendukung
        pencapaian CP secara keseluruhan.
        """
