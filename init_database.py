"""
Database Initialization Script
==============================

Script untuk initialize database tables dan setup awal
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import db_config, Base
from src.utils.models import *
from src.utils.logger import get_logger

logger = get_logger("DatabaseInit")

def create_database_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")

        # Test connection first
        engine = db_config.engine
        connection = engine.connect()
        logger.info("Database connection successful")
        connection.close()

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.success("All database tables created successfully")

        # Print table information
        inspector = engine.dialect.get_inspector(engine)
        table_names = inspector.get_table_names()

        logger.info(f"Created {len(table_names)} tables:")
        for table_name in table_names:
            logger.info(f"  - {table_name}")

        return True

    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

def test_database_connection():
    """Test database connections"""
    logger.info("Testing database connections...")

    # Test MySQL connection
    try:
        engine = db_config.engine
        connection = engine.connect()
        result = connection.execute("SELECT 1")
        logger.success("✓ MySQL connection successful")
        connection.close()
    except Exception as e:
        logger.error(f"✗ MySQL connection failed: {str(e)}")
        return False

    # Test MongoDB connection
    try:
        if db_config.mongo_client:
            db_config.mongo_client.admin.command('ping')
            logger.success("✓ MongoDB connection successful")
        else:
            logger.warning("⚠ MongoDB client not initialized")
    except Exception as e:
        logger.warning(f"⚠ MongoDB connection failed: {str(e)}")

    # Test Redis connection
    try:
        if db_config.redis_client:
            db_config.redis_client.ping()
            logger.success("✓ Redis connection successful")
        else:
            logger.warning("⚠ Redis client not initialized")
    except Exception as e:
        logger.warning(f"⚠ Redis connection failed: {str(e)}")

    return True

def show_database_info():
    """Show database configuration info"""
    logger.info("Database Configuration:")
    logger.info(f"MySQL Host: {db_config.mysql_host}:{db_config.mysql_port}")
    logger.info(f"MySQL Database: {db_config.mysql_database}")
    logger.info(f"MongoDB URL: {db_config.mongodb_url}")
    logger.info(f"MongoDB Database: {db_config.mongodb_database}")
    logger.info(f"Redis URL: {db_config.redis_url}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Database Initialization")
    parser.add_argument("--test", action="store_true", help="Test database connections")
    parser.add_argument("--create", action="store_true", help="Create database tables")
    parser.add_argument("--info", action="store_true", help="Show database info")
    parser.add_argument("--all", action="store_true", help="Run all operations")

    args = parser.parse_args()

    if args.all or args.info:
        show_database_info()

    if args.all or args.test:
        if not test_database_connection():
            logger.error("Database connection test failed")
            sys.exit(1)

    if args.all or args.create:
        if not create_database_tables():
            logger.error("Database table creation failed")
            sys.exit(1)

    if not any([args.test, args.create, args.info, args.all]):
        # Default: show info and test connection
        show_database_info()
        test_database_connection()

if __name__ == "__main__":
    main()
