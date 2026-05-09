# ALand-Evil AI + aland-ai Runtime

Sistem AI lokal lengkap: **aland-ai** (runtime) + **ALand-Evil AI** (web chat).

```
AI EVIL BY ALAND/
├── aland-ai/
│   ├── aland_ai.py     ← Runtime engine (server, CLI, inference)
│   ├── aland-ai        ← Entry point script
│   └── pyproject.toml  ← Package config
├── backend/
│   ├── server.js       ← Express, proxy ke aland-ai
│   └── package.json
└── frontend/
    └── index.html      ← Web chat UI
```

---

## Setup aland-ai (sekali saja)

### 1. Install Python dependencies

```bash
# Install llama-cpp-python (engine inferensi)
pip install llama-cpp-python

# Install aland-ai sebagai command global
cd "AI EVIL BY ALAND/aland-ai"
pip install -e .
```

> **GPU (opsional, lebih cepat):**
> ```bash
> CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall
> ```

### 2. Download model

```bash
aland-ai pull tinyllama    # 669MB — paling ringan, untuk test
aland-ai pull llama3.2     # 2.0GB — bagus untuk chat
aland-ai pull qwen2.5      # 2.0GB — bagus bahasa Indonesia
aland-ai pull mistral      # 4.1GB — bagus untuk coding
```

### 3. Jalankan aland-ai server

```bash
aland-ai serve
# Server berjalan di http://127.0.0.1:11435
```

### 4. Jalankan web backend

```bash
cd backend
npm install
npm start
# Web berjalan di http://localhost:3000
```

Buka browser → `http://localhost:3000`

---

## Perintah aland-ai

| Perintah | Keterangan |
|---|---|
| `aland-ai serve` | Jalankan API server (port 11435) |
| `aland-ai run <model>` | Chat interaktif di terminal |
| `aland-ai pull <model>` | Download model |
| `aland-ai list` | Tampilkan model lokal |
| `aland-ai show <model>` | Info detail model |
| `aland-ai rm <model>` | Hapus model |
| `aland-ai train` | Latih model dengan dataset bahasa Indonesia |
| `aland-ai train --export` | Latih + export hasil ke GGUF |

## Training Model Sendiri

```bash
# 1. Install dependencies training
pip install transformers peft datasets torch accelerate

# 2. Latih model (3 epoch, ~30 menit di CPU)
aland-ai train --epochs 3

# 3. Export hasil ke GGUF
aland-ai train --export
# atau langsung:
aland-ai train --epochs 3 --export

# 4. Jalankan model hasil training
aland-ai run aland-id
# atau lewat web: aland-ai serve
```

Dataset training ada di `aland-ai/training/dataset.jsonl` — bisa ditambah sendiri dengan format:
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Hasil training disimpan di `~/.aland-ai/training/` dan model GGUF di `~/.aland-ai/models/aland-id.gguf`.

## REST API aland-ai

| Endpoint | Method | Keterangan |
|---|---|---|
| `GET /api/tags` | GET | Daftar model |
| `POST /api/chat` | POST | Chat (streaming NDJSON) |
| `POST /api/generate` | POST | Generate teks |

---

## Catatan

- Semua berjalan **100% lokal** — tidak butuh internet setelah model didownload
- Model disimpan di `~/.aland-ai/models/`
- Format API kompatibel dengan Ollama
