"""
continuous_train.py — Scrape + train terus-menerus, upload model tiap 5 menit
"""
import json, random, re, time, pickle, subprocess, os
from pathlib import Path
from collections import defaultdict
from math import log

import requests
import wikipediaapi

DATASET   = Path("aland-ai/training/dataset.jsonl")
MODEL_OUT = Path("/tmp/aland-id-latest.gguf")
INTERVAL  = 300   # simpan & upload tiap 5 menit

WIKI = wikipediaapi.Wikipedia(language="id", user_agent="aland-ai/1.0")

TOPICS = [
    # Teknologi & Komputer
    "Kecerdasan buatan","Machine learning","Python (bahasa pemrograman)",
    "Jaringan saraf tiruan","Pemrosesan bahasa alami","Komputer","Internet",
    "Algoritma","Struktur data","Sistem operasi","Linux","Basis data",
    "Jaringan komputer","Keamanan siber","Pemrograman","JavaScript","Java",
    "C++","Kriptografi","Cloud computing","Blockchain","Internet of Things",
    "Robotika","Augmented reality","Virtual reality","Komputasi kuantum",
    "Pengembangan web","Aplikasi mobile","DevOps","Git","Docker",
    # Sains
    "Matematika","Fisika","Kimia","Biologi","Geografi","Astronomi",
    "Fisika kuantum","Relativitas","Termodinamika","Elektromagnetisme",
    "Genetika","Evolusi","Ekologi","Anatomi","Fisiologi","Mikrobiologi",
    "Kimia organik","Kimia anorganik","Fisika nuklir","Kosmologi",
    "Geologi","Meteorologi","Oseanografi","Paleontologi","Botani","Zoologi",
    # Indonesia & Sosial
    "Indonesia","Sejarah Indonesia","Pancasila","Bahasa Indonesia",
    "Suku bangsa di Indonesia","Budaya Indonesia","Pariwisata Indonesia",
    "Ekonomi Indonesia","Politik Indonesia","Hukum Indonesia",
    "Pendidikan di Indonesia","Kesehatan di Indonesia","Agama di Indonesia",
    "Pulau Jawa","Pulau Sumatera","Pulau Kalimantan","Pulau Sulawesi",
    "Bali","Jakarta","Surabaya","Bandung","Medan","Makassar",
    # Ilmu Sosial
    "Ekonomi","Sosiologi","Psikologi","Antropologi","Filsafat","Sejarah",
    "Geografi sosial","Ilmu politik","Hukum","Pendidikan","Komunikasi",
    "Manajemen","Akuntansi","Pemasaran","Kewirausahaan","Bisnis",
    # Kesehatan & Kedokteran
    "Kesehatan","Nutrisi","Olahraga","Kedokteran","Farmasi","Keperawatan",
    "Penyakit jantung","Diabetes","Kanker","Hipertensi","Obesitas",
    "Kesehatan mental","Psikiatri","Neurologi","Kardiologi","Onkologi",
    "Imunologi","Virologi","Epidemiologi","Gizi","Vitamin",
    # Seni & Budaya
    "Musik","Seni","Sastra","Film","Fotografi","Arsitektur","Desain",
    "Tari","Teater","Lukisan","Patung","Sastra Indonesia","Puisi",
    "Novel","Cerpen","Komik","Animasi","Sinematografi",
    # Alam & Lingkungan
    "Lingkungan hidup","Perubahan iklim","Energi terbarukan","Pertanian",
    "Kehutanan","Perikanan","Peternakan","Konservasi","Biodiversitas",
    "Pemanasan global","Polusi","Daur ulang","Energi surya","Angin",
    # Kehidupan Sehari-hari
    "Memasak","Kuliner Indonesia","Resep masakan","Olahraga","Yoga",
    "Meditasi","Perjalanan","Transportasi","Otomotif","Mode","Kecantikan",
    "Pernikahan","Parenting","Keuangan pribadi","Investasi","Properti",
    # Sejarah Dunia
    "Perang Dunia II","Perang Dunia I","Revolusi Perancis","Revolusi Industri",
    "Kekaisaran Romawi","Mesir kuno","Yunani kuno","Dinasti Ming",
    "Kolonialisme","Perang Dingin","PBB","NATO","Uni Eropa",
    # Tokoh
    "Soekarno","Mohammad Hatta","Ki Hajar Dewantara","R.A. Kartini",
    "Albert Einstein","Isaac Newton","Charles Darwin","Marie Curie",
    "Leonardo da Vinci","Aristoteles","Plato","Socrates",
]

