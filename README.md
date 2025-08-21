# RAG Multi-Strategy System

## 🎓 Sistem Pembuat Modul Ajar Kurikulum Merdeka

Sistem interaktif yang menggunakan teknologi RAG (Retrieval-Augmented Generation) dengan multiple strategy untuk menghasilkan Capaian Pembelajaran (CP) dan Alur Tujuan Pembelajaran (ATP) berkualitas tinggi sesuai Kurikulum Merdeka.

## 📋 Deskripsi

Sistem ini mengikuti flowchart yang telah didefinisikan dalam `prompt_builder1.md` dan mengimplementasikan arsitektur multi-orchestrator untuk pengelolaan proses yang efisien dan berkualitas tinggi.

### 🏗️ Arsitektur Sistem

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   User Input    │───▶│  Main Orchestrator   │───▶│   Final Input       │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                │
                                ▼
                       ┌──────────────────────┐
                       │ CP/ATP Orchestrator  │
                       └──────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │SimpleRAG │ │AdvancedRAG│ │ GraphRAG │
            └──────────┘ └──────────┘ └──────────┘
```

## 🚀 Fitur Utama

### 1. **Main Orchestrator**
- **Task Analysis**: Menganalisis kompleksitas dan kebutuhan request
- **Strategy Selection**: Memilih strategi RAG yang tepat
- **Decision Making**: Menentukan alur proses yang optimal
- **Monitoring**: Mengawasi kualitas output di setiap tahapan

### 2. **CP/ATP Generation Sub-Orchestrator**
- Pemilihan strategi RAG berdasarkan konteks pembelajaran
- Pengelolaan proses generation dan validation
- Handling iterative refinement berdasarkan feedback

### 3. **Multiple RAG Strategies**

#### 🔷 Simple RAG
- **Deskripsi**: Template-based retrieval dengan direct keyword matching
- **Use Case**: Query sederhana dengan template yang tersedia
- **Kelebihan**: Cepat, reliable, konsisten

#### 🔶 Advanced RAG
- **Deskripsi**: Query rewriting, semantic search, dan result reranking
- **Use Case**: Query kompleks yang memerlukan sintesis berbagai sumber
- **Kelebihan**: Komprehensif, multi-perspektif, kualitas tinggi

#### 🔸 Graph RAG
- **Deskripsi**: Knowledge graph navigation untuk relasi antar konsep
- **Use Case**: Kebutuhan relasional dan pemahaman holistik
- **Kelebihan**: Relational understanding, cross-curricular integration

## 🛠️ Teknologi yang Digunakan

- **Python 3.8+**: Bahasa pemrograman utama
- **FastAPI**: Web framework (untuk development selanjutnya)
- **Rich**: Beautiful terminal output dan logging
- **Asyncio**: Asynchronous programming
- **MySQL**: Database relational
- **MongoDB**: Database NoSQL
- **ChromaDB**: Vector database
- **Gemini & OpenAI**: Large Language Models

## 📦 Instalasi

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd penelitian
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file dengan konfigurasi Anda
   ```

4. **Setup database** (opsional untuk fase ini)
   ```bash
   # Setup MySQL dan MongoDB sesuai konfigurasi
   ```

## 🚀 Cara Penggunaan

### Menjalankan Aplikasi

```bash
python main.py
```

### Alur Penggunaan

1. **Input Data**: Masukkan informasi pembelajaran
   - Nama Guru
   - Nama Sekolah
   - Mata Pelajaran
   - Topik & Sub Topik
   - Kelas
   - Alokasi Waktu
   - Model LLM (Gemini/GPT-4)
   - CP & ATP (opsional)

2. **Proses Otomatis**: Sistem akan:
   - Menganalisis kompleksitas tugas
   - Memilih strategi RAG yang tepat
   - Generate CP/ATP (jika diperlukan)
   - Meminta validasi user
   - Melakukan refinement jika diperlukan

3. **Final Input**: Sistem menampilkan hasil final yang siap untuk tahap selanjutnya

## 📁 Struktur Project

