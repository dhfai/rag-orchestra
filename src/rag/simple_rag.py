import os
from typing import List, Dict, Any, Optional
from .base_rag import BaseRAG
from ..core.models import UserInput
from ..utils.logger import get_logger

logger = get_logger("SimpleRAG")

class SimpleRAG(BaseRAG):
    """
    Simple RAG implementation for straightforward template-based retrieval

    Strategy: Langsung mencari template yang sesuai berdasarkan keyword matching
    Use case: Ketika tersedia template yang cocok dan query sederhana
    """

    def __init__(self):
        super().__init__()
        self.document_cache = {}
        self._load_templates()

    def _load_templates(self):
        """Load and cache document templates"""
        logger.rag_log("Loading document templates", "Simple")

        # Simulate loading templates from file system
        # In actual implementation, this would read from data/cp/* and data/atp/*
        self.templates = {
            "cp": {
                "matematika": {
                    "kelas_1": "Template CP Matematika Kelas 1...",
                    "kelas_2": "Template CP Matematika Kelas 2...",
                    "kelas_3": "Template CP Matematika Kelas 3...",
                    "kelas_4": "Template CP Matematika Kelas 4...",
                    "kelas_5": "Template CP Matematika Kelas 5...",
                    "kelas_6": "Template CP Matematika Kelas 6...",
                },
                "bahasa_indonesia": {
                    "kelas_1": "Template CP Bahasa Indonesia Kelas 1...",
                    "kelas_2": "Template CP Bahasa Indonesia Kelas 2...",
                    "kelas_3": "Template CP Bahasa Indonesia Kelas 3...",
                    "kelas_4": "Template CP Bahasa Indonesia Kelas 4...",
                    "kelas_5": "Template CP Bahasa Indonesia Kelas 5...",
                    "kelas_6": "Template CP Bahasa Indonesia Kelas 6...",
                },
                "ipas": {
                    "kelas_3": "Template CP IPAS Kelas 3...",
                    "kelas_4": "Template CP IPAS Kelas 4...",
                    "kelas_5": "Template CP IPAS Kelas 5...",
                    "kelas_6": "Template CP IPAS Kelas 6...",
                },
                "ppkn": {
                    "kelas_1": "Template CP PPKn Kelas 1...",
                    "kelas_2": "Template CP PPKn Kelas 2...",
                    "kelas_3": "Template CP PPKn Kelas 3...",
                    "kelas_4": "Template CP PPKn Kelas 4...",
                    "kelas_5": "Template CP PPKn Kelas 5...",
                    "kelas_6": "Template CP PPKn Kelas 6...",
                }
            },
            "atp": {
                "matematika": {
                    "kelas_1": "Template ATP Matematika Kelas 1...",
                    "kelas_2": "Template ATP Matematika Kelas 2...",
                    "kelas_3": "Template ATP Matematika Kelas 3...",
                    "kelas_4": "Template ATP Matematika Kelas 4...",
                    "kelas_5": "Template ATP Matematika Kelas 5...",
                    "kelas_6": "Template ATP Matematika Kelas 6...",
                },
                "bahasa_indonesia": {
                    "kelas_1": "Template ATP Bahasa Indonesia Kelas 1...",
                    "kelas_2": "Template ATP Bahasa Indonesia Kelas 2...",
                    "kelas_3": "Template ATP Bahasa Indonesia Kelas 3...",
                    "kelas_4": "Template ATP Bahasa Indonesia Kelas 4...",
                    "kelas_5": "Template ATP Bahasa Indonesia Kelas 5...",
                    "kelas_6": "Template ATP Bahasa Indonesia Kelas 6...",
                },
                "ipas": {
                    "kelas_3": "Template ATP IPAS Kelas 3...",
                    "kelas_4": "Template ATP IPAS Kelas 4...",
                    "kelas_5": "Template ATP IPAS Kelas 5...",
                    "kelas_6": "Template ATP IPAS Kelas 6...",
                },
                "ppkn": {
                    "kelas_1": "Template ATP PPKn Kelas 1...",
                    "kelas_2": "Template ATP PPKn Kelas 2...",
                    "kelas_3": "Template ATP PPKn Kelas 3...",
                    "kelas_4": "Template ATP PPKn Kelas 4...",
                    "kelas_5": "Template ATP PPKn Kelas 5...",
                    "kelas_6": "Template ATP PPKn Kelas 6...",
                }
            }
        }

        logger.rag_log(f"Loaded {len(self.templates)} template categories", "Simple")

    async def retrieve_documents(
        self,
        query: str,
        document_type: str = "general",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using simple keyword matching

        Args:
            query: Search query
            document_type: Type of document (cp, atp)
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents
        """
        logger.rag_log(f"Retrieving documents for query: {query[:50]}...", "Simple")

        # Extract key information from query
        subject_key, grade_key = self._extract_key_info(query)

        retrieved_docs = []

        # Try to find exact match first
        if document_type in self.templates:
            subject_templates = self.templates[document_type].get(subject_key, {})
            if grade_key in subject_templates:
                retrieved_docs.append({
                    "content": subject_templates[grade_key],
                    "source": f"{document_type.upper()} {subject_key} {grade_key}",
                    "score": 0.95,
                    "metadata": {
                        "subject": subject_key,
                        "grade": grade_key,
                        "type": document_type
                    }
                })

        # Add related documents if available
        if len(retrieved_docs) < top_k:
            related_docs = self._find_related_documents(subject_key, grade_key, document_type, top_k - len(retrieved_docs))
            retrieved_docs.extend(related_docs)

        # If still not enough, add generic templates
        if len(retrieved_docs) < top_k:
            generic_docs = self._get_generic_templates(document_type, top_k - len(retrieved_docs))
            retrieved_docs.extend(generic_docs)

        logger.rag_log(f"Retrieved {len(retrieved_docs)} documents", "Simple")
        return retrieved_docs[:top_k]

    def _extract_key_info(self, query: str) -> tuple[str, str]:
        """Extract subject and grade information from query"""
        query_lower = query.lower()

        # Subject mapping
        subject_mapping = {
            "matematika": "matematika",
            "math": "matematika",
            "bahasa indonesia": "bahasa_indonesia",
            "b indonesia": "bahasa_indonesia",
            "b indo": "bahasa_indonesia",
            "indonesia": "bahasa_indonesia",
            "ipas": "ipas",
            "ipa": "ipas",
            "ips": "ipas",
            "ppkn": "ppkn",
            "pkn": "ppkn",
            "pendidikan pancasila": "ppkn",
            "bahasa inggris": "bahasa_inggris",
            "b inggris": "bahasa_inggris",
            "english": "bahasa_inggris"
        }

        # Find subject
        subject_key = "matematika"  # default
        for subject_name, key in subject_mapping.items():
            if subject_name in query_lower:
                subject_key = key
                break

        # Find grade
        grade_key = "kelas_1"  # default
        for i in range(1, 13):
            if f"kelas {i}" in query_lower or f"kelas{i}" in query_lower:
                grade_key = f"kelas_{i}"
                break
            elif f" {i} " in query_lower:
                grade_key = f"kelas_{i}"
                break

        return subject_key, grade_key

    def _find_related_documents(self, subject_key: str, grade_key: str, document_type: str, limit: int) -> List[Dict[str, Any]]:
        """Find related documents based on subject and grade"""
        related_docs = []

        if document_type not in self.templates:
            return related_docs

        # Get current grade number
        try:
            current_grade = int(grade_key.split("_")[1])
        except:
            current_grade = 1

        # Look for adjacent grades for same subject
        subject_templates = self.templates[document_type].get(subject_key, {})

        for offset in [1, -1, 2, -2]:  # Check grades ±1, ±2
            if len(related_docs) >= limit:
                break

            target_grade = current_grade + offset
            target_key = f"kelas_{target_grade}"

            if target_key in subject_templates and target_grade > 0:
                related_docs.append({
                    "content": subject_templates[target_key],
                    "source": f"{document_type.upper()} {subject_key} {target_key}",
                    "score": 0.8 - abs(offset) * 0.1,
                    "metadata": {
                        "subject": subject_key,
                        "grade": target_key,
                        "type": document_type,
                        "relation": "adjacent_grade"
                    }
                })

        return related_docs

    def _get_generic_templates(self, document_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get generic templates as fallback"""
        generic_docs = []

        if document_type not in self.templates:
            return generic_docs

        # Get some random templates as fallback
        count = 0
        for subject, grades in self.templates[document_type].items():
            if count >= limit:
                break

            for grade, content in grades.items():
                if count >= limit:
                    break

                generic_docs.append({
                    "content": content,
                    "source": f"{document_type.upper()} {subject} {grade} (Generic)",
                    "score": 0.5,
                    "metadata": {
                        "subject": subject,
                        "grade": grade,
                        "type": document_type,
                        "relation": "generic"
                    }
                })
                count += 1

        return generic_docs

    async def generate_content(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        content_type: str,
        user_input: UserInput,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate content using Simple RAG approach

        Args:
            query: Original query
            context_docs: Retrieved context documents
            content_type: Type of content to generate
            user_input: User input data
            additional_context: Additional context

        Returns:
            Generated content
        """
        logger.rag_log(f"Generating {content_type} content using Simple RAG", "Simple")

        # Prepare context from retrieved documents
        context = self._prepare_context(context_docs)

        # Build prompt
        prompt = self._build_prompt(query, context, content_type, user_input, additional_context)

        # Generate content using LLM
        generated_content = await self._simulate_llm_call(prompt, user_input.model_llm.value)

        # Post-process content for Simple RAG
        processed_content = self._post_process_simple_content(generated_content, content_type, user_input)

        logger.rag_log(f"Content generated successfully (length: {len(processed_content)} chars)", "Simple")
        return processed_content

    def _post_process_simple_content(self, content: str, content_type: str, user_input: UserInput) -> str:
        """Post-process generated content for Simple RAG"""

        # Add header with specific information
        header = f"""
        ═══════════════════════════════════════════════════════════
        {content_type.upper()} - {user_input.mata_pelajaran.upper()}
        Kelas: {user_input.kelas} | Topik: {user_input.topik}
        Generated using Simple RAG Strategy
        ═══════════════════════════════════════════════════════════
        """

        # Combine header with content
        final_content = header + "\n\n" + content.strip()

        # Add footer with metadata
        footer = f"""

        ═══════════════════════════════════════════════════════════
        Metadata:
        - Strategy: Simple RAG (Template-based)
        - Subject: {user_input.mata_pelajaran}
        - Grade: {user_input.kelas}
        - Topic: {user_input.topik}
        - Sub Topic: {user_input.sub_topik}
        - Duration: {user_input.alokasi_waktu}
        - Teacher: {user_input.nama_guru}
        - School: {user_input.nama_sekolah}
        ═══════════════════════════════════════════════════════════
        """

        return final_content + footer

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about Simple RAG strategy"""
        return {
            "name": "Simple RAG",
            "description": "Template-based retrieval with direct keyword matching",
            "strengths": [
                "Fast retrieval",
                "Reliable for common subjects",
                "Low computational cost",
                "Consistent format"
            ],
            "best_for": [
                "Standard curriculum subjects",
                "Well-documented topics",
                "Quick generation needs",
                "Basic requirements"
            ],
            "template_count": sum(
                len(grades) for subject_templates in self.templates.values()
                for grades in subject_templates.values()
            )
        }
