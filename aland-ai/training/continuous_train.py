"""
continuous_train.py — Infinite scraping, model naik tiap 1 menit, no duplicates
"""
import json, random, re, time, pickle, subprocess, os, gzip
from pathlib import Path
from collections import defaultdict
from math import log
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus, quote
import urllib.request

DATASET   = Path("aland-ai/training/dataset.jsonl")
MODEL_OUT = Path("/tmp/aland-id-latest.gguf")
UPLOAD_INTERVAL = 60   # upload tiap 1 menit

# ── Infinite topic generator ─────────────────────────────────────────────────
SEED_TOPICS = [
    "teknologi","sains","sejarah","budaya","kesehatan","pendidikan","ekonomi",
    "politik","hukum","agama","filsafat","matematika","fisika","kimia","biologi",
    "geografi","astronomi","komputer","internet","musik","seni","sastra","film",
    "olahraga","kuliner","pertanian","lingkungan","transportasi","arsitektur",
    "psikologi","sosiologi","antropologi","arkeologi","linguistik","kedokteran",
    "farmasi","nutrisi","ekologi","geologi","meteorologi","oseanografi",
    "Indonesia","Jawa","Sumatera","Kalimantan","Sulawesi","Bali","Papua",
    "Jakarta","Surabaya","Bandung","Medan","Makassar","Yogyakarta","Semarang",
    "Islam","Kristen","Hindu","Buddha","Konghucu",
    "Soekarno","Hatta","Kartini","Einstein","Newton","Darwin","Curie",
    "Majapahit","Sriwijaya","Mataram","Demak","Aceh","Ternate",
    "sepak bola","bulu tangkis","basket","renang","atletik","tinju","pencak silat",
    "nasi goreng","rendang","soto","gado-gado","sate","bakso","tempe","tahu",
    "roti","kopi","teh","coklat","gula","garam","minyak","beras",
    "mobil","motor","pesawat","kapal","kereta","sepeda","bus","truk",
    "rumah","gedung","jembatan","jalan","bendungan","pelabuhan","bandara",
    "pohon","bunga","hewan","ikan","burung","serangga","mamalia","reptil",
    "air","udara","tanah","api","listrik","magnet","cahaya","suara","panas",
    "demokrasi","republik","monarki","komunisme","kapitalisme","sosialisme",
    "perang","damai","diplomasi","perjanjian","konstitusi","undang-undang",
    "bank","saham","obligasi","inflasi","resesi","ekspor","impor","pajak",
    "sekolah","universitas","kurikulum","guru","siswa","ujian","beasiswa",
    "rumah sakit","dokter","perawat","obat","vaksin","virus","bakteri",
    "planet","bintang","galaksi","lubang hitam","meteor","komet","satelit",
    "atom","molekul","elektron","proton","neutron","ion","isotop","reaksi kimia",
    "evolusi","genetika","DNA","sel","jaringan","organ","sistem tubuh",
    "iklim","cuaca","hujan","angin","gempa","gunung berapi","tsunami","banjir",
    "energi surya","angin","air","nuklir","batu bara","minyak bumi","gas alam",
]

def get_wiki_categories(lang="id") -> list:
    """Ambil daftar kategori Wikipedia untuk topik baru."""
    url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=allcategories&aclimit=500&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aland-ai/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return [c["*"] for c in data.get("query", {}).get("allcategories", [])]
    except: return []

def get_wiki_random(lang="id", count=20) -> list:
    """Ambil judul artikel Wikipedia secara random."""
    url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit={count}&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aland-ai/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return [p["title"] for p in data.get("query", {}).get("random", [])]
    except: return []

def get_wiki_links(title: str, lang="id") -> list:
    """Ambil semua link dari artikel Wikipedia."""
    url = f"https://{lang}.wikipedia.org/w/api.php?action=query&titles={quote(title)}&prop=links&pllimit=50&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aland-ai/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        pages = data.get("query", {}).get("pages", {})
        links = []
        for page in pages.values():
            links += [l["title"] for l in page.get("links", [])]
        return links
    except: return []

# ── Scraper ──────────────────────────────────────────────────────────────────
def fetch(url, timeout=8) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 aland-ai/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except: return ""

def scrape_wiki(title: str, lang="id") -> list:
    pairs = []
    # Summary
    data = fetch(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}")
    if data:
        try:
            obj = json.loads(data)
            summary = obj.get("extract", "").strip()
            if len(summary) > 80:
                if lang == "id":
                    for q in [f"Apa itu {title}?", f"Jelaskan {title}",
                              f"Apa pengertian {title}?", f"Ceritakan tentang {title}",
                              f"Apa yang dimaksud {title}?"]:
                        pairs.append((q, summary[:600]))
                else:
                    pairs.append((f"What is {title}?", summary[:600]))
                    pairs.append((f"Explain {title}", summary[:600]))
        except: pass

    # Full text
    data = fetch(f"https://{lang}.wikipedia.org/w/api.php?action=query&titles={quote(title)}&prop=extracts&explaintext=1&format=json")
    if data:
        try:
            pages = json.loads(data).get("query", {}).get("pages", {})
            text = list(pages.values())[0].get("extract", "")
            for para in text.split("\n\n")[:15]:
                para = para.strip()
                if len(para) > 100:
                    q = f"Jelaskan tentang {title}" if lang == "id" else f"Tell me about {title}"
                    pairs.append((q, para[:600]))
        except: pass

    return pairs

