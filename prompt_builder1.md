Sistem di mulai dari

## 1. Input
    - Nama Guru
    - Nama Sekolah
    - Mata Pelajaran
    - Topik
    - Sub topik
    - Kelas
    - CP
    - ATP
    - Alokasi Waktu
    - Model LLM (gemini-1.5-flash or gpt-4)

## 2. Main Orchestrator (Task Analysis & Strategy Selection)
Main Orchestrator merupakan komponen inti yang berperan sebagai "conductor" atau dirigen dalam sistem, main orchestrator bertanggung jawab mengatur dan mengkoordinasikan seluruh proses komponen sistem. Komponen ini memiliki empat fungsi utama yang bekerja secara terintegrasi.

Tugas Dari Main Orchestration
### a.	Task Analysis
Berfungsi menganalisis kompleksitas dan kebutuhan dari setiap request yang masuk, termasuk mengevaluasi kelengkapan data input, mengidentifikasi komponen yang perlu digenerate, dan menentukan tingkat kesulitan pemrosesan.
### b.	Strategy Selection
Bertugas memilih strategi RAG yang paling tepat berdasarkan hasil analisis, apakah menggunakan Simple RAG untuk kasus sederhana, Advanced RAG untuk query kompleks, atau Graph RAG untuk kebutuhan relasional.
### c.	Decision Making
Menentukan alur proses yang akan dijalankan, seperti memutuskan apakah sistem perlu generate CP/ATP terlebih dahulu atau dapat langsung melanjutkan ke pembuatan modul jika data sudah lengkap.
### d.	Monitoring
Berfungsi mengawasi seluruh proses yang berjalan, memantau kinerja sub-orchestrators, mendeteksi bottleneck atau kegagalan, dan memastikan kualitas output di setiap tahapan.
Dengan arsitektur ini, Main Orchestrator memastikan bahwa setiap permintaan pembuatan modul ajar diproses dengan strategi yang optimal, efisien, dan menghasilkan output berkualitas tinggi sesuai standar Kurikulum Merdeka.


## 3. CP/ATP Generation Sub-Orchestrator
Jika Inputan User tidak mencakup CP/ATP maka alur akan masuk ke CP/ATP Generation Sub-Orchestrator.

CP/ATP Generation Sub-Orchestrator merupakan komponen khusus yang dirancang untuk menangani pembuatan Capaian Pembelajaran (CP) dan Alur Tujuan Pembelajaran (ATP) ketika pengguna tidak menyediakan informasi tersebut dalam input awal. Sub-orchestrator ini bekerja dengan tiga mekanisme utama yang saling terintegrasi.

### a. Pertama, komponen ini melakukan pemilihan strategi RAG berdasarkan konteks pembelajaran yang diberikan, di mana sistem akan menganalisis mata pelajaran, topik, kelas, dan alokasi waktu untuk menentukan apakah akan menggunakan Simple RAG jika sudah tersedia template yang sesuai, Advanced RAG untuk kasus yang memerlukan sintesis dari berbagai sumber, atau Graph RAG ketika diperlukan pemahaman relasi antar konsep pembelajaran.

### b.	Kedua, sub-orchestrator mengelola keseluruhan proses generation dan validation, mulai dari inisiasi retrieval, pemrosesan hasil pencarian, konstruksi prompt yang sesuai, hingga pengawasan proses generasi oleh Large Language Model (LLM) untuk memastikan CP/ATP yang dihasilkan sesuai dengan standar Kurikulum Merdeka.

### c.	Ketiga, sistem ini memiliki kemampuan handling iterative refinement yang memungkinkan perbaikan berkelanjutan jika pengguna tidak menyetujui hasil yang digenerate, di mana feedback dari pengguna akan dianalisis untuk menyesuaikan strategi, memodifikasi parameter pencarian, atau bahkan beralih ke strategi RAG yang berbeda hingga menghasilkan CP/ATP yang memenuhi ekspektasi pengguna.

Dengan desain ini, CP/ATP Generation Sub-Orchestrator memastikan bahwa setiap modul ajar memiliki fondasi pembelajaran yang solid dan sesuai dengan kebutuhan spesifik pengguna.
   - Memilih **strategi RAG** yang sesuai konteks:
     - **Simple RAG** → langsung tarik template.
     - **Advanced RAG** → _query rewriting_ + _reranking_.
     - **Graph RAG** → navigasi _knowledge graph_.

## 4. Select RAGStrategy Based on Context
Setelah melewati tahap orchestra cp/atp, maka sistem akan measuk kedalam pemilihan model untuk, disini terdapat 3 opsi pemilihan model, untuk lebih jelasnya lihat pada gambar yang saya berikan

## 5. Generate CP/ATP

## 6. User Validation CP/ATP
Kembalikan ke user untuk di validasi apakah user setuju atau ada perbaikan

## 7. Retrieve RAG Refinement Strategy
Alur ini jika user tidak setuju dengan CP/ATP yan dibuat, setelah masuk ke alur ini sistem akan melakukan analisis terhadap feedback yang diberikan oleh user dan kembalikan ke alur Generate CP/ATP

## 8. Final Input
Tampilkan hasil jika user setuju atau jika di inputan awal user itu ada CP/ATP yang di inputkan user.



Teknologi yang di gunakan
- Python
- MySQL
- MongoDB
- vector DB (chroma)
- Gemini dan OpenAI

saya juga memiliki data CP dan ATP di folder
data/cp/*
data/atp/*
data/modulajar/*



Buatkan programnya secara modular dan rapih, buat juga logs yang cantik di lihat dan terstruktur
