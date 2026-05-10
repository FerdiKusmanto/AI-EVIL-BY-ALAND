"""
continuous_train.py — Multi-source scraping: Wikipedia + DuckDuckGo + dataset publik
Target: +5-7MB per menit
"""
import json, random, re, time, pickle, subprocess, os, gzip, io
from pathlib import Path
from collections import defaultdict
from math import log
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

import requests
import wikipediaapi

DATASET   = Path("aland-ai/training/dataset.jsonl")
MODEL_OUT = Path("/tmp/aland-id-latest.gguf")
INTERVAL  = 60    # upload tiap 1 menit
WORKERS   = 20    # parallel threads

WIKI = wikipediaapi.Wikipedia(language="id", user_agent="aland-ai/1.0")
WIKI_EN = wikipediaapi.Wikipedia(language="en", user_agent="aland-ai/1.0")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; aland-ai/1.0)"})

# ── Sumber dataset publik (download langsung, sudah jadi) ────────────────────
PUBLIC_DATASETS = [
    # Wikipedia dumps (ringkasan semua artikel)
    "https://dumps.wikimedia.org/idwiki/latest/idwiki-latest-abstract.xml.gz",
    # IndoNLI, IndoQA, dll via HuggingFace datasets API
    "https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.id&split=train&offset=0&length=100",
    "https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.id&split=train&offset=100&length=100",
    "https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.id&split=train&offset=200&length=100",
    "https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.id&split=train&offset=300&length=100",
    "https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.id&split=train&offset=400&length=100",
]

TOPICS_ID = [
    "Kecerdasan buatan","Machine learning","Python","Jaringan saraf tiruan",
    "Pemrosesan bahasa alami","Komputer","Internet","Algoritma","Struktur data",
    "Sistem operasi","Linux","Basis data","Jaringan komputer","Keamanan siber",
    "Pemrograman","JavaScript","Java","C++","Kriptografi","Cloud computing",
    "Blockchain","Internet of Things","Robotika","Komputasi kuantum","Docker",
    "Matematika","Fisika","Kimia","Biologi","Geografi","Astronomi",
    "Fisika kuantum","Relativitas","Termodinamika","Elektromagnetisme",
    "Genetika","Evolusi","Ekologi","Anatomi","Fisiologi","Mikrobiologi",
    "Indonesia","Sejarah Indonesia","Pancasila","Bahasa Indonesia",
    "Budaya Indonesia","Ekonomi Indonesia","Politik Indonesia",
    "Pulau Jawa","Pulau Sumatera","Bali","Jakarta","Surabaya","Bandung",
    "Proklamasi kemerdekaan Indonesia","Kerajaan Majapahit","Sriwijaya",
    "Ekonomi","Sosiologi","Psikologi","Antropologi","Filsafat","Sejarah",
    "Ilmu politik","Hukum","Pendidikan","Komunikasi","Manajemen","Bisnis",
    "Kesehatan","Nutrisi","Olahraga","Kedokteran","Farmasi","Kanker",
    "Kesehatan mental","Neurologi","Imunologi","Virologi","Epidemiologi",
    "Musik","Seni","Sastra","Film","Fotografi","Arsitektur","Batik","Wayang",
    "Lingkungan hidup","Perubahan iklim","Energi terbarukan","Pertanian",
    "Perang Dunia II","Perang Dunia I","Revolusi Perancis","Revolusi Industri",
    "Kekaisaran Romawi","Mesir kuno","Yunani kuno","Perang Dingin",
    "Soekarno","Mohammad Hatta","Albert Einstein","Isaac Newton","Marie Curie",
    "Islam","Kristen","Hindu","Buddha","Filsafat Barat","Etika","Logika",
    "Sepak bola","Bulu tangkis","Basket","Olimpiade","Piala Dunia FIFA",
    "Kuliner Indonesia","Nasi goreng","Rendang","Soto","Batik","Gamelan",
    "Statistika","Kalkulus","Aljabar","Geometri","Biokimia","Astrofisika",
    "COVID-19","Vaksin","Diabetes","Hipertensi","Gizi","Vitamin",
    "Memasak","Pariwisata","Transportasi","Otomotif","Investasi","Properti",
]

