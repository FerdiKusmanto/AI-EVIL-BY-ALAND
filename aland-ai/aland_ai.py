"""
aland-ai — Local AI runtime (seperti Ollama)
Menjalankan model GGUF via llama-cpp-python
"""

import os
import re
import json
import time
import argparse
import threading
import urllib.request
from pathlib import Path
from typing import Iterator

# ── Paths ──────────────────────────────────────────────────────────────────
HOME = Path.home() / ".aland-ai"
MODELS_DIR = HOME / "models"
CONFIG_FILE = HOME / "config.json"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {"host": "127.0.0.1", "port": 11435}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    return DEFAULT_CONFIG

# ── Model registry (nama → URL download GGUF) ──────────────────────────────
MODEL_REGISTRY = {
    "tinyllama": {
        "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "size": "669MB",
        "desc": "TinyLlama 1.1B — sangat ringan, cepat",
    },
    "phi3-mini": {
        "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
        "size": "2.2GB",
        "desc": "Microsoft Phi-3 Mini — pintar untuk ukurannya",
    },
    "llama3.2": {
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "size": "2.0GB",
        "desc": "Meta Llama 3.2 3B — bagus untuk chat",
    },
    "mistral": {
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size": "4.1GB",
        "desc": "Mistral 7B — bagus untuk coding & reasoning",
    },
    "qwen2.5": {
        "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
        "size": "2.0GB",
        "desc": "Qwen 2.5 3B — bagus bahasa Indonesia",
    },
}

def model_path(name: str) -> Path:
    # Cek model hasil training lokal dulu
    local = MODELS_DIR / f"{name}.aland-model"
    if local.exists():
        return local
    info = MODEL_REGISTRY.get(name)
    if info:
        filename = info["url"].split("/")[-1]
        return MODELS_DIR / filename
    for f in MODELS_DIR.glob("*.gguf"):
        if name.lower() in f.name.lower():
            return f
    return MODELS_DIR / f"{name}.gguf"

def list_models() -> list[dict]:
    models = []
    # Model hasil training (.aland-model)
    for f in sorted(MODELS_DIR.glob("*.aland-model")):
        size_kb = f.stat().st_size // 1024
        models.append({
            "name": f.stem,
            "file": f.name,
            "size": f"{size_kb}KB",
            "modified": time.strftime("%Y-%m-%d", time.localtime(f.stat().st_mtime)),
        })
    # Model GGUF
    for f in sorted(MODELS_DIR.glob("*.gguf")):
        size_mb = f.stat().st_size // (1024 * 1024)
        short_name = f.stem
        for k, v in MODEL_REGISTRY.items():
            if v["url"].split("/")[-1] == f.name:
                short_name = k
                break
        models.append({
            "name": short_name,
            "file": f.name,
            "size": f"{size_mb}MB",
            "modified": time.strftime("%Y-%m-%d", time.localtime(f.stat().st_mtime)),
        })
    return models

