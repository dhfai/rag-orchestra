# RAG Orchestra - Orchestrated RAG Modul Ajar Digital

## 📋 Overview

Sistem **Orchestrated RAG (Retrieval-Augmented Generation)** untuk pembuatan modul ajar digital dengan pendekatan multi-strategy dan real-time interaction.

## 🏗️ Architecture

Sistem menggunakan pendekatan **Orchestrated RAG** dengan komponen:

1. **Main Orchestrator** - Pengendali proses utama dengan scoring system
2. **Prompt Builder Agent** - Memastikan input lengkap (Complete Input)
3. **Multi-Strategy RAG Components**:
   - Simple RAG (template matching ≥ 0.85)
   - Advanced RAG (complex queries ≥ 0.6)
   - Graph RAG (relational patterns ≥ 0.5)
   - Adaptive RAG (fallback strategy)
4. **Real-time WebSocket** - Komunikasi dinamis dengan user

## 🛠️ Tech Stack

- **Python 3.8+** - Core language
- **FastAPI** - RESTful API framework
- **WebSocket** - Real-time communication
- **ChromaDB** - Vector database
- **LLM APIs** - Gemini, OpenAI
- **DuckDuckGo Search** - Online content retrieval
- **MongoDB** - Document storage
- **Redis** - Caching layer

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd rag-orchestra
```

### 2. Run Setup
```bash
# Windows
python setup.py

# Linux/Mac
python3 setup.py
```

### 3. Configure Environment
Edit `.env` file and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Usage

### Option 1: WebSocket Server (Recommended)
```bash
# Windows
.\run.ps1

# Linux/Mac
./run.sh
```

Access WebSocket client: http://localhost:8000/client

### Option 2: Interactive Mode
```bash
python main_system.py
```

### Option 3: Demo Mode
```bash
python -c "import asyncio; from main_system import RAGOrchestraSystem; asyncio.run(RAGOrchestraSystem().run_demo())"
```

## 📡 WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/your_session_id');
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

### Response Format
```javascript
{
    "type": "processing_complete",
    "data": {
        "complete_input": {
            "basic_info": { ... },
            "curriculum_content": {
                "cp": "Generated CP content...",
                "atp": "Generated ATP content..."
            },
            "technical_info": { ... },
            "metadata": { ... }
        }
    },
    "timestamp": "2024-08-22T10:30:00"
}
```

## 🧠 Scoring System

Sistem menggunakan scoring transparan untuk strategy selection:

### Template Matching Score
```
S_tmpl = λ₁ · μₖ + λ₂ · Δ̂
```
- μₖ = rata-rata cosine similarity top-k
- Δ̂ = margin antara dokumen teratas
- λ₁ = 0.8, λ₂ = 0.2

### Advanced RAG Score
```
S_adv = α₁L' + α₂E' + α₃D + α₄S'
```
- L' = panjang query ternormalisasi
- E' = jumlah entitas ternormalisasi
- D = document dispersion
- S' = query specificity

### Monitoring Score
```
C_overall = min(C_r, C_g)
```
- C_r = retrieval confidence
- C_g = generation confidence

## 📁 Project Structure

```
rag-orchestra/
├── src/
│   ├── core/
│   │   ├── models.py
│   │   └── prompt_builder_agent.py
│   ├── orchestrator/
│   │   └── enhanced_main_orchestrator.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── vector_db_service.py
│   │   └── online_search_service.py
│   └── utils/
├── data/
│   ├── cp/
│   ├── atp/
│   └── modul_ajar/
├── config/
├── logs/
├── main_websocket_app.py
├── main_system.py
├── setup.py
└── run.ps1 / run.sh
```

## 🔧 Configuration

### Orchestrator Thresholds
- Simple RAG: S_tmpl ≥ 0.85
- Advanced RAG: S_adv ≥ 0.6
- Graph RAG: S_graph ≥ 0.5
- Overall Confidence: C_overall ≥ 0.8

### Model Support
- **Gemini**: 1.5 Flash, 1.5 Pro
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Active Sessions
```bash
curl http://localhost:8000/sessions
```

## 🐛 Troubleshooting

### Common Issues

1. **ImportError**: Run `python setup.py` to install dependencies
2. **API Key Error**: Check `.env` file configuration
3. **WebSocket Connection Failed**: Ensure port 8000 is available
4. **Vector DB Error**: Check `vector_db/` directory permissions

### Logs
Check logs in `logs/rag_orchestra.log` for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

[License information]

## 📞 Support

For issues and questions, please check the logs and documentation first.
