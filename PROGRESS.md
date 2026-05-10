# LAPORAN PROGRESS — ALand-Evil AI + aland-ai

**Terakhir diupdate:** 2026-05-10  
**GitHub Repo:** https://github.com/FerdiKusmanto/AI-EVIL-BY-ALAND  
**GitHub User:** FerdiKusmanto  

---

## Status Terkini

| Item | Status |
|---|---|
| aland-ai server lokal | ✅ Berjalan di `http://127.0.0.1:11435` |
| Backend web | ✅ Berjalan di `http://localhost:3000` |
| Model lokal | `aland-id` (TF-IDF, ~52MB) |
| Model cloud terbaru | `aland-id-latest.gguf` 136MB di GitHub Releases |
| Dataset cloud | `dataset.jsonl.gz` 20MB di GitHub Releases |
| Continuous Train | 🔄 Berjalan otomatis di GitHub Actions |
| Fine-tune Colab | 🔄 Sedang berjalan (Qwen2.5-0.5B, 20k data, ~3.5 jam) |

---

## Bug yang Sudah Diperbaiki

### 1. `_resolve_reference` merusak kata "tanya"
- **Masalah:** Regex `(\w+)nya\b` mencocokkan `ta+nya` dalam kata `tanya` → input "aku mau tanya sesuatu" jadi "aku mau ta baik sesuatu"
- **Fix:** Tambah `_NYA_EXCEPTIONS = {"tanya", "hanya", ...}` di `aland_ai.py`, skip kata pengecualian saat deteksi dan penggantian
- **File:** `aland-ai/aland_ai.py` fungsi `_resolve_reference()`

### 2. Entry kotor di model database
- **Masalah:** Ada 4 entry dengan jawaban tidak relevan (Google Translate UI, "kalimat tanya", "kebajikan sejati")
- **Fix:** Dihapus via script pickle langsung dari `~/.aland-ai/models/aland-id.aland-model`

### 3. Kata "ada" dapat jawaban ensiklopedis
- **Masalah:** Input "ada" → jawaban panjang tentang definisi kata "ada"
- **Fix:** Tambah entry casual di `_CASUAL` list di `training/train.py`:
  ```python
  (["ada", "ada?", "ada apa"], ["Ada apa? 😊", "Ya, ada yang bisa saya bantu?"])
  ```

### 4. Model mengecil saat restart workflow
- **Masalah:** Tiap restart GitHub Actions, dataset di-download ulang tapi kadang gagal → model reset ke ukuran kecil
- **Fix:** Tambah `--retry 3` pada curl download + fallback graceful di workflow

---

## Infrastruktur Cloud yang Dibangun

### GitHub Repository
- **URL:** https://github.com/FerdiKusmanto/AI-EVIL-BY-ALAND
- **Token:** Simpan di GitHub Secrets (jangan tulis di sini)

### GitHub Actions Workflows

| File | Jadwal | Fungsi |
|---|---|---|
| `.github/workflows/continuous-train.yml` | Tiap jam (+ self-trigger) | Scraping + build model tiap 5 menit |
| `.github/workflows/scrape-dataset.yml` | Tiap hari 02:00 UTC | Scrape Wikipedia → update dataset |
| `.github/workflows/auto-train.yml` | Tiap Minggu 03:00 UTC | Training mingguan |

### GitHub Releases

| Tag | File | Keterangan |
|---|---|---|
| `model-latest` | `aland-id-latest.gguf` | Model TF-IDF terbaru, terupdate tiap 5 menit |
| `dataset-latest` | `dataset.jsonl.gz` | Dataset training terkompresi |
| `model-500M` | `aland-id-500M-q4.gguf` | (Belum ada — menunggu Colab selesai) |

### Sumber Data Scraping
1. **HuggingFace Wikipedia ID** — 50k artikel via datasets API
2. **HuggingFace Wikipedia EN** — 20k artikel via datasets API  
3. **Wikipedia API (ID)** — scrape real-time, 20 topik parallel
4. **Wikipedia API (EN)** — scrape real-time, 20 topik parallel
5. **DuckDuckGo Instant Answer API** — gratis, no key, 20 query parallel

---

## File Penting

| File | Fungsi |
|---|---|
| `aland-ai/aland_ai.py` | Runtime engine utama (server, CLI, inference) |
| `aland-ai/training/train.py` | Model TF-IDF lokal + casual handler |
| `aland-ai/training/continuous_train.py` | Script scraping + training cloud |
| `aland-ai/training/scraper.py` | Scraper Wikipedia harian |
| `aland-ai/training/train_cloud.py` | Training ringan untuk GitHub Actions CPU |
| `colab_500M.ipynb` | Notebook fine-tune Qwen2.5-0.5B (494M params) |
| `monitor.py` | Monitor status cloud training realtime |
| `kaggle_kernel/kernel.ipynb` | Notebook Kaggle (backup, belum dipakai) |

---

## Yang Sedang Berjalan

### Continuous Train (GitHub Actions)
- Scrape Wikipedia ID + EN + DuckDuckGo secara parallel (20 thread)
- Build model TF-IDF dari semua pairs
- Upload `aland-id-latest.gguf` ke GitHub Releases **tiap 5 menit**
- Self-trigger otomatis tiap ~6 jam (batas GitHub Actions)
- Target: model 300MB+

### Fine-tune Colab (manual, sedang jalan)
- Model: **Qwen2.5-0.5B-Instruct** (494 juta parameter)
- Data: 20.000 pairs dari dataset cloud
- Estimasi selesai: ~3.5 jam dari mulai
- Output: `aland-id-500M-q4.gguf` → diupload ke release `model-500M`

---

## Langkah Selanjutnya (TODO)

- [ ] Tunggu Colab selesai → download model 500M: `aland-ai pull FerdiKusmanto/AI-EVIL-BY-ALAND`
- [ ] Setelah dataset mencapai 300MB → fine-tune Qwen2.5-1.5B (1.5B params) di Colab
- [ ] Untuk 2B+ parameter → butuh Colab Pro ($10/bulan) dengan GPU A100
- [ ] Integrasikan model 500M ke aland-ai server sebagai model default

---

## Cara Menjalankan Ulang Server Lokal

```bash
# Start aland-ai server
fuser -k 11435/tcp 2>/dev/null
aland-ai serve > /tmp/aland-serve.log 2>&1 &

# Start backend web
cd "AI EVIL BY ALAND/backend"
node server.js > /tmp/aland-backend.log 2>&1 &

# Buka browser
# http://localhost:3000
```

## Monitor Cloud Training

```bash
cd "AI EVIL BY ALAND"
python3 monitor.py
```

## Download Model Terbaru dari Cloud

```bash
aland-ai pull FerdiKusmanto/AI-EVIL-BY-ALAND
```

---

## Catatan Teknis

- Model lokal (`aland-id`) = TF-IDF pickle, bukan neural network
- Model cloud (`aland-id-latest.gguf`) = TF-IDF pickle juga, tapi dataset jauh lebih besar
- Model Colab (`aland-id-500M-q4.gguf`) = neural network Qwen2.5 fine-tuned, GGUF format
- Format API kompatibel dengan Ollama
- Semua berjalan 100% lokal setelah model didownload
