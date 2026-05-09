# Cara Train ALand-AI
**File utama:** `aland-ai/training/train.py`  
**Dataset:** `aland-ai/training/dataset.jsonl`  
**Model output:** `~/.aland-ai/models/aland-id.aland-model`

---

## Arsitektur Model

ALand-AI **tidak menggunakan neural network atau model besar**. Semua berjalan 100% lokal dengan pendekatan ringan:

| Komponen | Fungsi |
|---|---|
| Template matching | Cocokkan input user ke pasangan Q&A di dataset |
| Fuzzy similarity | Jaccard token overlap untuk menghitung kemiripan |
| Info token penalty | Bobot lebih pada token informatif (bukan stopwords) |
| Math handler | Evaluasi ekspresi matematika langsung |
| Casual handler | Respons hardcoded untuk small-talk |
| Markov chain | Generasi teks (orde 2) |
| Web search fallback | Cari di internet jika tidak ada di dataset |
| Auto-save | Simpan hasil web ke model secara otomatis |

---

## Sumber Data Training

### 1. Dataset Lokal (`dataset.jsonl`)
Format JSONL — setiap baris adalah satu percakapan:
```json
{"messages": [
  {"role": "user", "content": "Apa itu Python?"},
  {"role": "assistant", "content": "Python adalah bahasa pemrograman..."}
]}
```

Dataset saat ini berisi **430.000+ baris** mencakup:
- Percakapan sehari-hari (bahasa Indonesia, Inggris, Arab, Mandarin, Jepang, Korea, dll)
- Pengetahuan umum (sains, sejarah, budaya, teknologi)
- Konversi satuan, hari, bulan, warna, angka dalam berbagai bahasa
- Tokoh sejarah Indonesia (Soekarno, dll)
- Makanan, budaya, dan wisata Indonesia

### 2. File Generator Dataset
| File | Fungsi |
|---|---|
| `gen_dataset.py` | Generator dataset dasar |
| `gen_bulk.py` | Generator dataset massal |
| `gen_extra.py` | Generator dataset tambahan |

### 3. Internet (Web Search Fallback) — *Fitur Baru*
Jika topik tidak ada di dataset, model otomatis mencari di internet:
- **Sumber 1:** DuckDuckGo Instant Answer API (`api.duckduckgo.com`) — hasil terstruktur
- **Sumber 2:** DuckDuckGo HTML search — snippet dari berbagai situs web bebas
- Hasil langsung disimpan ke model → pertanyaan yang sama berikutnya dijawab dari cache lokal

---

## Cara Kerja Training

### Proses `train()` (dari dataset lokal)
```
dataset.jsonl
    ↓ load_pairs()
    ↓ Pisahkan pairs bahasa Indonesia dan Inggris
    ↓ Bangun vocab (set semua token)
    ↓ Bangun Markov chain (orde 2) dari semua jawaban
    ↓ Simpan ke ~/.aland-ai/models/aland-id.aland-model
```

### Proses `update_model()` (tambah data tanpa retrain penuh)
```
new_pairs (list Q&A baru)
    ↓ Load model existing
    ↓ Extend model.pairs
    ↓ Update en_pairs jika jawaban berbahasa Inggris
    ↓ Update vocab
    ↓ Merge Markov chain baru ke yang lama
    ↓ Simpan kembali ke file model
```

### Proses Web Search Auto-Learn (saat runtime)
```
User tanya → tidak ada di dataset (score < threshold)
    ↓ _web_search_answer(query)
    ↓ DuckDuckGo Instant Answer API
    ↓ (jika gagal) DuckDuckGo HTML snippet
    ↓ Bersihkan: decode HTML entities, hapus prefix media, hapus teks sumber
    ↓ Simpan langsung ke model.pairs
    ↓ Simpan model ke disk
    ↓ Kembalikan jawaban ke user
```

---

## Metode Training

> **Prinsip utama:** Training tidak boleh memuat ulang seluruh dataset dari disk (berat, lambat).
> Semua metode di bawah bersifat **incremental** — hanya menambah data baru ke model yang sudah ada.

| Metode | Trigger | Beban | Butuh Internet |
|---|---|---|---|
| Realtime Chat Learning | Otomatis saat user tanya | Sangat ringan (1 Q&A) | Ya |
| Incremental Update | Manual via kode/CLI | Ringan (N Q&A) | Tidak |
| Auto-train dari Internet | Manual atau terjadwal | Ringan (N topik) | Ya |
| Full retrain | Manual (`aland-ai train`) | Berat (430k+ baris) | Tidak |

> Full retrain hanya diperlukan jika `dataset.jsonl` diubah secara massal.

---

### Metode 1 — Realtime Chat Learning (Otomatis, sudah aktif)

Terjadi secara otomatis saat user chat. Tidak perlu perintah apapun.

**Alur:**
```
User tanya sesuatu yang tidak ada di model
    ↓ score < threshold → web search dipanggil
    ↓ Dapat jawaban dari DuckDuckGo
    ↓ model.pairs.append((pertanyaan, jawaban))
    ↓ model.save() — langsung tersimpan ke disk
    ↓ Jawab user
```

Efek: model makin pintar setiap kali ada pertanyaan baru yang dijawab dari internet.

---

### Metode 2 — Incremental Update (Manual, ringan)

Tambah satu atau beberapa Q&A ke model yang sudah ada **tanpa load ulang dataset**.

