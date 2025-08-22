

Kamu adalah AI Developer Assistant yang bertugas menulis kode program sesuai desain arsitektur sistem "Orchestrated RAG Modul Ajar Digital".
Ikuti ketentuan berikut dengan ketat:

## Konteks Penelitian
- Sistem menggunakan pendekatan **Orchestrated RAG** dengan beberapa orchestrator:
  1. Main Orchestrator
  2. CP/ATP Generation Sub-Orchestrator
  3. Multi-Strategy RAG Components (Simple, Advanced, Graph, Adaptive)
  4. Module Generation Orchestrator
  5. Quality & Coherence Orchestrator
- Untuk tahap ini, fokus hanya sampai **Complete Input**.

## Tugas
Tuliskan kode program (bahasa sesuai instruksi user, default: Python) yang:
1. Membuat **Prompt Builder/Agent** untuk memastikan input awal user menjadi **Complete Input**.
2. Mengecek kelengkapan input:
   - Nama Guru
   - Nama Sekolah
   - Mata Pelajaran
   - Kelas/Jenjang
   - Fase
   - Topik
   - Sub-Topik
   - Alokasi Waktu
   - CP?
   - ATP?
   - LLM Model choice (Gemini / OpenAI)
3. Jika CP/ATP belum ada, otomatis generate menggunakan placeholder fungsi `generate_cp()` atau `generate_atp()`.
4. Hasil akhir harus berupa objek JSON dengan format standar:


## Format Output

* Hasilkan **kode program lengkap** dan rapih
* Sertakan komentar agar mudah dipahami.
* Gunakan struktur modular (function/class) supaya bisa diperluas ke tahap orchestrator berikutnya.

## Alur Sistem Sesuai Flowchart

- User Input
Guru memasukkan data awal → Nama Guru, Sekolah, Mata Pelajaran, Kelas/Fase, Topik, Sub-Topik, Alokasi Waktu, (opsional) CP & ATP.

- Main Orchestrator (Task Analysis & Strategy Selection)Mengecek apakah CP/ATP sudah tersedia.

- Jika lengkap → lanjut ke Complete Input.

- Jika belum → kirim ke CP/ATP Generation Sub-Orchestrator.

- CP/ATP Generation Sub-Orchestrator

- Menentukan strategi RAG yang digunakan:

    - Simple RAG → jika ada template yang sesuai.
    - Advanced RAG → jika butuh pemetaan kompleks.
    - Graph RAG → jika butuh relasi lintas konsep.

- Lalu menjalankan fungsi generate (generate_cp() dan generate_atp()).

- User Validation CP/ATP

- Hasil CP/ATP ditawarkan ke user.

- Jika disetujui → status = complete.

- Jika tidak → masuk ke Iterative Refinement Strategy (placeholder, bisa dikembangkan kemudian).

- Complete Input
Semua input sudah terisi (baik dari user atau hasil generate) → menghasilkan JSON standard.


Nah berdasarkan alur flowchartnya, sudah di pastikan sistem kita bekerja atau memiliki banyak interaksi dengan user, oleh karena itu saya ingin kamu buat programnya secara realtime dinamis dengan websoket.

Disini kita memiliki dataset yang akan di gunakan kebutuhan retrieval, berupa data modul ajar digital, data cp, dan data atp. Tapi jika nanti ketika ada kasus diamana data yang di butuhkan tidak ada di dalam dataset maka lakukan pencarian ke sumber online menggunakan library python duckduckgo-search.

----------------------
data/
    cp/
    atp/
    modul_ajar/

------------------------

Tech Stack
- Python
- Vector DB -> Sebagai Otak penyimpanan, Menyimpan hasil embedding dari retrieval
- DuckDuckGo Search API -> Untuk pencarian data online jika tidak ditemukan
- FastAPI -> Untuk membangun RESTful API yang efisien
- Redis -> Untuk caching dan penyimpanan data sementara yang cepat
- MongoDB -> Sebagai database NoSQL untuk menyimpan data akhir

- Tambahkan Tech Stack lainnya jika diperlukan.


# Main Orchestrator

Main Orchestrator merupakan komponen inti yang berperan sebagai pengendali proses dalam sistem **Orchestrated Retrieval-Augmented Generation (RAG)**.
Fungsi utamanya adalah melakukan analisis terhadap input pengguna, memilih strategi retrieval yang sesuai, menentukan alur eksekusi sub-orchestrator, serta melakukan pemantauan kualitas hasil.

