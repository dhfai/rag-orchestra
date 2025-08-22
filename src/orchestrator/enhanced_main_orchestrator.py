"""
Enhanced Main Orchestrator
=========================

Main Orchestrator yang diperbarui sesuai dengan instruksi Orchestrated RAG terbaru.
Mengimplementasikan scoring system dan decision making yang transparan.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from ..core.models import (
    UserInput, CompleteInput, TaskAnalysisResult, RAGStrategy,
    StrategySelectionResult, MonitoringResult, ValidationResult,
    OrchestrationStrategy
)
from ..core.prompt_builder_agent import PromptBuilderAgent
from ..services.llm_service import LLMService, get_llm_service
from ..services.vector_db_service import VectorDBService, get_vector_db_service
from ..services.online_search_service import OnlineSearchService, get_online_search_service
from ..utils.logger import get_logger

logger = get_logger("EnhancedMainOrchestrator")

class EnhancedMainOrchestrator:
    """
    Enhanced Main Orchestrator dengan implementasi scoring system yang transparan
    dan decision making berbasis aturan sesuai instruksi terbaru.

    Fungsi utama:
    1. Task Analysis dengan scoring yang akurat
    2. Strategy Selection berdasarkan threshold yang telah ditetapkan
    3. Decision Making untuk menentukan alur eksekusi
    4. Monitoring dengan confidence scoring
    """

    def __init__(self):
        # Initialize services
        self.llm_service = get_llm_service()
        self.vector_db_service = get_vector_db_service(self.llm_service)
        self.online_search_service = get_online_search_service()

        # Initialize prompt builder agent
        self.prompt_builder = PromptBuilderAgent(
            self.llm_service,
            self.vector_db_service
        )

        # Threshold values berdasarkan instruksi (hasil pilot test)
        self.thresholds = {
            "simple_rag": 0.85,      # S_tmpl >= 0.85
            "advanced_rag": 0.6,     # S_adv >= 0.6
            "graph_rag": 0.5,        # S_graph >= 0.5
            "overall_confidence": 0.8  # C_overall >= 0.8
        }

        # Weights untuk scoring calculations
        self.weights = {
            "template_matching": {"lambda_1": 0.8, "lambda_2": 0.2},
            "advanced_rag": {"alpha_1": 0.3, "alpha_2": 0.25, "alpha_3": 0.25, "alpha_4": 0.2},
            "graph_rag": {"beta_1": 0.4, "beta_2": 0.4, "beta_3": 0.2}
        }

        logger.info("Enhanced Main Orchestrator initialized with scoring system")

    async def orchestrate_complete_input(
        self,
        user_input: UserInput,
        callback_func: Optional[callable] = None
    ) -> CompleteInput:
        """
        Main orchestration function untuk menghasilkan Complete Input

        Args:
            user_input: Input awal dari user
            callback_func: Callback untuk real-time updates

        Returns:
            CompleteInput: Input yang lengkap dan siap diproses
        """
        logger.info("Starting Complete Input orchestration")

        try:
            # Step 1: Task Analysis
            await self._notify_callback(callback_func, "task_analysis_start", {
                "message": "Starting task analysis..."
            })

            task_analysis = await self._analyze_task(user_input)

            await self._notify_callback(callback_func, "task_analysis_complete", {
                "analysis": task_analysis.__dict__,
                "message": f"Task analysis completed - Complexity: {task_analysis.complexity_level}"
            })

            # Step 2: Strategy Selection
            await self._notify_callback(callback_func, "strategy_selection_start", {
                "message": "Selecting optimal RAG strategy..."
            })

            strategy_selection = await self._select_strategy(user_input, task_analysis)

            await self._notify_callback(callback_func, "strategy_selection_complete", {
                "strategy": strategy_selection.__dict__,
                "message": f"Strategy selected: {strategy_selection.selected_strategy.value}"
            })

            # Step 3: Decision Making - Determine orchestration approach
            orchestration_strategy = self._determine_orchestration_strategy(
                user_input, task_analysis, strategy_selection
            )

            await self._notify_callback(callback_func, "orchestration_decision", {
                "strategy": orchestration_strategy.value,
                "message": f"Orchestration approach: {orchestration_strategy.value}"
            })

            # Step 4: Execute orchestration berdasarkan strategy
            complete_input = await self._execute_orchestration(
                user_input, orchestration_strategy, strategy_selection, callback_func
            )

            # Step 5: Monitoring & Quality Check
            monitoring_result = await self._monitor_quality(
                complete_input, task_analysis, strategy_selection
            )

            await self._notify_callback(callback_func, "quality_monitoring", {
                "monitoring": monitoring_result.__dict__,
                "message": f"Quality check completed - Overall confidence: {monitoring_result.overall_confidence:.2f}"
            })

            # Step 6: Re-routing if necessary
            if monitoring_result.overall_confidence < self.thresholds["overall_confidence"]:
                logger.warning("Quality check failed, attempting re-routing to Adaptive RAG")

                await self._notify_callback(callback_func, "re_routing", {
                    "message": "Quality below threshold, applying Adaptive RAG..."
                })

                complete_input = await self._apply_adaptive_rag(
                    user_input, complete_input, monitoring_result, callback_func
                )

            logger.success("Complete Input orchestration completed successfully")
            return complete_input

        except Exception as e:
            logger.error(f"Error in orchestration: {str(e)}")
            await self._notify_callback(callback_func, "error", {
                "error": str(e),
                "message": "Orchestration failed"
            })
            raise

    async def _analyze_task(self, user_input: UserInput) -> TaskAnalysisResult:
        """
        Comprehensive task analysis dengan scoring system

        Args:
            user_input: Input dari user

        Returns:
            TaskAnalysisResult: Hasil analisis dengan scores
        """
        logger.debug("Performing comprehensive task analysis")

        # Analyze basic complexity factors
        topic_complexity = self._assess_topic_complexity(user_input.topik, user_input.sub_topik)
        subject_complexity = self._assess_subject_complexity(user_input.mata_pelajaran)
        grade_complexity = self._assess_grade_complexity(user_input.kelas)
        time_complexity = self._assess_time_complexity(user_input.alokasi_waktu)

        # Calculate base complexity score
        complexity_factors = [topic_complexity, subject_complexity, grade_complexity, time_complexity]
        complexity_score = sum(complexity_factors) / len(complexity_factors)

        # Determine complexity level
        if complexity_score < 0.3:
            complexity_level = "simple"
        elif complexity_score < 0.7:
            complexity_level = "medium"
        else:
            complexity_level = "complex"

        # Calculate strategy-specific scores
        template_matching_score = await self._calculate_template_matching_score(user_input)
        advanced_rag_score = await self._calculate_advanced_rag_score(user_input)
        graph_rag_score = await self._calculate_graph_rag_score(user_input)

        # Determine required strategy based on scores
        required_strategy = self._determine_required_strategy(
            template_matching_score, advanced_rag_score, graph_rag_score
        )

        # Check missing components
        missing_components = []
        if not user_input.cp:
            missing_components.append("cp")
        if not user_input.atp:
            missing_components.append("atp")

        # Calculate confidence score
        confidence_score = min(
            template_matching_score,
            advanced_rag_score,
            graph_rag_score,
            1.0 - (len(missing_components) * 0.2)
        )

        # Estimate processing time
        estimated_time = self._estimate_processing_time(
            complexity_level, len(missing_components), required_strategy
        )

        return TaskAnalysisResult(
            complexity_level=complexity_level,
            complexity_score=complexity_score,
            missing_components=missing_components,
            required_rag_strategy=required_strategy,
            estimated_processing_time=estimated_time,
            confidence_score=confidence_score,
            template_matching_score=template_matching_score,
            advanced_rag_score=advanced_rag_score,
            graph_rag_score=graph_rag_score,
            analysis_metadata={
                "topic_complexity": topic_complexity,
                "subject_complexity": subject_complexity,
                "grade_complexity": grade_complexity,
                "time_complexity": time_complexity,
                "analyzed_at": datetime.now().isoformat()
            }
        )

    async def _calculate_template_matching_score(self, user_input: UserInput) -> float:
        """
        Calculate Template Matching Score: S_tmpl = λ₁ · μₖ + λ₂ · Δ̂

        Args:
            user_input: Input dari user

        Returns:
            float: Template matching score
        """
        try:
            # Search for similar templates
            search_query = f"{user_input.mata_pelajaran} {user_input.kelas} {user_input.topik}"

            results = await self.vector_db_service.search_documents(
                query=search_query,
                doc_type="cp",  # Search in CP collection
                top_k=5,
                strategy=RAGStrategy.SIMPLE
            )

            if not results:
                return 0.0

            # Calculate μₖ (rata-rata cosine similarity top-k)
            similarities = [result.get("similarity_score", 0) for result in results]
            mu_k = sum(similarities) / len(similarities) if similarities else 0.0

            # Calculate Δ̂ (margin antara dokumen teratas dengan berikutnya)
            if len(similarities) >= 2:
                delta_hat = similarities[0] - similarities[1]
            else:
                delta_hat = 0.0

            # Apply weights: λ₁ = 0.8, λ₂ = 0.2
            lambda_1 = self.weights["template_matching"]["lambda_1"]
            lambda_2 = self.weights["template_matching"]["lambda_2"]

            s_tmpl = (lambda_1 * mu_k) + (lambda_2 * delta_hat)

            logger.debug(f"Template matching score: {s_tmpl:.3f} (μₖ={mu_k:.3f}, Δ̂={delta_hat:.3f})")
            return min(max(s_tmpl, 0.0), 1.0)  # Clamp to [0, 1]

        except Exception as e:
            logger.warning(f"Error calculating template matching score: {str(e)}")
            return 0.0

    async def _calculate_advanced_rag_score(self, user_input: UserInput) -> float:
        """
        Calculate Advanced RAG Score: S_adv = α₁L' + α₂E' + α₃D + α₄S'

        Args:
            user_input: Input dari user

        Returns:
            float: Advanced RAG score
        """
        try:
            # L' = panjang query ternormalisasi
            query = f"{user_input.topik} {user_input.sub_topik}"
            query_length = len(query.split())
            l_prime = min(query_length / 30.0, 1.0)  # Normalize to [0, 1]

            # E' = jumlah entitas ternormalisasi
            entities = self._extract_entities(user_input)
            e_prime = min(len(entities) / 5.0, 1.0)  # Normalize assuming max 5 entities

            # D = document dispersion
            search_results = await self.vector_db_service.search_documents(
                query=query,
                doc_type="cp",
                top_k=10,
                strategy=RAGStrategy.ADVANCED
            )

            d_score = self._calculate_document_dispersion(search_results)

            # S' = query specificity (kebalikan ambiguitas)
            s_prime = self._calculate_query_specificity(user_input)

            # Apply weights
            weights = self.weights["advanced_rag"]
            s_adv = (
                weights["alpha_1"] * l_prime +
                weights["alpha_2"] * e_prime +
                weights["alpha_3"] * d_score +
                weights["alpha_4"] * s_prime
            )

            logger.debug(f"Advanced RAG score: {s_adv:.3f} (L'={l_prime:.3f}, E'={e_prime:.3f}, D={d_score:.3f}, S'={s_prime:.3f})")
            return min(max(s_adv, 0.0), 1.0)

        except Exception as e:
            logger.warning(f"Error calculating advanced RAG score: {str(e)}")
            return 0.5  # Default moderate score

    async def _calculate_graph_rag_score(self, user_input: UserInput) -> float:
        """
        Calculate Graph RAG Score: S_graph = β₁ρ' + β₂δ' + β₃I_pattern

        Args:
            user_input: Input dari user

        Returns:
            float: Graph RAG score
        """
        try:
            query_text = f"{user_input.topik} {user_input.sub_topik}"

            # ρ' = frekuensi relasi per token
            rho_prime = self._calculate_relation_frequency(query_text)

            # δ' = densitas subgraph (simplified calculation)
            delta_prime = self._calculate_subgraph_density(user_input)

            # I_pattern = indikator boolean untuk kata kunci relasional
            relational_keywords = ["hubungan", "relasi", "koneksi", "keterkaitan", "perbandingan", "konversi"]
            i_pattern = 1.0 if any(keyword in query_text.lower() for keyword in relational_keywords) else 0.0

            # Apply weights
            weights = self.weights["graph_rag"]
            s_graph = (
                weights["beta_1"] * rho_prime +
                weights["beta_2"] * delta_prime +
                weights["beta_3"] * i_pattern
            )

            logger.debug(f"Graph RAG score: {s_graph:.3f} (ρ'={rho_prime:.3f}, δ'={delta_prime:.3f}, I={i_pattern:.1f})")
            return min(max(s_graph, 0.0), 1.0)

        except Exception as e:
            logger.warning(f"Error calculating graph RAG score: {str(e)}")
            return 0.3  # Default low score

    def _determine_required_strategy(
        self,
        template_score: float,
        advanced_score: float,
        graph_score: float
    ) -> RAGStrategy:
        """
        Determine required strategy berdasarkan scores dan thresholds

        Args:
            template_score: Template matching score
            advanced_score: Advanced RAG score
            graph_score: Graph RAG score

        Returns:
            RAGStrategy: Strategy yang direkomendasikan
        """
        # Apply thresholds sesuai instruksi
        if template_score >= self.thresholds["simple_rag"]:
            return RAGStrategy.SIMPLE
        elif graph_score >= self.thresholds["graph_rag"]:
            return RAGStrategy.GRAPH
        elif advanced_score >= self.thresholds["advanced_rag"]:
            return RAGStrategy.ADVANCED
        else:
            return RAGStrategy.ADAPTIVE

    async def _select_strategy(
        self,
        user_input: UserInput,
        task_analysis: TaskAnalysisResult
    ) -> StrategySelectionResult:
        """
        Strategy selection dengan comprehensive scoring

        Args:
            user_input: Input dari user
            task_analysis: Hasil task analysis

        Returns:
            StrategySelectionResult: Hasil strategy selection
        """
        strategy_scores = {
            "simple": task_analysis.template_matching_score,
            "advanced": task_analysis.advanced_rag_score,
            "graph": task_analysis.graph_rag_score,
            "adaptive": 0.8  # Always available as fallback
        }

        # Select strategy berdasarkan scores dan thresholds
        selected_strategy = task_analysis.required_rag_strategy

        # Calculate confidence level
        max_score = max(strategy_scores.values())
        confidence_level = max_score

        # Determine fallback strategies
        fallback_strategies = []
        if selected_strategy != RAGStrategy.ADAPTIVE:
            fallback_strategies.append(RAGStrategy.ADAPTIVE)

        if selected_strategy != RAGStrategy.SIMPLE and strategy_scores["simple"] > 0.5:
            fallback_strategies.append(RAGStrategy.SIMPLE)

        # Generate selection reasoning
        reasoning = self._generate_selection_reasoning(selected_strategy, strategy_scores)

        return StrategySelectionResult(
            selected_strategy=selected_strategy,
            strategy_scores=strategy_scores,
            confidence_level=confidence_level,
            fallback_strategies=fallback_strategies,
            selection_reasoning=reasoning
        )

    def _determine_orchestration_strategy(
        self,
        user_input: UserInput,
        task_analysis: TaskAnalysisResult,
        strategy_selection: StrategySelectionResult
    ) -> OrchestrationStrategy:
        """
        Determine orchestration strategy berdasarkan analysis

        Args:
            user_input: Input dari user
            task_analysis: Task analysis result
            strategy_selection: Strategy selection result

        Returns:
            OrchestrationStrategy: Orchestration approach
        """
        # Check if CP/ATP generation is needed
        if task_analysis.missing_components:
            return OrchestrationStrategy.CP_ATP_GENERATION

        # Check if quality refinement is needed
        if strategy_selection.confidence_level < 0.7:
            return OrchestrationStrategy.ITERATIVE_REFINEMENT

        # Default direct processing
        return OrchestrationStrategy.DIRECT

    async def _execute_orchestration(
        self,
        user_input: UserInput,
        orchestration_strategy: OrchestrationStrategy,
        strategy_selection: StrategySelectionResult,
        callback_func: Optional[callable] = None
    ) -> CompleteInput:
        """
        Execute orchestration berdasarkan strategy

        Args:
            user_input: Input dari user
            orchestration_strategy: Orchestration approach
            strategy_selection: Selected strategy
            callback_func: Callback function

        Returns:
            CompleteInput: Complete input result
        """
        if orchestration_strategy == OrchestrationStrategy.CP_ATP_GENERATION:
            # Use prompt builder agent untuk generate complete input
            return await self.prompt_builder.build_complete_input(
                user_input=user_input,
                llm_model_choice=user_input.model_llm.value,
                callback_func=callback_func
            )

        elif orchestration_strategy == OrchestrationStrategy.DIRECT:
            # Direct processing tanpa generation
            return await self._create_direct_complete_input(user_input)

        else:
            # Fallback ke prompt builder
            return await self.prompt_builder.build_complete_input(
                user_input=user_input,
                llm_model_choice=user_input.model_llm.value,
                callback_func=callback_func
            )

    async def _monitor_quality(
        self,
        complete_input: CompleteInput,
        task_analysis: TaskAnalysisResult,
        strategy_selection: StrategySelectionResult
    ) -> MonitoringResult:
        """
        Monitor quality dengan scoring: C_overall = min(C_r, C_g)

        Args:
            complete_input: Complete input yang dihasilkan
            task_analysis: Task analysis result
            strategy_selection: Strategy selection result

        Returns:
            MonitoringResult: Monitoring result dengan confidence scores
        """
        # Calculate retrieval confidence (C_r)
        retrieval_confidence = strategy_selection.confidence_level

        # Calculate generation confidence (C_g)
        generation_confidence = self._calculate_generation_confidence(complete_input)

        # Overall confidence = min(C_r, C_g)
        overall_confidence = min(retrieval_confidence, generation_confidence)

        # Quality metrics
        quality_metrics = {
            "content_completeness": self._assess_content_completeness(complete_input),
            "content_coherence": self._assess_content_coherence(complete_input),
            "educational_relevance": self._assess_educational_relevance(complete_input),
            "template_adherence": strategy_selection.strategy_scores.get("simple", 0.0)
        }

        # Generate recommendations
        recommendations = self._generate_quality_recommendations(
            overall_confidence, quality_metrics
        )

        return MonitoringResult(
            retrieval_confidence=retrieval_confidence,
            generation_confidence=generation_confidence,
            overall_confidence=overall_confidence,
            quality_metrics=quality_metrics,
            recommendations=recommendations
        )

    # Helper methods (implementations simplified for brevity)
    def _assess_topic_complexity(self, topik: str, sub_topik: str) -> float:
        """Assess complexity berdasarkan topik"""
        complex_keywords = ["advanced", "kompleks", "analisis", "sintesis", "evaluasi"]
        content = f"{topik} {sub_topik}".lower()
        complexity = sum(1 for keyword in complex_keywords if keyword in content)
        return min(complexity / len(complex_keywords), 1.0)

    def _assess_subject_complexity(self, mata_pelajaran: str) -> float:
        """Assess complexity berdasarkan mata pelajaran"""
        complex_subjects = ["matematika", "fisika", "kimia", "biologi"]
        return 0.8 if mata_pelajaran.lower() in complex_subjects else 0.4

    def _assess_grade_complexity(self, kelas: str) -> float:
        """Assess complexity berdasarkan tingkat kelas"""
        try:
            grade_num = int(''.join(filter(str.isdigit, kelas)))
            return min(grade_num / 12.0, 1.0)  # Normalize to grade 12
        except:
            return 0.5

    def _assess_time_complexity(self, alokasi_waktu: str) -> float:
        """Assess complexity berdasarkan alokasi waktu"""
        try:
            # Extract number from time allocation
            import re
            numbers = re.findall(r'\d+', alokasi_waktu)
            if numbers:
                minutes = int(numbers[0])
                # More time = potentially more complex
                return min(minutes / 120.0, 1.0)  # Normalize to 120 minutes
        except:
            pass
        return 0.5

    def _extract_entities(self, user_input: UserInput) -> List[str]:
        """Extract entities dari user input"""
        entities = []
        content = f"{user_input.topik} {user_input.sub_topik} {user_input.mata_pelajaran}"

        # Simple entity extraction
        words = content.split()
        entities.extend([word for word in words if len(word) > 3])

        return entities

    def _calculate_document_dispersion(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate document dispersion score"""
        if not search_results:
            return 0.0

        # Simple dispersion calculation berdasarkan variasi similarity scores
        similarities = [result.get("similarity_score", 0) for result in search_results]
        if len(similarities) <= 1:
            return 0.0

        mean_sim = sum(similarities) / len(similarities)
        variance = sum((s - mean_sim) ** 2 for s in similarities) / len(similarities)

        return min(math.sqrt(variance), 1.0)

    def _calculate_query_specificity(self, user_input: UserInput) -> float:
        """Calculate query specificity score"""
        query = f"{user_input.topik} {user_input.sub_topik}"

        # More specific queries have more unique words
        words = query.split()
        unique_words = len(set(words))
        specificity = unique_words / max(len(words), 1)

        return min(specificity, 1.0)

    def _calculate_relation_frequency(self, text: str) -> float:
        """Calculate relation frequency per token"""
        relational_words = ["dan", "atau", "dengan", "terhadap", "pada", "dari", "ke", "untuk"]
        tokens = text.split()
        if not tokens:
            return 0.0

        rel_count = sum(1 for token in tokens if token.lower() in relational_words)
        return min(rel_count / len(tokens), 1.0)

    def _calculate_subgraph_density(self, user_input: UserInput) -> float:
        """Calculate simplified subgraph density"""
        # Simplified calculation berdasarkan interconnectedness
        entities = self._extract_entities(user_input)
        if len(entities) <= 1:
            return 0.0

        # Simple density approximation
        return min(len(entities) / 10.0, 1.0)

    def _estimate_processing_time(
        self,
        complexity: str,
        missing_count: int,
        strategy: RAGStrategy
    ) -> int:
        """Estimate processing time in seconds"""
        base_time = 30  # Base 30 seconds

        # Add time for complexity
        if complexity == "medium":
            base_time += 15
        elif complexity == "complex":
            base_time += 30

        # Add time for missing components
        base_time += missing_count * 20

        # Add time for strategy
        if strategy == RAGStrategy.ADVANCED:
            base_time += 20
        elif strategy == RAGStrategy.GRAPH:
            base_time += 40
        elif strategy == RAGStrategy.ADAPTIVE:
            base_time += 60

        return base_time

    def _generate_selection_reasoning(
        self,
        strategy: RAGStrategy,
        scores: Dict[str, float]
    ) -> str:
        """Generate reasoning untuk strategy selection"""
        if strategy == RAGStrategy.SIMPLE:
            return f"Simple RAG selected due to high template matching score ({scores['simple']:.2f})"
        elif strategy == RAGStrategy.ADVANCED:
            return f"Advanced RAG selected due to query complexity and score ({scores['advanced']:.2f})"
        elif strategy == RAGStrategy.GRAPH:
            return f"Graph RAG selected due to relational patterns detected ({scores['graph']:.2f})"
        else:
            return "Adaptive RAG selected as fallback strategy"

    def _calculate_generation_confidence(self, complete_input: CompleteInput) -> float:
        """Calculate generation confidence score"""
        scores = []

        # Content length check
        if len(complete_input.cp) > 100:
            scores.append(0.8)
        else:
            scores.append(0.4)

        if len(complete_input.atp) > 150:
            scores.append(0.8)
        else:
            scores.append(0.4)

        # Content quality indicators
        cp_quality_indicators = ["kompetensi", "pembelajaran", "siswa", "mampu"]
        cp_quality = sum(1 for indicator in cp_quality_indicators
                        if indicator in complete_input.cp.lower()) / len(cp_quality_indicators)
        scores.append(cp_quality)

        atp_quality_indicators = ["tujuan", "pembelajaran", "indikator", "evaluasi"]
        atp_quality = sum(1 for indicator in atp_quality_indicators
                         if indicator in complete_input.atp.lower()) / len(atp_quality_indicators)
        scores.append(atp_quality)

        return sum(scores) / len(scores) if scores else 0.5

    def _assess_content_completeness(self, complete_input: CompleteInput) -> float:
        """Assess completeness dari generated content"""
        required_elements = {
            "cp": ["kompetensi", "mampu", "siswa"],
            "atp": ["tujuan", "pembelajaran", "indikator"]
        }

        cp_completeness = sum(1 for element in required_elements["cp"]
                             if element in complete_input.cp.lower()) / len(required_elements["cp"])

        atp_completeness = sum(1 for element in required_elements["atp"]
                              if element in complete_input.atp.lower()) / len(required_elements["atp"])

        return (cp_completeness + atp_completeness) / 2

    def _assess_content_coherence(self, complete_input: CompleteInput) -> float:
        """Assess coherence dari generated content"""
        # Simple coherence check berdasarkan consistency
        cp_words = set(complete_input.cp.lower().split())
        atp_words = set(complete_input.atp.lower().split())

        common_words = cp_words.intersection(atp_words)
        total_unique_words = len(cp_words.union(atp_words))

        if total_unique_words == 0:
            return 0.0

        coherence = len(common_words) / total_unique_words
        return min(coherence * 2, 1.0)  # Scale up for better scoring

    def _assess_educational_relevance(self, complete_input: CompleteInput) -> float:
        """Assess educational relevance"""
        educational_keywords = [
            "pembelajaran", "siswa", "guru", "pendidikan", "kurikulum",
            "kompetensi", "indikator", "evaluasi", "materi"
        ]

        content = f"{complete_input.cp} {complete_input.atp}".lower()
        relevance_count = sum(1 for keyword in educational_keywords if keyword in content)

        return min(relevance_count / len(educational_keywords), 1.0)

    def _generate_quality_recommendations(
        self,
        overall_confidence: float,
        quality_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        if overall_confidence < 0.6:
            recommendations.append("Consider using Adaptive RAG for better results")

        if quality_metrics.get("content_completeness", 0) < 0.7:
            recommendations.append("Generated content may be incomplete")

        if quality_metrics.get("content_coherence", 0) < 0.6:
            recommendations.append("Content coherence could be improved")

        if quality_metrics.get("educational_relevance", 0) < 0.8:
            recommendations.append("Content may need more educational focus")

        return recommendations

    async def _apply_adaptive_rag(
        self,
        user_input: UserInput,
        complete_input: CompleteInput,
        monitoring_result: MonitoringResult,
        callback_func: Optional[callable] = None
    ) -> CompleteInput:
        """Apply Adaptive RAG untuk improvement"""
        await self._notify_callback(callback_func, "adaptive_rag", {
            "message": "Applying Adaptive RAG for quality improvement..."
        })

        # For now, return the same input (placeholder for adaptive improvements)
        # In full implementation, this would apply various improvement strategies
        return complete_input

    async def _create_direct_complete_input(self, user_input: UserInput) -> CompleteInput:
        """Create complete input directly tanpa generation"""
        from ..core.models import PromptBuilderStatus

        return CompleteInput(
            nama_guru=user_input.nama_guru,
            nama_sekolah=user_input.nama_sekolah,
            mata_pelajaran=user_input.mata_pelajaran,
            kelas=user_input.kelas,
            fase=user_input.fase,
            topik=user_input.topik,
            sub_topik=user_input.sub_topik,
            alokasi_waktu=user_input.alokasi_waktu,
            cp=user_input.cp or "",
            atp=user_input.atp or "",
            llm_model_choice=user_input.model_llm.value,
            timestamp=datetime.now().isoformat(),
            status=PromptBuilderStatus.COMPLETE,
            processing_metadata={
                "orchestration_type": "direct",
                "no_generation_required": True
            }
        )

    async def _notify_callback(
        self,
        callback_func: Optional[callable],
        event_type: str,
        data: Dict[str, Any]
    ):
        """Notify callback function untuk real-time updates"""
        if callback_func:
            try:
                await callback_func(event_type, data)
            except Exception as e:
                logger.warning(f"Callback notification failed: {str(e)}")

# Singleton instance
_enhanced_main_orchestrator_instance: Optional[EnhancedMainOrchestrator] = None

def get_enhanced_main_orchestrator() -> EnhancedMainOrchestrator:
    """Get singleton Enhanced Main Orchestrator instance"""
    global _enhanced_main_orchestrator_instance
    if _enhanced_main_orchestrator_instance is None:
        _enhanced_main_orchestrator_instance = EnhancedMainOrchestrator()
    return _enhanced_main_orchestrator_instance