```python
from training.train import update_model

update_model([
    ("Apa itu X?", "X adalah ..."),
    ("Siapa Y?", "Y adalah ..."),
])
```

Atau lewat CLI:
```bash
aland-ai train  # hanya jika dataset.jsonl diubah
```

Fungsi `update_model` hanya:
1. Load model existing (bukan dataset)
2. Append pairs baru
3. Update vocab & Markov
4. Simpan kembali

---

### Metode 3 — Auto-Train dari Internet (Otomatis, background)

Model mencari sendiri topik-topik populer dari internet secara berkala, tanpa menunggu user bertanya.

Implementasi di `train.py` — fungsi `auto_train_from_web`:

```python
aland-ai autotrain           # Jalankan sekali
aland-ai autotrain --loop    # Jalankan terus di background (interval 1 jam)
```

**Topik yang dicari otomatis** (bisa dikustomisasi di `AUTO_TOPICS`):
- Berita terkini Indonesia
- Tokoh-tokoh penting
- Istilah teknologi terbaru
- Pengetahuan umum populer

Setiap topik yang berhasil di-fetch langsung disimpan ke model via `update_model`.

---

### Cara Menjalankan Training Penuh (Jika Diperlukan)

> Hanya lakukan ini jika dataset.jsonl diubah secara massal.

```bash
aland-ai train              # Training dari dataset lokal
aland-ai train --export     # Training + export ke GGUF
```

### Tambah Data Manual ke Dataset
Edit `aland-ai/training/dataset.jsonl`, tambahkan baris baru:
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```
Lalu jalankan `aland-ai train` untuk rebuild model.

---

## Alur Inferensi (`respond`)

Saat user mengirim pesan, model melewati pipeline ini secara berurutan:

```
Input user
  │
  ├─ 1. Math handler
  │      Deteksi ekspresi matematika → hitung langsung
  │      Contoh: "999 * 7" → "999 * 7 = 6993"
  │
  ├─ 2. Casual handler
  │      Cocokkan dengan pola small-talk hardcoded
  │      Contoh: "haii" → "Hey! Senang bertemu kamu 😄"
  │
  ├─ 3. Deteksi bahasa (ID / EN)
  │
  ├─ 4. Template matching dari dataset
  │      Hitung similarity setiap Q di dataset vs input
  │      Terapkan info token penalty:
  │        - info_overlap = 0  → score × 0.1  (penalti besar)
  │        - info_overlap > 0  → score × (0.5 + 0.5 × overlap)
  │        - tidak ada q_info  → score × 0.3
  │      Pilih jawaban dengan score tertinggi
  │
  ├─ 5. Threshold check
  │      score ≥ 0.5  → jawab dari dataset (ID)
  │      score ≥ 0.4  → jawab dari en_pairs (EN)
  │      score ≥ 0.45 → jawab dari dataset (fallback)
  │
  ├─ 6. Web search fallback (jika ada info_tokens)
  │      Fetch dari DuckDuckGo → bersihkan → simpan ke model
  │
  └─ 7. "Maaf, saya belum punya informasi tentang itu."
```

---

## Fungsi Utama di `train.py`

| Fungsi | Keterangan |
|---|---|
| `load_pairs()` | Baca dataset.jsonl → list (Q, A) |
| `tokenize(text)` | Pecah teks jadi token (lowercase, strip tanda baca) |
| `normalize(text)` | Normalisasi teks untuk perbandingan |
| `similarity(a, b)` | Jaccard similarity antar dua teks |
| `build_markov(texts)` | Bangun Markov chain orde 2 dari list teks |
| `_solve_math(text)` | Evaluasi ekspresi matematika |
| `_detect_lang(text)` | Deteksi bahasa (ID/EN) |
| `_casual_response(text)` | Respons small-talk hardcoded |
| `_web_search_answer(query)` | Cari jawaban dari internet |
| `AlandModel.train(pairs)` | Training dari list pairs |
| `AlandModel.respond(input)` | Inferensi — hasilkan jawaban |
| `AlandModel.save(path)` | Simpan model ke file .aland-model |
| `AlandModel.load(path)` | Muat model dari file |
| `update_model(new_pairs)` | Tambah data ke model tanpa retrain penuh |
| `train()` | Entry point training dari CLI |

---

## Format File Model

Model disimpan sebagai file pickle Python (`.aland-model`):
```python
{
    "pairs": [(q, a), ...],        # Semua pasangan Q&A bahasa Indonesia
    "en_pairs": [(q, a), ...],     # Pasangan Q&A bahasa Inggris
    "markov": {tuple: [str]},      # Markov chain
    "markov_order": 2,             # Orde Markov
    "vocab": set([str]),           # Semua token yang dikenal
}
```

---

## Perintah CLI

```bash
aland-ai train              # Training dari dataset lokal
aland-ai train --export     # Training + export ke GGUF
aland-ai serve              # Jalankan API server (port 11435)
aland-ai run aland-id       # Chat interaktif di terminal
aland-ai list               # Tampilkan model yang tersedia
```

---

## Catatan

- Model berjalan **100% lokal** — tidak butuh GPU, tidak butuh internet (kecuali web search fallback)
- Web search fallback hanya aktif saat model tidak menemukan jawaban yang cukup relevan
- Setiap jawaban dari internet otomatis di-cache ke model — makin sering dipakai, makin pintar
- Untuk menambah topik baru secara massal, tambahkan ke `dataset.jsonl` lalu jalankan `aland-ai train`
