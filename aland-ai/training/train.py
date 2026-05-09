"""
aland-ai trainer v2 — Tanpa download model eksternal
Melatih model AI sederhana dari dataset lokal menggunakan:
- Template matching (exact & fuzzy)
- N-gram language model
- Markov chain untuk generasi teks
Hasil disimpan sebagai file .aland-model yang bisa langsung dipakai aland-ai serve
"""

import json
import math
import os
import pickle
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote_plus
from urllib.error import URLError
from html import unescape

DATASET   = Path(__file__).parent / "dataset.jsonl"
MODEL_OUT = Path.home() / ".aland-ai" / "models"
MODEL_FILE = MODEL_OUT / "aland-id.aland-model"
MODEL_OUT.mkdir(parents=True, exist_ok=True)

# ── Load dataset ────────────────────────────────────────────────────────────
def load_pairs() -> list[tuple[str, str]]:
    pairs = []
    raw = DATASET.read_text()
    # Support JSON array atau JSONL
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        items = [json.loads(l) for l in raw.splitlines() if l.strip()]
    for item in items:
        msgs = item["messages"]
        for i in range(len(msgs) - 1):
            if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant":
                pairs.append((msgs[i]["content"], msgs[i+1]["content"]))
    return pairs

# ── Tokenizer sederhana ─────────────────────────────────────────────────────
def tokenize(text: str) -> list[str]:
    return re.findall(r'\w+|[^\w\s]', text.lower())

def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip().lower())

# ── Similarity (cosine bag-of-words) ───────────────────────────────────────
def similarity(a: str, b: str) -> float:
    ta, tb = set(tokenize(a)), set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / math.sqrt(len(ta) * len(tb))

# ── Markov chain trainer ────────────────────────────────────────────────────
def build_markov(texts: list[str], order: int = 2) -> dict:
    chain = defaultdict(list)
    for text in texts:
        words = tokenize(text)
        for i in range(len(words) - order):
            key = tuple(words[i:i+order])
            chain[key].append(words[i+order])
    return dict(chain)

def markov_generate(chain: dict, seed_words: list[str], order: int = 2, max_tokens: int = 80) -> str:
    if not chain:
        return ""
    # Cari starting key yang mengandung seed
    candidates = [k for k in chain if any(w in k for w in seed_words)]
    if not candidates:
        candidates = list(chain.keys())
    key = list(random.choice(candidates))
    result = list(key)
    for _ in range(max_tokens):
        k = tuple(result[-order:])
        nexts = chain.get(k)
        if not nexts:
            break
        result.append(random.choice(nexts))
    return detokenize(result)

def detokenize(tokens: list[str]) -> str:
    result = ""
    for i, t in enumerate(tokens):
        if i == 0:
            result = t
        elif re.match(r'[^\w]', t):
            result += t
        else:
            result += " " + t
    # Capitalize first letter
    return result[0].upper() + result[1:] if result else result

