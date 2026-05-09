# Panduan Training Cloud (Tanpa Bebankan Laptop)

Alur lengkap: scraping otomatis → fine-tuning di cloud → download model jadi ke laptop.

```
GitHub Actions          Google Colab             Laptop kamu
(tiap hari)             (manual, ~1 jam)
─────────────           ────────────────         ─────────────
scraper.py              colab_finetune.ipynb      aland-ai pull
  ↓                       ↓                         ↓
dataset.jsonl  ──────→  fine-tune Qwen2.5  ──→  aland-id-q4.gguf
(di repo)               export GGUF              aland-ai run aland-id
                        upload HuggingFace
```

---

## Langkah 1 — Setup GitHub Repository

```bash
# Di laptop (sekali saja)
cd "AI EVIL BY ALAND"
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/USERNAME/AI-EVIL-BY-ALAND.git
git push -u origin main
```

Aktifkan GitHub Actions: Settings → Actions → Allow all actions ✓

---

## Langkah 2 — Scraping Otomatis (GitHub Actions)

File `.github/workflows/scrape-dataset.yml` sudah dibuat.

Scraper berjalan **tiap hari jam 02:00 UTC** — scrape Wikipedia Indonesia,
tambah ke `dataset.jsonl`, commit otomatis ke repo.

Untuk jalankan manual: GitHub → Actions → "Scrape Dataset" → Run workflow

---

## Langkah 3 — Fine-tuning di Google Colab

1. Buka [colab.research.google.com](https://colab.research.google.com)
2. Upload `colab_finetune.ipynb`
3. Runtime → Change runtime type → **T4 GPU**
4. Edit cell ke-2:
   ```python
   GITHUB_REPO = 'https://github.com/USERNAME/AI-EVIL-BY-ALAND.git'
   HF_TOKEN    = 'hf_...'   # dari huggingface.co/settings/tokens
   HF_REPO     = 'USERNAME/aland-id'
   ```
5. Runtime → Run all
6. Tunggu ~45-60 menit

Model otomatis terupload ke HuggingFace setelah selesai.

---

## Langkah 4 — Download Model ke Laptop

```bash
# Download dari HuggingFace (ganti USERNAME)
aland-ai pull USERNAME/aland-id

# Atau jalankan langsung
aland-ai run USERNAME/aland-id
```

---

## Jadwal yang Disarankan

| Frekuensi | Aksi |
|---|---|
| Tiap hari (otomatis) | GitHub Actions scrape Wikipedia |
| Tiap minggu (manual) | Buka Colab, run fine-tuning |
| Setelah Colab selesai | `aland-ai pull USERNAME/aland-id` |

---

## Catatan

- **Google Colab gratis**: GPU T4, ~12 jam/hari — cukup untuk 1-2x training/minggu
- **GitHub Actions gratis**: 2000 menit/bulan — scraper ~2 menit/hari = 60 menit/bulan
- **HuggingFace gratis**: storage model unlimited untuk model publik
- Laptop hanya dipakai untuk `aland-ai pull` dan `aland-ai serve` — tidak ada proses berat
