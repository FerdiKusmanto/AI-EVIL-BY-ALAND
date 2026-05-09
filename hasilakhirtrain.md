# Laporan Perkembangan Training ALand-AI
**File:** `aland-ai/training/train.py`  
**Tanggal:** 9 Mei 2026

---

## Ringkasan

Dokumen ini mencatat seluruh perubahan yang dilakukan pada sistem training dan inferensi ALand-AI, dari kondisi awal hingga versi akhir yang berjalan saat ini.

---

## Tahap 1 — Kondisi Awal: Scoring Dasar

### Masalah
Model menggunakan similarity murni (Jaccard/token overlap) tanpa mempertimbangkan **token informatif**. Akibatnya:

- "Apa itu NASA?" → dijawab dengan "Python adalah bahasa pemrograman..."
- "Apa itu FIFA?" → dijawab dengan jawaban tidak relevan
- Semua pertanyaan "Apa itu X?" punya skor yang sama karena token "apa" dan "itu" mendominasi overlap

### Kode Awal
```python
score = similarity(norm_input, nq)
if score > best_score:
    best_score = score
    best_answer = a
```

---

## Tahap 2 — Penambahan Info Token Penalty

### Perubahan
Ditambahkan logika **stopwords** untuk memisahkan token informatif dari token struktural. Skor disesuaikan berdasarkan overlap token informatif.

```python
_stop = {"apa","itu","siapa","kapan","dimana","di","mana","berapa","bagaimana",
         "jelaskan","ceritakan","tentang","adalah","yang","dan","atau","dari",
         "what","is","who","where","when","how","the","a","an","kamu","saya","?"}

info_tokens = norm_tokens - _stop

if info_tokens and q_info:
    info_overlap = len(info_tokens & q_info) / max(len(info_tokens), len(q_info))
    score = score * (0.5 + 0.5 * info_overlap)
elif info_tokens and not q_info:
    score = score * 0.3
```

### Hasil
- Pertanyaan dengan topik berbeda mulai dibedakan
- Namun masih ada kasus: "Apa itu NASA?" dan "Apa itu wayang?" mendapat skor sama (0.375) karena `info_overlap` rendah tapi tidak nol

---

## Tahap 3 — Penalti Zero-Overlap

### Masalah
`info_overlap = 0` (token informatif sama sekali tidak cocok) hanya mendapat penalti ringan dari formula `0.5 + 0.5 * 0 = 0.5`. Skor masih cukup tinggi untuk lolos threshold.

### Perubahan
Ditambahkan cabang khusus: jika `info_overlap == 0`, penalti jauh lebih besar.

```python
if info_overlap == 0:
    # Token informatif sama sekali tidak cocok — penalti besar
    score = score * 0.1
else:
    score = score * (0.5 + 0.5 * info_overlap)
```

### Hasil Test
```
Q: Apa itu NASA?  → Maaf, saya belum punya informasi tentang itu.  ✅ (tidak salah jawab)
Q: Apa itu FIFA?  → Maaf, saya belum punya informasi tentang itu.  ✅
Q: Apa itu Python? → Python adalah bahasa pemrograman...            ✅
Q: Apa itu Rendang? → Rendang adalah masakan daging sapi...         ✅
Q: Siapa Soekarno? → Soekarno adalah Presiden pertama Indonesia...  ✅
Q: Berapa 999 kali 7? → 999 * 7 = 6993                             ✅
```

**Catatan:** NASA dan FIFA fallback ke "Maaf..." karena memang tidak ada di dataset — ini **benar**.

---

## Tahap 4 — Web Search Fallback (Auto-Learn dari Internet)

### Masalah
Jika topik tidak ada di dataset, model hanya bisa menjawab "Maaf, saya belum punya informasi". Tidak ada mekanisme untuk belajar topik baru secara otomatis.

### Perubahan
Ditambahkan fungsi `_web_search_answer()` yang dipanggil saat model tidak menemukan jawaban. Hasil langsung disimpan ke model agar pertanyaan yang sama berikutnya dijawab dari cache lokal.

**Sumber pencarian (berurutan):**
1. DuckDuckGo Instant Answer API (`api.duckduckgo.com`) — hasil terstruktur, bahasa Indonesia
2. DuckDuckGo HTML search — snippet dari berbagai situs web

```python
def _web_search_answer(query: str) -> str | None:
    # Coba DuckDuckGo Instant Answer API
    for q in [query, query.rstrip("?") + " adalah"]:
        url = f"https://api.duckduckgo.com/?q={quote_plus(q)}&format=json&no_html=1&skip_disambig=1&kl=id-id"
        ...
        text = data.get("AbstractText", "").strip()
        if text and len(text) > 40:
            return text

    # Fallback: DuckDuckGo HTML snippet
    url2 = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' adalah')}&kl=id-id"
    ...
```

