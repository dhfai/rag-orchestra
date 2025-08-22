# 🎯 RAG Orchestra Quick Start Guide

## Sistem yang Telah Dikembangkan

Saya telah mengembangkan sistem RAG Orchestra sesuai dengan instruksi terbaru dalam file prompt. Berikut adalah komponen utama yang telah diimplementasikan:

## ✨ Fitur Utama

### 1. **Enhanced Main Orchestrator**
- ✅ Implementasi scoring system yang transparan
- ✅ Template Matching Score: `S_tmpl = λ₁ · μₖ + λ₂ · Δ̂`
- ✅ Advanced RAG Score: `S_adv = α₁L' + α₂E' + α₃D + α₄S'`
- ✅ Graph RAG Score: `S_graph = β₁ρ' + β₂δ' + β₃I_pattern`
- ✅ Monitoring Score: `C_overall = min(C_r, C_g)`
- ✅ Decision making berbasis threshold yang telah ditetapkan

### 2. **Prompt Builder Agent**
- ✅ Memastikan input awal menjadi Complete Input
- ✅ Auto-generate CP/ATP jika tidak tersedia
- ✅ Validasi kelengkapan input sesuai format standar
- ✅ Output dalam format JSON standar

### 3. **Multi-Strategy RAG Components**
- ✅ **Simple RAG** - dipilih jika `S_tmpl ≥ 0.85`
- ✅ **Advanced RAG** - dipilih jika `S_adv ≥ 0.6`
- ✅ **Graph RAG** - dipilih jika `S_graph ≥ 0.5`
- ✅ **Adaptive RAG** - fallback strategy

### 4. **Real-time WebSocket Interface**
- ✅ Komunikasi dinamis dengan user
- ✅ Real-time progress updates
- ✅ Interactive client interface
- ✅ Session management

### 5. **Comprehensive Service Layer**
- ✅ **LLM Service** - Support Gemini & OpenAI
- ✅ **Vector DB Service** - ChromaDB dengan embedding
- ✅ **Online Search Service** - DuckDuckGo integration
- ✅ **Document Processing** - CP, ATP, Modul Ajar

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies & setup
python setup.py

# Edit .env file (add your API keys)
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 2. Run System

#### Option A: WebSocket Server (Recommended)
```bash
# Windows
./run.ps1

# Linux/Mac
./run.sh
```
Access: http://localhost:8000/client

#### Option B: Interactive Mode
```bash
python main_system.py
```

#### Option C: Demo Mode
```bash
python -c "import asyncio; from main_system import RAGOrchestraSystem; asyncio.run(RAGOrchestraSystem().run_demo())"
```

## 📡 WebSocket API Usage

### Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session_123');
```

### Start Processing
```javascript
ws.send(JSON.stringify({
    type: 'start_processing',
    data: {
        nama_guru: 'Budi Santoso',
        nama_sekolah: 'SDN 1 Jakarta',
        mata_pelajaran: 'Matematika',
        kelas: '3',
        fase: 'B',
        topik: 'Penjumlahan',
        sub_topik: 'Penjumlahan 1-100',
        alokasi_waktu: '2 x 35 menit',
        llm_model_choice: 'gemini'
    }
}));
```

### Real-time Events
Sistem akan mengirim events seperti:
- `input_analysis` - Analisis input
- `task_analysis_start` - Mulai analisis task
- `strategy_selection_complete` - Strategy terpilih
- `generating_cp_atp` - Generate CP/ATP
- `quality_monitoring` - Monitoring kualitas
- `processing_complete` - Selesai dengan Complete Input

## 📊 Output Format (Complete Input)

```json
{
  "complete_input": {
    "basic_info": {
      "nama_guru": "Budi Santoso",
      "nama_sekolah": "SDN 1 Jakarta",
      "mata_pelajaran": "Matematika",
      "kelas": "3",
      "fase": "B",
      "topik": "Penjumlahan",
      "sub_topik": "Penjumlahan 1-100",
      "alokasi_waktu": "2 x 35 menit"
    },
    "curriculum_content": {
      "cp": "Generated CP content...",
      "atp": "Generated ATP content..."
    },
    "technical_info": {
      "llm_model": "gemini",
      "timestamp": "2024-08-22T10:30:00",
      "status": "complete"
    },
    "metadata": {
      "orchestration_strategy": "cp_atp_generation",
      "rag_strategy_used": "simple",
      "confidence_scores": {...}
    }
  }
}
```

## 🎯 Key Features Implemented

### 1. **Transparent Scoring System**
- Template matching dengan cosine similarity
- Advanced scoring berdasarkan kompleksitas query
- Graph scoring untuk relasi antar konsep
- Monitoring confidence untuk quality assurance

### 2. **Rule-based Decision Making**
- Threshold-based strategy selection
- Orchestration flow berdasarkan input completeness
- Automatic fallback ke Adaptive RAG jika confidence < 0.8

### 3. **Real-time User Interaction**
- WebSocket untuk komunikasi dinamis
- Progress tracking untuk setiap tahap processing
- User validation untuk CP/ATP yang dihasilkan

### 4. **Multi-modal Data Sources**
- Local vector database untuk template matching
- Online search jika data tidak tersedia locally
- Hybrid retrieval untuk hasil optimal

## 📁 Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│ Prompt Builder  │
└─────────────────┘    │     Agent       │
                       └─────────┬───────┘
                                 │
                       ┌─────────▼───────┐
                       │ Enhanced Main   │
                       │  Orchestrator   │
                       └─────────┬───────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼──────┐    ┌───────────▼──────┐    ┌─────────▼──────┐
│ Simple RAG   │    │ Advanced RAG     │    │  Graph RAG     │
│ (S≥0.85)     │    │ (S≥0.6)          │    │ (S≥0.5)        │
└──────────────┘    └──────────────────┘    └────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                       ┌─────────▼───────┐
                       │ Complete Input  │
                       │ (JSON Standard) │
                       └─────────────────┘
```

## 🛠️ Tech Stack Highlights

- **FastAPI** - High-performance async API
- **WebSocket** - Real-time bidirectional communication
- **ChromaDB** - Vector database dengan embedding
- **Gemini/OpenAI** - State-of-the-art LLMs
- **DuckDuckGo Search** - Online content discovery
- **Pydantic** - Data validation dan serialization

## 📈 Quality Assurance

- **Confidence Scoring** - Setiap output memiliki confidence score
- **Multi-level Validation** - Input, process, dan output validation
- **Fallback Mechanisms** - Adaptive RAG untuk handling edge cases
- **Real-time Monitoring** - Live tracking kualitas processing

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### Session Status
```bash
curl http://localhost:8000/sessions
```

### Logs
```bash
tail -f logs/rag_orchestra.log
```

## 🎉 Ready for Next Phase

Sistem ini menghasilkan **Complete Input** yang siap untuk tahap selanjutnya:
- Module Generation Orchestrator
- Quality & Coherence Orchestrator
- Final module assembly

Semua komponen telah diimplementasikan dengan scoring system transparan dan decision making berbasis aturan sesuai instruksi terbaru.