# ── Math solver ─────────────────────────────────────────────────────────────
def _solve_math(text: str) -> str | None:
    """Selesaikan operasi matematika — hanya jika ada kata tanya/perintah hitung."""
    t = text.lower().strip()

    # Harus ada trigger kata tanya/hitung, bukan sekadar angka acak
    math_triggers = r'\b(berapa|hitung|calculate|what is|hasil|nilai|compute)\b'
    has_trigger = bool(re.search(math_triggers, t))
    # Atau format eksplisit: "X op Y =" atau "X op Y?"
    explicit = bool(re.search(r'^\s*\d[\d\s]*[+\-*/×÷]\s*\d[\d\s]*[=?]?\s*$', t))
    if not has_trigger and not explicit:
        return None

    # Normalisasi kata ke simbol
    t = re.sub(r'\bdibagi\b', '/', t)
    t = re.sub(r'\bdikali\b|\bkali\b', '*', t)
    t = re.sub(r'\bditambah\b|\btambah\b', '+', t)
    t = re.sub(r'\bdikurang\b|\bkurang\b|\bminus\b', '-', t)
    t = re.sub(r'\btimes\b|\bmultiplied by\b', '*', t)
    t = re.sub(r'\bdivided by\b', '/', t)
    t = re.sub(r'\bplus\b', '+', t)

    # Persen: "X% dari Y"
    pct = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:dari|of)\s*(\d+(?:\.\d+)?)', t)
    if pct:
        a, b = float(pct.group(1)), float(pct.group(2))
        return f"{a:g}% dari {b:g} = {a/100*b:g}"

    # Kuadrat: "X pangkat 2" atau "kuadrat dari X"
    sq = re.search(r'(?:kuadrat dari|kuadrat)\s*(\d+)|(\d+)\s*pangkat\s*2', t)
    if sq:
        n = int(sq.group(1) or sq.group(2))
        return f"{n}² = {n*n}"

    # Akar: "akar dari X" atau "akar X"
    sqrt_m = re.search(r'akar(?:\s*kuadrat)?\s*(?:dari\s*)?(\d+)', t)
    if sqrt_m:
        import math
        n = int(sqrt_m.group(1))
        r = math.sqrt(n)
        return f"√{n} = {r:g}"

    # Ekspresi angka + operator
    expr = re.search(r'(\d+(?:\.\d+)?)\s*([+\-*/×÷])\s*(\d+(?:\.\d+)?)', t)
    if expr:
        a, op, b = float(expr.group(1)), expr.group(2), float(expr.group(3))
        op = op.replace('×', '*').replace('÷', '/')
        try:
            if op == '+':   result = a + b
            elif op == '-': result = a - b
            elif op == '*': result = a * b
            elif op == '/':
                if b == 0: return "Tidak bisa dibagi dengan nol."
                result = a / b
            else:
                return None
            return f"{a:g} {op} {b:g} = {result:g}"
        except Exception:
            return None

    return None

# ── Language detector ────────────────────────────────────────────────────────
_EN_WORDS = {"what", "is", "are", "the", "a", "an", "how", "why", "who",
             "where", "when", "which", "does", "do", "can", "tell", "me",
             "about", "explain", "define", "meaning", "of", "in", "and"}

def _detect_lang(text: str) -> str:
    words = set(tokenize(text))
    en_count = len(words & _EN_WORDS)
    return "en" if en_count >= 2 else "id"

# ── Casual / small-talk responses ───────────────────────────────────────────
_CASUAL: list[tuple[list[str], list[str]]] = [
    # sapaan
    (["hai", "halo", "helo", "hello", "hi", "hey", "assalamu", "selamat pagi",
      "selamat siang", "selamat sore", "selamat malam"],
     ["Hai! Ada yang bisa saya bantu? 😊", "Halo! Apa kabar?",
      "Hey! Senang bertemu kamu 😄"]),
    # sapaan bahasa daerah / gaul
    (["opo", "opo kabar", "piye", "piye kabar"],
     ["Halo! Ada yang bisa saya bantu? 😊", "Hai! Apa kabar?"]),
    # kabar
    (["apa kabar", "gimana kabar", "how are you", "kabar kamu"],
     ["Kabar saya baik, terima kasih! Kamu sendiri? 😊",
      "Baik-baik saja! Ada yang bisa saya bantu?"]),
    # baik / oke / sip / bagus
    (["baik", "baik juga", "oke", "ok", "sip", "fine", "good", "alright",
      "bagus", "mantap", "keren", "oke bagus", "ok bagus", "baik bagus"],
     ["Senang mendengarnya! 😊 Silakan, mau tanya apa?",
      "Oke! Bisa saya bantu apa?",
      "Siap! Ada yang ingin ditanyakan?"]),
    # ada / ada apa / ada yang bisa dibantu
    (["ada", "ada?", "ada apa", "ada yang bisa dibantu", "ada sesuatu"],
     ["Ada apa? 😊", "Ya, ada yang bisa saya bantu?", "Halo! Ada yang ingin ditanyakan?"]),
    # tunggu / sebentar
    (["sebentar", "tunggu", "wait", "hold on", "bentar", "ntar"],
     ["Oke, saya tunggu! 😊", "Siap, tidak kemana-mana! 😄"]),
    # mau tanya / ingin tanya
    (["ingin tanya", "mau tanya", "boleh tanya", "bisa tanya",
      "ingin bertanya", "mau bertanya", "want to ask", "i have a question"],
     ["Tentu! Silakan tanyakan apa saja 😊",
      "Boleh, saya siap menjawab! Apa yang ingin kamu tanyakan?",
      "Silakan! Saya siap membantu 🤖"]),
    # mau tanya sesuatu yang berbeda / topik baru
    (["tanya sesuatu yang berbeda", "topik berbeda", "hal lain", "sesuatu yang lain",
      "different topic", "something else"],
     ["Tentu! Silakan, mau tanya apa? 😊",
      "Oke, ganti topik! Ada yang ingin kamu tanyakan?"]),
    # terima kasih
    (["terima kasih", "makasih", "thanks", "thank you", "thx"],
     ["Sama-sama! 😊", "Dengan senang hati!", "No problem!"]),
    # perpisahan
    (["bye", "dadah", "sampai jumpa", "selamat tinggal", "goodbye", "ciao"],
     ["Sampai jumpa! 👋", "Dadah! Semoga harimu menyenangkan 😊"]),
    # siapa kamu
    (["siapa kamu", "kamu siapa", "who are you", "nama kamu", "your name"],
     ["Saya ALand-AI, asisten AI buatan ALand. Siap membantu kamu! 🤖"]),
    # apa yang bisa kamu lakukan
    (["apa yang bisa kamu lakukan", "kamu bisa apa", "what can you do",
      "kemampuan kamu", "fitur kamu"],
     ["Saya bisa menjawab pertanyaan, menghitung matematika, menjelaskan topik "
      "dalam bahasa Indonesia maupun Inggris. Coba tanya saja! 😊"]),
]

