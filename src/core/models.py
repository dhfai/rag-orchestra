from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

class LLMModel(Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GPT_4 = "gpt-4"

class RAGStrategy(Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    GRAPH = "graph"

@dataclass
class UserInput:
    """Data class for user input"""
    nama_guru: str
    nama_sekolah: str
    mata_pelajaran: str
    topik: str
    sub_topik: str
    kelas: str
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
            "alokasi_waktu": self.alokasi_waktu,
            "model_llm": self.model_llm.value,
            "cp": self.cp,
            "atp": self.atp
        }

@dataclass
class TaskAnalysisResult:
    """Result of task analysis"""
    complexity_level: str  # "simple", "medium", "complex"
    missing_components: List[str]
    required_rag_strategy: RAGStrategy
    estimated_processing_time: int  # in seconds
    confidence_score: float  # 0.0 to 1.0

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
    """Result of user validation"""
    is_approved: bool
    feedback: Optional[str] = None
    requested_changes: Optional[List[str]] = None

    def has_feedback(self) -> bool:
        """Check if user provided feedback"""
        return bool(self.feedback or self.requested_changes)

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
