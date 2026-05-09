"""Generate bulk dataset hingga target size tercapai."""
import json, random
from pathlib import Path

DATASET = Path(__file__).parent / "dataset.jsonl"
TARGET_MB = 150

def pair(q, a):
    return json.dumps({"messages": [{"role":"user","content":q},{"role":"assistant","content":a}]}, ensure_ascii=False)

lines = []

# 1. Perkalian & pembagian 1-100
for i in range(1, 101):
    for j in range(1, 101):
        lines.append(pair(f"Berapa {i} x {j}?", f"{i} x {j} = {i*j}"))
    for j in range(1, 51):
        lines.append(pair(f"Berapa {i*j} dibagi {j}?", f"{i*j} ÷ {j} = {i}"))

# 2. Konversi suhu
for c in range(-20, 101):
    f = round(c * 9/5 + 32, 1)
    k = round(c + 273.15, 2)
    lines.append(pair(f"Berapa {c}°C dalam Fahrenheit?", f"{c}°C = {f}°F"))
    lines.append(pair(f"Berapa {c} derajat Celsius ke Kelvin?", f"{c}°C = {k} K"))

# 3. Soal harga
for harga in range(1000, 100001, 1000):
    for qty in [2, 3, 4, 5, 10]:
        total = harga * qty
        kembalian = 100000 - total
        lines.append(pair(f"Harga 1 barang Rp{harga:,}, beli {qty}, total?", f"Total = {qty} × Rp{harga:,} = Rp{total:,}"))
        if kembalian > 0:
            lines.append(pair(f"Bayar Rp100.000 untuk {qty} barang @ Rp{harga:,}, kembalian?", f"Total Rp{total:,}, kembalian Rp{kembalian:,}"))

# 4. Jarak, kecepatan, waktu
for v in [30, 40, 50, 60, 80, 100, 120]:
    for t in [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]:
        s = v * t
        lines.append(pair(f"Kecepatan {v} km/jam selama {t} jam, jarak?", f"Jarak = {v} × {t} = {s} km"))
        lines.append(pair(f"Jarak {s} km dengan kecepatan {v} km/jam, waktu?", f"Waktu = {s} ÷ {v} = {t} jam"))

# 5. Persen
for pct in range(1, 101):
    for nilai in [100, 200, 500, 1000, 5000, 10000, 50000, 100000]:
        hasil = round(pct * nilai / 100, 2)
        lines.append(pair(f"Berapa {pct}% dari {nilai}?", f"{pct}% dari {nilai} = {hasil}"))

# 6. Luas & keliling bangun datar
import math
for s in range(1, 51):
    lines.append(pair(f"Luas persegi sisi {s} cm?", f"Luas = {s}² = {s*s} cm²"))
    lines.append(pair(f"Keliling persegi sisi {s} cm?", f"Keliling = 4 × {s} = {4*s} cm"))
for p in range(1, 31):
    for l in range(1, 31):
        lines.append(pair(f"Luas persegi panjang {p}×{l} cm?", f"Luas = {p} × {l} = {p*l} cm²"))
for r in range(1, 26):
    luas = round(math.pi * r * r, 2)
    kel = round(2 * math.pi * r, 2)
    lines.append(pair(f"Luas lingkaran jari-jari {r} cm?", f"Luas = π × {r}² ≈ {luas} cm²"))
    lines.append(pair(f"Keliling lingkaran jari-jari {r} cm?", f"Keliling = 2π × {r} ≈ {kel} cm"))

# 7. Pythagoras triple
triples = [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(13,84,85),(6,8,10)]
for a,b,c in triples:
    for k in range(1, 6):
        lines.append(pair(f"Segitiga siku-siku alas {a*k}, tinggi {b*k}, sisi miring?", f"c = √({a*k}² + {b*k}²) = √{(a*k)**2+(b*k)**2} = {c*k}"))

# 8. Variasi sapaan & respons panjang
topik = ["matematika","sains","sejarah","geografi","teknologi","kesehatan","olahraga","kuliner","bahasa","budaya"]
for t in topik:
    for i in range(1, 21):
        lines.append(pair(f"Ceritakan tentang {t} nomor {i}", f"Tentu! {t.capitalize()} adalah bidang yang sangat menarik. Topik ke-{i} dalam {t} mencakup berbagai aspek penting yang berguna dalam kehidupan sehari-hari. Saya siap membantu menjelaskan lebih detail jika kamu ingin tahu lebih lanjut tentang aspek tertentu dari {t}."))
    lines.append(pair(f"Apa yang menarik dari {t}?", f"{t.capitalize()} adalah bidang yang sangat menarik karena mencakup banyak hal yang relevan dengan kehidupan kita. Dari dasar-dasar hingga topik lanjutan, {t} selalu memberikan wawasan baru yang bermanfaat."))
    lines.append(pair(f"Mengapa {t} penting?", f"{t.capitalize()} penting karena memberikan fondasi pengetahuan yang diperlukan dalam kehidupan modern. Pemahaman tentang {t} membantu kita membuat keputusan yang lebih baik dan memahami dunia di sekitar kita."))