**Integrasi di `respond()`:**
```python
# 5. Web search fallback — hanya untuk pertanyaan informatif
if info_tokens:
    web_answer = _web_search_answer(user_input)
    if web_answer:
        web_answer = unescape(web_answer)
        self.pairs.append((user_input, web_answer))
        ...
        self.save(MODEL_FILE)  # Simpan langsung ke model
        return web_answer
```

---

## Tahap 5 — Perbaikan Kualitas Jawaban Web

### Masalah yang Ditemukan
1. **HTML entities** tidak di-decode: `NASA&#x27;s mission` → seharusnya `NASA's mission`
2. **Prefix media berita** ikut masuk: `JAKARTA, KOMPAS.com - BRICS adalah...`
3. **Teks sumber** ikut masuk: `...pebisnis Amerika Serikat. (Sumber: Wikipedia/Elon Musk)`
4. **"who"** ada di stopwords → "Apa itu WHO?" menghasilkan `info_tokens` kosong → salah jawab

### Perubahan

**a. Hapus "who" dari stopwords** (WHO adalah nama organisasi, bukan kata tanya):
```python
_stop = {"apa","itu","siapa","kapan","dimana","di","mana","berapa","bagaimana",
         "jelaskan","ceritakan","tentang","adalah","yang","dan","atau","dari",
         "what","is","where","when","how","the","a","an","kamu","saya","?"}
# "who" dihapus dari daftar ini
```

**b. Cleaning hasil web di `_web_search_answer()`:**
```python
clean = unescape(re.sub(r"<[^>]+>", "", s))          # decode HTML entities
clean = re.sub(r"^[A-Z ,\.]+,\s*[A-Za-z\.]+\s*[-–]\s*", "", clean)  # hapus prefix media
clean = re.sub(r"\s*[\(\[]?[Ss]umber[:\s][^\)\]]*[\)\]]?\.?\s*$", "", clean)  # hapus teks sumber
```

**c. Naikkan threshold fallback** dari `0.3` → `0.45` agar jawaban dengan skor rendah tidak lolos:
```python
if best_score >= 0.45 and best_answer:
    return best_answer
```

---

## Hasil Akhir

### Test Komprehensif
```
Q: Apa itu NASA?
A: Badan Penerbangan dan Antariksa Amerika Serikat (National Aeronautics and Space Administration)...  ✅

Q: Apa itu FIFA?
A: FIFA (Federation Internationale de Football Association) adalah induk organisasi sepak bola dunia...  ✅

Q: Apa itu WHO?
A: World Health Organization (WHO) didirikan pada 7 April 1948 sebagai otoritas pengarah...  ✅

Q: Apa itu BRICS?
A: BRICS adalah singkatan dari Brazil, Russia, India, China, dan South Africa...  ✅

Q: Siapa Elon Musk?
A: Elon Reeve Musk FRS (; lahir 28 Juni 1971) adalah seorang pebisnis Amerika Serikat.  ✅

Q: Apa itu Python?
A: Python adalah bahasa pemrograman yang mudah dipelajari...  ✅ (dari dataset lokal)

Q: Siapa Soekarno?
A: Soekarno adalah Presiden pertama Indonesia, proklamator kemerdekaan...  ✅ (dari dataset lokal)

Q: haii
A: Hey! Senang bertemu kamu 😄  ✅ (casual handler)

Q: Berapa 999 kali 7?
A: 999 * 7 = 6993  ✅ (math handler)
```

---

## Ringkasan Perubahan Teknis

| Tahap | Perubahan | Dampak |
|---|---|---|
| 1 | Scoring dasar (similarity murni) | Banyak jawaban salah topik |
| 2 | Info token penalty (`0.5 + 0.5 * overlap`) | Topik berbeda mulai dibedakan |
| 3 | Zero-overlap penalty (`× 0.1`) | Tidak ada lagi jawaban lintas topik |
| 4 | Web search fallback + auto-save ke model | Topik baru dipelajari otomatis dari internet |
| 5 | HTML cleaning, hapus "who" dari stopwords, threshold 0.45 | Jawaban web bersih dan akurat |

---

## Alur Respond Final

```
Input user
  │
  ├─ Math? → jawab langsung
  ├─ Casual/small-talk? → jawab langsung
  ├─ Ada di dataset (score ≥ 0.5)? → jawab dari dataset
  ├─ Ada di dataset (score ≥ 0.45)? → jawab dari dataset
  ├─ Ada info_tokens? → fetch dari internet → simpan ke model → jawab
  └─ Tidak ada sama sekali → "Maaf, saya belum punya informasi..."
```
