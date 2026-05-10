"""
continuous_train.py — Fast parallel scraping, target model 300MB+
"""
import json, random, re, time, pickle, subprocess, os, gzip
from pathlib import Path
from collections import defaultdict
from math import log
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import wikipediaapi

DATASET   = Path("aland-ai/training/dataset.jsonl")
MODEL_OUT = Path("/tmp/aland-id-latest.gguf")
INTERVAL  = 300   # upload tiap 5 menit
WORKERS   = 10    # parallel scraping threads

WIKI = wikipediaapi.Wikipedia(language="id", user_agent="aland-ai/1.0")

# 300+ topik untuk dataset masif
TOPICS = [
    # Teknologi
    "Kecerdasan buatan","Machine learning","Python (bahasa pemrograman)",
    "Jaringan saraf tiruan","Pemrosesan bahasa alami","Komputer","Internet",
    "Algoritma","Struktur data","Sistem operasi","Linux","Basis data",
    "Jaringan komputer","Keamanan siber","Pemrograman","JavaScript","Java",
    "C++","Kriptografi","Cloud computing","Blockchain","Internet of Things",
    "Robotika","Augmented reality","Virtual reality","Komputasi kuantum",
    "Pengembangan web","Aplikasi mobile","DevOps","Git","Docker","Kubernetes",
    "Kecerdasan buatan umum","Deep learning","Reinforcement learning",
    "Computer vision","Pengenalan suara","Chatbot","Otomasi","Semikonduktor",
    # Sains
    "Matematika","Fisika","Kimia","Biologi","Geografi","Astronomi",
    "Fisika kuantum","Relativitas","Termodinamika","Elektromagnetisme",
    "Genetika","Evolusi","Ekologi","Anatomi","Fisiologi","Mikrobiologi",
    "Kimia organik","Kimia anorganik","Fisika nuklir","Kosmologi",
    "Geologi","Meteorologi","Oseanografi","Paleontologi","Botani","Zoologi",
    "Biokimia","Biofisika","Astrofisika","Mekanika","Optika","Akustik",
    "Statistika","Kalkulus","Aljabar","Geometri","Teori bilangan",
    # Indonesia
    "Indonesia","Sejarah Indonesia","Pancasila","Bahasa Indonesia",
    "Suku bangsa di Indonesia","Budaya Indonesia","Pariwisata Indonesia",
    "Ekonomi Indonesia","Politik Indonesia","Hukum Indonesia",
    "Pendidikan di Indonesia","Pulau Jawa","Pulau Sumatera",
    "Pulau Kalimantan","Pulau Sulawesi","Bali","Jakarta","Surabaya",
    "Bandung","Medan","Makassar","Yogyakarta","Semarang","Palembang",
    "Proklamasi kemerdekaan Indonesia","Orde Baru","Reformasi Indonesia",
    "Kerajaan Majapahit","Kerajaan Sriwijaya","Kerajaan Mataram",
    # Sosial & Humaniora
    "Ekonomi","Sosiologi","Psikologi","Antropologi","Filsafat","Sejarah",
    "Ilmu politik","Hukum","Pendidikan","Komunikasi","Manajemen",
    "Akuntansi","Pemasaran","Kewirausahaan","Bisnis","Perbankan",
    "Pasar modal","Inflasi","Globalisasi","Demokrasi","Hak asasi manusia",
    # Kesehatan
    "Kesehatan","Nutrisi","Olahraga","Kedokteran","Farmasi","Keperawatan",
    "Penyakit jantung","Diabetes","Kanker","Hipertensi","Obesitas",
    "Kesehatan mental","Psikiatri","Neurologi","Kardiologi","Onkologi",
    "Imunologi","Virologi","Epidemiologi","Gizi","Vitamin","Vaksin",
    "COVID-19","Influenza","Tuberkulosis","Malaria","HIV/AIDS",
    # Seni & Budaya
    "Musik","Seni","Sastra","Film","Fotografi","Arsitektur","Desain",
    "Tari","Teater","Lukisan","Patung","Sastra Indonesia","Puisi",
    "Novel","Komik","Animasi","Sinematografi","Gamelan","Batik","Wayang",
    # Alam
    "Lingkungan hidup","Perubahan iklim","Energi terbarukan","Pertanian",
    "Kehutanan","Perikanan","Peternakan","Konservasi","Biodiversitas",
    "Pemanasan global","Polusi","Energi surya","Energi angin","Hutan hujan",
    # Sejarah Dunia
    "Perang Dunia II","Perang Dunia I","Revolusi Perancis","Revolusi Industri",
    "Kekaisaran Romawi","Mesir kuno","Yunani kuno","Dinasti Ming",
    "Kolonialisme","Perang Dingin","PBB","NATO","Uni Eropa","Perang Vietnam",
    "Revolusi Amerika","Renaissance","Abad Pertengahan","Peradaban Islam",
    # Tokoh
    "Soekarno","Mohammad Hatta","Ki Hajar Dewantara","R.A. Kartini",
    "Albert Einstein","Isaac Newton","Charles Darwin","Marie Curie",
    "Leonardo da Vinci","Aristoteles","Plato","Socrates","Galileo Galilei",
    "Stephen Hawking","Nikola Tesla","Thomas Edison","Alan Turing",
    # Agama & Filosofi
    "Islam","Kristen","Hindu","Buddha","Konfusianisme","Filsafat Barat",
    "Filsafat Timur","Etika","Logika","Metafisika","Epistemologi",
    # Olahraga
    "Sepak bola","Bulu tangkis","Basket","Tenis","Renang","Atletik",
    "Tinju","Pencak silat","Olimpiade","Piala Dunia FIFA",
    # Kuliner
    "Kuliner Indonesia","Nasi goreng","Rendang","Soto","Gado-gado",
    "Sate","Bakso","Tempe","Tahu","Sambal","Masakan Padang","Masakan Jawa",
]