# ── Download ────────────────────────────────────────────────────────────────
def pull_model(name: str):
    # Support format "username/repo" atau "username/repo/file.gguf" dari HuggingFace
    if "/" in name:
        parts = name.split("/")
        if len(parts) == 2:
            hf_user, hf_repo = parts
            api_url = f"https://huggingface.co/api/models/{hf_user}/{hf_repo}"
            try:
                with urllib.request.urlopen(api_url) as r:
                    meta = json.loads(r.read())
                gguf_files = [s["rfilename"] for s in meta.get("siblings", [])
                              if s["rfilename"].endswith(".gguf")]
                if not gguf_files:
                    print(f"❌ Tidak ada file .gguf di {name}")
                    return
                chosen = next((f for f in gguf_files if "q4_k_m" in f.lower()), gguf_files[0])
                url = f"https://huggingface.co/{hf_user}/{hf_repo}/resolve/main/{chosen}"
                dest = MODELS_DIR / chosen
                model_display = chosen
            except Exception as e:
                print(f"❌ Gagal ambil info dari HuggingFace: {e}")
                return
        elif len(parts) == 3:
            hf_user, hf_repo, filename = parts
            url = f"https://huggingface.co/{hf_user}/{hf_repo}/resolve/main/{filename}"
            dest = MODELS_DIR / filename
            model_display = filename
        else:
            print(f"❌ Format: aland-ai pull username/repo  atau  username/repo/file.gguf")
            return

        if dest.exists():
            print(f"✓ Model sudah ada di {dest}")
            return
        print(f"⬇  Mengunduh {model_display} dari HuggingFace...")
        print(f"   {url}\n")

        def _hf_progress(count, block_size, total_size):
            if total_size > 0:
                pct = min(count * block_size * 100 // total_size, 100)
                done = pct // 2
                mb_done = min(count * block_size, total_size) // (1024*1024)
                mb_total = total_size // (1024*1024)
                print(f"\r   [{'█'*done}{'░'*(50-done)}] {pct}% ({mb_done}/{mb_total}MB)", end="", flush=True)

        try:
            urllib.request.urlretrieve(url, dest, _hf_progress)
            print(f"\n✓ Selesai! Jalankan: aland-ai run {dest.stem}")
        except Exception as e:
            if dest.exists(): dest.unlink()
            print(f"\n❌ Gagal: {e}")
        return

    if name not in MODEL_REGISTRY:
        print(f"❌ Model '{name}' tidak ditemukan di registry.")
        print(f"   Model tersedia: {', '.join(MODEL_REGISTRY.keys())}")
        print(f"   Atau: aland-ai pull username/repo-huggingface")
        return

    info = MODEL_REGISTRY[name]
    dest = MODELS_DIR / info["url"].split("/")[-1]

    if dest.exists():
        print(f"✓ Model '{name}' sudah ada di {dest}")
        return

    print(f"⬇  Mengunduh {name} ({info['size']})...")
    print(f"   {info['desc']}")
    print(f"   Dari: {info['url']}")
    print()

    def progress_hook(count, block_size, total_size):
        if total_size > 0:
            pct = min(count * block_size * 100 // total_size, 100)
            done = pct // 2
            bar = "█" * done + "░" * (50 - done)
            mb_done = min(count * block_size, total_size) // (1024 * 1024)
            mb_total = total_size // (1024 * 1024)
            print(f"\r   [{bar}] {pct}% ({mb_done}/{mb_total}MB)", end="", flush=True)

    try:
        urllib.request.urlretrieve(info["url"], dest, progress_hook)
        print(f"\n✓ Selesai! Disimpan di: {dest}")
    except Exception as e:
        if dest.exists():
            dest.unlink()
        print(f"\n❌ Gagal mengunduh: {e}")

# ── Inference engine ────────────────────────────────────────────────────────
_loaded_models: dict = {}
_model_mtimes: dict = {}
_model_lock = threading.Lock()

def get_llm(name: str):
    path = model_path(name)
    if not path.exists():
        raise FileNotFoundError(
            f"Model '{name}' tidak ditemukan.\n"
            f"Jalankan: aland-ai train  atau  aland-ai pull {name}"
        )

    with _model_lock:
        # Reload jika file model berubah di disk (misal setelah auto-learn)
        mtime = path.stat().st_mtime
        if name in _loaded_models and _model_mtimes.get(name) != mtime:
            del _loaded_models[name]

        if name not in _loaded_models:
            if path.suffix == ".aland-model":
                # Load model hasil training lokal pakai AlandModel (punya respond() lengkap)
                import sys as _sys
                _train_dir = str(path.parent.parent.parent)  # ~/.aland-ai/../.. tidak reliable
                # Cari train.py
                import importlib.util, pathlib
                _candidates = [
                    pathlib.Path.home() / "AI EVIL BY ALAND" / "aland-ai" / "training" / "train.py",
                    pathlib.Path(__file__).parent / "training" / "train.py",
                ]
                _train_mod = None
                for _c in _candidates:
                    if _c.exists():
                        _spec = importlib.util.spec_from_file_location("train", _c)
                        _train_mod = importlib.util.module_from_spec(_spec)
                        _spec.loader.exec_module(_train_mod)
                        break
                if _train_mod:
                    print(f"⚙  Memuat model lokal {name}...", flush=True)
                    _loaded_models[name] = _train_mod.AlandModel.load(path)
                    _loaded_models[name].is_local = True
                else:
                    # Fallback: load manual
                    import pickle
                    print(f"⚙  Memuat model lokal {name} (fallback)...", flush=True)
                    with open(path, "rb") as f:
                        data = pickle.load(f)
                    class LocalModel:
                        def __init__(self, d):
                            self.pairs = d["pairs"]
                            self.en_pairs = d.get("en_pairs", [])
                            self.markov = d["markov"]
                            self.markov_order = d["markov_order"]
                            self.vocab = d["vocab"]
                            self.is_local = True
                        def respond(self, text):
                            return "Maaf, modul training tidak ditemukan."
                    _loaded_models[name] = LocalModel(data)
            else:
                try:
                    from llama_cpp import Llama
                except ImportError:
                    raise RuntimeError("pip install llama-cpp-python")
                print(f"⚙  Memuat model {name}...", flush=True)
                _loaded_models[name] = Llama(
                    model_path=str(path),
                    n_ctx=4096,
                    n_threads=os.cpu_count(),
                    verbose=False,
                )
            print(f"✓ Model {name} siap", flush=True)
            _model_mtimes[name] = path.stat().st_mtime
    return _loaded_models[name]

def _local_respond(model, user_input: str) -> str:
    """Inference untuk model .aland-model — delegasi ke model.respond()"""
    # model adalah AlandModel dari train.py yang sudah punya semua fix
    if hasattr(model, "respond"):
        return model.respond(user_input)
    return "Maaf, saya belum bisa menjawab."

def _search_internet(question: str) -> str | None:
    """Cari jawaban dari multiple sumber internet, kumpulkan sebanyak mungkin."""
    import urllib.request, urllib.parse, json, re

    headers = {"User-Agent": "ALand-AI/1.0"}

    def fetch(url, timeout=4):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception:
            return None

    def clean(text, max_len=400):
        from html import unescape as _unescape
        text = _unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Hapus notasi fonetik IPA
        text = re.sub(r"/\s*[ˈˌ][^/]{0,80}/", "", text)
        text = re.sub(r"\(/?[ˈˌ][^)]{0,120}\)", "", text)
        text = re.sub(r"\[[^\]]{0,60}\]\s*[ⓘ]?", "", text)
        text = re.sub(r"\s*[ⓘ]\s*", " ", text)
        # Hapus prefix media berita
        text = re.sub(r"^[A-Z ,\.]+,\s*[A-Za-z\.]+\s*[-–]\s*", "", text)
        # Hapus teks sumber
        text = re.sub(r"\s*[\(\[]?[Ss]umber[:\s][^\)\]]*[\)\]]?\.?\s*$", "", text)
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = ""
        for s in sentences:
            result += (" " if result else "") + s
            if len(result) >= 120:
                break
        return result[:max_len]

    stop = {"apa","itu","siapa","kapan","dimana","di","mana","berapa","bagaimana",
            "jelaskan","ceritakan","tentang","adalah","yang","dan","atau","dari",
            "what","is","who","where","when","how","tell","me","about","the","a","an"}
    words = re.findall(r'\w+', question.lower())
    keywords = " ".join(w for w in words if w not in stop and len(w) > 2)
    if not keywords:
        keywords = question
    kw_enc = urllib.parse.quote(keywords)

    answers = []  # kumpulkan semua jawaban dari semua sumber

    # ── Sumber 1: DuckDuckGo Instant Answer API ──────────────────────────
    try:
        ddg = fetch(f"https://api.duckduckgo.com/?q={kw_enc}&format=json&no_html=1&skip_disambig=1")
        if ddg:
            abstract = ddg.get("AbstractText", "").strip()
            if abstract and len(abstract) > 30:
                answers.append(clean(abstract))
            # Related topics
            for topic in ddg.get("RelatedTopics", [])[:3]:
                text = topic.get("Text", "").strip() if isinstance(topic, dict) else ""
                if text and len(text) > 30:
                    answers.append(clean(text, 200))
    except Exception:
        pass

    # ── Sumber 2: Wikipedia Bahasa Indonesia ─────────────────────────────
    for lang in ["id", "en"]:
        try:
            search = fetch(f"https://{lang}.wikipedia.org/w/api.php?"
                           f"action=query&list=search&srsearch={kw_enc}"
                           f"&format=json&srlimit=3&utf8=1")
            if not search:
                continue
            results = search.get("query", {}).get("search", [])
            for r in results[:2]:
                title = r["title"]
                detail = fetch(f"https://{lang}.wikipedia.org/w/api.php?"
                               f"action=query&prop=extracts&exintro=1&explaintext=1"
                               f"&titles={urllib.parse.quote(title)}&format=json&utf8=1")
                if not detail:
                    continue
                for page in detail.get("query", {}).get("pages", {}).values():
                    extract = page.get("extract", "").strip()
                    if extract and len(extract) > 50:
                        answers.append(clean(extract))
        except Exception:
            continue

    # ── Sumber 3: Wikidata description ───────────────────────────────────
    try:
        wd = fetch(f"https://www.wikidata.org/w/api.php?"
                   f"action=wbsearchentities&search={kw_enc}"
                   f"&language=id&format=json&limit=3")
        if wd:
            for item in wd.get("search", [])[:3]:
                desc = item.get("description", "").strip()
                label = item.get("label", "").strip()
                if desc and len(desc) > 10:
                    answers.append(f"{label} adalah {desc}." if label else desc)
    except Exception:
        pass

    if not answers:
        return None

    # Deduplikasi & ambil jawaban terbaik (terpanjang & paling informatif)
    seen, unique = set(), []
    for a in answers:
        key = a[:60].lower()
        if key not in seen and len(a) > 20:
            seen.add(key)
            unique.append(a)

    # Return jawaban pertama (terpanjang/terbaik) — tanpa label sumber
    best = max(unique, key=len)
    return best, unique  # (jawaban utama, semua jawaban untuk disimpan)


def _learn(model, question: str, answer: str):
    """Simpan pasangan Q&A baru ke model secara realtime."""
    import re, threading, json
    from pathlib import Path

    q, a = question.strip(), answer.strip()
    if not q or not a or len(a) < 5:
        return
    # Jangan simpan jawaban fallback, identitas AI, atau jawaban tidak relevan
    skip_answers = ["maaf, saya belum", "coba tanyakan hal lain", "tidak bisa menjawab",
                    "nama saya aland-ai", "saya aland-ai",
                    "tujuan pembuatan artikel", "cara membuat artikel",
                    "gunakan tombol panah", "layanan google"]
    identity_q = ["siapa kamu", "kamu siapa", "nama kamu", "who are you", "your name"]
    a_low, q_low = a.lower(), q.lower()
    if any(s in a_low for s in skip_answers):
        if not any(iq in q_low for iq in identity_q):
            return

    # Tambah ke model in-memory
    model.pairs.append((q, a))
    def _tok(t): return re.findall(r'\w+|[^\w\s]', t.lower())
    en_words = {"what","is","are","the","a","an","how","why","who","where","when","which","does","do","can"}
    if len(set(_tok(a)) & en_words) >= 2:
        model.en_pairs.append((q, a))
    for tok in _tok(q) + _tok(a):
        model.vocab.add(tok)

    # Append ke dataset JSONL
    dataset = Path.home() / "AI EVIL BY ALAND" / "aland-ai" / "training" / "dataset.jsonl"
    if dataset.exists():
        with open(dataset, "a", encoding="utf-8") as f:
            f.write(json.dumps({"messages": [
                {"role": "user", "content": q},
                {"role": "assistant", "content": a}
            ]}, ensure_ascii=False) + "\n")

    # Simpan model di background
    def _save():
        try:
            import pickle, os
            from pathlib import Path as P
            path = P.home() / ".aland-ai" / "models" / "aland-id.aland-model"
            tmp = str(path) + ".tmp"
            with open(tmp, "wb") as f:
                pickle.dump({
                    "pairs": model.pairs, "en_pairs": model.en_pairs,
                    "markov": model.markov, "markov_order": model.markov_order,
                    "vocab": model.vocab,
                }, f)
            os.replace(tmp, path)
        except Exception:
            pass
    threading.Thread(target=_save, daemon=True).start()


def messages_to_prompt(messages: list[dict], model_name: str = "") -> str:
    """Format messages ke prompt string sesuai model."""
    result = ""
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "system":
            result += f"<|system|>\n{content}\n"
        elif role == "user":
            result += f"<|user|>\n{content}\n<|assistant|>\n"
        elif role == "assistant":
            result += f"{content}\n"
    return result

def _resolve_reference(user_input: str, messages: list[dict]) -> str:
    """Ganti pronoun/referensi ('nya', 'itu', 'dia') dengan topik dari history."""
    # Kata utuh yang kebetulan berakhiran "nya" — bukan suffix referensi
    _NYA_EXCEPTIONS = {"tanya", "hanya", "anya", "unya", "sanya", "ranya",
                       "lanya", "kanya", "panya", "manya", "banya", "danya",
                       "ganya", "wanya", "nanya", "anya"}

    def _has_nya_suffix(text: str) -> bool:
        for m in re.finditer(r'\b\w+nya\b', text, re.I):
            if m.group(0).lower() not in _NYA_EXCEPTIONS:
                return True
        return False

    # Deteksi kata referensi: standalone atau suffix "nya" (membuatnya, harganya, dll)
    has_ref = bool(re.search(r'\b(itu|dia|mereka|tersebut|tadi|it|they|them|that)\b', user_input, re.I)
                   or _has_nya_suffix(user_input))
    if not has_ref:
        return user_input

    # Cari topik terakhir dari history
    stop = {"apa","itu","siapa","kapan","dimana","di","mana","berapa","bagaimana",
            "jelaskan","ceritakan","tentang","adalah","yang","dan","atau","dari",
            "what","is","where","when","how","the","a","an","?","cara","gimana",
            "tolong","bisa","boleh","maksud","artinya"}
    last_topic = ""
    for m in reversed(messages[:-1]):
        if m["role"] == "user":
            words = [w for w in m["content"].lower().split() if w not in stop and len(w) > 2]
            if words:
                last_topic = " ".join(words[:3])
                break
        elif m["role"] == "assistant" and not last_topic:
            words = [w for w in m["content"].lower().split() if w not in stop and len(w) > 3]
            if words:
                last_topic = words[0]

    if last_topic:
        # Ganti suffix "nya" pada kata kerja/benda dengan "topik" — skip kata pengecualian
        def _replace_nya(m):
            full = m.group(0).lower()
            if full in _NYA_EXCEPTIONS:
                return m.group(0)
            return m.group(1) + " " + last_topic
        resolved = re.sub(r'(\w+)nya\b', _replace_nya, user_input, flags=re.I)
        # Ganti "itu/tersebut" hanya jika tidak ada topik baru di kalimat
        topic_words = set(last_topic.lower().split())
        input_words = set(re.findall(r'\w+', user_input.lower())) - stop
        has_new_topic = bool(input_words - topic_words - {"nya","itu","dia","tersebut","tadi"})
        if not has_new_topic:
            resolved = re.sub(r'\b(itu|tersebut|tadi|it|that|them|they)\b', last_topic, resolved, flags=re.I)
        return resolved
    return user_input


def chat_stream(model_name: str, messages: list[dict]) -> Iterator[str]:
    llm = get_llm(model_name)

    if getattr(llm, "is_local", False):
        user_input = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_input = m["content"]
                break

        # Resolusi referensi menggunakan history
        user_input = _resolve_reference(user_input, messages)

        response = _local_respond(llm, user_input)

        # Jika tidak tahu → cari dari internet
        if "belum punya informasi" in response or "belum bisa menjawab" in response:
            result = _search_internet(user_input)
            if result:
                best, all_answers = result
                response = best
                # Simpan SEMUA jawaban dari internet ke model
                for ans in all_answers:
                    _learn(llm, user_input, ans)
                # Skip _learn di bawah (sudah disimpan)
                for word in response.split(" "):
                    yield word + " "
                return

        # Realtime learning — simpan ke model
        _learn(llm, user_input, response)

        for word in response.split(" "):
            yield word + " "
        return

    # Model GGUF via llama.cpp
    prompt = messages_to_prompt(messages, model_name)
    stream = llm(
        prompt,
        max_tokens=2048,
        temperature=0.7,
        stop=["<|user|>", "<|system|>", "</s>"],
        stream=True,
    )
    for chunk in stream:
        token = chunk["choices"][0]["text"]
        if token:
            yield token

# ── REST API Server ─────────────────────────────────────────────────────────
def run_server(host: str, port: int):
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # suppress default logs

        def send_json(self, data: dict, status=200):
            body = json.dumps(data).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", len(body))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except BrokenPipeError:
                pass

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            if self.path == "/api/tags":
                models = list_models()
                self.send_json({"models": [
                    {"name": m["name"], "size": m["size"], "modified_at": m["modified"]}
                    for m in models
                ]})
            elif self.path == "/":
                self.send_json({"name": "aland-ai", "version": "1.0.0"})
            else:
                self.send_json({"error": "not found"}, 404)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            if self.path == "/api/chat":
                model = body.get("model", "")
                messages = body.get("messages", [])
                stream = body.get("stream", True)

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    try:
                        for token in chat_stream(model, messages):
                            chunk = {
                                "model": model,
                                "message": {"role": "assistant", "content": token},
                                "done": False,
                            }
                            self.wfile.write((json.dumps(chunk) + "\n").encode())
                            self.wfile.flush()
                        done_chunk = {"model": model, "message": {"role": "assistant", "content": ""}, "done": True}
                        self.wfile.write((json.dumps(done_chunk) + "\n").encode())
                    except BrokenPipeError:
                        pass  # client disconnect — normal, abaikan
                    except Exception as e:
                        try:
                            self.wfile.write((json.dumps({"error": str(e), "done": True}) + "\n").encode())
                        except BrokenPipeError:
                            pass
                else:
                    try:
                        full = "".join(chat_stream(model, messages))
                        self.send_json({
                            "model": model,
                            "message": {"role": "assistant", "content": full},
                            "done": True,
                        })
                    except Exception as e:
                        self.send_json({"error": str(e)}, 500)

            elif self.path == "/api/generate":
                model = body.get("model", "")
                prompt = body.get("prompt", "")
                messages = [{"role": "user", "content": prompt}]
                stream = body.get("stream", True)

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    try:
                        for token in chat_stream(model, messages):
                            self.wfile.write((json.dumps({"response": token, "done": False}) + "\n").encode())
                            self.wfile.flush()
                        self.wfile.write((json.dumps({"response": "", "done": True}) + "\n").encode())
                    except BrokenPipeError:
                        pass  # client disconnect — normal, abaikan
                    except Exception as e:
                        try:
                            self.wfile.write((json.dumps({"error": str(e), "done": True}) + "\n").encode())
                        except BrokenPipeError:
                            pass
                else:
                    try:
                        full = "".join(chat_stream(model, messages))
                        self.send_json({"response": full, "done": True})
                    except Exception as e:
                        self.send_json({"error": str(e)}, 500)
            else:
                self.send_json({"error": "not found"}, 404)

    server = HTTPServer((host, port), Handler)
    print(f"🚀 aland-ai server berjalan di http://{host}:{port}")
    print(f"   Models dir: {MODELS_DIR}")
    print(f"   Tekan Ctrl+C untuk berhenti\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 aland-ai berhenti.")

# ── Interactive chat (CLI) ──────────────────────────────────────────────────
def run_chat(model_name: str):
    path = model_path(model_name)
    if not path.exists():
        print(f"❌ Model '{model_name}' tidak ditemukan.")
        print(f"   Jalankan: aland-ai pull {model_name}")
        return

    print(f"💬 Chat dengan {model_name} (ketik /bye untuk keluar)\n")
    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Sampai jumpa!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/bye", "/exit", "/quit"):
            print("👋 Sampai jumpa!")
            break

        history.append({"role": "user", "content": user_input})
        print(f"\n{model_name}: ", end="", flush=True)

        full = ""
        try:
            for token in chat_stream(model_name, history):
                print(token, end="", flush=True)
                full += token
        except Exception as e:
            print(f"\n❌ Error: {e}")
            history.pop()
            continue

        print("\n")
        history.append({"role": "assistant", "content": full})

# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="aland-ai",
        description="🤖 aland-ai — Local AI runtime",
    )
    sub = parser.add_subparsers(dest="command")

    # serve
    p_serve = sub.add_parser("serve", help="Jalankan API server")
    p_serve.add_argument("--host", default=None)
    p_serve.add_argument("--port", type=int, default=None)

    # run
    p_run = sub.add_parser("run", help="Chat interaktif dengan model")
    p_run.add_argument("model")

    # pull
    p_pull = sub.add_parser("pull", help="Download model")
    p_pull.add_argument("model")

    # list
    sub.add_parser("list", help="Tampilkan model yang sudah didownload")

    # models (alias list)
    sub.add_parser("models", help="Alias untuk list")

    # show
    p_show = sub.add_parser("show", help="Info model")
    p_show.add_argument("model")

    # rm
    p_rm = sub.add_parser("rm", help="Hapus model")
    p_rm.add_argument("model")

    # train
    p_train = sub.add_parser("train", help="Latih model dengan dataset bahasa Indonesia")
    p_train.add_argument("--epochs", type=int, default=3)
    p_train.add_argument("--export", action="store_true", help="Export ke GGUF setelah training")

    # autotrain
    p_autotrain = sub.add_parser("autotrain", help="Auto-train topik dari internet")
    p_autotrain.add_argument("--loop", action="store_true", help="Jalankan berkala tiap 1 jam")

    args = parser.parse_args()

    if args.command == "serve":
        cfg = load_config()
        host = args.host or cfg["host"]
        port = args.port or cfg["port"]
        run_server(host, port)

    elif args.command == "run":
        run_chat(args.model)

    elif args.command == "pull":
        pull_model(args.model)

    elif args.command in ("list", "models"):
        models = list_models()
        if not models:
            print("Belum ada model. Jalankan: aland-ai pull <nama>")
            print(f"\nModel tersedia:")
            for name, info in MODEL_REGISTRY.items():
                print(f"  {name:<15} {info['size']:<8}  {info['desc']}")
        else:
            print(f"{'NAME':<20} {'SIZE':<10} {'MODIFIED'}")
            print("-" * 45)
            for m in models:
                print(f"{m['name']:<20} {m['size']:<10} {m['modified']}")

    elif args.command == "show":
        info = MODEL_REGISTRY.get(args.model)
        path = model_path(args.model)
        if info:
            print(f"Name:     {args.model}")
            print(f"Desc:     {info['desc']}")
            print(f"Size:     {info['size']}")
            print(f"File:     {path}")
            print(f"Exists:   {'✓ Ya' if path.exists() else '✗ Belum didownload'}")
        else:
            print(f"Model '{args.model}' tidak ada di registry.")

    elif args.command == "rm":
        path = model_path(args.model)
        if path.exists():
            path.unlink()
            print(f"✓ Model '{args.model}' dihapus.")
        else:
            print(f"❌ Model '{args.model}' tidak ditemukan.")

    elif args.command == "train":
        import subprocess, sys as _sys
        train_script = Path(__file__).parent / "training" / "train.py"
        cmd = [_sys.executable, str(train_script), "train", str(args.epochs)]
        subprocess.run(cmd)
        if args.export:
            subprocess.run([_sys.executable, str(train_script), "export"])

    elif args.command == "autotrain":
        import subprocess, sys as _sys
        train_script = Path(__file__).parent / "training" / "train.py"
        cmd = [_sys.executable, str(train_script), "autotrain"]
        if getattr(args, "loop", False):
            cmd.append("--loop")
        subprocess.run(cmd)

    else:
        print("🤖 aland-ai — Local AI Runtime\n")
        print("Perintah:")
        print("  aland-ai serve               Jalankan API server (port 11435)")
        print("  aland-ai run <model>         Chat interaktif")
        print("  aland-ai pull <model>        Download model")
        print("  aland-ai list                Tampilkan model lokal")
        print("  aland-ai show <model>        Info model")
        print("  aland-ai rm <model>          Hapus model")
        print("  aland-ai train [--epochs N]  Latih model bahasa Indonesia")
        print("  aland-ai train --export      Latih + export ke GGUF")
        print("  aland-ai autotrain           Auto-train topik dari internet (sekali)")
        print("  aland-ai autotrain --loop    Auto-train berkala (tiap 1 jam)")
        print("\nContoh:")
        print("  aland-ai pull tinyllama")
        print("  aland-ai train --epochs 5 --export")
        print("  aland-ai run aland-id")
        print("  aland-ai serve")

if __name__ == "__main__":
    main()