def _casual_response(text: str) -> str | None:
    """Cek apakah input adalah percakapan kasual, kembalikan respons yang sesuai."""
    t = normalize(text)
    t = re.sub(r'(.)\1+', r'\1', t)
    tokens = set(tokenize(t))
    n = len(tokens)

    for keywords, responses in _CASUAL:
        for kw in keywords:
            kw_tokens = tokenize(kw)
            kw_set = set(kw_tokens)
            kw_len = len(kw_tokens)
            if kw_set <= tokens:
                # Keyword 1 kata: hanya cocok jika input pendek (≤3 token)
                if kw_len == 1 and n > 3:
                    continue
                # Keyword multi-kata: toleransi proporsional
                if kw_len >= 2 and n > kw_len + 4:
                    continue
                return random.choice(responses)

    # Fallback: deteksi pola "ingin/mau tanya" di kalimat panjang apapun
    _tanya_pat = re.compile(
        r'\b(ingin|mau|boleh|bisa|want to|i want|let me)\b.{0,20}\b(tanya|bertanya|ask|question)\b',
        re.I
    )
    if _tanya_pat.search(t):
        return random.choice(["Tentu! Silakan tanyakan apa saja 😊",
                               "Boleh, saya siap menjawab! Apa yang ingin kamu tanyakan?"])

    return None


# ── Web search fallback ─────────────────────────────────────────────────────

