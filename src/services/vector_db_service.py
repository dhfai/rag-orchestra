"""
Vector Database Service
======================

Service untuk manajemen vector database menggunakan ChromaDB.
Menangani embedding, indexing, dan retrieval dokumen.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import hashlib
from datetime import datetime

import chromadb
from chromadb.config import Settings
import numpy as np

from ..core.models import RAGStrategy
from ..utils.logger import get_logger
from ..services.llm_service import LLMService

logger = get_logger("VectorDBService")

class VectorDBService:
    """
    Service untuk manajemen vector database
    """

    def __init__(self, persist_directory: str = "./vector_db", llm_service: Optional[LLMService] = None):
        self.persist_directory = persist_directory
        self.llm_service = llm_service
        self.client = None
        self.collections = {}

        # Collection names untuk berbagai jenis dokumen
        self.collection_names = {
            "cp": "curriculum_planning",
            "atp": "learning_targets",
            "modul_ajar": "teaching_modules",
            "general": "general_documents"
        }

        self._initialize_client()
        logger.info("Vector DB Service initialized")

    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            # Ensure persist directory exists
            os.makedirs(self.persist_directory, exist_ok=True)

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Initialize collections
            self._initialize_collections()

            logger.success("ChromaDB client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise

    def _initialize_collections(self):
        """Initialize collections untuk berbagai jenis dokumen"""
        for doc_type, collection_name in self.collection_names.items():
            try:
                # Get or create collection
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"doc_type": doc_type}
                )
                self.collections[doc_type] = collection
                logger.debug(f"Collection '{collection_name}' initialized for {doc_type}")

            except Exception as e:
                logger.warning(f"Failed to initialize collection for {doc_type}: {str(e)}")

    async def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_type: str = "general",
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add dokumen ke vector database

        Args:
            content: Content dokumen
            metadata: Metadata dokumen
            doc_type: Jenis dokumen (cp, atp, modul_ajar, general)
            doc_id: Document ID (optional, akan digenerate jika tidak ada)

        Returns:
            str: Document ID
        """
        try:
            if doc_type not in self.collections:
                raise ValueError(f"Invalid doc_type: {doc_type}")

            collection = self.collections[doc_type]

            # Generate document ID if not provided
            if not doc_id:
                doc_id = self._generate_doc_id(content, metadata)

            # Generate embedding if LLM service available
            if self.llm_service:
                embedding = await self.llm_service.generate_embedding(content)
            else:
                logger.warning("LLM service not available, using dummy embedding")
                embedding = np.random.rand(1536).tolist()  # Dummy embedding

            # Prepare metadata
            enhanced_metadata = {
                **metadata,
                "doc_type": doc_type,
                "added_at": datetime.now().isoformat(),
                "content_length": len(content)
            }

            # Add to collection
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[enhanced_metadata]
            )

            logger.debug(f"Document added to {doc_type} collection: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise

    async def search_documents(
        self,
        query: str,
        doc_type: str = "general",
        top_k: int = 5,
        strategy: RAGStrategy = RAGStrategy.SIMPLE,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search dokumen berdasarkan query

        Args:
            query: Search query
            doc_type: Jenis dokumen untuk dicari
            top_k: Jumlah hasil teratas
            strategy: RAG strategy yang digunakan
            filters: Filter metadata (optional)

        Returns:
            List[Dict]: Hasil pencarian
        """
        try:
            if doc_type not in self.collections:
                logger.warning(f"Collection for {doc_type} not found")
                return []

            collection = self.collections[doc_type]

            # Generate query embedding
            if self.llm_service:
                query_embedding = await self.llm_service.generate_embedding(query)
            else:
                logger.warning("LLM service not available for search")
                return []

            # Prepare search parameters based on strategy
            search_params = self._prepare_search_params(strategy, top_k, filters)

            # Perform search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=search_params["n_results"],
                where=search_params.get("where"),
                include=["documents", "metadatas", "distances"]
            )

            # Process results
            processed_results = self._process_search_results(results, strategy)

            logger.debug(f"Found {len(processed_results)} documents for query in {doc_type}")
            return processed_results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def _prepare_search_params(
        self,
        strategy: RAGStrategy,
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare search parameters berdasarkan strategy"""
        params = {"n_results": top_k}

        if filters:
            params["where"] = filters

        # Adjust parameters based on strategy
        if strategy == RAGStrategy.ADVANCED:
            params["n_results"] = min(top_k * 2, 20)  # Get more results for advanced processing
        elif strategy == RAGStrategy.GRAPH:
            params["n_results"] = min(top_k * 3, 30)  # Get even more for graph analysis

        return params

    def _process_search_results(
        self,
        results: Dict[str, Any],
        strategy: RAGStrategy
    ) -> List[Dict[str, Any]]:
        """Process hasil search berdasarkan strategy"""
        processed = []

        if not results["documents"] or not results["documents"][0]:
            return processed

        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
        distances = results["distances"][0] if results["distances"] else [0.0] * len(documents)

        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            similarity_score = 1.0 - distance  # Convert distance to similarity

            result = {
                "content": doc,
                "metadata": metadata,
                "similarity_score": similarity_score,
                "rank": i + 1,
                "strategy_used": strategy.value
            }

            # Add strategy-specific information
            if strategy == RAGStrategy.ADVANCED:
                result["advanced_score"] = self._calculate_advanced_score(doc, metadata, similarity_score)
            elif strategy == RAGStrategy.GRAPH:
                result["graph_relevance"] = self._calculate_graph_relevance(doc, metadata)

            processed.append(result)

        # Apply strategy-specific reranking
        processed = self._rerank_results(processed, strategy)

        return processed

    def _calculate_advanced_score(self, content: str, metadata: Dict[str, Any], similarity: float) -> float:
        """Calculate advanced scoring untuk Advanced RAG"""
        # Simple advanced scoring berdasarkan content length dan metadata
        content_score = min(len(content) / 1000.0, 1.0)  # Normalize content length
        metadata_score = len(metadata) / 10.0  # Metadata richness

        return (similarity * 0.7) + (content_score * 0.2) + (metadata_score * 0.1)

    def _calculate_graph_relevance(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate graph relevance untuk Graph RAG"""
        # Simple graph relevance berdasarkan keyword co-occurrence
        keywords = ["hubungan", "relasi", "koneksi", "keterkaitan", "perbandingan"]
        relevance = sum(1 for keyword in keywords if keyword.lower() in content.lower())
        return min(relevance / len(keywords), 1.0)

    def _rerank_results(self, results: List[Dict[str, Any]], strategy: RAGStrategy) -> List[Dict[str, Any]]:
        """Rerank results berdasarkan strategy"""
        if strategy == RAGStrategy.SIMPLE:
            # Simple ranking by similarity score
            return sorted(results, key=lambda x: x["similarity_score"], reverse=True)

        elif strategy == RAGStrategy.ADVANCED:
            # Advanced ranking menggunakan advanced score
            return sorted(results, key=lambda x: x.get("advanced_score", 0), reverse=True)

        elif strategy == RAGStrategy.GRAPH:
            # Graph ranking menggunakan graph relevance dan similarity
            def graph_score(result):
                similarity = result["similarity_score"]
                graph_rel = result.get("graph_relevance", 0)
                return (similarity * 0.6) + (graph_rel * 0.4)

            return sorted(results, key=graph_score, reverse=True)

        else:
            return results

    def _generate_doc_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique document ID"""
        # Create hash dari content dan key metadata
        hash_input = content + str(sorted(metadata.items()))
        return hashlib.md5(hash_input.encode()).hexdigest()

    async def get_collection_stats(self, doc_type: str = None) -> Dict[str, Any]:
        """Get statistics untuk collections"""
        stats = {}

        if doc_type and doc_type in self.collections:
            collections_to_check = {doc_type: self.collections[doc_type]}
        else:
            collections_to_check = self.collections

        for dtype, collection in collections_to_check.items():
            try:
                count = collection.count()
                stats[dtype] = {
                    "document_count": count,
                    "collection_name": self.collection_names[dtype]
                }
            except Exception as e:
                logger.warning(f"Failed to get stats for {dtype}: {str(e)}")
                stats[dtype] = {"error": str(e)}

        return stats

    async def delete_document(self, doc_id: str, doc_type: str) -> bool:
        """Delete dokumen dari collection"""
        try:
            if doc_type not in self.collections:
                raise ValueError(f"Invalid doc_type: {doc_type}")

            collection = self.collections[doc_type]
            collection.delete(ids=[doc_id])

            logger.debug(f"Document deleted: {doc_id} from {doc_type}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False

    async def clear_collection(self, doc_type: str) -> bool:
        """Clear semua dokumen dalam collection"""
        try:
            if doc_type not in self.collections:
                raise ValueError(f"Invalid doc_type: {doc_type}")

            # Delete and recreate collection
            collection_name = self.collection_names[doc_type]
            self.client.delete_collection(collection_name)

            # Recreate collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"doc_type": doc_type}
            )
            self.collections[doc_type] = collection

            logger.info(f"Collection {doc_type} cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Error clearing collection {doc_type}: {str(e)}")
            return False

# Singleton instance
_vector_db_service_instance: Optional[VectorDBService] = None

def get_vector_db_service(llm_service: Optional[LLMService] = None) -> VectorDBService:
    """Get singleton Vector DB service instance"""
    global _vector_db_service_instance
    if _vector_db_service_instance is None:
        _vector_db_service_instance = VectorDBService(llm_service=llm_service)
    return _vector_db_service_instance
