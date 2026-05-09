"""
scraper.py — Scrape Wikipedia ID + sumber lain → tambah ke dataset.jsonl
Dijalankan oleh GitHub Actions tiap hari.
"""
import json, random, re, time
from pathlib import Path

import requests
import wikipediaapi

DATASET = Path(__file__).parent / "dataset.jsonl"
WIKI = wikipediaapi.Wikipedia(language="id", user_agent="aland-ai-scraper/1.0")

# Topik yang di-scrape tiap hari (acak 20 dari daftar ini)
TOPICS = [
    # Sains & teknologi
    "Kecerdasan buatan","Machine learning","Python (bahasa pemrograman)",
    "Jaringan saraf tiruan","Pemrosesan bahasa alami","Komputer","Internet",
    "Basis data","Algoritma","Struktur data","Sistem operasi","Linux",
    # Umum
    "Indonesia","Sejarah Indonesia","Pancasila","Bahasa Indonesia",
    "Matematika","Fisika","Kimia","Biologi","Geografi","Ekonomi",
    "Kesehatan","Nutrisi","Olahraga","Musik","Seni","Sastra",
    # Kehidupan sehari-hari
    "Memasak","Pertanian","Lingkungan hidup","Perubahan iklim",
    "Energi terbarukan","Transportasi","Pendidikan","Psikologi",
]

def wiki_to_pairs(title: str) -> list[dict]:
    """Ambil artikel Wikipedia → buat pasangan Q&A."""
    page = WIKI.page(title)
    if not page.exists():
        return []

    pairs = []
    summary = page.summary[:500].strip()
    if len(summary) > 50:
        pairs.append({"messages": [
            {"role": "user", "content": f"Apa itu {title}?"},
            {"role": "assistant", "content": summary},
        ]})
        pairs.append({"messages": [
            {"role": "user", "content": f"Jelaskan tentang {title}"},
            {"role": "assistant", "content": summary},
        ]})
        pairs.append({"messages": [
            {"role": "user", "content": f"Ceritakan tentang {title}"},
            {"role": "assistant", "content": summary},
        ]})

    # Ambil tiap section sebagai Q&A tambahan
    for section in page.sections:
        text = section.text.strip()
        if len(text) < 80 or len(text) > 800:
            continue
        pairs.append({"messages": [
            {"role": "user", "content": f"Apa yang dimaksud dengan {section.title} dalam konteks {title}?"},
            {"role": "assistant", "content": text[:500]},
        ]})

    return pairs

def load_existing_questions() -> set:
    """Load pertanyaan yang sudah ada agar tidak duplikat."""
    existing = set()
    if DATASET.exists():
        with open(DATASET, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    msgs = obj.get("messages", [])
                    if msgs and msgs[0]["role"] == "user":
                        existing.add(msgs[0]["content"].strip().lower())
                except Exception:
                    pass
    return existing

def main():
    existing = load_existing_questions()
    topics = random.sample(TOPICS, min(20, len(TOPICS)))
    new_pairs = []

    for topic in topics:
        print(f"Scraping: {topic}")
        try:
            pairs = wiki_to_pairs(topic)
            for p in pairs:
                q = p["messages"][0]["content"].strip().lower()
                if q not in existing:
                    new_pairs.append(p)
                    existing.add(q)
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(0.5)  # jangan spam API

    if new_pairs:
        with open(DATASET, "a", encoding="utf-8") as f:
            for p in new_pairs:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        print(f"✅ Ditambahkan {len(new_pairs)} pasangan baru ke dataset.jsonl")
    else:
        print("Tidak ada data baru.")

if __name__ == "__main__":
    main()