def scrape_ddg(query: str) -> list:
    pairs = []
    data = fetch(f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1")
    if not data: return pairs
    try:
        obj = json.loads(data)
        abstract = obj.get("AbstractText", "").strip()
        if len(abstract) > 80:
            pairs.append((f"Apa itu {query}?", abstract[:600]))
        for t in obj.get("RelatedTopics", [])[:10]:
            text = t.get("Text", "").strip()
            if len(text) > 60:
                name = t.get("FirstURL", "").split("/")[-1].replace("_", " ")
                pairs.append((f"Apa itu {name}?", text[:600]))
    except: pass
    return pairs

# ── Model builder ─────────────────────────────────────────────────────────────
def normalize(t): return re.sub(r'\s+', ' ', t.lower().strip())
def tokenize(t):  return re.findall(r'\w+', normalize(t))

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
    """Upload file ke GitHub Releases via API."""
    token = os.environ.get("GH_TOKEN", "")
    repo  = "FerdiKusmanto/AI-EVIL-BY-ALAND"

    # Ambil release
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/tags/{tag}",
        headers={"Authorization": f"token {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            rel = json.loads(r.read())
    except: return

    # Hapus asset lama
    for asset in rel.get("assets", []):
        if asset["name"] == filepath.name:
            del_req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/releases/assets/{asset['id']}",
                method="DELETE", headers={"Authorization": f"token {token}"})
            try: urllib.request.urlopen(del_req)
            except: pass

    # Upload baru
    with open(filepath, "rb") as f:
        content = f.read()
    up_req = urllib.request.Request(
        f"https://uploads.github.com/repos/{repo}/releases/{rel['id']}/assets?name={filepath.name}",
        data=content, method="POST",
        headers={"Authorization": f"token {token}",
                 "Content-Type": "application/octet-stream",
                 "Content-Length": str(len(content))})
    try:
        urllib.request.urlopen(up_req)
        mb = len(content) / 1024 / 1024
        print(f"  ✅ {filepath.name} {mb:.1f}MB → {tag}")
    except Exception as e:
        print(f"  ❌ Upload gagal: {e}")

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    # Load dataset
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

    # Seed topic queue — infinite supply
    topic_queue = list(SEED_TOPICS)
    random.shuffle(topic_queue)
    used_topics = set(t.lower() for t in topic_queue)
    last_upload = time.time()
    last_expand = time.time()

    while True:
        # Expand topic queue tiap 5 menit dengan topik random dari Wikipedia
        if time.time() - last_expand > 300:
            new_random = get_wiki_random("id", 50) + get_wiki_random("en", 30)
            added_topics = 0
            for t in new_random:
                if t.lower() not in used_topics:
                    topic_queue.append(t)
                    used_topics.add(t.lower())
                    added_topics += 1
            print(f"  📚 +{added_topics} topik baru dari Wikipedia random")
            last_expand = time.time()

        # Ambil batch 20 topik
        if len(topic_queue) < 20:
            topic_queue += get_wiki_random("id", 50)

        batch = topic_queue[:20]
        topic_queue = topic_queue[20:]

        # Scrape parallel: Wiki ID + Wiki EN + DDG
        tasks = []
        for t in batch:
            tasks.append(("id", t))
            tasks.append(("en", t))
            tasks.append(("ddg", t))

        def run(task):
            kind, t = task
            if kind == "id":  return scrape_wiki(t, "id")
            if kind == "en":  return scrape_wiki(t, "en")
            if kind == "ddg": return scrape_ddg(t)
            return []

        added = 0
        with ThreadPoolExecutor(max_workers=30) as ex:
            for new_pairs in ex.map(run, tasks):
                for q, a in new_pairs:
                    if q.lower() not in existing_q:
                        pairs.append((q, a))
                        existing_q.add(q.lower())
                        added += 1

                        # Expand queue dari links artikel
                        if added % 100 == 0:
                            pass  # dilakukan di expand loop

        size_mb = sum(len(q)+len(a) for q,a in pairs) / 1024 / 1024
        print(f"+{added} pairs | total: {len(pairs)} | ~{size_mb:.0f}MB | queue: {len(topic_queue)}")

        # Upload tiap 1 menit
        if time.time() - last_upload >= UPLOAD_INTERVAL:
            print(f"\n⏱ Saving & uploading...")

            # Simpan dataset
            with open(DATASET, "w", encoding="utf-8") as f:
                for q, a in pairs:
                    f.write(json.dumps({"messages": [
                        {"role": "user", "content": q},
                        {"role": "assistant", "content": a}
                    ]}, ensure_ascii=False) + "\n")

            # Build + upload model
            model = build_model(pairs)
            with open(MODEL_OUT, "wb") as f:
                pickle.dump(model, f)
            upload("model-latest", MODEL_OUT)

            # Upload dataset
            gz = Path(str(DATASET) + ".gz")
            subprocess.run(["gzip", "-kf", str(DATASET)], capture_output=True)
            upload("dataset-latest", gz)

            last_upload = time.time()

            # Expand queue dari linked pages artikel terbaru
            sample_topics = random.sample(batch, min(5, len(batch)))
            for t in sample_topics:
                links = get_wiki_links(t, "id")[:20]
                for link in links:
                    if link.lower() not in used_topics:
                        topic_queue.append(link)
                        used_topics.add(link.lower())
            print(f"  Queue diperluas: {len(topic_queue)} topik tersisa\n")

if __name__ == "__main__":
    main()