def _web_search_answer(query: str) -> str | None:
    """Cari jawaban dari internet (DuckDuckGo Instant Answer + HTML snippet).
    Kembalikan teks jawaban bersih tanpa sumber, atau None jika gagal."""
    def clean_text(t: str) -> str:
        t = unescape(t)
        t = re.sub(r"<[^>]+>", "", t)
        # Hapus notasi fonetik IPA dan referensi Wikipedia
        t = re.sub(r"\(/?[ˈˌ][^)]{0,120}\)", "", t)   # (/ ˈaɪn... /) atau (ˈaɪn...)
        t = re.sub(r"/\s*[ˈˌ][^/]{0,80}/", "", t)      # / ˈaɪnstaɪn /
        t = re.sub(r"\[[^\]]{0,60}\]\s*[ⓘ]?", "", t)   # [teks fonetik] ⓘ
        t = re.sub(r"\s*[ⓘ]\s*", " ", t)
        # Hapus prefix media berita
        t = re.sub(r"^[A-Z ,\.]+,\s*[A-Za-z\.]+\s*[-–]\s*", "", t)
        # Hapus teks sumber di akhir
        t = re.sub(r"\s*[\(\[]?[Ss]umber[:\s][^\)\]]*[\)\]]?\.?\s*$", "", t)
        return re.sub(r"\s+", " ", t).strip()

    try:
        # 1. DuckDuckGo Instant Answer API
        for q in [query, query.rstrip("?") + " adalah"]:
            url = f"https://api.duckduckgo.com/?q={quote_plus(q)}&format=json&no_html=1&skip_disambig=1&kl=id-id"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urlopen(req, timeout=6).read())
            text = clean_text(data.get("AbstractText", ""))
            if len(text) > 80:
                return text
            for topic in data.get("RelatedTopics", []):
                t = clean_text(topic.get("Text", "")) if isinstance(topic, dict) else ""
                if len(t) > 80:
                    return t

        # 2. DuckDuckGo HTML search — gabungkan beberapa snippet jadi satu jawaban lengkap
        url2 = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' adalah')}&kl=id-id"
        req2 = Request(url2, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req2, timeout=6).read().decode("utf-8", errors="ignore")

        # Ambil semua snippet dari hasil pertama (satu domain)
        results = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</a>',
            html, re.S
        )
        best = ""
        for s in results[:3]:
            c = clean_text(s)
            if len(c) > len(best):
                best = c
        if len(best) > 40:
            return best

    except (URLError, Exception):
        pass
    return None


class AlandModel:
    def __init__(self):
        self.pairs: list[tuple[str, str]] = []
        self.markov: dict = {}
        self.markov_order = 2
        self.vocab: set = set()
        self.en_pairs: list[tuple[str, str]] = []  # index English pairs

    def train(self, pairs: list[tuple[str, str]]):
        self.pairs = pairs
        self.en_pairs = [(q, a) for q, a in pairs if _detect_lang(normalize(a)) == "en"]
        all_responses = [r for _, r in pairs]
        self.markov = build_markov(all_responses, self.markov_order)
        for q, a in pairs:
            self.vocab.update(tokenize(q))
            self.vocab.update(tokenize(a))
        print(f"  ✓ {len(pairs)} pasang Q&A diindeks")
        print(f"  ✓ {len(self.en_pairs)} pasang English diindeks")
        print(f"  ✓ {len(self.markov)} n-gram states dibangun")
        print(f"  ✓ Vocab size: {len(self.vocab)} kata")

    def respond(self, user_input: str) -> str:
        norm_input = normalize(user_input)

        # 0. Math handler
        math_result = _solve_math(norm_input)
        if math_result is not None:
            return math_result

        # 1. Casual / small-talk handler (sebelum dataset lookup)
        casual = _casual_response(norm_input)
        if casual:
            return casual

        # 2. Deteksi bahasa
        input_lang = _detect_lang(norm_input)

        # 3. Template matching dari dataset
        best_score = 0.0
        best_answer = None
        en_best_score = 0.0
        en_best_answer = None

        _stop = {"apa","itu","siapa","kapan","dimana","di","mana","berapa","bagaimana",
                 "jelaskan","ceritakan","tentang","adalah","yang","dan","atau","dari",
                 "what","is","where","when","how","the","a","an","kamu","saya","?"}
        norm_tokens = set(tokenize(norm_input))
        info_tokens = norm_tokens - _stop

        for q, a in self.pairs:
            nq = normalize(q)
            # Exact match → skor 1.0 langsung
            if nq == norm_input:
                best_score = 1.0
                best_answer = a
                continue
            score = similarity(norm_input, nq)
            if score <= 0:
                continue
            q_tokens = set(tokenize(nq))
            q_info = q_tokens - _stop
            if info_tokens and q_info:
                info_overlap = len(info_tokens & q_info) / max(len(info_tokens), len(q_info))
                if info_overlap == 0:
                    # Token informatif sama sekali tidak cocok — penalti besar
                    score = score * 0.1
                else:
                    score = score * (0.5 + 0.5 * info_overlap)
            elif info_tokens and not q_info:
                score = score * 0.3
            if score > best_score:
                best_score = score
                best_answer = a

        if input_lang == "en":
            for q, a in self.en_pairs:
                score = similarity(norm_input, normalize(q))
                if score > en_best_score:
                    en_best_score = score
                    en_best_answer = a

        if input_lang == "en" and en_best_score >= 0.4 and en_best_answer:
            return en_best_answer

        if best_score >= 0.5 and best_answer:
            return best_answer

        # 4. Fallback — jangan pakai Markov (terlalu noise)
        if best_score >= 0.45 and best_answer:
            return best_answer

        # 5. Web search fallback — hanya untuk pertanyaan informatif (ada info_tokens)
        # Guard: jika info_tokens hanya berisi kata tanya/generik tanpa topik nyata, minta klarifikasi
        _generic = {"artinya","arti","maksud","maksudnya","jelaskan","ceritakan",
                    "meaning","means","define","definition","explain"}
        if info_tokens and not (info_tokens <= _generic):
            web_answer = _web_search_answer(user_input)
            if web_answer:
                web_answer = unescape(web_answer)
                self.pairs.append((user_input, web_answer))
                if _detect_lang(normalize(web_answer)) == "en":
                    self.en_pairs.append((user_input, web_answer))
                self.vocab.update(tokenize(user_input))
                self.vocab.update(tokenize(web_answer))
                if MODEL_FILE.exists():
                    self.save(MODEL_FILE)
                return web_answer

        # Jika pertanyaan tidak lengkap (hanya kata tanya tanpa topik)
        if not info_tokens or (info_tokens <= _generic):
            return "Maksud kamu apa? Coba tanyakan lebih lengkap, misalnya: 'Apa artinya serendipity?' 😊"

        return "Maaf, saya belum punya informasi tentang itu. Coba tanyakan hal lain? 😊"

    def save(self, path: Path):
        with open(path, "wb") as f:
            pickle.dump({
                "pairs": self.pairs,
                "en_pairs": self.en_pairs,
                "markov": self.markov,
                "markov_order": self.markov_order,
                "vocab": self.vocab,
            }, f)

    @classmethod
    def load(cls, path: Path) -> "AlandModel":
        with open(path, "rb") as f:
            data = pickle.load(f)
        m = cls()
        m.pairs = data["pairs"]
        m.en_pairs = data.get("en_pairs", [])
        m.markov = data["markov"]
        m.markov_order = data["markov_order"]
        m.vocab = data["vocab"]
        return m