def normalize(t): return re.sub(r'\s+', ' ', t.lower().strip())
def tokenize(t):  return re.findall(r'\w+', normalize(t))

def scrape_topic(title: str) -> list:
    page = WIKI.page(title)
    if not page.exists(): return []
    pairs = []
    summary = page.summary[:800].strip()
    if len(summary) > 50:
        for q in [
            f"Apa itu {title}?",
            f"Jelaskan tentang {title}",
            f"Ceritakan tentang {title}",
            f"Apa yang dimaksud dengan {title}?",
            f"Berikan penjelasan singkat tentang {title}",
            f"Tolong jelaskan {title}",
            f"Apa pengertian {title}?",
        ]:
            pairs.append((q, summary))

    for s in page.sections:
        text = s.text.strip()
        if len(text) < 80: continue
        chunks = [text[i:i+600] for i in range(0, min(len(text), 2400), 600)]
        for i, chunk in enumerate(chunks):
            if len(chunk) < 80: continue
            pairs.append((f"Jelaskan {s.title} dalam konteks {title}", chunk))
            pairs.append((f"Apa itu {s.title}?", chunk))
            if i == 0:
                pairs.append((f"Bagaimana {s.title} berkaitan dengan {title}?", chunk))

    # Ambil linked pages (topik terkait)
    for link_title in list(page.links.keys())[:10]:
        linked = WIKI.page(link_title)
        if not linked.exists(): continue
        s2 = linked.summary[:400].strip()
        if len(s2) > 80:
            pairs.append((f"Apa hubungan {link_title} dengan {title}?", s2))

    return pairs

def build_model(pairs: list) -> dict:
    N = max(len(pairs), 1)
    df = defaultdict(int)
    for q, _ in pairs:
        for w in set(tokenize(q)): df[w] += 1
    idf = {w: log(N / (c + 1)) for w, c in df.items()}
    vectors = []
    for q, a in pairs:
        tf = defaultdict(int)
        for w in tokenize(q): tf[w] += 1
        vectors.append(({w: tf[w] * idf.get(w, 0) for w in tf}, a))
    return {"pairs": pairs, "vectors": vectors, "idf": idf}

def upload_model():
    subprocess.run(
        ["gh", "release", "upload", "model-latest", str(MODEL_OUT), "--clobber"],
        capture_output=True
    )
    print(f"  ✅ Model diupload ({MODEL_OUT.stat().st_size//(1024*1024)}MB)")

def upload_dataset():
    gz = Path(str(DATASET) + ".gz")
    subprocess.run(["gzip", "-kf", str(DATASET)], capture_output=True)
    subprocess.run(
        ["gh", "release", "upload", "dataset-latest", str(gz), "--clobber"],
        capture_output=True
    )
    print(f"  ✅ Dataset diupload")

def main():
    # Load dataset awal
    pairs = []
    existing_q = set()
    if DATASET.exists():
        with open(DATASET, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    msgs = obj.get("messages", [])
                    if len(msgs) >= 2:
                        q, a = msgs[0]["content"].strip(), msgs[1]["content"].strip()
                        if q and a:
                            pairs.append((q, a))
                            existing_q.add(q.lower())
                except: pass
    print(f"Dataset awal: {len(pairs)} pairs")

    last_save = time.time()
    topics = TOPICS.copy()
    random.shuffle(topics)
    topic_idx = 0
    new_count = 0

    while True:
        # Scrape 1 topik
        topic = topics[topic_idx % len(topics)]
        topic_idx += 1
        if topic_idx % len(topics) == 0:
            random.shuffle(topics)

        print(f"Scraping: {topic}")
        try:
            new_pairs = scrape_topic(topic)
            added = 0
            for q, a in new_pairs:
                if q.lower() not in existing_q:
                    pairs.append((q, a))
                    existing_q.add(q.lower())
                    added += 1
            new_count += added
            print(f"  +{added} pairs (total: {len(pairs)})")
        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(1)

        # Tiap 5 menit: build model + upload
        if time.time() - last_save >= INTERVAL:
            print(f"\n⏱ 5 menit — build & upload model...")

            # Simpan dataset
            with open(DATASET, "w", encoding="utf-8") as f:
                for q, a in pairs:
                    f.write(json.dumps({"messages": [
                        {"role": "user", "content": q},
                        {"role": "assistant", "content": a}
                    ]}, ensure_ascii=False) + "\n")

            # Build model
            model = build_model(pairs)
            with open(MODEL_OUT, "wb") as f:
                pickle.dump(model, f)

            upload_model()
            upload_dataset()

            last_save = time.time()
            new_count = 0
            print()

if __name__ == "__main__":
    main()