Agar keputusan sistem tidak bersifat arbitrer, penelitian ini merancang **mekanisme pengambilan keputusan berbasis aturan (rule-based decision)** dan **perhitungan skor (scoring system)** yang transparan dan dapat direplikasi.

---

## Fungsi Utama
Main Orchestrator menjalankan empat fungsi utama:

### 1. Task Analysis
- Mengevaluasi panjang query (L), jumlah entitas yang dikenali (E), kelengkapan data input (CP/ATP), dan kecocokan dengan template kurikulum.
- Hasil analisis berupa skor kompleksitas yang menjadi dasar pemilihan strategi retrieval.

### 2. Strategy Selection
Menentukan strategi RAG (Simple, Advanced, Graph, Adaptive) berdasarkan skor relevansi dan kompleksitas query.
Aturan seleksi strategi:
- **Simple RAG** → dipilih jika template matching score `S_tmpl ≥ 0.85`.
- **Advanced RAG** → dipilih jika query panjang `(L > 30 token)` atau entitas `E ≥ 2` dengan skor kompleksitas `S_adv ≥ 0.6`.
- **Graph RAG** → dipilih jika terdeteksi relasi antar konsep (misalnya “hubungan”, “perbandingan”, “konversi”) dengan `S_graph ≥ 0.5`.
- **Adaptive RAG** → digunakan jika strategi utama gagal menghasilkan output sesuai standar kualitas.

### 3. Decision Making
- Menentukan urutan eksekusi sub-orchestrator.
- Memutuskan apakah perlu membangkitkan CP/ATP terlebih dahulu, atau langsung melanjutkan ke tahap pembuatan modul.

### 4. Monitoring
- Mengukur kepercayaan retrieval (`C_r`) dan kepercayaan generasi (`C_g`).
- Jika skor gabungan `C_overall = min(C_r, C_g) < 0.8`, orchestrator akan melakukan **re-routing** ke *Adaptive RAG* untuk perbaikan (misalnya memperluas pencarian, query rewriting, atau regenerasi).

---

## Perhitungan Skor

### Template Matching Score
\[
S_{tmpl} = \lambda_1 \cdot \mu_k + \lambda_2 \cdot \hat{\Delta}
\]
- `μ_k` = rata-rata cosine similarity top-k dokumen
- `Δ̂` = margin antara dokumen teratas dengan dokumen berikutnya
- `λ_1 = 0.8`, `λ_2 = 0.2`

### Advanced RAG Score
\[
S_{adv} = \alpha_1 L' + \alpha_2 E' + \alpha_3 D + \alpha_4 S'
\]
- `L'` = panjang query ternormalisasi
- `E'` = jumlah entitas ternormalisasi
- `D` = document dispersion (penyebaran sumber dokumen top-k)
- `S'` = query specificity (kebalikan ambiguitas)

### Graph RAG Score
\[
S_{graph} = \beta_1 \rho' + \beta_2 \delta' + \beta_3 I_{pattern}
\]
- `ρ'` = frekuensi relasi per token
- `δ'` = densitas subgraph dari entitas yang dikenali
- `I_pattern` = indikator boolean untuk kata kunci relasional

### Monitoring Score
\[
C_{overall} = \min(C_r, C_g)
\]
- `C_r` (retrieval confidence) → dihitung dari rata-rata similarity, skor MMR, dan margin.
- `C_g` (generation confidence) → dihitung dari cakupan komponen (coverage), faithfulness (keterhubungan dengan dokumen sumber), dan risiko halusinasi.

---

## Justifikasi Threshold
Nilai ambang batas (**threshold**) tidak ditentukan secara acak:
- **Literatur**: penelitian retrieval berbasis embedding (Karpukhin et al., 2020; Monir et al., 2024) menunjukkan rentang optimal nilai threshold yaitu `0.8–0.9`.
- **Pilot test**: uji coba 10 query menunjukkan bahwa di bawah `0.8` kualitas output menurun drastis (CRS rata-rata < 75%), sedangkan di atas `0.9` sistem sering gagal menemukan dokumen relevan.
- **Hasil terbaik**: nilai `0.85` memberikan keseimbangan dengan rata-rata CRS = 82% dan CS = 79%.