# ── Incremental update ──────────────────────────────────────────────────────
def update_model(new_pairs: list[tuple[str, str]]):
    """Tambah pairs baru ke model yang sudah ada tanpa retrain penuh."""
    if not MODEL_FILE.exists():
        print("❌ Model belum ada. Jalankan train dulu.")
        return
    print(f"📂 Memuat model existing...")
    model = AlandModel.load(MODEL_FILE)
    print(f"  Model lama: {len(model.pairs)} pairs")

    model.pairs.extend(new_pairs)
    # Update en_pairs
    for q, a in new_pairs:
        if _detect_lang(normalize(a)) == "en":
            model.en_pairs.append((q, a))
    # Update vocab
    for q, a in new_pairs:
        model.vocab.update(tokenize(q))
        model.vocab.update(tokenize(a))
    # Update markov dengan teks baru
    new_texts = [a for _, a in new_pairs]
    new_markov = build_markov(new_texts, model.markov_order)
    for k, v in new_markov.items():
        if k in model.markov:
            model.markov[k].extend(v)
        else:
            model.markov[k] = v

    print(f"  Model baru: {len(model.pairs)} pairs (+{len(new_pairs)})")
    print(f"  English pairs: {len(model.en_pairs)}")
    model.save(MODEL_FILE)
    size_kb = MODEL_FILE.stat().st_size // 1024
    print(f"✓ Model diupdate: {MODEL_FILE} ({size_kb}KB)")

# ── Auto-train dari internet ────────────────────────────────────────────────

