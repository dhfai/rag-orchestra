import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from .base_rag import BaseRAG
from ..core.models import UserInput
from ..utils.logger import get_logger

logger = get_logger("GraphRAG")

class GraphRAG(BaseRAG):
    """
    Graph RAG implementation for knowledge graph navigation and relational learning

    Strategy: Navigate knowledge graph untuk menemukan relasi antar konsep pembelajaran
    Use case: Kebutuhan relasional dan pemahaman holistik antar mata pelajaran
    """

    def __init__(self):
        super().__init__()
        self.knowledge_graph = None
        self.concept_relationships = {}
        self.learning_pathways = {}
        self._build_knowledge_graph()

    def _build_knowledge_graph(self):
        """Build knowledge graph for curriculum concepts"""
        logger.rag_log("Building curriculum knowledge graph", "Graph")

        # Simulate knowledge graph construction
        # In actual implementation, this would be built from structured curriculum data

        self.knowledge_graph = CurriculumKnowledgeGraph()
        self.concept_mapper = ConceptMapper()
        self.pathway_finder = LearningPathwayFinder()
        self.relationship_analyzer = RelationshipAnalyzer()

        # Initialize curriculum concepts and relationships
        self._initialize_curriculum_concepts()
        self._initialize_concept_relationships()
        self._initialize_learning_pathways()

        logger.rag_log("Knowledge graph built successfully", "Graph")

    def _initialize_curriculum_concepts(self):
        """Initialize curriculum concepts in the knowledge graph"""

        # Core subjects and their concepts
        self.curriculum_concepts = {
            "matematika": {
                "kelas_1": ["bilangan", "penjumlahan", "pengurangan", "geometri_dasar"],
                "kelas_2": ["perkalian", "pembagian", "pecahan_sederhana", "pengukuran"],
                "kelas_3": ["bilangan_ribuan", "pecahan", "bangun_datar", "waktu"],
                "kelas_4": ["bilangan_besar", "pecahan_campuran", "bangun_ruang", "statistik_dasar"],
                "kelas_5": ["desimal", "persentase", "volume", "data_dan_diagram"],
                "kelas_6": ["aljabar_dasar", "rasio", "lingkaran", "probabilitas"]
            },
            "bahasa_indonesia": {
                "kelas_1": ["huruf", "kata", "kalimat_sederhana", "cerita_pendek"],
                "kelas_2": ["paragraf", "puisi", "dialog", "pantun"],
                "kelas_3": ["teks_deskripsi", "teks_narasi", "kamus", "tanda_baca"],
                "kelas_4": ["teks_eksplanasi", "teks_prosedur", "sinonim_antonim", "majas"],
                "kelas_5": ["teks_argumentasi", "teks_laporan", "diskusi", "presentasi"],
                "kelas_6": ["teks_persuasi", "kritik_sastra", "debat", "karya_ilmiah"]
            },
            "ipas": {
                "kelas_3": ["makhluk_hidup", "benda_mati", "energi", "lingkungan"],
                "kelas_4": ["ekosistem", "siklus_air", "cuaca", "teknologi"],
                "kelas_5": ["sistem_tubuh", "planet", "perubahan_materi", "inovasi"],
                "kelas_6": ["evolusi", "tata_surya", "kimia_dasar", "teknologi_modern"]
            },
            "ppkn": {
                "kelas_1": ["pancasila", "norma", "keberagaman", "gotong_royong"],
                "kelas_2": ["nilai_pancasila", "aturan", "toleransi", "kerjasama"],
                "kelas_3": ["simbol_negara", "hak_kewajiban", "persatuan", "demokrasi_sederhana"],
                "kelas_4": ["konstitusi", "pemerintahan", "bhinneka_tunggal_ika", "musyawarah"],
                "kelas_5": ["sistem_pemerintahan", "otonomi_daerah", "wawasan_nusantara", "partisipasi"],
                "kelas_6": ["globalisasi", "diplomasi", "nasionalisme", "kepemimpinan"]
            }
        }

    def _initialize_concept_relationships(self):
        """Initialize relationships between concepts"""

        # Cross-subject relationships
        self.concept_relationships = {
            # Math-Science relationships
            ("matematika.geometri_dasar", "ipas.benda_mati"): "spatial_understanding",
            ("matematika.pengukuran", "ipas.siklus_air"): "quantitative_analysis",
            ("matematika.statistik_dasar", "ipas.cuaca"): "data_interpretation",
            ("matematika.probabilitas", "ipas.evolusi"): "scientific_prediction",

            # Language-Social relationships
            ("bahasa_indonesia.teks_deskripsi", "ppkn.keberagaman"): "descriptive_analysis",
            ("bahasa_indonesia.diskusi", "ppkn.musyawarah"): "democratic_communication",
            ("bahasa_indonesia.teks_argumentasi", "ppkn.demokrasi_sederhana"): "persuasive_reasoning",
            ("bahasa_indonesia.debat", "ppkn.partisipasi"): "civic_engagement",

            # Science-Social relationships
            ("ipas.lingkungan", "ppkn.gotong_royong"): "environmental_responsibility",
            ("ipas.teknologi", "ppkn.inovasi"): "technological_citizenship",
            ("ipas.teknologi_modern", "ppkn.globalisasi"): "digital_citizenship",

            # Sequential relationships within subjects
            ("matematika.bilangan", "matematika.penjumlahan"): "foundational_prerequisite",
            ("matematika.penjumlahan", "matematika.perkalian"): "operational_progression",
            ("bahasa_indonesia.huruf", "bahasa_indonesia.kata"): "literacy_progression",
            ("bahasa_indonesia.kata", "bahasa_indonesia.kalimat_sederhana"): "linguistic_development"
        }

    def _initialize_learning_pathways(self):
        """Initialize learning pathways across grades and subjects"""

        self.learning_pathways = {
            "mathematical_literacy": [
                "matematika.kelas_1.bilangan",
                "matematika.kelas_2.perkalian",
                "matematika.kelas_3.pecahan",
                "matematika.kelas_4.pecahan_campuran",
                "matematika.kelas_5.desimal",
                "matematika.kelas_6.aljabar_dasar"
            ],
            "scientific_inquiry": [
                "ipas.kelas_3.makhluk_hidup",
                "ipas.kelas_4.ekosistem",
                "ipas.kelas_5.sistem_tubuh",
                "ipas.kelas_6.evolusi"
            ],
            "civic_engagement": [
                "ppkn.kelas_1.gotong_royong",
                "ppkn.kelas_2.kerjasama",
                "ppkn.kelas_3.persatuan",
                "ppkn.kelas_4.musyawarah",
                "ppkn.kelas_5.partisipasi",
                "ppkn.kelas_6.kepemimpinan"
            ],
            "communication_skills": [
                "bahasa_indonesia.kelas_1.kalimat_sederhana",
                "bahasa_indonesia.kelas_2.dialog",
                "bahasa_indonesia.kelas_3.teks_deskripsi",
                "bahasa_indonesia.kelas_4.teks_prosedur",
                "bahasa_indonesia.kelas_5.diskusi",
                "bahasa_indonesia.kelas_6.debat"
            ]
        }

    async def retrieve_documents(
        self,
        query: str,
        document_type: str = "general",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using knowledge graph navigation

        Args:
            query: Search query
            document_type: Type of document to search
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents with relationship context
        """
        logger.rag_log(f"Starting Graph RAG retrieval for: {query[:50]}...", "Graph")

        # Step 1: Map query to concepts in knowledge graph
        query_concepts = await self.concept_mapper.map_query_to_concepts(query)
        logger.rag_log(f"Mapped to {len(query_concepts)} concepts", "Graph")

        # Step 2: Find related concepts through graph traversal
        related_concepts = await self.knowledge_graph.find_related_concepts(
            query_concepts, max_depth=3
        )
        logger.rag_log(f"Found {len(related_concepts)} related concepts", "Graph")

        # Step 3: Identify learning pathways
        relevant_pathways = await self.pathway_finder.find_relevant_pathways(
            query_concepts, related_concepts
        )
        logger.rag_log(f"Identified {len(relevant_pathways)} learning pathways", "Graph")

        # Step 4: Retrieve documents based on graph insights
        graph_documents = await self._retrieve_graph_based_documents(
            query_concepts, related_concepts, relevant_pathways, document_type, top_k
        )

        # Step 5: Analyze relationships and add metadata
        enriched_documents = await self.relationship_analyzer.enrich_with_relationships(
            graph_documents, query_concepts
        )

        logger.rag_log(f"Retrieved {len(enriched_documents)} graph-based documents", "Graph")
        return enriched_documents

    async def _retrieve_graph_based_documents(
        self,
        query_concepts: List[str],
        related_concepts: List[str],
        pathways: List[str],
        document_type: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Retrieve documents based on graph analysis"""

        documents = []

        # Direct concept matches (highest priority)
        for concept in query_concepts[:3]:
            doc = await self._create_concept_document(concept, document_type, 0.95)
            if doc:
                documents.append(doc)

        # Related concept matches (medium priority)
        for concept in related_concepts[:3]:
            doc = await self._create_concept_document(concept, document_type, 0.8)
            if doc:
                documents.append(doc)

        # Pathway-based matches (contextual priority)
        for pathway in pathways[:2]:
            doc = await self._create_pathway_document(pathway, document_type, 0.75)
            if doc:
                documents.append(doc)

        # Cross-curricular connections
        cross_curricular_docs = await self._get_cross_curricular_documents(
            query_concepts, document_type
        )
        documents.extend(cross_curricular_docs)

        return documents[:top_k]

    async def _create_concept_document(self, concept: str, document_type: str, base_score: float) -> Optional[Dict[str, Any]]:
        """Create document for a specific concept"""

        # Parse concept (e.g., "matematika.kelas_5.desimal")
        parts = concept.split('.')
        if len(parts) >= 3:
            subject, grade, topic = parts[0], parts[1], parts[2]

            content = f"""
            {document_type.upper()} untuk {subject} {grade} - {topic}

            Konsep: {topic}
            Mata Pelajaran: {subject}
            Tingkat: {grade}

            Deskripsi: Pembelajaran {topic} pada {subject} untuk {grade} dengan pendekatan
            yang terintegrasi dan mempertimbangkan relasi dengan konsep lainnya.

            Koneksi lintas kurikulum: Konsep ini terhubung dengan berbagai mata pelajaran
            lain dan mendukung pembelajaran holistik sesuai Kurikulum Merdeka.
            """

            return {
                "content": content,
                "source": f"Graph-{document_type.upper()}-{subject}-{grade}-{topic}",
                "score": base_score,
                "metadata": {
                    "concept": concept,
                    "subject": subject,
                    "grade": grade,
                    "topic": topic,
                    "type": document_type,
                    "retrieval_method": "concept_mapping"
                }
            }

        return None

    async def _create_pathway_document(self, pathway: str, document_type: str, base_score: float) -> Optional[Dict[str, Any]]:
        """Create document for a learning pathway"""

        pathway_concepts = self.learning_pathways.get(pathway, [])
        if not pathway_concepts:
            return None

        content = f"""
        {document_type.upper()} untuk jalur pembelajaran: {pathway}

        Jalur Pembelajaran: {pathway}
        Progres Konsep: {' → '.join(pathway_concepts)}

        Deskripsi: Pembelajaran bertahap yang mengikuti jalur {pathway} untuk
        memastikan pemahaman yang berkelanjutan dan terintegrasi.

        Konsep-konsep dalam jalur ini saling berkaitan dan membangun fondasi
        untuk pembelajaran yang lebih kompleks di tingkat selanjutnya.
        """

        return {
            "content": content,
            "source": f"Graph-Pathway-{pathway}-{document_type}",
            "score": base_score,
            "metadata": {
                "pathway": pathway,
                "concepts": pathway_concepts,
                "type": document_type,
                "retrieval_method": "pathway_analysis"
            }
        }

    async def _get_cross_curricular_documents(self, query_concepts: List[str], document_type: str) -> List[Dict[str, Any]]:
        """Get documents that show cross-curricular connections"""

        cross_docs = []

        for concept in query_concepts:
            # Find relationships involving this concept
            related_relationships = [
                (rel_key, rel_type) for rel_key, rel_type in self.concept_relationships.items()
                if concept in rel_key[0] or concept in rel_key[1]
            ]

            for (concept_pair, relationship_type), _ in related_relationships[:2]:
                content = f"""
                {document_type.upper()} dengan koneksi lintas kurikulum

                Konsep 1: {concept_pair[0]}
                Konsep 2: {concept_pair[1]}
                Jenis Relasi: {relationship_type}

                Deskripsi: Pembelajaran yang mengintegrasikan kedua konsep ini untuk
                memberikan pemahaman yang lebih mendalam dan kontekstual.

                Pendekatan lintas kurikulum ini mendukung pembelajaran holistik
                sesuai dengan prinsip Kurikulum Merdeka.
                """

                cross_docs.append({
                    "content": content,
                    "source": f"Graph-CrossCurricular-{relationship_type}",
                    "score": 0.7,
                    "metadata": {
                        "concept_pair": concept_pair,
                        "relationship_type": relationship_type,
                        "type": document_type,
                        "retrieval_method": "cross_curricular_analysis"
                    }
                })

        return cross_docs[:2]  # Limit to 2 cross-curricular documents

    async def generate_content(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate content using Graph RAG with relationship-aware synthesis

        Args:
            query: Original query
            context_docs: Retrieved context documents with graph metadata
            content_type: Type of content to generate
            user_input: User input data
            additional_context: Additional context

        Returns:
            Generated content with graph-based insights
        """
        logger.rag_log(f"Generating {content_type} content using Graph RAG", "Graph")

        # Step 1: Analyze graph relationships in context
        graph_analysis = await self._analyze_graph_context(context_docs, user_input)

        # Step 2: Build graph-enhanced prompt
        graph_prompt = await self._build_graph_prompt(
            query, context_docs, content_type, user_input, additional_context, graph_analysis
        )

        # Step 3: Generate content with graph insights
        generated_content = await self._simulate_llm_call(graph_prompt, user_input.model_llm.value)

        # Step 4: Post-process with graph enhancements
        final_content = await self._post_process_graph_content(
            generated_content, content_type, user_input, graph_analysis
        )

        logger.rag_log(f"Graph RAG content generated (length: {len(final_content)} chars)", "Graph")
        return final_content

    async def _analyze_graph_context(self, context_docs: List[Dict[str, Any]], user_input: UserInput) -> Dict[str, Any]:
        """Analyze graph relationships in the context documents"""

        analysis = {
            "direct_concepts": [],
            "related_concepts": [],
            "pathways": [],
            "cross_curricular_connections": [],
            "prerequisite_chains": [],
            "advanced_concepts": []
        }

        for doc in context_docs:
            metadata = doc.get('metadata', {})
            retrieval_method = metadata.get('retrieval_method', '')

            if retrieval_method == 'concept_mapping':
                concept = metadata.get('concept', '')
                if concept:
                    analysis['direct_concepts'].append(concept)

            elif retrieval_method == 'pathway_analysis':
                pathway = metadata.get('pathway', '')
                if pathway:
                    analysis['pathways'].append(pathway)

            elif retrieval_method == 'cross_curricular_analysis':
                relationship = metadata.get('relationship_type', '')
                if relationship:
                    analysis['cross_curricular_connections'].append(relationship)

        # Analyze learning progression
        current_grade = self._extract_grade_number(user_input.kelas)
        analysis['prerequisite_chains'] = await self._find_prerequisite_chains(
            user_input.mata_pelajaran, current_grade
        )
        analysis['advanced_concepts'] = await self._find_advanced_concepts(
            user_input.mata_pelajaran, current_grade
        )

        return analysis

    def _extract_grade_number(self, kelas: str) -> int:
        """Extract grade number from kelas string"""
        import re
        numbers = re.findall(r'\d+', kelas)
        return int(numbers[0]) if numbers else 1

    async def _find_prerequisite_chains(self, subject: str, current_grade: int) -> List[str]:
        """Find prerequisite concept chains for current learning"""

        prerequisite_chains = []
        subject_concepts = self.curriculum_concepts.get(subject, {})

        # Get concepts from previous grades
        for grade in range(max(1, current_grade - 2), current_grade):
            grade_key = f"kelas_{grade}"
            if grade_key in subject_concepts:
                concepts = subject_concepts[grade_key]
                prerequisite_chains.extend([f"{subject}.{grade_key}.{concept}" for concept in concepts])

        return prerequisite_chains

    async def _find_advanced_concepts(self, subject: str, current_grade: int) -> List[str]:
        """Find advanced concepts for future learning"""

        advanced_concepts = []
        subject_concepts = self.curriculum_concepts.get(subject, {})

        # Get concepts from next grades
        for grade in range(current_grade + 1, min(current_grade + 3, 7)):
            grade_key = f"kelas_{grade}"
            if grade_key in subject_concepts:
                concepts = subject_concepts[grade_key]
                advanced_concepts.extend([f"{subject}.{grade_key}.{concept}" for concept in concepts])

        return advanced_concepts

    async def _build_graph_prompt(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]],
        graph_analysis: Dict[str, Any]
    ) -> str:
        """Build prompt enhanced with graph insights"""

        # Base prompt
        base_prompt = self._build_prompt(query, self._prepare_context(context_docs), content_type, user_input, additional_context)

        # Graph-specific enhancements
        graph_enhancements = f"""

        === GRAPH RAG INSIGHTS ===

        🔗 Konsep Terkait Langsung:
        {', '.join(graph_analysis['direct_concepts'][:5])}

        🛤️ Jalur Pembelajaran:
        {', '.join(graph_analysis['pathways'])}

        🌐 Koneksi Lintas Kurikulum:
        {', '.join(graph_analysis['cross_curricular_connections'])}

        📈 Konsep Prasyarat:
        {', '.join(graph_analysis['prerequisite_chains'][:3])}

        🚀 Konsep Lanjutan:
        {', '.join(graph_analysis['advanced_concepts'][:3])}

        === INSTRUKSI GRAPH RAG ===

        Gunakan insights dari knowledge graph di atas untuk:
        1. Menunjukkan hubungan antar konsep
        2. Mempertimbangkan prasyarat pembelajaran
        3. Mengintegrasikan koneksi lintas kurikulum
        4. Memberikan jalur pembelajaran yang jelas
        5. Mempersiapkan fondasi untuk konsep lanjutan
        6. Menerapkan pendekatan pembelajaran holistik

        Pastikan {content_type} yang dihasilkan mencerminkan pemahaman relational
        dan mendukung pembelajaran yang terintegrasi sesuai Kurikulum Merdeka.
        """

        return base_prompt + graph_enhancements

    async def _post_process_graph_content(
        self,
        content: str,
        content_type: str,
        user_input: UserInput,
        graph_analysis: Dict[str, Any]
    ) -> str:
        """Post-process content with graph-specific enhancements"""

        # Graph RAG header
        header = f"""
        ╔═══════════════════════════════════════════════════════════════════╗
        ║  🕸️  GRAPH RAG - {content_type.upper()}
        ║  Knowledge Graph-Based Learning Design                             ║
        ╚═══════════════════════════════════════════════════════════════════╝

        📚 Subject: {user_input.mata_pelajaran}  |  🎓 Grade: {user_input.kelas}
        📖 Topic: {user_input.topik}  |  📝 Sub-topic: {user_input.sub_topik}
        ⏰ Duration: {user_input.alokasi_waktu}
        👨‍🏫 Teacher: {user_input.nama_guru}  |  🏫 School: {user_input.nama_sekolah}
        """

        # Enhanced content with graph structure
        enhanced_content = self._add_graph_structure_markers(content, content_type)

        # Graph insights section
        graph_insights = f"""

        ╔═══════════════════════════════════════════════════════════════════╗
        ║  🕸️  KNOWLEDGE GRAPH INSIGHTS                                     ║
        ╚═══════════════════════════════════════════════════════════════════╝

        🔗 RELATIONAL CONNECTIONS:
        {self._format_graph_connections(graph_analysis)}

        🛤️ LEARNING PATHWAYS:
        {self._format_learning_pathways(graph_analysis)}

        🌐 CROSS-CURRICULAR INTEGRATION:
        {self._format_cross_curricular(graph_analysis)}

        📊 PREREQUISITE ANALYSIS:
        {self._format_prerequisites(graph_analysis)}

        🚀 PROGRESSION ROADMAP:
        {self._format_progression(graph_analysis)}
        """

        # Technical metadata
        technical_metadata = f"""

        ╔═══════════════════════════════════════════════════════════════════╗
        ║  ⚙️  TECHNICAL METADATA                                           ║
        ╚═══════════════════════════════════════════════════════════════════╝

        🧠 Generation Strategy: Graph RAG
        🕸️ Knowledge Graph: Curriculum Concept Network
        🔄 Relationship Analysis: Multi-dimensional
        📈 Concept Mapping: Hierarchical & Cross-curricular
        🎯 Learning Pathway: Progression-aware
        🌐 Integration Level: Holistic

        📊 Graph Statistics:
        - Direct Concepts: {len(graph_analysis['direct_concepts'])}
        - Related Concepts: {len(graph_analysis['related_concepts'])}
        - Active Pathways: {len(graph_analysis['pathways'])}
        - Cross-curricular Links: {len(graph_analysis['cross_curricular_connections'])}
        - Prerequisite Chains: {len(graph_analysis['prerequisite_chains'])}
        - Advanced Concepts: {len(graph_analysis['advanced_concepts'])}

        🎨 Model: {user_input.model_llm.value}
        📏 Content Length: {len(enhanced_content)} characters
        ✅ Curriculum Alignment: Kurikulum Merdeka (Graph-enhanced)
        """

        return header + "\n\n" + enhanced_content + graph_insights + technical_metadata

    def _add_graph_structure_markers(self, content: str, content_type: str) -> str:
        """Add graph-specific structure markers to content"""

        graph_markers = {
            "1.": "🔗 1.",
            "2.": "🔗 2.",
            "3.": "🔗 3.",
            "Tujuan": "🎯 Tujuan",
            "Indikator": "📊 Indikator",
            "Kegiatan": "🎲 Kegiatan",
            "Penilaian": "📈 Penilaian",
            "PENGETAHUAN": "🧠 PENGETAHUAN (Graph-linked)",
            "KETERAMPILAN": "🛠️ KETERAMPILAN (Graph-linked)",
            "SIKAP": "💫 SIKAP (Graph-linked)"
        }

        enhanced_content = content
        for original, enhanced in graph_markers.items():
            enhanced_content = enhanced_content.replace(original, enhanced)

        return enhanced_content

    def _format_graph_connections(self, analysis: Dict[str, Any]) -> str:
        """Format graph connections for display"""
        connections = analysis.get('direct_concepts', [])[:3]
        if not connections:
            return "   • No direct connections identified"

        formatted = []
        for connection in connections:
            formatted.append(f"   🔗 {connection}")

        return "\n".join(formatted)

    def _format_learning_pathways(self, analysis: Dict[str, Any]) -> str:
        """Format learning pathways for display"""
        pathways = analysis.get('pathways', [])
        if not pathways:
            return "   • No specific pathways identified"

        formatted = []
        for pathway in pathways:
            pathway_concepts = self.learning_pathways.get(pathway, [])
            if pathway_concepts:
                formatted.append(f"   🛤️ {pathway}: {' → '.join(pathway_concepts[:3])}...")

        return "\n".join(formatted) if formatted else "   • No pathway details available"

    def _format_cross_curricular(self, analysis: Dict[str, Any]) -> str:
        """Format cross-curricular connections for display"""
        connections = analysis.get('cross_curricular_connections', [])
        if not connections:
            return "   • No cross-curricular connections identified"

        formatted = []
        for connection in connections:
            formatted.append(f"   🌐 {connection.replace('_', ' ').title()}")

        return "\n".join(formatted)

    def _format_prerequisites(self, analysis: Dict[str, Any]) -> str:
        """Format prerequisite analysis for display"""
        prerequisites = analysis.get('prerequisite_chains', [])[:3]
        if not prerequisites:
            return "   • No specific prerequisites identified"

        formatted = []
        for prereq in prerequisites:
            formatted.append(f"   📊 {prereq}")

        return "\n".join(formatted)

    def _format_progression(self, analysis: Dict[str, Any]) -> str:
        """Format progression roadmap for display"""
        advanced = analysis.get('advanced_concepts', [])[:3]
        if not advanced:
            return "   • No progression roadmap available"

        formatted = []
        for concept in advanced:
            formatted.append(f"   🚀 {concept}")

        return "\n".join(formatted)

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about Graph RAG strategy"""
        return {
            "name": "Graph RAG",
            "description": "Knowledge graph navigation for relational learning",
            "features": [
                "Concept relationship mapping",
                "Learning pathway analysis",
                "Cross-curricular integration",
                "Prerequisite chain analysis",
                "Progression roadmapping",
                "Holistic curriculum view"
            ],
            "strengths": [
                "Relational understanding",
                "Comprehensive curriculum integration",
                "Learning progression awareness",
                "Cross-subject connections",
                "Prerequisite consideration",
                "Future learning preparation"
            ],
            "best_for": [
                "Complex topic relationships",
                "Integrated curriculum design",
                "Holistic learning approaches",
                "Progressive skill building",
                "Cross-curricular projects",
                "Advanced learning design"
            ],
            "graph_stats": {
                "concepts": sum(len(grades) for grades in self.curriculum_concepts.values()),
                "relationships": len(self.concept_relationships),
                "pathways": len(self.learning_pathways),
                "subjects": len(self.curriculum_concepts)
            }
        }


class CurriculumKnowledgeGraph:
    """Knowledge graph for curriculum concepts and relationships"""

    async def find_related_concepts(self, query_concepts: List[str], max_depth: int = 3) -> List[str]:
        """Find related concepts through graph traversal"""

        related = set()
        current_level = set(query_concepts)

        for depth in range(max_depth):
            next_level = set()

            for concept in current_level:
                # Find direct relationships
                direct_related = self._find_direct_relationships(concept)
                next_level.update(direct_related)
                related.update(direct_related)

            current_level = next_level - related  # Only explore new concepts

            if not current_level:  # No more concepts to explore
                break

        return list(related)

    def _find_direct_relationships(self, concept: str) -> List[str]:
        """Find directly related concepts"""
        # Simulate finding relationships
        # In actual implementation, this would query the knowledge graph

        related = []

        # Same subject, different grades
        if '.' in concept:
            parts = concept.split('.')
            if len(parts) >= 3:
                subject, grade, topic = parts[0], parts[1], parts[2]

                # Add same topic from adjacent grades
                grade_num = int(grade.split('_')[1]) if '_' in grade else 1
                for adj_grade in [grade_num - 1, grade_num + 1]:
                    if 1 <= adj_grade <= 6:
                        related.append(f"{subject}.kelas_{adj_grade}.{topic}")

        return related


class ConceptMapper:
    """Maps queries to curriculum concepts"""

    async def map_query_to_concepts(self, query: str) -> List[str]:
        """Map query text to curriculum concepts"""

        query_lower = query.lower()
        mapped_concepts = []

        # Subject detection
        subject_mapping = {
            "matematika": "matematika",
            "bahasa indonesia": "bahasa_indonesia",
            "ipas": "ipas",
            "ppkn": "ppkn"
        }

        detected_subject = None
        for subject_name, subject_key in subject_mapping.items():
            if subject_name in query_lower:
                detected_subject = subject_key
                break

        if detected_subject:
            # Grade detection
            for grade in range(1, 7):
                if f"kelas {grade}" in query_lower:
                    grade_key = f"kelas_{grade}"

                    # Topic detection (simplified)
                    topic_keywords = {
                        "bilangan": "bilangan",
                        "penjumlahan": "penjumlahan",
                        "pengurangan": "pengurangan",
                        "perkalian": "perkalian",
                        "pembagian": "pembagian",
                        "pecahan": "pecahan",
                        "geometri": "geometri_dasar",
                        "bangun": "bangun_datar"
                    }

                    for keyword, topic in topic_keywords.items():
                        if keyword in query_lower:
                            mapped_concepts.append(f"{detected_subject}.{grade_key}.{topic}")

                    break

        # If no specific concepts found, return general ones
        if not mapped_concepts:
            mapped_concepts = ["matematika.kelas_1.bilangan"]

        return mapped_concepts


class LearningPathwayFinder:
    """Finds relevant learning pathways"""

    async def find_relevant_pathways(
        self,
        query_concepts: List[str],
        related_concepts: List[str]
    ) -> List[str]:
        """Find learning pathways relevant to the concepts"""

        # Simulate pathway detection
        relevant_pathways = []

        all_concepts = query_concepts + related_concepts

        # Check which pathways contain these concepts
        pathway_definitions = {
            "mathematical_literacy": ["bilangan", "perkalian", "pecahan"],
            "scientific_inquiry": ["makhluk_hidup", "ekosistem", "sistem_tubuh"],
            "civic_engagement": ["gotong_royong", "kerjasama", "persatuan"],
            "communication_skills": ["kalimat", "dialog", "teks", "diskusi"]
        }

        for pathway, keywords in pathway_definitions.items():
            concept_text = " ".join(all_concepts).lower()
            if any(keyword in concept_text for keyword in keywords):
                relevant_pathways.append(pathway)

        return relevant_pathways


class RelationshipAnalyzer:
    """Analyzes and enriches relationships between concepts"""

    async def enrich_with_relationships(
        self,
        documents: List[Dict[str, Any]],
        query_concepts: List[str]
    ) -> List[Dict[str, Any]]:
        """Enrich documents with relationship metadata"""

        enriched_docs = []

        for doc in documents:
            # Add relationship analysis to metadata
            doc_metadata = doc.get('metadata', {})
            doc_metadata['relationship_analysis'] = self._analyze_document_relationships(doc, query_concepts)
            doc['metadata'] = doc_metadata

            # Boost score based on relationship strength
            relationship_boost = self._calculate_relationship_boost(doc_metadata['relationship_analysis'])
            doc['score'] = min(doc.get('score', 0.5) + relationship_boost, 1.0)

            enriched_docs.append(doc)

        # Sort by enhanced score
        enriched_docs.sort(key=lambda x: x['score'], reverse=True)

        return enriched_docs

    def _analyze_document_relationships(self, document: Dict[str, Any], query_concepts: List[str]) -> Dict[str, Any]:
        """Analyze relationships between document and query concepts"""

        analysis = {
            "direct_matches": 0,
            "indirect_matches": 0,
            "relationship_types": [],
            "strength": 0.0
        }

        doc_content = document.get('content', '').lower()
        doc_metadata = document.get('metadata', {})

        # Count direct concept matches
        for concept in query_concepts:
            if concept.lower() in doc_content:
                analysis['direct_matches'] += 1

        # Analyze relationship types from metadata
        if 'relationship_type' in doc_metadata:
            analysis['relationship_types'].append(doc_metadata['relationship_type'])

        # Calculate overall relationship strength
        analysis['strength'] = (
            analysis['direct_matches'] * 0.4 +
            analysis['indirect_matches'] * 0.2 +
            len(analysis['relationship_types']) * 0.3
        )

        return analysis

    def _calculate_relationship_boost(self, relationship_analysis: Dict[str, Any]) -> float:
        """Calculate score boost based on relationship strength"""

        base_boost = relationship_analysis.get('strength', 0.0) * 0.1
        direct_boost = relationship_analysis.get('direct_matches', 0) * 0.05

        return min(base_boost + direct_boost, 0.2)  # Max boost of 0.2
