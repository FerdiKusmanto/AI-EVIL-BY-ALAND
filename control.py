#!/usr/bin/env python3
"""
control.py — Control panel untuk ALand-AI Cloud Training
Usage: python3 control.py
"""
import urllib.request, urllib.parse, json, sys, os, time, gzip, subprocess

TOKEN = os.environ.get("ALAND_TOKEN", "")  # set: export ALAND_TOKEN=ghp_...
if not TOKEN:
    TOKEN = input("Masukkan GitHub Token (ghp_...): ").strip()
REPO  = "FerdiKusmanto/AI-EVIL-BY-ALAND"
DATASET = "aland-ai/training/dataset.jsonl"

# ── GitHub API helpers ───────────────────────────────────────────────────────
def gh(method, path, data=None):
    url = f"https://api.github.com{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
          headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()) if r.length != 0 else {}
    except urllib.error.HTTPError as e:
        return {"error": e.code, "msg": e.read().decode()}

def get_runs(n=3):
    return gh("GET", f"/repos/{REPO}/actions/runs?per_page={n}").get("workflow_runs", [])

def get_releases():
    return gh("GET", f"/repos/{REPO}/releases")

# ── Scrape topik dari berbagai sumber ────────────────────────────────────────
def scrape_topic_web(topic: str) -> list:
    """Cari data tentang topik dari Wikipedia ID + EN + DuckDuckGo."""
    import re
    # Bersihkan input — hapus kata tidak perlu
    topic = re.sub(r'\b(adalah|itu|merupakan|yaitu|yakni|tentang|mengenai)\b', '', topic, flags=re.I).strip()
    topic = re.sub(r'\s+', ' ', topic).strip()

    pairs = []

    def fetch(url, timeout=8):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 aland-ai/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="ignore")
        except: return ""

    def wiki_search_id(q):
        """Cari judul artikel Wikipedia ID yang paling relevan."""
        url = f"https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json&srlimit=3"
        data = fetch(url)
        if not data: return []
        try:
            results = json.loads(data).get("query", {}).get("search", [])
            return [r["title"] for r in results]
        except: return []

    def wiki_summary_id(title):
        url = f"https://id.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
        data = fetch(url)
        if not data: return ""
        try: return json.loads(data).get("extract", "").strip()
        except: return ""

    def wiki_full_id(title):
        url = f"https://id.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=extracts&explaintext=1&format=json"
        data = fetch(url)
        if not data: return ""
        try:
            pages = json.loads(data).get("query", {}).get("pages", {})
            return list(pages.values())[0].get("extract", "")
        except: return ""

    def wiki_summary_en(title):
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
        data = fetch(url)
        if not data: return ""
        try: return json.loads(data).get("extract", "").strip()
        except: return ""

    def ddg(q):
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1&skip_disambig=1"
        data = fetch(url)
        results = []
        if not data: return results
        try:
            obj = json.loads(data)
            abstract = obj.get("AbstractText", "").strip()
            if len(abstract) > 60: results.append(abstract)
            for t in obj.get("RelatedTopics", [])[:8]:
                text = t.get("Text", "").strip()
                if len(text) > 60: results.append(text)
        except: pass
        return results

    # 1. Cari artikel Wikipedia ID yang relevan
    titles = wiki_search_id(topic)
    if not titles:
        titles = [topic]  # fallback langsung pakai topik

    for title in titles[:3]:
        summary = wiki_summary_id(title)
        if len(summary) > 80:
            for q in [f"Apa itu {title}?", f"Jelaskan {title}",
                      f"Apa pengertian {title}?", f"Ceritakan tentang {title}"]:
                pairs.append((q, summary[:600]))
        # Ambil full text, pecah per paragraf
        full = wiki_full_id(title)
        for para in full.split("\n\n")[:8]:
            para = para.strip()
            if len(para) > 100:
                pairs.append((f"Ceritakan tentang {title}", para[:600]))

    # 2. Wikipedia English
    en_summary = wiki_summary_en(topic)
    if len(en_summary) > 80:
        pairs.append((f"What is {topic}?", en_summary[:600]))
        pairs.append((f"Explain {topic}", en_summary[:600]))

    # 3. DuckDuckGo
    for text in ddg(topic):
        pairs.append((f"Apa itu {topic}?", text[:600]))
    for text in ddg(f"{topic} Indonesia"):
        pairs.append((f"Jelaskan {topic} di Indonesia", text[:600]))

    # Deduplikasi
    seen = set()
    unique = []
    for q, a in pairs:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            unique.append((q, a))

    return unique