```
penelitian/
├── main.py                 # Aplikasi utama
├── requirements.txt        # Dependencies
├── .env.example           # Template environment variables
├── prompt_builder1.md     # Spesifikasi sistem
├── config/
│   └── config.py          # Konfigurasi sistem
├── src/
│   ├── core/              # Core components
│   │   ├── models.py      # Data models
│   │   └── user_interface.py  # Interactive UI
│   ├── orchestrator/      # Orchestrator components
│   │   ├── main_orchestrator.py
│   │   └── cp_atp_orchestrator.py
│   ├── rag/               # RAG implementations
│   │   ├── base_rag.py
│   │   ├── simple_rag.py
│   │   ├── advanced_rag.py
│   │   └── graph_rag.py
│   └── utils/
│       └── logger.py      # Logging utilities
├── logs/                  # Log files
└── data/                  # Data directory
    ├── cp/                # Capaian Pembelajaran docs
    ├── atp/               # Alur Tujuan Pembelajaran docs
    └── modul_ajar/        # Modul Ajar docs
```

## 🎯 Current Status

**✅ Completed (Phase 1)**
- ✅ User Input Collection
- ✅ Main Orchestrator Implementation
- ✅ CP/ATP Generation Sub-Orchestrator
- ✅ Three RAG Strategy Implementations
- ✅ User Validation Flow
- ✅ Refinement Strategy
- ✅ Final Input Display
- ✅ Beautiful Logging System
- ✅ Interactive User Interface

**🚧 Next Phase (Development Plan)**
- 🔄 Database Integration (MySQL, MongoDB, ChromaDB)
- 🔄 Real LLM API Integration (Gemini, OpenAI)
- 🔄 Document Processing from data/ directory
- 🔄 Web Interface with FastAPI
- 🔄 Modul Ajar Generation
- 🔄 Advanced Analytics & Reporting

## 📊 Logging & Monitoring

Sistem dilengkapi dengan logging yang komprehensif dan visual:

- **Rich Console Output**: Tampilan terminal yang indah dan informatif
- **File Logging**: Log terstruktur disimpan di `logs/` directory
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Component-Specific Logging**: Orchestrator, RAG, User Interaction
- **Progress Tracking**: Visual progress untuk proses panjang

### Log Locations
- **Console**: Rich formatted output
- **File**: `logs/rag_system_YYYYMMDD.log`

## 🔧 Konfigurasi

Edit file `.env` untuk konfigurasi:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=rag_multi_strategy

MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=rag_multi_strategy

# Vector Database
CHROMA_PERSIST_DIRECTORY=./vector_db

# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Application Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## 🎨 Contoh Output

```
╔══════════════════════════════════════════════════════════════╗
║  🎓 RAG Multi-Strategy System                                ║
║  Sistem Pembuat Modul Ajar Kurikulum Merdeka               ║
╚══════════════════════════════════════════════════════════════╝

🚀 STEP: Input Collection - Mengumpulkan data dari pengguna

📝 Silakan masukkan informasi berikut:

Nama Guru: [User Input]
Nama Sekolah: [User Input]
...

🚀 STEP: Orchestrator Processing - Memproses melalui Main Orchestrator

🎭 [Main Orchestrator] Starting request processing
🔍 [Simple] Using Simple RAG for direct template retrieval
✅ CP/ATP generation completed successfully

🚀 STEP: Final Input Display - Menampilkan hasil final

╔══════════════════════════════════════════════════════════════╗
║  🎉 FINAL INPUT - SIAP UNTUK TAHAP SELANJUTNYA              ║
╚══════════════════════════════════════════════════════════════╝
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

- **AI Assistant**: System Architecture & Implementation
- **Developer**: Further Development & Integration

## 📞 Support

Untuk pertanyaan atau dukungan, silakan:
- Buat issue di repository
- Contact developer team
- Check logs di `logs/` directory untuk debugging

---

**🎓 RAG Multi-Strategy System** - Revolutionizing curriculum development with AI-powered multi-strategy approach.