def normalize(t): return re.sub(r'\s+', ' ', t.lower().strip())
def tokenize(t):  return re.findall(r'\w+', normalize(t))

def scrape_topic(title: str) -> list:
    try:
        page = WIKI.page(title)
        if not page.exists(): return []
        pairs = []
        summary = page.summary[:800].strip()
        if len(summary) > 50:
            for q in [
                f"Apa itu {title}?", f"Jelaskan tentang {title}",
                f"Ceritakan tentang {title}", f"Apa yang dimaksud dengan {title}?",
                f"Berikan penjelasan tentang {title}", f"Apa pengertian {title}?",
                f"Tolong jelaskan {title}", f"Apa definisi {title}?",
            ]:
                pairs.append((q, summary))

        for s in page.sections:
            text = s.text.strip()
            if len(text) < 80: continue
            for i, chunk in enumerate([text[j:j+600] for j in range(0, min(len(text), 3000), 600)]):
                if len(chunk) < 80: continue
                pairs.append((f"Jelaskan {s.title} dalam {title}", chunk))
                pairs.append((f"Apa itu {s.title}?", chunk))
                if i == 0:
                    pairs.append((f"Bagaimana {s.title} berkaitan dengan {title}?", chunk))

        # Linked pages
        for link_title in list(page.links.keys())[:15]:
            try:
                linked = WIKI.page(link_title)
                if not linked.exists(): continue
                s2 = linked.summary[:500].strip()
                if len(s2) > 80:
                    pairs.append((f"Apa itu {link_title}?", s2))
                    pairs.append((f"Hubungan {link_title} dengan {title}?", s2))
            except: pass

        return pairs
    except: return []

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

def upload(tag: str, filepath: Path):
    subprocess.run(
        ["gh", "release", "upload", tag, str(filepath), "--clobber"],
        capture_output=True
    )
    mb = filepath.stat().st_size / 1024 / 1024
    print(f"  ✅ Uploaded {filepath.name} ({mb:.1f}MB) → {tag}")

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

    topics = TOPICS.copy()
    random.shuffle(topics)
    last_save = time.time()
    idx = 0

    while True:
        # Ambil batch 10 topik sekaligus (parallel)
        batch = [topics[(idx + i) % len(topics)] for i in range(WORKERS)]
        idx = (idx + WORKERS) % len(topics)
        if idx < WORKERS: random.shuffle(topics)

        print(f"Scraping {WORKERS} topik parallel: {batch[:3]}...")
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(scrape_topic, t): t for t in batch}
            for fut in as_completed(futures):
                new_pairs = fut.result()
                added = 0
                for q, a in new_pairs:
                    if q.lower() not in existing_q:
                        pairs.append((q, a))
                        existing_q.add(q.lower())
                        added += 1
                if added:
                    print(f"  +{added} ({futures[fut]}) → total: {len(pairs)}")

        # Tiap 5 menit: build + upload
        if time.time() - last_save >= INTERVAL:
            print(f"\n⏱ Build & upload model ({len(pairs)} pairs)...")

            with open(DATASET, "w", encoding="utf-8") as f:
                for q, a in pairs:
                    f.write(json.dumps({"messages": [
                        {"role": "user", "content": q},
                        {"role": "assistant", "content": a}
                    ]}, ensure_ascii=False) + "\n")

            model = build_model(pairs)
            with open(MODEL_OUT, "wb") as f:
                pickle.dump(model, f)

            upload("model-latest", MODEL_OUT)

            gz = Path(str(DATASET) + ".gz")
            subprocess.run(["gzip", "-kf", str(DATASET)], capture_output=True)
            upload("dataset-latest", gz)

            last_save = time.time()
            print()

if __name__ == "__main__":
    main()
