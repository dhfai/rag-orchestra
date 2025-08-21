"""
API Schemas untuk RAG Multi-Strategy System
===========================================

Pydantic models untuk request/response API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class LLMModelEnum(str, Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GPT_4 = "gpt-4"

class RAGStrategyEnum(str, Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    GRAPH = "graph"

class SessionStatusEnum(str, Enum):
    CREATED = "created"
    INPUT_COLLECTION = "input_collection"
    PROCESSING = "processing"
    CP_ATP_GENERATION = "cp_atp_generation"
    USER_VALIDATION = "user_validation"
    REFINEMENT = "refinement"
    COMPLETED = "completed"
    ERROR = "error"

# === REQUEST SCHEMAS ===

class CreateSessionRequest(BaseModel):
    """Request untuk membuat session baru"""
    user_id: Optional[str] = Field(None, description="ID user (optional)")
    session_name: Optional[str] = Field(None, description="Nama session (optional)")

class UserInputRequest(BaseModel):
    """Request untuk input user"""
    nama_guru: str = Field(..., description="Nama guru")
    nama_sekolah: str = Field(..., description="Nama sekolah")
    mata_pelajaran: str = Field(..., description="Mata pelajaran")
    topik: str = Field(..., description="Topik pembelajaran")
    sub_topik: str = Field(..., description="Sub topik pembelajaran")
    kelas: str = Field(..., description="Kelas (contoh: 'Kelas 5')")
    alokasi_waktu: str = Field(..., description="Alokasi waktu (contoh: '2 x 45 menit')")
    model_llm: LLMModelEnum = Field(..., description="Model LLM yang digunakan")
    cp: Optional[str] = Field(None, description="Capaian Pembelajaran (optional)")
    atp: Optional[str] = Field(None, description="Alur Tujuan Pembelajaran (optional)")

class ValidationRequest(BaseModel):
    """Request untuk validasi CP/ATP"""
    is_approved: bool = Field(..., description="Apakah user menyetujui CP/ATP")
    feedback: Optional[str] = Field(None, description="Feedback dari user")
    requested_changes: Optional[List[str]] = Field(None, description="Perubahan yang diminta")

class RefinementRequest(BaseModel):
    """Request untuk refinement berdasarkan feedback"""
    feedback: str = Field(..., description="Feedback user untuk perbaikan")
    specific_changes: Optional[List[str]] = Field(None, description="Perubahan spesifik")

class ConfigRequest(BaseModel):
    """Request untuk konfigurasi session"""
    max_processing_time: Optional[int] = Field(3600, description="Maksimal waktu processing (detik)")
    preferred_strategy: Optional[RAGStrategyEnum] = Field(RAGStrategyEnum.SIMPLE, description="Strategi RAG yang diinginkan")
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Preferensi user")
    timeout_settings: Optional[Dict[str, int]] = Field(default_factory=dict, description="Setting timeout")

# === RESPONSE SCHEMAS ===

class SessionResponse(BaseModel):
    """Response untuk session"""
    session_id: str = Field(..., description="ID session")
    status: SessionStatusEnum = Field(..., description="Status session")
    created_at: str = Field(..., description="Waktu pembuatan session")
    updated_at: str = Field(..., description="Waktu update terakhir")
    user_id: Optional[str] = Field(None, description="ID user")
    session_name: Optional[str] = Field(None, description="Nama session")

class SessionCreateResponse(BaseModel):
    """Response untuk pembuatan session baru"""
    session_id: str = Field(..., description="ID session yang dibuat")
    status: SessionStatusEnum = Field(..., description="Status session")
    created_at: str = Field(..., description="Waktu pembuatan session")
    config: Dict[str, Any] = Field(default_factory=dict, description="Konfigurasi session")

class SessionStatusResponse(BaseModel):
    """Response untuk status session detail"""
    session_id: str = Field(..., description="ID session")
    status: SessionStatusEnum = Field(..., description="Status session")
    current_step: str = Field(..., description="Step saat ini")
    progress_percentage: float = Field(..., description="Persentase progress")
    created_at: str = Field(..., description="Waktu pembuatan")
    last_activity: str = Field(..., description="Aktivitas terakhir")
    processing_status: Optional[Dict[str, Any]] = Field(None, description="Status processing detail")
    has_user_input: bool = Field(..., description="Apakah sudah ada user input")
    has_cp_atp_result: bool = Field(..., description="Apakah sudah ada hasil CP/ATP")
    has_final_input: bool = Field(..., description="Apakah sudah ada final input")
    validation_count: int = Field(..., description="Jumlah validasi")
    error_count: int = Field(..., description="Jumlah error")
    last_error: Optional[str] = Field(None, description="Error terakhir")

class TaskAnalysisResponse(BaseModel):
    """Response untuk analisis task"""
    complexity_level: str = Field(..., description="Level kompleksitas")
    missing_components: List[str] = Field(..., description="Komponen yang hilang")
    required_rag_strategy: RAGStrategyEnum = Field(..., description="Strategi RAG yang diperlukan")
    estimated_processing_time: int = Field(..., description="Estimasi waktu proses (detik)")
    confidence_score: float = Field(..., description="Skor confidence (0.0-1.0)")

class CPATPResponse(BaseModel):
    """Response untuk CP/ATP yang dihasilkan"""
    cp_content: str = Field(..., description="Konten Capaian Pembelajaran")
    atp_content: str = Field(..., description="Konten Alur Tujuan Pembelajaran")
    generation_strategy: RAGStrategyEnum = Field(..., description="Strategi yang digunakan")
    confidence_score: float = Field(..., description="Skor confidence")
    sources_used: List[str] = Field(..., description="Sumber yang digunakan")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata generasi")

class ProcessingStatusResponse(BaseModel):
    """Response untuk status processing"""
    session_id: str = Field(..., description="ID session")
    status: SessionStatusEnum = Field(..., description="Status saat ini")
    current_step: str = Field(..., description="Step yang sedang berjalan")
    progress_percentage: float = Field(..., description="Persentase progress (0.0-100.0)")
    estimated_remaining_time: Optional[int] = Field(None, description="Estimasi waktu tersisa (detik)")
    last_updated: str = Field(..., description="Waktu update terakhir")

class FinalInputResponse(BaseModel):
    """Response untuk final input"""
    session_id: str = Field(..., description="ID session")
    user_input: UserInputRequest = Field(..., description="Input user original")
    cp_content: str = Field(..., description="Final CP content")
    atp_content: str = Field(..., description="Final ATP content")
    processing_metadata: Dict[str, Any] = Field(..., description="Metadata processing")
    validation_history: List[Dict[str, Any]] = Field(..., description="History validasi")
    completed_at: str = Field(..., description="Waktu penyelesaian")

class ErrorResponse(BaseModel):
    """Response untuk error"""
    error_code: str = Field(..., description="Kode error")
    error_message: str = Field(..., description="Pesan error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detail tambahan")
    timestamp: str = Field(..., description="Waktu error")
    session_id: Optional[str] = Field(None, description="ID session (jika ada)")

# === WEBSOCKET SCHEMAS ===

class WebSocketMessage(BaseModel):
    """Base schema untuk WebSocket messages"""
    type: str = Field(..., description="Tipe message")
    session_id: str = Field(..., description="ID session")
    timestamp: str = Field(..., description="Timestamp message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Data payload")

class WebSocketUserInputMessage(WebSocketMessage):
    """WebSocket message untuk user input"""
    type: str = Field(default="user_input", description="Tipe message")
    data: UserInputRequest = Field(..., description="User input data")

class WebSocketValidationMessage(WebSocketMessage):
    """WebSocket message untuk validation"""
    type: str = Field(default="validation", description="Tipe message")
    data: ValidationRequest = Field(..., description="Validation data")

class WebSocketStatusMessage(WebSocketMessage):
    """WebSocket message untuk status update"""
    type: str = Field(default="status_update", description="Tipe message")
    data: ProcessingStatusResponse = Field(..., description="Status data")

class WebSocketCPATPMessage(WebSocketMessage):
    """WebSocket message untuk CP/ATP hasil generasi"""
    type: str = Field(default="cp_atp_generated", description="Tipe message")
    data: CPATPResponse = Field(..., description="CP/ATP data")

class WebSocketFinalMessage(WebSocketMessage):
    """WebSocket message untuk final result"""
    type: str = Field(default="final_result", description="Tipe message")
    data: FinalInputResponse = Field(..., description="Final result data")

class WebSocketErrorMessage(WebSocketMessage):
    """WebSocket message untuk error"""
    type: str = Field(default="error", description="Tipe message")
    data: ErrorResponse = Field(..., description="Error data")

# === UTILITY SCHEMAS ===

class HealthCheckResponse(BaseModel):
    """Response untuk health check"""
    status: str = Field(default="healthy", description="Status sistem")
    version: str = Field(..., description="Versi aplikasi")
    timestamp: str = Field(..., description="Timestamp check")
    components: Dict[str, str] = Field(default_factory=dict, description="Status komponen")

class SystemInfoResponse(BaseModel):
    """Response untuk system info"""
    version: str = Field(..., description="Versi sistem")
    available_strategies: List[RAGStrategyEnum] = Field(..., description="Strategi RAG tersedia")
    supported_models: List[LLMModelEnum] = Field(..., description="Model LLM yang didukung")
    max_concurrent_sessions: int = Field(..., description="Maksimal session bersamaan")
    current_active_sessions: int = Field(..., description="Session aktif saat ini")

class SessionListResponse(BaseModel):
    """Response untuk daftar session"""
    sessions: List[SessionResponse] = Field(..., description="Daftar session")
    total_count: int = Field(..., description="Total jumlah session")
    active_count: int = Field(..., description="Jumlah session aktif")

# === VALIDATION SCHEMAS ===

class SessionValidation(BaseModel):
    """Validation untuk session operations"""

    @classmethod
    def validate_session_id(cls, session_id: str) -> bool:
        """Validasi format session ID"""
        return len(session_id) > 0 and session_id.replace('-', '').replace('_', '').isalnum()

    @classmethod
    def validate_user_input(cls, user_input: UserInputRequest) -> List[str]:
        """Validasi user input dan return list error messages"""
        errors = []

        if not user_input.nama_guru.strip():
            errors.append("Nama guru tidak boleh kosong")

        if not user_input.mata_pelajaran.strip():
            errors.append("Mata pelajaran tidak boleh kosong")

        if not user_input.topik.strip():
            errors.append("Topik tidak boleh kosong")

        if not user_input.kelas.strip():
            errors.append("Kelas tidak boleh kosong")

        return errors

# === CONFIG SCHEMAS ===

class APIConfig(BaseModel):
    """Configuration untuk API"""
    host: str = Field(default="0.0.0.0", description="Host API")
    port: int = Field(default=8000, description="Port API")
    reload: bool = Field(default=False, description="Auto reload")
    workers: int = Field(default=1, description="Jumlah workers")
    log_level: str = Field(default="info", description="Log level")

class WebSocketConfig(BaseModel):
    """Configuration untuk WebSocket"""
    max_connections: int = Field(default=100, description="Maksimal koneksi WebSocket")
    heartbeat_interval: int = Field(default=30, description="Interval heartbeat (detik)")
    message_timeout: int = Field(default=300, description="Timeout message (detik)")

class RAGConfig(BaseModel):
    """Configuration untuk RAG processing"""
    default_strategy: RAGStrategyEnum = Field(default=RAGStrategyEnum.SIMPLE, description="Strategi default")
    max_documents: int = Field(default=10, description="Maksimal dokumen per retrieval")
    confidence_threshold: float = Field(default=0.7, description="Threshold confidence")
    max_retries: int = Field(default=3, description="Maksimal retry")
    timeout_seconds: int = Field(default=300, description="Timeout processing (detik)")

# === WEBSOCKET SCHEMAS ===

class WebSocketMessageType(str, Enum):
    """Enum untuk WebSocket message types"""
    CONNECTION_ESTABLISHED = "connection_established"
    STATUS_UPDATE = "status_update"
    CP_ATP_GENERATED = "cp_atp_generated"
    VALIDATION_REQUEST = "validation_request"
    FINAL_RESULT = "final_result"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"

class WebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: WebSocketMessageType = Field(..., description="Tipe message")
    session_id: str = Field(..., description="ID session")
    timestamp: str = Field(..., description="Timestamp message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Data message")

class WebSocketStatusUpdate(BaseModel):
    """WebSocket status update message"""
    message: str = Field(..., description="Status message")
    step: str = Field(..., description="Current step")
    progress: Optional[float] = Field(None, description="Progress percentage")

class WebSocketCPATPGenerated(BaseModel):
    """WebSocket CP/ATP generated message"""
    cp_content: str = Field(..., description="Generated CP content")
    atp_content: str = Field(..., description="Generated ATP content")
    confidence_score: float = Field(..., description="Confidence score")
    sources_used: List[str] = Field(..., description="Sources used")
    message: str = Field(..., description="User message")

class WebSocketError(BaseModel):
    """WebSocket error message"""
    error_message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")