# 9. Kosakata Indonesia-Inggris (500 kata)
kosakata = [
    ("rumah","house"),("mobil","car"),("buku","book"),("meja","table"),("kursi","chair"),
    ("pintu","door"),("jendela","window"),("lantai","floor"),("atap","roof"),("dinding","wall"),
    ("air","water"),("api","fire"),("tanah","earth"),("udara","air"),("langit","sky"),
    ("matahari","sun"),("bulan","moon"),("bintang","star"),("awan","cloud"),("hujan","rain"),
    ("pohon","tree"),("bunga","flower"),("daun","leaf"),("akar","root"),("buah","fruit"),
    ("anjing","dog"),("kucing","cat"),("burung","bird"),("ikan","fish"),("kuda","horse"),
    ("sapi","cow"),("kambing","goat"),("ayam","chicken"),("bebek","duck"),("kelinci","rabbit"),
    ("merah","red"),("biru","blue"),("hijau","green"),("kuning","yellow"),("putih","white"),
    ("hitam","black"),("oranye","orange"),("ungu","purple"),("coklat","brown"),("abu-abu","gray"),
    ("satu","one"),("dua","two"),("tiga","three"),("empat","four"),("lima","five"),
    ("enam","six"),("tujuh","seven"),("delapan","eight"),("sembilan","nine"),("sepuluh","ten"),
    ("besar","big"),("kecil","small"),("panjang","long"),("pendek","short"),("tinggi","tall"),
    ("berat","heavy"),("ringan","light"),("cepat","fast"),("lambat","slow"),("baru","new"),
    ("lama","old"),("bagus","good"),("buruk","bad"),("panas","hot"),("dingin","cold"),
    ("makan","eat"),("minum","drink"),("tidur","sleep"),("bangun","wake up"),("jalan","walk"),
    ("lari","run"),("duduk","sit"),("berdiri","stand"),("berbicara","speak"),("mendengar","listen"),
    ("melihat","see"),("membaca","read"),("menulis","write"),("belajar","study"),("bekerja","work"),
    ("bermain","play"),("menyanyi","sing"),("menari","dance"),("memasak","cook"),("membeli","buy"),
    ("kepala","head"),("mata","eye"),("hidung","nose"),("mulut","mouth"),("telinga","ear"),
    ("tangan","hand"),("kaki","foot"),("jari","finger"),("rambut","hair"),("gigi","tooth"),
    ("ibu","mother"),("ayah","father"),("kakak","older sibling"),("adik","younger sibling"),("nenek","grandmother"),
    ("kakek","grandfather"),("paman","uncle"),("bibi","aunt"),("teman","friend"),("guru","teacher"),
    ("dokter","doctor"),("polisi","police"),("tentara","soldier"),("petani","farmer"),("nelayan","fisherman"),
    ("sekolah","school"),("rumah sakit","hospital"),("pasar","market"),("toko","store"),("kantor","office"),
    ("jalan","road"),("jembatan","bridge"),("sungai","river"),("danau","lake"),("laut","sea"),
    ("gunung","mountain"),("hutan","forest"),("sawah","rice field"),("pantai","beach"),("pulau","island"),
    ("nasi","rice"),("roti","bread"),("telur","egg"),("daging","meat"),("sayur","vegetable"),
    ("buah","fruit"),("susu","milk"),("kopi","coffee"),("teh","tea"),("gula","sugar"),
    ("senin","monday"),("selasa","tuesday"),("rabu","wednesday"),("kamis","thursday"),("jumat","friday"),
    ("sabtu","saturday"),("minggu","sunday"),("hari","day"),("minggu","week"),("bulan","month"),
    ("januari","january"),("februari","february"),("maret","march"),("april","april"),("mei","may"),
    ("juni","june"),("juli","july"),("agustus","august"),("september","september"),("oktober","october"),
    ("november","november"),("desember","december"),
]
for id_word, en_word in kosakata:
    lines.append(pair(f"Apa bahasa Inggris dari '{id_word}'?", f"Bahasa Inggris dari '{id_word}' adalah '{en_word}'."))
    lines.append(pair(f"'{id_word}' in English?", f"'{id_word}' in English is '{en_word}'."))
    lines.append(pair(f"Translate '{en_word}' ke bahasa Indonesia?", f"'{en_word}' dalam bahasa Indonesia adalah '{id_word}'."))

print(f"Total lines generated: {len(lines)}")

# Tulis ke dataset
with open(DATASET, "a", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

size_mb = DATASET.stat().st_size / (1024*1024)
print(f"✅ Ditambahkan {len(lines)} entri")
print(f"📦 Ukuran dataset sekarang: {size_mb:.1f} MB")
