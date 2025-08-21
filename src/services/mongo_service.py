"""
MongoDB Service
===============

Service untuk document storage menggunakan MongoDB
Untuk menyimpan RAG documents, embeddings, dan unstructured data
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import pymongo
from bson import ObjectId

from ..utils.database import db_config
from ..utils.logger import get_logger

logger = get_logger("MongoService")

class MongoService:
    """Service untuk MongoDB operations"""

    def __init__(self):
        self.db = db_config.mongo_db
        self.collections = {
            'documents': 'rag_documents',
            'embeddings': 'document_embeddings',
            'user_sessions': 'user_sessions',
            'processing_logs': 'processing_logs',
            'rag_sources': 'rag_sources'
        }

        # Create indexes
        self._create_indexes()

        logger.info("MongoDB Service initialized")

    def _create_indexes(self):
        """Create MongoDB indexes untuk performance"""
        if not self.db:
            return

        try:
            # Documents collection indexes
            docs_collection = self.db[self.collections['documents']]
            docs_collection.create_index([("document_id", 1)], unique=True)
            docs_collection.create_index([("mata_pelajaran", 1), ("kelas", 1)])
            docs_collection.create_index([("created_at", -1)])

            # Embeddings collection indexes
            embeddings_collection = self.db[self.collections['embeddings']]
            embeddings_collection.create_index([("document_id", 1)])
            embeddings_collection.create_index([("chunk_index", 1)])

            # User sessions collection indexes
            sessions_collection = self.db[self.collections['user_sessions']]
            sessions_collection.create_index([("session_id", 1)], unique=True)
            sessions_collection.create_index([("created_at", -1)])
            sessions_collection.create_index([("status", 1)])

            logger.info("MongoDB indexes created successfully")

        except Exception as e:
            logger.warning(f"Error creating MongoDB indexes: {str(e)}")

    async def store_document(self, document_data: Dict[str, Any]) -> Optional[str]:
        """
        Store document di MongoDB

        Args:
            document_data: Document data yang akan disimpan

        Returns:
            str: Document ID jika berhasil
        """
        if not self.db:
            logger.error("MongoDB not connected")
            return None

        try:
            collection = self.db[self.collections['documents']]

            # Add metadata
            document_data.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': 'active'
            })

            result = collection.insert_one(document_data)
            document_id = str(result.inserted_id)

            logger.info(f"Document stored: {document_id}")
            return document_id

        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            return None

    async def store_embeddings(self, document_id: str, embeddings_data: List[Dict[str, Any]]) -> bool:
        """
        Store document embeddings

        Args:
            document_id: ID document
            embeddings_data: List embedding data

        Returns:
            bool: True jika berhasil
        """
        if not self.db:
            logger.error("MongoDB not connected")
            return False

        try:
            collection = self.db[self.collections['embeddings']]

            # Prepare embedding documents
            embedding_docs = []
            for idx, embedding_data in enumerate(embeddings_data):
                doc = {
                    'document_id': document_id,
                    'chunk_index': idx,
                    'created_at': datetime.utcnow(),
                    **embedding_data
                }
                embedding_docs.append(doc)

            if embedding_docs:
                collection.insert_many(embedding_docs)
                logger.info(f"Stored {len(embedding_docs)} embeddings for document: {document_id}")
                return True

        except Exception as e:
            logger.error(f"Error storing embeddings: {str(e)}")

        return False

    async def search_documents(
        self,
        mata_pelajaran: Optional[str] = None,
        kelas: Optional[str] = None,
        topik: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search documents berdasarkan filter

        Args:
            mata_pelajaran: Filter mata pelajaran
            kelas: Filter kelas
            topik: Filter topik
            limit: Limit hasil

        Returns:
            List[Dict]: List documents
        """
        if not self.db:
            return []

        try:
            collection = self.db[self.collections['documents']]

            # Build query
            query = {'status': 'active'}
            if mata_pelajaran:
                query['mata_pelajaran'] = mata_pelajaran
            if kelas:
                query['kelas'] = kelas
            if topik:
                query['topik'] = {'$regex': topik, '$options': 'i'}

            # Execute query
            cursor = collection.find(query).limit(limit).sort('created_at', -1)
            documents = []

            for doc in cursor:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
                documents.append(doc)

            logger.info(f"Found {len(documents)} documents matching criteria")
            return documents

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    async def get_document_embeddings(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get embeddings untuk document tertentu

        Args:
            document_id: ID document

        Returns:
            List[Dict]: List embeddings
        """
        if not self.db:
            return []

        try:
            collection = self.db[self.collections['embeddings']]

            cursor = collection.find({'document_id': document_id}).sort('chunk_index', 1)
            embeddings = []

            for embedding in cursor:
                embedding['_id'] = str(embedding['_id'])
                embeddings.append(embedding)

            return embeddings

        except Exception as e:
            logger.error(f"Error getting document embeddings: {str(e)}")
            return []

    async def store_user_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Store user session data di MongoDB

        Args:
            session_data: Session data

        Returns:
            bool: True jika berhasil
        """
        if not self.db:
            return False

        try:
            collection = self.db[self.collections['user_sessions']]

            # Update or insert
            filter_query = {'session_id': session_data['session_id']}
            update_data = {
                '$set': {
                    **session_data,
                    'updated_at': datetime.utcnow()
                },
                '$setOnInsert': {
                    'created_at': datetime.utcnow()
                }
            }

            collection.update_one(filter_query, update_data, upsert=True)
            logger.debug(f"User session stored: {session_data['session_id']}")
            return True

        except Exception as e:
            logger.error(f"Error storing user session: {str(e)}")
            return False

    async def log_processing_step(self, session_id: str, step_data: Dict[str, Any]) -> bool:
        """
        Log processing step di MongoDB

        Args:
            session_id: ID session
            step_data: Step data

        Returns:
            bool: True jika berhasil
        """
        if not self.db:
            return False

        try:
            collection = self.db[self.collections['processing_logs']]

            log_data = {
                'session_id': session_id,
                'timestamp': datetime.utcnow(),
                **step_data
            }

            collection.insert_one(log_data)
            return True

        except Exception as e:
            logger.error(f"Error logging processing step: {str(e)}")
            return False

    async def store_rag_sources(self, session_id: str, sources: List[Dict[str, Any]]) -> bool:
        """
        Store RAG sources yang digunakan

        Args:
            session_id: ID session
            sources: List sources

        Returns:
            bool: True jika berhasil
        """
        if not self.db:
            return False

        try:
            collection = self.db[self.collections['rag_sources']]

            source_docs = []
            for source in sources:
                doc = {
                    'session_id': session_id,
                    'timestamp': datetime.utcnow(),
                    **source
                }
                source_docs.append(doc)

            if source_docs:
                collection.insert_many(source_docs)
                logger.info(f"Stored {len(source_docs)} RAG sources for session: {session_id}")
                return True

        except Exception as e:
            logger.error(f"Error storing RAG sources: {str(e)}")

        return False

    async def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get complete session history dari MongoDB

        Args:
            session_id: ID session

        Returns:
            Dict: Session history
        """
        if not self.db:
            return {}

        try:
            # Get session data
            sessions_collection = self.db[self.collections['user_sessions']]
            session_data = sessions_collection.find_one({'session_id': session_id})

            # Get processing logs
            logs_collection = self.db[self.collections['processing_logs']]
            processing_logs = list(logs_collection.find({'session_id': session_id}).sort('timestamp', 1))

            # Get RAG sources
            sources_collection = self.db[self.collections['rag_sources']]
            rag_sources = list(sources_collection.find({'session_id': session_id}))

            # Convert ObjectIds to strings
            if session_data:
                session_data['_id'] = str(session_data['_id'])

            for log in processing_logs:
                log['_id'] = str(log['_id'])

            for source in rag_sources:
                source['_id'] = str(source['_id'])

            return {
                'session_data': session_data,
                'processing_logs': processing_logs,
                'rag_sources': rag_sources
            }

        except Exception as e:
            logger.error(f"Error getting session history: {str(e)}")
            return {}

    def get_connection_status(self) -> Dict[str, Any]:
        """Get MongoDB connection status"""
        try:
            if self.db and db_config.mongo_client:
                # Test connection
                db_config.mongo_client.admin.command('ping')
                return {
                    'connected': True,
                    'database': self.db.name,
                    'collections': list(self.db.list_collection_names())
                }
            else:
                return {'connected': False, 'error': 'No connection'}

        except Exception as e:
            return {'connected': False, 'error': str(e)}

# Global MongoDB service instance
mongo_service = MongoService()

def get_mongo_service() -> MongoService:
    """Get MongoDB service dependency untuk FastAPI"""
    return mongo_service
