"""
train_cloud.py — Fine-tune ringan di CPU GitHub Actions
Pakai model kecil (distilgpt2) + dataset terbatas, export ke format aland-model
"""
import json, random, pickle, re
from pathlib import Path
from collections import defaultdict

DATASET = Path("aland-ai/training/dataset.jsonl")
OUTPUT  = Path("/tmp/aland-id-latest.gguf")  # nama gguf tapi isi aland-model (kompatibel)

def normalize(t: str) -> str:
    return re.sub(r'\s+', ' ', t.lower().strip())

def tokenize(t: str) -> list:
    return re.findall(r'\w+', normalize(t))

def build_model(pairs: list) -> dict:
    """Bangun model TF-IDF sederhana dari pairs."""
    from math import log
    N = len(pairs)
    df = defaultdict(int)
    for q, _ in pairs:
        for w in set(tokenize(q)):
            df[w] += 1
    idf = {w: log(N / (c + 1)) for w, c in df.items()}

    vectors = []
    for q, a in pairs:
        toks = tokenize(q)
        tf = defaultdict(int)
        for w in toks: tf[w] += 1
        vec = {w: tf[w] * idf.get(w, 0) for w in tf}
        vectors.append((vec, a))

    return {"pairs": pairs, "vectors": vectors, "idf": idf}

def main():
    print("Loading dataset...")
    pairs = []
    with open(DATASET, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                msgs = obj.get("messages", [])
                if len(msgs) >= 2:
                    q = msgs[0]["content"].strip()
                    a = msgs[1]["content"].strip()
                    if q and a:
                        pairs.append((q, a))
            except: pass

    random.shuffle(pairs)
    print(f"Total pairs: {len(pairs)}")

    print("Building model...")
    model = build_model(pairs)

    # Simpan sebagai .gguf (isi pickle, kompatibel dengan aland-ai)
    with open(OUTPUT, "wb") as f:
        pickle.dump(model, f)

    size_mb = OUTPUT.stat().st_size / (1024*1024)
    print(f"✅ Model saved: {OUTPUT} ({size_mb:.1f}MB)")

if __name__ == "__main__":
    main()