AUTO_TOPICS = [
    # Teknologi & sains
    "apa itu artificial intelligence", "apa itu machine learning", "apa itu blockchain",
    "apa itu quantum computing", "apa itu 5G", "apa itu metaverse",
    # Indonesia
    "sejarah Indonesia", "apa itu Pancasila", "tokoh pahlawan Indonesia",
    "wisata Indonesia", "makanan khas Indonesia",
    # Dunia
    "apa itu PBB", "apa itu NATO", "apa itu G20", "apa itu ASEAN",
    # Sains populer
    "apa itu DNA", "apa itu black hole", "apa itu climate change",
    # Tokoh
    "siapa Albert Einstein", "siapa Nikola Tesla", "siapa Marie Curie",
]

def auto_train_from_web(topics: list[str] | None = None, verbose: bool = True) -> int:
    """Cari topik dari internet dan langsung update model. Kembalikan jumlah topik berhasil."""
    if not MODEL_FILE.exists():
        print("❌ Model belum ada. Jalankan train dulu.")
        return 0

    topics = topics or AUTO_TOPICS
    new_pairs: list[tuple[str, str]] = []

    for topic in topics:
        answer = _web_search_answer(topic)
        if answer:
            from html import unescape
            answer = unescape(answer)
            new_pairs.append((topic, answer))
            if verbose:
                print(f"  ✓ {topic[:50]}")
        else:
            if verbose:
                print(f"  ✗ {topic[:50]} (tidak ditemukan)")

    if new_pairs:
        update_model(new_pairs)
        if verbose:
            print(f"\n✓ {len(new_pairs)}/{len(topics)} topik berhasil ditambahkan ke model.")
    return len(new_pairs)


def auto_train_loop(interval_seconds: int = 3600):
    """Jalankan auto_train_from_web secara berkala di background."""
    import time
    print(f"🔄 Auto-train loop aktif (interval: {interval_seconds//60} menit). Ctrl+C untuk berhenti.")
    while True:
        print(f"\n[{__import__('datetime').datetime.now().strftime('%H:%M:%S')}] Mulai auto-train...")
        count = auto_train_from_web(verbose=False)
        print(f"  ✓ {count} topik diperbarui.")
        time.sleep(interval_seconds)


def train():
    print("=" * 55)
    print("  aland-ai Trainer v2 — Local Training")
    print("=" * 55)
    print(f"\n⚙  Dataset : {DATASET}")
    print(f"⚙  Output  : {MODEL_FILE}\n")

    print("📚 Memuat dataset...")
    pairs = load_pairs()
    print(f"✓ {len(pairs)} sampel percakapan dimuat\n")

    print("🚀 Melatih model...")
    model = AlandModel()
    model.train(pairs)

    print("\n💾 Menyimpan model...")
    model.save(MODEL_FILE)
    size_kb = MODEL_FILE.stat().st_size // 1024
    print(f"✓ Model disimpan: {MODEL_FILE} ({size_kb}KB)")

    print("\n" + "=" * 55)
    print("  Training selesai! 🎉")
    print("=" * 55)
    print(f"\nCara pakai:")
    print(f"  python3 train.py chat          # Test di terminal")
    print(f"  aland-ai serve                 # Jalankan server")
    print(f"  # Pilih model 'aland-id' di web chat")

# ── Quick chat test ─────────────────────────────────────────────────────────
def quick_chat():
    if not MODEL_FILE.exists():
        print("❌ Model belum ditraining. Jalankan: python3 train.py train")
        sys.exit(1)

    print(f"💬 Memuat model dari {MODEL_FILE}...")
    model = AlandModel.load(MODEL_FILE)
    print("✓ Model siap! (ketik 'exit' untuk keluar)\n")

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user or user.lower() in ("exit", "quit", "/bye"):
            break
        print(f"\nALand-AI: {model.respond(user)}\n")

# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "train":
        train()
    elif cmd == "chat":
        quick_chat()
    elif cmd == "autotrain":
        if "--loop" in sys.argv:
            auto_train_loop()
        else:
            print("🌐 Auto-train dari internet...")
            auto_train_from_web()
    else:
        print("Perintah: python3 train.py [train|chat|autotrain|autotrain --loop]")
