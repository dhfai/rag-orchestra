from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class LLMModel(Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

class RAGStrategy(Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    GRAPH = "graph"
    ADAPTIVE = "adaptive"

class PromptBuilderStatus(Enum):
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VALIDATING = "validating"
    COMPLETE = "complete"
    ERROR = "error"

class OrchestrationStrategy(Enum):
    DIRECT = "direct"
    CP_ATP_GENERATION = "cp_atp_generation"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    QUALITY_CHECK = "quality_check"

@dataclass
class UserInput:
    """Data class for user input"""
    nama_guru: str
    nama_sekolah: str
    mata_pelajaran: str
    topik: str
    sub_topik: str
    kelas: str
    fase: str  # Added fase field
    alokasi_waktu: str
    model_llm: LLMModel
    cp: Optional[str] = None
    atp: Optional[str] = None

    def __post_init__(self):
        """Validate input after initialization"""
        if isinstance(self.model_llm, str):
            self.model_llm = LLMModel(self.model_llm)

    def has_cp_atp(self) -> bool:
        """Check if CP and ATP are provided"""
        return bool(self.cp and self.atp)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "nama_guru": self.nama_guru,
            "nama_sekolah": self.nama_sekolah,
            "mata_pelajaran": self.mata_pelajaran,
            "topik": self.topik,
            "sub_topik": self.sub_topik,
            "kelas": self.kelas,
            "fase": self.fase,
            "alokasi_waktu": self.alokasi_waktu,
            "model_llm": self.model_llm.value,
            "cp": self.cp,
            "atp": self.atp
        }

@dataclass
class CompleteInput:
    """Complete Input dengan semua field yang diperlukan"""
    nama_guru: str
    nama_sekolah: str
    mata_pelajaran: str
    kelas: str
    fase: str
    topik: str
    sub_topik: str
    alokasi_waktu: str
    cp: str
    atp: str
    llm_model_choice: str
    timestamp: str
    status: PromptBuilderStatus
    processing_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "nama_guru": self.nama_guru,
            "nama_sekolah": self.nama_sekolah,
            "mata_pelajaran": self.mata_pelajaran,
            "kelas": self.kelas,
            "fase": self.fase,
            "topik": self.topik,
            "sub_topik": self.sub_topik,
            "alokasi_waktu": self.alokasi_waktu,
            "cp": self.cp,
            "atp": self.atp,
            "llm_model_choice": self.llm_model_choice,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "processing_metadata": self.processing_metadata
        }

    def to_json_standard(self) -> Dict[str, Any]:
        """Convert to standard JSON format untuk output sistem"""
        return {
            "complete_input": {
                "basic_info": {
                    "nama_guru": self.nama_guru,
                    "nama_sekolah": self.nama_sekolah,
                    "mata_pelajaran": self.mata_pelajaran,
                    "kelas": self.kelas,
                    "fase": self.fase,
                    "topik": self.topik,
                    "sub_topik": self.sub_topik,
                    "alokasi_waktu": self.alokasi_waktu
                },
                "curriculum_content": {
                    "cp": self.cp,
                    "atp": self.atp
                },
                "technical_info": {
                    "llm_model": self.llm_model_choice,
                    "timestamp": self.timestamp,
                    "status": self.status.value
                },
                "metadata": self.processing_metadata
            }
        }

@dataclass
class TaskAnalysisResult:
    """Result of task analysis dengan scoring system"""
    complexity_level: str  # "simple", "medium", "complex"
    complexity_score: float  # 0.0 to 1.0
    missing_components: List[str]
    required_rag_strategy: RAGStrategy
    estimated_processing_time: int  # in seconds
    confidence_score: float  # 0.0 to 1.0

    # Scoring components sesuai instruksi
    template_matching_score: float  # S_tmpl
    advanced_rag_score: float  # S_adv
    graph_rag_score: float  # S_graph

    # Additional metadata
    analysis_metadata: Dict[str, Any]

@dataclass
class StrategySelectionResult:
    """Result dari strategy selection dengan scoring"""
    selected_strategy: RAGStrategy
    strategy_scores: Dict[str, float]
    confidence_level: float
    fallback_strategies: List[RAGStrategy]
    selection_reasoning: str

@dataclass
class MonitoringResult:
    """Result dari monitoring process"""
    retrieval_confidence: float  # C_r
    generation_confidence: float  # C_g
    overall_confidence: float  # C_overall
    quality_metrics: Dict[str, float]
    recommendations: List[str]

@dataclass
class CPATPResult:
    """Result of CP/ATP generation"""
    cp_content: str
    atp_content: str
    generation_strategy: RAGStrategy
    confidence_score: float
    sources_used: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "cp_content": self.cp_content,
            "atp_content": self.atp_content,
            "generation_strategy": self.generation_strategy.value,
            "confidence_score": self.confidence_score,
            "sources_used": self.sources_used
        }

@dataclass
class ValidationResult:
    """Result of validation process"""
    is_valid: bool
    is_approved: bool = True  # For user approval
    feedback: Optional[str] = None
    requested_changes: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    validation_score: float = 1.0

    def has_feedback(self) -> bool:
        """Check if user provided feedback"""
        return bool(self.feedback or self.requested_changes)

    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return bool(self.errors)

    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return bool(self.warnings)

@dataclass
class FinalInput:
    """Final processed input ready for module generation"""
    user_input: UserInput
    cp_content: str
    atp_content: str
    processing_metadata: Dict[str, Any]
    validation_history: List[ValidationResult]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_input": self.user_input.to_dict(),
            "cp_content": self.cp_content,
            "atp_content": self.atp_content,
            "processing_metadata": self.processing_metadata,
            "validation_history": [
                {
                    "is_approved": v.is_approved,
                    "feedback": v.feedback,
                    "requested_changes": v.requested_changes
                } for v in self.validation_history
            ]
        }
