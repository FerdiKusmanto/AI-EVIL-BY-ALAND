#!/bin/bash
# setup_cloud.sh — jalankan SEKALI untuk konfigurasi username
# Usage: bash setup_cloud.sh <kaggle_username>

set -e
USERNAME="$1"

if [ -z "$USERNAME" ]; then
  echo "Usage: bash setup_cloud.sh <kaggle_username>"
  echo "Contoh: bash setup_cloud.sh aland123"
  exit 1
fi

echo "Mengatur username: $USERNAME"

# Ganti KAGGLE_USERNAME di semua file
sed -i "s/KAGGLE_USERNAME/$USERNAME/g" \
  kaggle_kernel/kernel-metadata.json \
  aland-ai/training/dataset-metadata.json \
  .github/workflows/auto-train.yml

echo "✅ Selesai! Langkah selanjutnya:"
echo ""
echo "1. Push ke GitHub:"
echo "   git add . && git commit -m 'setup cloud training' && git push"
echo ""
echo "2. Tambah secrets di GitHub:"
echo "   → Settings → Secrets → New repository secret"
echo "   → KAGGLE_USERNAME = $USERNAME"
echo "   → KAGGLE_KEY      = (dari kaggle.com/settings → API → Create Token)"
echo ""
echo "3. Upload dataset pertama kali ke Kaggle:"
echo "   pip install kaggle"
echo "   cd aland-ai/training"
echo "   kaggle datasets create -p . --dir-mode zip"
echo ""
echo "Setelah itu training berjalan otomatis tiap Minggu — tidak perlu buka laptop lagi!"