TOPICS_EN = [
    "Artificial intelligence","Machine learning","Deep learning","Neural network",
    "Natural language processing","Computer science","Algorithm","Data structure",
    "Operating system","Database","Cryptography","Cloud computing","Blockchain",
    "Mathematics","Physics","Chemistry","Biology","Astronomy","Quantum physics",
    "Genetics","Evolution","Ecology","Anatomy","Microbiology","Biochemistry",
    "History","World War II","World War I","Cold War","Renaissance",
    "Economics","Psychology","Sociology","Philosophy","Ethics","Logic",
    "Health","Medicine","Nutrition","Cancer","Immunology","Virology",
    "Music","Art","Literature","Film","Architecture","Photography",
    "Climate change","Renewable energy","Agriculture","Conservation",
    "Football","Basketball","Olympics","Tennis","Swimming",
]

def normalize(t): return re.sub(r'\s+', ' ', t.lower().strip())
def tokenize(t):  return re.findall(r'\w+', normalize(t))

def scrape_wiki_id(title: str) -> list:
    try:
        page = WIKI.page(title)
        if not page.exists(): return []
        pairs = []
        summary = page.summary[:800].strip()
        if len(summary) > 50:
            for q in [f"Apa itu {title}?", f"Jelaskan {title}",
                      f"Apa pengertian {title}?", f"Ceritakan tentang {title}",
                      f"Apa yang dimaksud {title}?", f"Tolong jelaskan {title}"]:
                pairs.append((q, summary))
        for s in page.sections:
            text = s.text.strip()
            if len(text) < 80: continue
            for chunk in [text[i:i+600] for i in range(0, min(len(text),3000), 600)]:
                if len(chunk) < 80: continue
                pairs.append((f"Jelaskan {s.title} dalam {title}", chunk))
                pairs.append((f"Apa itu {s.title}?", chunk))
        for link in list(page.links.keys())[:20]:
            try:
                lp = WIKI.page(link)
                if lp.exists() and len(lp.summary) > 80:
                    pairs.append((f"Apa itu {link}?", lp.summary[:500]))
            except: pass
        return pairs
    except: return []

def scrape_wiki_en(title: str) -> list:
    """Scrape Wikipedia English → terjemahkan pertanyaan ke Indonesia."""
    try:
        page = WIKI_EN.page(title)
        if not page.exists(): return []
        pairs = []
        summary = page.summary[:800].strip()
        if len(summary) > 50:
            for q in [f"What is {title}?", f"Explain {title}",
                      f"Tell me about {title}", f"Define {title}"]:
                pairs.append((q, summary))
            # Versi Indonesia
            for q in [f"Apa itu {title}?", f"Jelaskan {title}"]:
                pairs.append((q, summary))
        for s in page.sections:
            text = s.text.strip()
            if 80 <= len(text) <= 800:
                pairs.append((f"What is {s.title} in {title}?", text[:600]))
        return pairs
    except: return []

def scrape_duckduckgo(query: str) -> list:
    """DuckDuckGo Instant Answer API — gratis, no key."""
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        r = SESSION.get(url, timeout=5)
        d = r.json()
        pairs = []
        abstract = d.get("AbstractText", "").strip()
        if len(abstract) > 80:
            pairs.append((f"Apa itu {query}?", abstract))
            pairs.append((f"Jelaskan {query}", abstract))
        for topic in d.get("RelatedTopics", [])[:10]:
            text = topic.get("Text", "").strip()
            if len(text) > 60:
                pairs.append((f"Apa itu {topic.get('FirstURL','').split('/')[-1].replace('_',' ')}?", text))
        return pairs
    except: return []

def fetch_hf_wikipedia(url: str) -> list:
    """Fetch dari HuggingFace datasets API — Wikipedia ID."""
    try:
        r = SESSION.get(url, timeout=15)
        rows = r.json().get("rows", [])
        pairs = []
        for row in rows:
            row_data = row.get("row", {})
            title = row_data.get("title", "").strip()
            text  = row_data.get("text", "").strip()
            if not title or len(text) < 100: continue
            summary = text[:600]
            pairs.append((f"Apa itu {title}?", summary))
            pairs.append((f"Jelaskan tentang {title}", summary))
            # Ambil paragraf-paragraf
            for para in text.split("\n\n")[:5]:
                para = para.strip()
                if len(para) > 100:
                    pairs.append((f"Ceritakan tentang {title}", para[:500]))
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
    subprocess.run(["gh","release","upload",tag,str(filepath),"--clobber"], capture_output=True)
    mb = filepath.stat().st_size / 1024 / 1024
    print(f"  ✅ {filepath.name} {mb:.1f}MB → {tag}")

