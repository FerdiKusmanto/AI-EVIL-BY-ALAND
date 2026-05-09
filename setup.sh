#!/usr/bin/env bash
# setup.sh — Setup otomatis ALand-Evil AI + aland-ai
# Jalankan: bash setup.sh
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
ALAND_AI="$ROOT/aland-ai"
BACKEND="$ROOT/backend"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓ $1${NC}"; }
info() { echo -e "${YELLOW}▶ $1${NC}"; }
err()  { echo -e "${RED}✗ $1${NC}"; exit 1; }

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     ALand-Evil AI — Setup Otomatis       ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Install Python dependencies ─────────────────────────────────────────
info "Menginstall Python dependencies..."
pip install -q --upgrade pip
pip install -q llama-cpp-python
pip install -q transformers peft datasets torch accelerate
ok "Python dependencies terinstall"

# ── 2. Install aland-ai sebagai command ────────────────────────────────────
info "Menginstall aland-ai CLI..."
cd "$ALAND_AI"
pip install -q -e .
ok "aland-ai CLI terinstall"

# ── 3. Install Node.js dependencies ────────────────────────────────────────
info "Menginstall Node.js dependencies..."
cd "$BACKEND"
npm install --silent
ok "Node.js dependencies terinstall"

# ── 4. Training model ───────────────────────────────────────────────────────
info "Memulai training model bahasa Indonesia..."
echo "   (Ini mungkin butuh 10-40 menit tergantung CPU)"
cd "$ALAND_AI"
python3 training/train.py train 3
ok "Training selesai"

# ── 5. Export ke GGUF ──────────────────────────────────────────────────────
info "Mengexport model ke GGUF..."
python3 training/train.py export
ok "Export GGUF selesai"

# ── 6. Verifikasi model tersedia ────────────────────────────────────────────
GGUF="$HOME/.aland-ai/models/aland-id.gguf"
if [ -f "$GGUF" ]; then
    SIZE=$(du -sh "$GGUF" | cut -f1)
    ok "Model aland-id.gguf tersedia ($SIZE)"
else
    err "Model GGUF tidak ditemukan di $GGUF"
fi

# ── 7. Selesai ──────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║           Setup Selesai! 🎉              ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Cara test model:"
echo ""
echo "  Terminal 1 — Jalankan aland-ai server:"
echo "    aland-ai serve"
echo ""
echo "  Terminal 2 — Jalankan web:"
echo "    cd backend && npm start"
echo ""
echo "  Buka browser → http://localhost:3000"
echo "  Pilih model 'aland-id' di dropdown"
echo ""
echo "  Atau test langsung di terminal:"
echo "    aland-ai run aland-id"
echo ""
