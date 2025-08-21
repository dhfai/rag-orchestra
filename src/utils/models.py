"""
Database Models
===============

SQLAlchemy models untuk session persistence dan data storage
Optimized untuk MySQL dengan proper charset dan indexing
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, Index
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMTEXT
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from ..utils.database import Base

class SessionModel(Base):
    """Model untuk session storage"""
    __tablename__ = "sessions"

    # Add MySQL specific table options
    __table_args__ = (
        Index('idx_session_status', 'status'),
        Index('idx_session_created_at', 'created_at'),
        Index('idx_session_updated_at', 'updated_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(50), nullable=False, default="idle")
    current_step = Column(String(100), default="")
    progress_percentage = Column(Float, default=0.0)

    # User input data (use LONGTEXT for MySQL)
    user_input_data = Column(LONGTEXT, nullable=True)

    # Processing results (use LONGTEXT for large JSON data)
    task_analysis = Column(LONGTEXT, nullable=True)
    cp_atp_result = Column(LONGTEXT, nullable=True)
    final_input_data = Column(JSON, nullable=True)

    # Validation history
    validation_history = Column(JSON, default=list)

    # Session metadata
    config = Column(JSON, default=dict)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    processing_start_time = Column(DateTime, nullable=True)
    processing_end_time = Column(DateTime, nullable=True)

    # Expiry
    expires_at = Column(DateTime, nullable=True)

class ProcessingLogModel(Base):
    """Model untuk processing logs"""
    __tablename__ = "processing_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)

    step_name = Column(String, nullable=False)
    step_status = Column(String, nullable=False)  # started, completed, failed
    step_data = Column(JSON, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

class UserInputModel(Base):
    """Model untuk user input history"""
    __tablename__ = "user_inputs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)

    # User input fields
    nama_guru = Column(String, nullable=False)
    nama_sekolah = Column(String, nullable=False)
    mata_pelajaran = Column(String, nullable=False)
    topik = Column(String, nullable=False)
    sub_topik = Column(String, nullable=True)
    kelas = Column(String, nullable=False)
    alokasi_waktu = Column(String, nullable=False)
    model_llm = Column(String, nullable=False)

    # Optional CP/ATP
    cp = Column(Text, nullable=True)
    atp = Column(Text, nullable=True)

    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

class CPATPResultModel(Base):
    """Model untuk CP/ATP generation results"""
    __tablename__ = "cp_atp_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)

    # Generated content
    cp_content = Column(Text, nullable=False)
    atp_content = Column(Text, nullable=False)

    # Generation metadata
    generation_strategy = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    sources_used = Column(JSON, default=list)
    generation_metadata = Column(JSON, default=dict)

    # Processing info
    processing_time_seconds = Column(Float, nullable=True)
    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Validation
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, nullable=True)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)

class ValidationModel(Base):
    """Model untuk validation history"""
    __tablename__ = "validations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    cp_atp_result_id = Column(String, nullable=True)

    # Validation data
    is_approved = Column(Boolean, nullable=False)
    feedback = Column(Text, nullable=True)
    requested_changes = Column(JSON, default=list)

    # Validation metadata
    validation_score = Column(Float, nullable=True)
    validator_type = Column(String, default="user")  # user, auto, expert

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)

class APIUsageModel(Base):
    """Model untuk API usage tracking"""
    __tablename__ = "api_usage"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=True)

    # Request info
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)

    # Performance
    response_time_ms = Column(Float, nullable=False)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)

    # Client info
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Error info
    error_message = Column(Text, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemMetricsModel(Base):
    """Model untuk system metrics"""
    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Metrics
    active_sessions = Column(Integer, nullable=False)
    total_sessions_today = Column(Integer, nullable=False)
    avg_processing_time = Column(Float, nullable=False)
    success_rate = Column(Float, nullable=False)

    # Resource usage
    cpu_usage_percent = Column(Float, nullable=True)
    memory_usage_mb = Column(Float, nullable=True)
    disk_usage_percent = Column(Float, nullable=True)

    # API metrics
    requests_per_minute = Column(Float, nullable=False)
    websocket_connections = Column(Integer, nullable=False)

    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow)