def main():
    pairs, existing_q = [], set()
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
    size_mb = sum(len(q)+len(a) for q,a in pairs) / 1024 / 1024
    print(f"Dataset awal: {len(pairs)} pairs (~{size_mb:.0f}MB)")

    # Fetch HuggingFace Wikipedia ID — 50000 artikel (target dataset 300MB)
    print("Fetching HuggingFace Wikipedia ID dataset (target 300MB)...")
    hf_urls = [
        f"https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.id&split=train&offset={i}&length=100"
        for i in range(0, 50000, 100)
    ]
    with ThreadPoolExecutor(max_workers=30) as ex:
        for new_pairs in ex.map(fetch_hf_wikipedia, hf_urls):
            for q, a in new_pairs:
                if q.lower() not in existing_q:
                    pairs.append((q, a))
                    existing_q.add(q.lower())
    size_mb = sum(len(q)+len(a) for q,a in pairs) / 1024 / 1024
    print(f"  ID fetch: {len(pairs)} pairs (~{size_mb:.0f}MB)")

    print("Fetching HuggingFace Wikipedia EN dataset...")
    hf_en_urls = [
        f"https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.en&split=train&offset={i}&length=100"
        for i in range(0, 20000, 100)
    ]
    with ThreadPoolExecutor(max_workers=30) as ex:
        for new_pairs in ex.map(fetch_hf_wikipedia, hf_en_urls):
            for q, a in new_pairs:
                if q.lower() not in existing_q:
                    pairs.append((q, a))
                    existing_q.add(q.lower())
    size_mb = sum(len(q)+len(a) for q,a in pairs) / 1024 / 1024
    print(f"Setelah HF fetch: {len(pairs)} pairs (~{size_mb:.0f}MB)")

    topics_id = TOPICS_ID.copy()
    topics_en = TOPICS_EN.copy()
    random.shuffle(topics_id)
    random.shuffle(topics_en)
    last_save = time.time()
    idx = 0

    while True:
        # Batch parallel: Wiki ID + Wiki EN + DuckDuckGo
        batch_tasks = []
        for i in range(10):
            batch_tasks.append(("wiki_id", topics_id[(idx+i) % len(topics_id)]))
            batch_tasks.append(("wiki_en", topics_en[(idx+i) % len(topics_en)]))
            batch_tasks.append(("ddg", topics_id[(idx+i) % len(topics_id)]))
        idx = (idx + 10) % len(topics_id)
        if idx < 10: random.shuffle(topics_id); random.shuffle(topics_en)

        def run_task(task):
            kind, topic = task
            if kind == "wiki_id": return scrape_wiki_id(topic)
            if kind == "wiki_en": return scrape_wiki_en(topic)
            if kind == "ddg":     return scrape_duckduckgo(topic)
            return []

        added_total = 0
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for new_pairs in ex.map(run_task, batch_tasks):
                for q, a in new_pairs:
                    if q.lower() not in existing_q:
                        pairs.append((q, a))
                        existing_q.add(q.lower())
                        added_total += 1

        size_kb = sum(len(q)+len(a) for q,a in pairs) // 1024
        print(f"+{added_total} pairs | total: {len(pairs)} | ~{size_kb//1024}MB raw")

        if time.time() - last_save >= INTERVAL:
            print(f"\n⏱ Saving & uploading...")
            with open(DATASET, "w", encoding="utf-8") as f:
                for q, a in pairs:
                    f.write(json.dumps({"messages":[
                        {"role":"user","content":q},
                        {"role":"assistant","content":a}
                    ]}, ensure_ascii=False) + "\n")
            model = build_model(pairs)
            with open(MODEL_OUT, "wb") as f:
                pickle.dump(model, f)
            upload("model-latest", MODEL_OUT)
            gz = Path(str(DATASET)+".gz")
            subprocess.run(["gzip","-kf",str(DATASET)], capture_output=True)
            upload("dataset-latest", gz)
            last_save = time.time()
            print()

if __name__ == "__main__":
    main()
