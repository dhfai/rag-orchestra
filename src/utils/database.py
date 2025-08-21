"""
Database Configuration dan Setup
================================

Database configuration untuk RAG Multi-Strategy Backend
Mendukung MySQL, MongoDB, dan Redis
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import pymongo
from typing import Optional, Dict, Any

from ..utils.logger import get_logger

logger = get_logger("DatabaseConfig")

# Base untuk SQLAlchemy models
Base = declarative_base()

class DatabaseConfig:
    """Configuration untuk database connections"""

    def __init__(self):
        # MySQL Configuration
        self.mysql_host = os.getenv("MYSQL_HOST", "if.unismuh.ac.id")
        self.mysql_port = int(os.getenv("MYSQL_PORT", "3388"))
        self.mysql_user = os.getenv("MYSQL_USER", "root")
        self.mysql_password = os.getenv("MYSQL_PASSWORD", "mariabelajar")
        self.mysql_database = os.getenv("MYSQL_DATABASE", "rag_multi_strategy")

        # MongoDB Configuration
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "rag_multi_strategy")

        # SQLAlchemy URL
        self.database_url = os.getenv(
            "DATABASE_URL",
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )
        self.database_echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # Ensure data directory exists
        data_dir = Path("./data")
        data_dir.mkdir(exist_ok=True)

        # Initialize connections
        self._engine = None
        self._session_local = None
        self._redis_client = None
        self._mongo_client = None
        self._mongo_db = None

        logger.info(f"MySQL Host: {self.mysql_host}:{self.mysql_port}")
        logger.info(f"MySQL Database: {self.mysql_database}")
        logger.info(f"MongoDB URL: {self.mongodb_url}")
        logger.info(f"Redis URL: {self.redis_url}")

    @property
    def engine(self):
        """Get SQLAlchemy engine"""
        if self._engine is None:
            if self.database_url.startswith("sqlite"):
                # SQLite configuration
                self._engine = create_engine(
                    self.database_url,
                    echo=self.database_echo,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 30
                    },
                    poolclass=StaticPool
                )
            elif self.database_url.startswith("mysql"):
                # MySQL configuration
                self._engine = create_engine(
                    self.database_url,
                    echo=self.database_echo,
                    pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
                    max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "30")),
                    pool_timeout=30,
                    pool_recycle=3600,
                    pool_pre_ping=True,
                    connect_args={
                        "charset": "utf8mb4",
                        "connect_timeout": 60,
                        "read_timeout": 60,
                        "write_timeout": 60
                    }
                )
            else:
                # PostgreSQL configuration
                self._engine = create_engine(
                    self.database_url,
                    echo=self.database_echo,
                    pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
                    max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "30")),
                    pool_timeout=30,
                    pool_recycle=3600
                )

            logger.info(f"Database engine created: {type(self._engine.dialect).__name__}")

        return self._engine

    @property
    def mongo_client(self):
        """Get MongoDB client"""
        if self._mongo_client is None:
            try:
                self._mongo_client = pymongo.MongoClient(
                    self.mongodb_url,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000
                )
                # Test connection
                self._mongo_client.admin.command('ping')
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {str(e)}")
                self._mongo_client = None

        return self._mongo_client

    @property
    def mongo_db(self):
        """Get MongoDB database"""
        if self._mongo_db is None and self.mongo_client:
            self._mongo_db = self.mongo_client[self.mongodb_database]
        return self._mongo_db

    @property
    def session_local(self):
        """Get SQLAlchemy session local"""
        if self._session_local is None:
            self._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._session_local

    @property
    def redis_client(self) -> Optional[redis.Redis]:
        """Get Redis client"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self.redis_url,
                    password=os.getenv("REDIS_PASSWORD", None),
                    socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
                    max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
                    decode_responses=True
                )

                # Test connection
                self._redis_client.ping()
                logger.info("Redis connection established")

            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}")
                self._redis_client = None

        return self._redis_client

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    def get_db_session(self):
        """Get database session"""
        db = self.session_local()
        try:
            yield db
        finally:
            db.close()

    async def close_connections(self):
        """Close all database connections"""
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("Database engine disposed")

            if self._redis_client:
                await self._redis_client.aclose()
                logger.info("Redis connection closed")

        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

# Global database config instance
db_config = DatabaseConfig()

# Database dependency untuk FastAPI
def get_database():
    """Database dependency untuk FastAPI endpoints"""
    return next(db_config.get_db_session())

# Redis dependency untuk FastAPI
def get_redis():
    """Redis dependency untuk FastAPI endpoints"""
    return db_config.redis_client
