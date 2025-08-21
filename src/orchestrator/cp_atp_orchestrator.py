from typing import Dict, Any, List
import asyncio
from ..core.models import UserInput, RAGStrategy, CPATPResult
from ..rag.simple_rag import SimpleRAG
from ..rag.advanced_rag import AdvancedRAG
from ..rag.graph_rag import GraphRAG
from ..utils.logger import get_logger

logger = get_logger("CPATPOrchestrator")

class CPATPOrchestrator:
    """
    CP/ATP Generation Sub-Orchestrator

    Komponen khusus untuk menangani pembuatan Capaian Pembelajaran (CP) dan
    Alur Tujuan Pembelajaran (ATP) dengan tiga mekanisme utama:
    1. Pemilihan strategi RAG berdasarkan konteks pembelajaran
    2. Pengelolaan proses generation dan validation
    3. Handling iterative refinement berdasarkan feedback
    """

    def __init__(self):
        self.simple_rag = SimpleRAG()
        self.advanced_rag = AdvancedRAG()
        self.graph_rag = GraphRAG()
        logger.orchestrator_log("CP/ATP Orchestrator initialized", "CP/ATP")

    async def generate_cp_atp(self, user_input: UserInput, strategy: RAGStrategy) -> CPATPResult:
        """
        Generate CP and ATP using specified RAG strategy

        Args:
            user_input: User input data
            strategy: RAG strategy to use

        Returns:
            CPATPResult: Generated CP and ATP content
        """
        logger.orchestrator_log(f"Starting CP/ATP generation with {strategy.value} strategy", "CP/ATP")

        try:
            # Select appropriate RAG implementation
            rag_instance = self._select_rag_instance(strategy)

            # Generate CP
            logger.orchestrator_log("Generating Capaian Pembelajaran (CP)", "CP/ATP")
            cp_content = await self._generate_cp(user_input, rag_instance)

            # Generate ATP
            logger.orchestrator_log("Generating Alur Tujuan Pembelajaran (ATP)", "CP/ATP")
            atp_content = await self._generate_atp(user_input, rag_instance, cp_content)

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(strategy, user_input)

            # Get sources used
            sources_used = self._get_sources_used(strategy, user_input)

            result = CPATPResult(
                cp_content=cp_content,
                atp_content=atp_content,
                generation_strategy=strategy,
                confidence_score=confidence_score,
                sources_used=sources_used
            )

            logger.orchestrator_log(
                f"CP/ATP generation completed with confidence: {confidence_score:.2f}",
                "CP/ATP"
            )

            return result

        except Exception as e:
            logger.error(f"Error in CP/ATP generation: {str(e)}")
            raise

    def _select_rag_instance(self, strategy: RAGStrategy):
        """Select appropriate RAG instance based on strategy"""
        if strategy == RAGStrategy.SIMPLE:
            logger.rag_log("Using Simple RAG for direct template retrieval", "Simple")
            return self.simple_rag
        elif strategy == RAGStrategy.ADVANCED:
            logger.rag_log("Using Advanced RAG with query rewriting and reranking", "Advanced")
            return self.advanced_rag
        elif strategy == RAGStrategy.GRAPH:
            logger.rag_log("Using Graph RAG for knowledge graph navigation", "Graph")
            return self.graph_rag
        else:
            raise ValueError(f"Unknown RAG strategy: {strategy}")

    async def _generate_cp(self, user_input: UserInput, rag_instance) -> str:
        """
        Generate Capaian Pembelajaran (CP) content

        Args:
            user_input: User input data
            rag_instance: RAG instance to use

        Returns:
            str: Generated CP content
        """
        logger.rag_log("Starting CP generation process")

        # Construct query for CP generation
        cp_query = self._construct_cp_query(user_input)

        # Retrieve relevant documents
        retrieved_docs = await rag_instance.retrieve_documents(cp_query, document_type="cp")

        # Generate CP using LLM
        cp_content = await rag_instance.generate_content(
            query=cp_query,
            context_docs=retrieved_docs,
            content_type="cp",
            user_input=user_input
        )

        logger.rag_log(f"CP generated successfully (length: {len(cp_content)} chars)")
        return cp_content

    async def _generate_atp(self, user_input: UserInput, rag_instance, cp_content: str) -> str:
        """
        Generate Alur Tujuan Pembelajaran (ATP) content

        Args:
            user_input: User input data
            rag_instance: RAG instance to use
            cp_content: Already generated CP content for context

        Returns:
            str: Generated ATP content
        """
        logger.rag_log("Starting ATP generation process")

        # Construct query for ATP generation
        atp_query = self._construct_atp_query(user_input, cp_content)

        # Retrieve relevant documents
        retrieved_docs = await rag_instance.retrieve_documents(atp_query, document_type="atp")

        # Generate ATP using LLM
        atp_content = await rag_instance.generate_content(
            query=atp_query,
            context_docs=retrieved_docs,
            content_type="atp",
            user_input=user_input,
            additional_context={"cp_content": cp_content}
        )

        logger.rag_log(f"ATP generated successfully (length: {len(atp_content)} chars)")
        return atp_content

    def _construct_cp_query(self, user_input: UserInput) -> str:
        """Construct search query for CP generation"""
        query = f"""
        Capaian Pembelajaran untuk mata pelajaran {user_input.mata_pelajaran}
        kelas {user_input.kelas} dengan topik {user_input.topik}
        dan sub topik {user_input.sub_topik}.
        Alokasi waktu: {user_input.alokasi_waktu}
        """
        return query.strip()

    def _construct_atp_query(self, user_input: UserInput, cp_content: str) -> str:
        """Construct search query for ATP generation"""
        query = f"""
        Alur Tujuan Pembelajaran untuk mata pelajaran {user_input.mata_pelajaran}
        kelas {user_input.kelas} dengan topik {user_input.topik}
        dan sub topik {user_input.sub_topik}.
        Alokasi waktu: {user_input.alokasi_waktu}

        Berdasarkan Capaian Pembelajaran berikut:
        {cp_content[:500]}...
        """
        return query.strip()

    def _calculate_confidence_score(self, strategy: RAGStrategy, user_input: UserInput) -> float:
        """Calculate confidence score based on strategy and input quality"""
        base_confidence = {
            RAGStrategy.SIMPLE: 0.7,
            RAGStrategy.ADVANCED: 0.8,
            RAGStrategy.GRAPH: 0.9
        }

        confidence = base_confidence[strategy]

        # Adjust based on input completeness
        if user_input.sub_topik and len(user_input.sub_topik) > 10:
            confidence += 0.05

        if user_input.alokasi_waktu and "menit" in user_input.alokasi_waktu.lower():
            confidence += 0.02

        # Adjust based on common subjects
        common_subjects = ["matematika", "bahasa indonesia", "ipas", "ppkn"]
        if user_input.mata_pelajaran.lower() in common_subjects:
            confidence += 0.03

        return min(confidence, 1.0)

    def _get_sources_used(self, strategy: RAGStrategy, user_input: UserInput) -> List[str]:
        """Get list of sources that would be used for generation"""
        sources = []

        # Add relevant CP documents
        sources.append(f"CP {user_input.mata_pelajaran} - Kurikulum Merdeka")

        # Add relevant ATP documents
        sources.append(f"ATP {user_input.mata_pelajaran} Kelas {user_input.kelas}")

        # Add strategy-specific sources
        if strategy == RAGStrategy.ADVANCED:
            sources.extend([
                "Panduan Pembelajaran Kurikulum Merdeka",
                "Modul Ajar Template"
            ])
        elif strategy == RAGStrategy.GRAPH:
            sources.extend([
                "Knowledge Graph - Relasi Konsep Pembelajaran",
                "Metadata Kurikulum Terstruktur",
                "Referensi Silang Mata Pelajaran"
            ])

        return sources

    async def refine_cp_atp(
        self,
        original_result: CPATPResult,
        feedback: str,
        user_input: UserInput
    ) -> CPATPResult:
        """
        Refine CP/ATP based on user feedback

        Args:
            original_result: Original CP/ATP generation result
            feedback: User feedback
            user_input: Original user input

        Returns:
            CPATPResult: Refined CP/ATP
        """
        logger.orchestrator_log("Starting CP/ATP refinement based on feedback", "CP/ATP")

        # Analyze feedback to determine refinement strategy
        refined_strategy = self._analyze_feedback_for_strategy(feedback, original_result.generation_strategy)

        # Get appropriate RAG instance
        rag_instance = self._select_rag_instance(refined_strategy)

        # Refine CP with feedback context
        refined_cp = await self._refine_cp_with_feedback(
            original_result.cp_content, feedback, user_input, rag_instance
        )

        # Refine ATP with feedback context
        refined_atp = await self._refine_atp_with_feedback(
            original_result.atp_content, feedback, user_input, rag_instance, refined_cp
        )

        # Calculate new confidence score
        new_confidence = min(original_result.confidence_score + 0.1, 1.0)

        refined_result = CPATPResult(
            cp_content=refined_cp,
            atp_content=refined_atp,
            generation_strategy=refined_strategy,
            confidence_score=new_confidence,
            sources_used=original_result.sources_used + ["User Feedback Analysis"]
        )

        logger.orchestrator_log("CP/ATP refinement completed", "CP/ATP")
        return refined_result

    def _analyze_feedback_for_strategy(self, feedback: str, current_strategy: RAGStrategy) -> RAGStrategy:
        """Analyze user feedback to determine best refinement strategy"""
        feedback_lower = feedback.lower()

        # Keywords that suggest need for more detailed approach
        detail_keywords = ['detail', 'lengkap', 'spesifik', 'mendalam', 'komprehensif']

        # Keywords that suggest need for simpler approach
        simple_keywords = ['sederhana', 'singkat', 'ringkas', 'simple', 'basic']

        if any(keyword in feedback_lower for keyword in detail_keywords):
            # User wants more detail, upgrade strategy
            if current_strategy == RAGStrategy.SIMPLE:
                return RAGStrategy.ADVANCED
            elif current_strategy == RAGStrategy.ADVANCED:
                return RAGStrategy.GRAPH

        elif any(keyword in feedback_lower for keyword in simple_keywords):
            # User wants simpler approach, downgrade strategy
            if current_strategy == RAGStrategy.GRAPH:
                return RAGStrategy.ADVANCED
            elif current_strategy == RAGStrategy.ADVANCED:
                return RAGStrategy.SIMPLE

        # Default: try next strategy in sequence
        strategy_cycle = [RAGStrategy.SIMPLE, RAGStrategy.ADVANCED, RAGStrategy.GRAPH]
        current_index = strategy_cycle.index(current_strategy)
        next_index = (current_index + 1) % len(strategy_cycle)

        return strategy_cycle[next_index]

    async def _refine_cp_with_feedback(
        self,
        original_cp: str,
        feedback: str,
        user_input: UserInput,
        rag_instance
    ) -> str:
        """Refine CP content based on feedback"""

        refinement_query = f"""
        Perbaiki Capaian Pembelajaran berikut berdasarkan feedback pengguna:

        CP Original:
        {original_cp}

        Feedback: {feedback}

        Konteks: {user_input.mata_pelajaran} - {user_input.topik} - Kelas {user_input.kelas}
        """

        # Retrieve additional documents for refinement
        retrieved_docs = await rag_instance.retrieve_documents(refinement_query, document_type="cp")

        # Generate refined CP
        refined_cp = await rag_instance.generate_content(
            query=refinement_query,
            context_docs=retrieved_docs,
            content_type="cp_refinement",
            user_input=user_input,
            additional_context={"original_content": original_cp, "feedback": feedback}
        )

        return refined_cp

    async def _refine_atp_with_feedback(
        self,
        original_atp: str,
        feedback: str,
        user_input: UserInput,
        rag_instance,
        refined_cp: str
    ) -> str:
        """Refine ATP content based on feedback"""

        refinement_query = f"""
        Perbaiki Alur Tujuan Pembelajaran berikut berdasarkan feedback pengguna:

        ATP Original:
        {original_atp}

        Feedback: {feedback}

        CP yang sudah diperbaiki:
        {refined_cp}

        Konteks: {user_input.mata_pelajaran} - {user_input.topik} - Kelas {user_input.kelas}
        """

        # Retrieve additional documents for refinement
        retrieved_docs = await rag_instance.retrieve_documents(refinement_query, document_type="atp")

        # Generate refined ATP
        refined_atp = await rag_instance.generate_content(
            query=refinement_query,
            context_docs=retrieved_docs,
            content_type="atp_refinement",
            user_input=user_input,
            additional_context={
                "original_content": original_atp,
                "feedback": feedback,
                "refined_cp": refined_cp
            }
        )

        return refined_atp

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "orchestrator": "CP/ATP",
            "status": "ready",
            "available_strategies": [strategy.value for strategy in RAGStrategy],
            "rag_instances": {
                "simple": "initialized",
                "advanced": "initialized",
                "graph": "initialized"
            }
        }