def add_to_dataset(pairs: list):
    """Tambah pairs ke dataset lokal dan upload ke GitHub Releases."""
    if not pairs:
        print("Tidak ada data baru.")
        return

    # Append ke dataset lokal
    os.makedirs(os.path.dirname(DATASET), exist_ok=True)
    with open(DATASET, "a", encoding="utf-8") as f:
        for q, a in pairs:
            f.write(json.dumps({"messages": [
                {"role": "user", "content": q},
                {"role": "assistant", "content": a}
            ]}, ensure_ascii=False) + "\n")

    # Upload ke GitHub Releases
    gz_path = DATASET + ".gz"
    subprocess.run(["gzip", "-kf", DATASET], capture_output=True)
    env = {**os.environ, "GH_TOKEN": TOKEN}
    result = subprocess.run(
        ["gh", "release", "upload", "dataset-latest", gz_path, "--clobber",
         "--repo", REPO],
        capture_output=True, text=True, env=env
    )
    if result.returncode == 0:
        size = os.path.getsize(gz_path) / 1024 / 1024
        print(f"  ✅ Dataset diupload ({size:.1f}MB)")
    else:
        # Fallback: upload via API
        with open(gz_path, "rb") as f:
            content = f.read()
        # Ambil release ID
        releases = get_releases()
        rel_id = next((r["id"] for r in releases if r["tag_name"] == "dataset-latest"), None)
        if rel_id:
            req = urllib.request.Request(
                f"https://uploads.github.com/repos/{REPO}/releases/{rel_id}/assets?name=dataset.jsonl.gz",
                data=content, method="POST",
                headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/gzip"}
            )
            try:
                urllib.request.urlopen(req)
                print(f"  ✅ Dataset diupload via API")
            except: print(f"  ⚠ Upload gagal: {result.stderr}")

# ── Workflow controls ────────────────────────────────────────────────────────
def start_train():
    r = gh("POST", f"/repos/{REPO}/actions/workflows/continuous-train.yml/dispatches",
           {"ref": "main"})
    if "error" not in r:
        print("✅ Continuous Train dimulai")
    else:
        print(f"❌ Gagal: {r}")

def stop_train():
    runs = get_runs(10)
    stopped = 0
    for run in runs:
        if run["status"] == "in_progress":
            r = gh("POST", f"/repos/{REPO}/actions/runs/{run['id']}/cancel")
            stopped += 1
    print(f"✅ {stopped} run dihentikan" if stopped else "Tidak ada run yang berjalan")

def status():
    os.system("clear")
    print("=" * 55)
    print("  🤖 ALand-AI Control Panel")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    print("\n📋 WORKFLOW:")
    for r in get_runs(4):
        icon = "🔄" if r["status"] == "in_progress" else \
               "✅" if r.get("conclusion") == "success" else \
               "⏳" if r["status"] == "queued" else "❌"
        print(f"  {icon} {r['name']:<22} {r['status']} ({r['created_at'][11:16]} UTC)")

    print("\n📦 RELEASES:")
    for rel in get_releases():
        for a in rel.get("assets", []):
            mb = round(a["size"] / 1024 / 1024, 2)
            print(f"  📄 {a['name']:<30} {mb}MB  {a['updated_at'][11:16]} UTC")

    # Dataset lokal
    if os.path.exists(DATASET):
        lines = sum(1 for _ in open(DATASET, encoding="utf-8"))
        size  = os.path.getsize(DATASET) / 1024 / 1024
        print(f"\n💾 DATASET LOKAL: {lines} pairs ({size:.1f}MB)")
    print("=" * 55)

# ── Main menu ────────────────────────────────────────────────────────────────
def menu():
    print("\n" + "=" * 55)
    print("  🤖 ALand-AI Control Panel")
    print("=" * 55)
    print("  [1] Status (workflow + model size)")
    print("  [2] Mulai training cloud")
    print("  [3] Hentikan training cloud")
    print("  [4] Tambah dataset — ketik topik (contoh: roti)")
    print("  [5] Monitor realtime (refresh 30 detik)")
    print("  [0] Keluar")
    print("=" * 55)
    return input("  Pilih: ").strip()

def main():
    while True:
        choice = menu()

        if choice == "1":
            status()
            input("\nTekan Enter untuk kembali...")

        elif choice == "2":
            start_train()
            input("\nTekan Enter untuk kembali...")

        elif choice == "3":
            stop_train()
            input("\nTekan Enter untuk kembali...")

        elif choice == "4":
            topic = input("\n  Ketik topik (contoh: roti, fisika, Jakarta): ").strip()
            if not topic:
                print("  Topik kosong.")
                continue
            print(f"\n  🔍 Mencari data tentang '{topic}' dari internet...")
            pairs = scrape_topic_web(topic)
            print(f"  Ditemukan: {len(pairs)} pasangan Q&A")
            if pairs:
                for q, a in pairs[:3]:
                    print(f"    Q: {q}")
                    print(f"    A: {a[:80]}...")
                    print()
                confirm = input(f"  Tambah {len(pairs)} pairs ke dataset? [y/n]: ").strip().lower()
                if confirm == "y":
                    add_to_dataset(pairs)
                    print(f"  ✅ {len(pairs)} pairs ditambahkan")
            input("\nTekan Enter untuk kembali...")

        elif choice == "5":
            print("  Monitor aktif — Ctrl+C untuk kembali ke menu\n")
            try:
                while True:
                    status()
                    time.sleep(30)
            except KeyboardInterrupt:
                pass

        elif choice == "0":
            print("  Sampai jumpa!")
            sys.exit(0)

if __name__ == "__main__":
    main()
