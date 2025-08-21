import asyncio
from typing import List, Dict, Any, Optional
from .base_rag import BaseRAG
from ..core.models import UserInput
from ..utils.logger import get_logger

logger = get_logger("AdvancedRAG")

class AdvancedRAG(BaseRAG):
    """
    Advanced RAG implementation with query rewriting and reranking

    Strategy: Query expansion, semantic search, result reranking, and contextual generation
    Use case: Complex queries yang memerlukan sintesis dari berbagai sumber
    """

    def __init__(self):
        super().__init__()
        self.query_cache = {}
        self.embedding_cache = {}
        self._initialize_advanced_components()

    def _initialize_advanced_components(self):
        """Initialize advanced RAG components"""
        logger.rag_log("Initializing Advanced RAG components", "Advanced")

        # Simulate initialization of advanced components
        self.query_rewriter = QueryRewriter()
        self.semantic_searcher = SemanticSearcher()
        self.result_reranker = ResultReranker()
        self.context_synthesizer = ContextSynthesizer()

        logger.rag_log("Advanced RAG components initialized", "Advanced")

    async def retrieve_documents(
        self,
        query: str,
        document_type: str = "general",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Advanced document retrieval with query rewriting and semantic search

        Args:
            query: Original search query
            document_type: Type of document to search
            top_k: Number of top documents to retrieve

        Returns:
            List of retrieved and reranked documents
        """
        logger.rag_log(f"Starting advanced retrieval for: {query[:50]}...", "Advanced")

        # Step 1: Query Rewriting and Expansion
        expanded_queries = await self.query_rewriter.rewrite_and_expand(query, document_type)
        logger.rag_log(f"Generated {len(expanded_queries)} expanded queries", "Advanced")

        # Step 2: Semantic Search for each expanded query
        all_candidates = []
        for expanded_query in expanded_queries:
            candidates = await self.semantic_searcher.search(expanded_query, document_type, top_k * 2)
            all_candidates.extend(candidates)

        # Step 3: Remove duplicates and merge results
        unique_candidates = self._deduplicate_documents(all_candidates)
        logger.rag_log(f"Found {len(unique_candidates)} unique candidate documents", "Advanced")

        # Step 4: Rerank results based on relevance and quality
        reranked_docs = await self.result_reranker.rerank(
            query, unique_candidates, document_type, top_k
        )

        logger.rag_log(f"Retrieved {len(reranked_docs)} reranked documents", "Advanced")
        return reranked_docs

    async def generate_content(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate content using Advanced RAG with contextual synthesis

        Args:
            query: Original query
            context_docs: Retrieved context documents
            content_type: Type of content to generate
            user_input: User input data
            additional_context: Additional context

        Returns:
            Generated and synthesized content
        """
        logger.rag_log(f"Generating {content_type} content using Advanced RAG", "Advanced")

        # Step 1: Synthesize context from multiple sources
        synthesized_context = await self.context_synthesizer.synthesize(
            context_docs, query, content_type
        )

        # Step 2: Build advanced prompt with structured context
        prompt = self._build_advanced_prompt(
            query, synthesized_context, content_type, user_input, additional_context
        )

        # Step 3: Generate content with iterative refinement
        generated_content = await self._generate_with_refinement(
            prompt, user_input.model_llm.value, content_type
        )

        # Step 4: Post-process and validate content
        final_content = self._post_process_advanced_content(
            generated_content, content_type, user_input, context_docs
        )

        logger.rag_log(f"Advanced content generated (length: {len(final_content)} chars)", "Advanced")
        return final_content

    def _deduplicate_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate documents based on content similarity"""
        unique_docs = []
        seen_contents = set()

        for doc in documents:
            content_hash = hash(doc.get('content', '')[:200])  # Use first 200 chars for similarity
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_docs.append(doc)

        return unique_docs

    def _build_advanced_prompt(
        self,
        query: str,
        synthesized_context: str,
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build advanced prompt with structured context"""

        base_prompt = self._build_prompt(query, synthesized_context, content_type, user_input, additional_context)

        # Add advanced instructions for better generation
        advanced_instructions = """

        INSTRUKSI LANJUTAN:
        1. Gunakan pendekatan multi-perspektif dalam analisis
        2. Sintesis informasi dari berbagai sumber yang tersedia
        3. Pastikan konten yang dihasilkan komprehensif dan mendalam
        4. Sertakan variasi metode dan pendekatan pembelajaran
        5. Perhatikan diferensiasi untuk keberagaman peserta didik
        6. Integrasikan teknologi dan metode pembelajaran modern
        7. Pastikan kesesuaian dengan karakteristik Kurikulum Merdeka
        """

        return base_prompt + advanced_instructions

    async def _generate_with_refinement(
        self,
        prompt: str,
        model: str,
        content_type: str,
        max_iterations: int = 2
    ) -> str:
        """Generate content with iterative refinement"""

        # Initial generation
        content = await self._simulate_llm_call(prompt, model)

        # Iterative refinement
        for iteration in range(max_iterations):
            logger.rag_log(f"Refinement iteration {iteration + 1}", "Advanced")

            # Analyze content quality
            quality_score = self._analyze_content_quality(content, content_type)

            if quality_score > 0.8:  # Good enough quality
                break

            # Refine prompt and regenerate
            refined_prompt = self._refine_prompt_for_quality(prompt, content, content_type)
            content = await self._simulate_llm_call(refined_prompt, model)

        return content

    def _analyze_content_quality(self, content: str, content_type: str) -> float:
        """Analyze quality of generated content"""

        quality_factors = []

        # Length appropriateness
        min_length = 500 if content_type in ["cp", "atp"] else 200
        length_score = min(len(content) / min_length, 1.0)
        quality_factors.append(length_score)

        # Structure presence
        structure_keywords = ["1.", "2.", "3.", "-", "•", "TUJUAN", "INDIKATOR", "KEGIATAN"]
        structure_score = sum(1 for keyword in structure_keywords if keyword in content) / len(structure_keywords)
        quality_factors.append(structure_score)

        # Educational terminology
        edu_keywords = [
            "pembelajaran", "peserta didik", "kompetensi", "indikator",
            "tujuan", "kegiatan", "penilaian", "metode"
        ]
        edu_score = sum(1 for keyword in edu_keywords if keyword.lower() in content.lower()) / len(edu_keywords)
        quality_factors.append(edu_score)

        return sum(quality_factors) / len(quality_factors)

    def _refine_prompt_for_quality(self, original_prompt: str, current_content: str, content_type: str) -> str:
        """Refine prompt to improve content quality"""

        refinement_instruction = f"""

        PERBAIKAN DIPERLUKAN:
        Konten sebelumnya kurang memenuhi standar kualitas. Silakan perbaiki dengan:

        Konten Sebelumnya:
        {current_content[:300]}...

        Perbaikan yang diperlukan:
        1. Struktur yang lebih jelas dan sistematis
        2. Terminologi pendidikan yang lebih tepat
        3. Detail yang lebih komprehensif
        4. Format yang lebih terorganisir
        5. Kesesuaian dengan standar Kurikulum Merdeka

        {original_prompt}
        """

        return refinement_instruction

    def _post_process_advanced_content(
        self,
        content: str,
        content_type: str,
        user_input: UserInput,
        context_docs: List[Dict[str, Any]]
    ) -> str:
        """Post-process content with advanced enhancements"""

        # Add advanced header
        header = f"""
        ╔══════════════════════════════════════════════════════════════╗
        ║  {content_type.upper()} - {user_input.mata_pelajaran.upper()}
        ║  Generated using Advanced RAG Strategy                      ║
        ╚══════════════════════════════════════════════════════════════╝

        📚 Mata Pelajaran: {user_input.mata_pelajaran}
        🎓 Kelas: {user_input.kelas}
        📖 Topik: {user_input.topik}
        📝 Sub Topik: {user_input.sub_topik}
        ⏰ Alokasi Waktu: {user_input.alokasi_waktu}
        👨‍🏫 Guru: {user_input.nama_guru}
        🏫 Sekolah: {user_input.nama_sekolah}
        """

        # Add content structure markers
        structured_content = self._add_content_structure(content, content_type)

        # Add references from context documents
        references = self._generate_references(context_docs)

        # Add metadata and analytics
        metadata = f"""

        ╔══════════════════════════════════════════════════════════════╗
        ║  METADATA & ANALYTICS                                        ║
        ╚══════════════════════════════════════════════════════════════╝

        📊 Generation Strategy: Advanced RAG
        🔍 Query Expansion: Multi-perspective analysis
        📚 Sources Analyzed: {len(context_docs)} documents
        🎯 Synthesis Approach: Multi-source integration
        ⚡ Refinement Iterations: Applied
        🎨 Content Enhancement: Structure optimization

        📖 References Used:
        {references}

        ⚙️ Technical Details:
        - Model: {user_input.model_llm.value}
        - Content Length: {len(structured_content)} characters
        - Quality Score: Advanced validation applied
        - Curriculum Alignment: Kurikulum Merdeka
        """

        return header + "\n\n" + structured_content + metadata

    def _add_content_structure(self, content: str, content_type: str) -> str:
        """Add visual structure to content"""

        # Add visual separators and structure
        if content_type == "cp":
            structure_markers = {
                "PENGETAHUAN": "🧠 ASPEK PENGETAHUAN",
                "KETERAMPILAN": "🛠️ ASPEK KETERAMPILAN",
                "SIKAP": "💫 ASPEK SIKAP",
                "1.": "📌 1.",
                "2.": "📌 2.",
                "3.": "📌 3."
            }
        elif content_type == "atp":
            structure_markers = {
                "Tujuan Pembelajaran": "🎯 Tujuan Pembelajaran",
                "Indikator": "✅ Indikator",
                "Kegiatan": "🎲 Kegiatan",
                "Penilaian": "📊 Penilaian"
            }
        else:
            structure_markers = {}

        enhanced_content = content
        for original, enhanced in structure_markers.items():
            enhanced_content = enhanced_content.replace(original, enhanced)

        return enhanced_content

    def _generate_references(self, context_docs: List[Dict[str, Any]]) -> str:
        """Generate formatted references from context documents"""
        if not context_docs:
            return "Tidak ada referensi khusus"

        references = []
        for i, doc in enumerate(context_docs[:5], 1):  # Top 5 references
            source = doc.get('source', 'Unknown')
            score = doc.get('score', 0.0)
            references.append(f"  {i}. {source} (Relevansi: {score:.2f})")

        return "\n".join(references)

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about Advanced RAG strategy"""
        return {
            "name": "Advanced RAG",
            "description": "Query rewriting, semantic search, and result reranking",
            "features": [
                "Query expansion and rewriting",
                "Semantic document search",
                "Multi-source synthesis",
                "Result reranking",
                "Iterative refinement",
                "Quality validation"
            ],
            "strengths": [
                "Comprehensive content generation",
                "Multi-perspective analysis",
                "High quality output",
                "Adaptive to complex queries"
            ],
            "best_for": [
                "Complex learning topics",
                "Multi-faceted subjects",
                "High-quality requirements",
                "Detailed analysis needs"
            ]
        }


class QueryRewriter:
    """Component for query rewriting and expansion"""

    async def rewrite_and_expand(self, query: str, document_type: str) -> List[str]:
        """Rewrite and expand query for better retrieval"""

        expanded_queries = [query]  # Original query

        # Add synonym variations
        expanded_queries.extend(self._generate_synonym_queries(query))

        # Add context-specific expansions
        expanded_queries.extend(self._generate_context_queries(query, document_type))

        # Add learning-specific expansions
        expanded_queries.extend(self._generate_learning_queries(query))

        return expanded_queries[:5]  # Limit to top 5 queries

    def _generate_synonym_queries(self, query: str) -> List[str]:
        """Generate queries with synonyms"""
        synonym_map = {
            "pembelajaran": ["belajar", "pendidikan", "pengajaran"],
            "peserta didik": ["siswa", "murid", "pelajar"],
            "tujuan": ["target", "capaian", "sasaran"],
            "kegiatan": ["aktivitas", "latihan", "praktik"]
        }

        synonym_queries = []
        for original, synonyms in synonym_map.items():
            if original in query.lower():
                for synonym in synonyms:
                    synonym_queries.append(query.lower().replace(original, synonym))

        return synonym_queries[:3]

    def _generate_context_queries(self, query: str, document_type: str) -> List[str]:
        """Generate context-specific queries"""
        if document_type == "cp":
            return [
                f"capaian pembelajaran {query}",
                f"kompetensi {query}",
                f"learning outcome {query}"
            ]
        elif document_type == "atp":
            return [
                f"alur tujuan pembelajaran {query}",
                f"learning trajectory {query}",
                f"rencana pembelajaran {query}"
            ]
        return []

    def _generate_learning_queries(self, query: str) -> List[str]:
        """Generate learning-specific expanded queries"""
        return [
            f"metode pembelajaran {query}",
            f"strategi mengajar {query}",
            f"pendekatan kurikulum merdeka {query}"
        ]


class SemanticSearcher:
    """Component for semantic document search"""

    async def search(self, query: str, document_type: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform semantic search"""

        # Simulate semantic search with vector embeddings
        # In actual implementation, this would use ChromaDB or similar

        search_results = []

        # Generate mock semantic search results
        base_score = 0.9
        for i in range(top_k):
            search_results.append({
                "content": f"Semantic search result {i+1} for query: {query[:30]}...",
                "source": f"Semantic Document {i+1}",
                "score": base_score - (i * 0.1),
                "metadata": {
                    "search_type": "semantic",
                    "query": query,
                    "document_type": document_type
                }
            })

        return search_results


class ResultReranker:
    """Component for reranking search results"""

    async def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        document_type: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Rerank candidates based on multiple factors"""

        # Calculate reranking scores
        for doc in candidates:
            rerank_score = self._calculate_rerank_score(doc, query, document_type)
            doc['rerank_score'] = rerank_score

        # Sort by rerank score
        reranked = sorted(candidates, key=lambda x: x.get('rerank_score', 0), reverse=True)

        return reranked[:top_k]

    def _calculate_rerank_score(self, doc: Dict[str, Any], query: str, document_type: str) -> float:
        """Calculate reranking score based on multiple factors"""

        base_score = doc.get('score', 0.5)

        # Factor 1: Content relevance
        content = doc.get('content', '').lower()
        query_words = query.lower().split()
        relevance_score = sum(1 for word in query_words if word in content) / len(query_words)

        # Factor 2: Source quality
        source = doc.get('source', '')
        quality_score = 0.8 if 'official' in source.lower() or 'kurikulum' in source.lower() else 0.6

        # Factor 3: Document type match
        type_score = 1.0 if document_type in source.lower() else 0.7

        # Combine scores
        final_score = (base_score * 0.4 + relevance_score * 0.3 + quality_score * 0.2 + type_score * 0.1)

        return min(final_score, 1.0)


class ContextSynthesizer:
    """Component for synthesizing context from multiple sources"""

    async def synthesize(
        self,
        documents: List[Dict[str, Any]],
        query: str,
        content_type: str
    ) -> str:
        """Synthesize context from multiple documents"""

        if not documents:
            return "Tidak ada dokumen konteks yang tersedia."

        # Group documents by relevance score
        high_relevance = [doc for doc in documents if doc.get('score', 0) > 0.8]
        medium_relevance = [doc for doc in documents if 0.5 <= doc.get('score', 0) <= 0.8]
        low_relevance = [doc for doc in documents if doc.get('score', 0) < 0.5]

        synthesis_parts = []

        # High relevance sources - primary context
        if high_relevance:
            synthesis_parts.append("=== SUMBER UTAMA (Relevansi Tinggi) ===")
            for doc in high_relevance[:3]:
                synthesis_parts.append(f"📚 {doc.get('source', 'Unknown')}")
                synthesis_parts.append(f"Konten: {doc.get('content', '')[:400]}...")
                synthesis_parts.append("")

        # Medium relevance sources - supporting context
        if medium_relevance:
            synthesis_parts.append("=== SUMBER PENDUKUNG (Relevansi Sedang) ===")
            for doc in medium_relevance[:2]:
                synthesis_parts.append(f"📖 {doc.get('source', 'Unknown')}")
                synthesis_parts.append(f"Konten: {doc.get('content', '')[:200]}...")
                synthesis_parts.append("")

        # Additional insights from all sources
        synthesis_parts.append("=== INSIGHT TAMBAHAN ===")
        key_insights = self._extract_key_insights(documents, content_type)
        synthesis_parts.extend(key_insights)

        return "\n".join(synthesis_parts)

    def _extract_key_insights(self, documents: List[Dict[str, Any]], content_type: str) -> List[str]:
        """Extract key insights from all documents"""

        insights = []

        # Extract common themes
        all_content = " ".join([doc.get('content', '') for doc in documents])

        if content_type == "cp":
            if "pengetahuan" in all_content.lower():
                insights.append("🧠 Fokus pada aspek pengetahuan teridentifikasi")
            if "keterampilan" in all_content.lower():
                insights.append("🛠️ Komponen keterampilan ditemukan")
            if "sikap" in all_content.lower():
                insights.append("💫 Aspek sikap perlu dipertimbangkan")

        elif content_type == "atp":
            if "urutan" in all_content.lower() or "tahap" in all_content.lower():
                insights.append("🔄 Struktur pembelajaran bertahap diperlukan")
            if "penilaian" in all_content.lower():
                insights.append("📊 Komponen penilaian harus terintegrasi")

        # Add general insights
        insights.append(f"📈 Total sumber referensi: {len(documents)}")
        insights.append("🎯 Pendekatan multi-perspektif direkomendasikan")

        return insights
