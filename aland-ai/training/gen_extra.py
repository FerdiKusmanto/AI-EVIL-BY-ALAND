"""
Generator dataset tambahan - target naik ke 150MB+
Topik baru: coding, kesehatan, agama, olahraga, teknologi, resep, motivasi
"""
import json, random
from pathlib import Path

DATASET = Path(__file__).parent / "dataset.jsonl"

def pair(q, a):
    return json.dumps({"messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]}, ensure_ascii=False)

lines = []

# ── 1. Pemrograman Python ────────────────────────────────────────────────────
python_qa = [
    ("Bagaimana cara print di Python?", 'Gunakan fungsi print():\n```python\nprint("Hello, World!")\nprint("Nama:", "ALand")\n```'),
    ("Bagaimana cara membuat variabel di Python?", 'Di Python tidak perlu deklarasi tipe:\n```python\nnama = "ALand"\numur = 20\ntinggi = 1.75\naktif = True\n```'),
    ("Bagaimana cara membuat list di Python?", '```python\nbuah = ["apel", "mangga", "jeruk"]\nbuah.append("pisang")  # tambah\nbuah.remove("apel")    # hapus\nprint(buah[0])         # akses index\n```'),
    ("Bagaimana cara membuat dictionary di Python?", '```python\norang = {"nama": "ALand", "umur": 20, "kota": "Jakarta"}\nprint(orang["nama"])   # ALand\norang["email"] = "aland@email.com"  # tambah key\n```'),
    ("Bagaimana cara membuat fungsi di Python?", '```python\ndef sapa(nama):\n    return f"Halo, {nama}!"\n\nhasil = sapa("ALand")\nprint(hasil)  # Halo, ALand!\n```'),
    ("Bagaimana cara membuat loop for di Python?", '```python\n# Loop list\nfor buah in ["apel", "mangga"]:\n    print(buah)\n\n# Loop range\nfor i in range(5):\n    print(i)  # 0,1,2,3,4\n```'),
    ("Bagaimana cara membuat loop while di Python?", '```python\ni = 0\nwhile i < 5:\n    print(i)\n    i += 1\n```'),
    ("Bagaimana cara if else di Python?", '```python\nnilai = 85\nif nilai >= 90:\n    print("A")\nelif nilai >= 80:\n    print("B")\nelse:\n    print("C")\n```'),
    ("Bagaimana cara membaca file di Python?", '```python\n# Baca file\nwith open("file.txt", "r") as f:\n    isi = f.read()\n    print(isi)\n\n# Baca per baris\nwith open("file.txt", "r") as f:\n    for baris in f:\n        print(baris.strip())\n```'),
    ("Bagaimana cara menulis file di Python?", '```python\nwith open("output.txt", "w") as f:\n    f.write("Hello, World!\\n")\n    f.write("Baris kedua\\n")\n```'),
    ("Bagaimana cara import modul di Python?", '```python\nimport os\nimport json\nfrom pathlib import Path\nfrom datetime import datetime\n\nprint(os.getcwd())  # direktori saat ini\nprint(datetime.now())\n```'),
    ("Bagaimana cara membuat class di Python?", '```python\nclass Hewan:\n    def __init__(self, nama, suara):\n        self.nama = nama\n        self.suara = suara\n\n    def bersuara(self):\n        return f"{self.nama} berkata {self.suara}"\n\nkucing = Hewan("Kucing", "Meow")\nprint(kucing.bersuara())\n```'),
    ("Bagaimana cara handle exception di Python?", '```python\ntry:\n    hasil = 10 / 0\nexcept ZeroDivisionError:\n    print("Tidak bisa dibagi nol!")\nexcept Exception as e:\n    print(f"Error: {e}")\nfinally:\n    print("Selesai")\n```'),
    ("Bagaimana cara menggunakan list comprehension?", '```python\n# Tanpa comprehension\nkuadrat = []\nfor i in range(10):\n    kuadrat.append(i**2)\n\n# Dengan comprehension (lebih ringkas)\nkuadrat = [i**2 for i in range(10)]\ngenap = [i for i in range(20) if i % 2 == 0]\n```'),
    ("Bagaimana cara sort list di Python?", '```python\nangka = [3, 1, 4, 1, 5, 9, 2, 6]\nangka.sort()           # sort in-place ascending\nangka.sort(reverse=True)  # descending\n\nterurut = sorted(angka)  # return list baru\n```'),
    ("Bagaimana cara menggunakan lambda di Python?", '```python\n# Lambda = fungsi anonim singkat\ntambah = lambda x, y: x + y\nprint(tambah(3, 5))  # 8\n\n# Sering dipakai dengan sorted/map/filter\norang = [{"nama": "Budi", "umur": 25}, {"nama": "Ani", "umur": 20}]\nterurut = sorted(orang, key=lambda x: x["umur"])\n```'),
    ("Apa itu pip di Python?", "pip adalah package manager Python untuk menginstall library. Contoh:\n```bash\npip install requests\npip install numpy pandas\npip list          # lihat yang terinstall\npip uninstall requests\n```"),
    ("Bagaimana cara install library Python?", "Gunakan pip:\n```bash\npip install nama-library\n# Contoh:\npip install requests flask numpy pandas\n\n# Install dari requirements.txt\npip install -r requirements.txt\n```"),
    ("Apa itu virtual environment Python?", "Virtual environment adalah lingkungan Python terisolasi untuk setiap project:\n```bash\npython -m venv venv        # buat venv\nsource venv/bin/activate   # aktifkan (Linux/Mac)\nvenv\\Scripts\\activate      # aktifkan (Windows)\npip install flask          # install di venv\ndeactivate                 # nonaktifkan\n```"),
    ("Bagaimana cara menggunakan requests di Python?", '```python\nimport requests\n\n# GET request\nresponse = requests.get("https://api.example.com/data")\ndata = response.json()\n\n# POST request\nresponse = requests.post("https://api.example.com/users",\n    json={"nama": "ALand", "email": "aland@email.com"})\nprint(response.status_code)\n```'),
]
for q, a in python_qa:
    lines.append(pair(q, a))
    lines.append(pair("Python: " + q, a))

# ── 2. JavaScript ────────────────────────────────────────────────────────────
js_qa = [
    ("Bagaimana cara console.log di JavaScript?", 'console.log("Hello, World!");\nconsole.log("Nilai:", 42);\nconsole.error("Error!");\nconsole.warn("Peringatan!");'),
    ("Bagaimana cara deklarasi variabel di JavaScript?", 'const nama = "ALand";  // tidak bisa diubah\nlet umur = 20;         // bisa diubah\nvar lama = "hindari";  // cara lama\n\numur = 21;  // OK\n// nama = "Budi";  // Error!'),
    ("Bagaimana cara membuat fungsi di JavaScript?", '// Function declaration\nfunction sapa(nama) {\n    return `Halo, ${nama}!`;\n}\n\n// Arrow function\nconst sapa2 = (nama) => `Halo, ${nama}!`;\n\nconsole.log(sapa("ALand"));'),
    ("Bagaimana cara fetch API di JavaScript?", 'fetch("https://api.example.com/data")\n    .then(res => res.json())\n    .then(data => console.log(data))\n    .catch(err => console.error(err));\n\n// Dengan async/await\nasync function getData() {\n    const res = await fetch("https://api.example.com/data");\n    const data = await res.json();\n    return data;\n}'),
    ("Bagaimana cara manipulasi DOM di JavaScript?", 'const el = document.getElementById("myId");\nconst els = document.querySelectorAll(".myClass");\n\nel.textContent = "Teks baru";\nel.style.color = "red";\nel.classList.add("active");\n\n// Event listener\nel.addEventListener("click", () => {\n    console.log("Diklik!");\n});'),
    ("Apa itu async await JavaScript?", 'async/await adalah cara modern menangani operasi asinkron:\n```javascript\nasync function ambilData() {\n    try {\n        const res = await fetch("/api/data");\n        const data = await res.json();\n        return data;\n    } catch (error) {\n        console.error("Error:", error);\n    }\n}\n```'),
    ("Apa itu Promise di JavaScript?", 'Promise adalah objek yang merepresentasikan operasi asinkron:\n```javascript\nconst janji = new Promise((resolve, reject) => {\n    setTimeout(() => resolve("Berhasil!"), 1000);\n});\n\njanji.then(hasil => console.log(hasil));\n```'),
    ("Bagaimana cara filter array di JavaScript?", 'const angka = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n\nconst genap = angka.filter(n => n % 2 === 0);\n// [2, 4, 6, 8, 10]\n\nconst besar = angka.filter(n => n > 5);\n// [6, 7, 8, 9, 10]'),
    ("Bagaimana cara map array di JavaScript?", 'const angka = [1, 2, 3, 4, 5];\n\nconst kuadrat = angka.map(n => n * n);\n// [1, 4, 9, 16, 25]\n\nconst orang = [{nama: "Budi"}, {nama: "Ani"}];\nconst nama = orang.map(o => o.nama);\n// ["Budi", "Ani"]'),
    ("Apa itu spread operator JavaScript?", 'const arr1 = [1, 2, 3];\nconst arr2 = [4, 5, 6];\nconst gabung = [...arr1, ...arr2];  // [1,2,3,4,5,6]\n\nconst obj1 = {a: 1, b: 2};\nconst obj2 = {c: 3};\nconst gabungObj = {...obj1, ...obj2};  // {a:1, b:2, c:3}'),
]
for q, a in js_qa:
    lines.append(pair(q, a))

print(f"Coding: {len(lines)} entries")

# ── 3. Kesehatan & medis ─────────────────────────────────────────────────────
kesehatan = [
    ("Apa itu diabetes?", "Diabetes adalah penyakit kronis di mana kadar gula darah terlalu tinggi. Ada dua tipe: Tipe 1 (autoimun, pankreas tidak produksi insulin) dan Tipe 2 (resistensi insulin, paling umum). Gejala: sering haus, sering buang air kecil, lemas."),
    ("Apa itu hipertensi?", "Hipertensi atau tekanan darah tinggi adalah kondisi di mana tekanan darah ≥140/90 mmHg. Disebut 'silent killer' karena sering tanpa gejala. Faktor risiko: obesitas, stres, kurang olahraga, konsumsi garam berlebih."),
    ("Apa itu kolesterol?", "Kolesterol adalah lemak dalam darah. Ada LDL (kolesterol jahat) dan HDL (kolesterol baik). Kolesterol tinggi meningkatkan risiko penyakit jantung. Normal: total <200 mg/dL, LDL <130 mg/dL, HDL >40 mg/dL."),
    ("Apa itu BMI?", "BMI (Body Mass Index) adalah ukuran lemak tubuh berdasarkan berat dan tinggi badan. Rumus: BMI = berat (kg) / tinggi² (m). Kategori: <18.5 (kurus), 18.5-24.9 (normal), 25-29.9 (gemuk), ≥30 (obesitas)."),
    ("Berapa tekanan darah normal?", "Tekanan darah normal adalah 120/80 mmHg. Angka pertama (sistolik) adalah tekanan saat jantung memompa, angka kedua (diastolik) saat jantung istirahat. Hipertensi: ≥140/90 mmHg."),
    ("Berapa detak jantung normal?", "Detak jantung normal orang dewasa saat istirahat adalah 60-100 kali per menit. Atlet bisa lebih rendah (40-60). Di atas 100 disebut takikardia, di bawah 60 disebut bradikardia."),
    ("Apa manfaat olahraga?", "Manfaat olahraga: meningkatkan kesehatan jantung, memperkuat otot dan tulang, menurunkan berat badan, mengurangi stres dan depresi, meningkatkan kualitas tidur, memperpanjang umur. WHO merekomendasikan 150 menit olahraga sedang per minggu."),
    ("Berapa jam tidur yang ideal?", "Kebutuhan tidur berdasarkan usia: bayi 14-17 jam, anak 9-11 jam, remaja 8-10 jam, dewasa 7-9 jam, lansia 7-8 jam. Kurang tidur meningkatkan risiko obesitas, diabetes, dan penyakit jantung."),
    ("Apa itu vitamin C?", "Vitamin C (asam askorbat) adalah vitamin larut air yang penting untuk imunitas, produksi kolagen, dan antioksidan. Sumber: jeruk, jambu biji, paprika, brokoli. Kebutuhan harian: 75-90 mg untuk dewasa."),
    ("Apa itu vitamin D?", "Vitamin D penting untuk penyerapan kalsium dan kesehatan tulang. Diproduksi kulit saat terkena sinar matahari. Sumber makanan: ikan berlemak, telur, susu fortifikasi. Defisiensi menyebabkan tulang lemah (rakhitis/osteoporosis)."),
    ("Apa itu protein?", "Protein adalah makronutrien penting untuk membangun dan memperbaiki jaringan tubuh, enzim, dan hormon. Sumber: daging, ikan, telur, kacang-kacangan, tahu, tempe. Kebutuhan: 0.8-1.2 gram per kg berat badan per hari."),
    ("Apa itu karbohidrat?", "Karbohidrat adalah sumber energi utama tubuh. Ada karbohidrat sederhana (gula, cepat diserap) dan kompleks (nasi, roti, lambat diserap). Karbohidrat kompleks lebih baik karena tidak menyebabkan lonjakan gula darah."),
    ("Apa itu lemak sehat?", "Lemak sehat (tak jenuh) ditemukan dalam alpukat, kacang-kacangan, minyak zaitun, dan ikan berlemak. Berbeda dengan lemak jenuh (daging merah, mentega) dan lemak trans (makanan olahan) yang meningkatkan risiko penyakit jantung."),
    ("Berapa banyak air yang harus diminum per hari?", "Rekomendasi umum adalah 8 gelas (2 liter) per hari, namun kebutuhan bervariasi tergantung berat badan, aktivitas, dan iklim. Cara mudah: minum saat haus dan pastikan urin berwarna kuning muda."),
    ("Apa itu BPJS Kesehatan?", "BPJS Kesehatan adalah program jaminan kesehatan nasional Indonesia yang dikelola pemerintah. Peserta membayar iuran bulanan dan mendapat layanan kesehatan di fasilitas yang bekerja sama. Ada kelas 1, 2, dan 3."),
    ("Apa itu COVID-19?", "COVID-19 adalah penyakit infeksi saluran pernapasan yang disebabkan virus SARS-CoV-2. Gejala: demam, batuk, sesak napas, kehilangan penciuman/rasa. Pencegahan: vaksinasi, masker, cuci tangan, jaga jarak."),
    ("Apa itu vaksin?", "Vaksin adalah sediaan biologis yang merangsang sistem imun untuk mengenali dan melawan patogen tertentu. Vaksin mengandung antigen yang dilemahkan/dimatikan atau protein spesifik. Vaksinasi adalah cara paling efektif mencegah penyakit menular."),
    ("Apa itu antibiotik?", "Antibiotik adalah obat yang membunuh atau menghambat pertumbuhan bakteri. Hanya efektif untuk infeksi bakteri, tidak untuk virus. Penggunaan tidak tepat menyebabkan resistensi antibiotik. Selalu habiskan antibiotik sesuai resep dokter."),
    ("Apa itu demam?", "Demam adalah suhu tubuh di atas normal (>37.5°C). Merupakan respons imun terhadap infeksi. Demam ringan (37.5-38.5°C) biasanya tidak perlu obat. Demam tinggi (>39°C) perlu penanganan. Kompres hangat dan minum banyak air."),
    ("Apa itu pertolongan pertama?", "Pertolongan pertama (P3K) adalah tindakan awal untuk korban kecelakaan atau sakit mendadak sebelum bantuan medis tiba. Prinsip dasar: pastikan keamanan, panggil bantuan (119), lakukan CPR jika perlu, hentikan perdarahan, jangan pindahkan korban cedera tulang belakang."),
]
for q, a in kesehatan:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Tolong jelaskan ").replace("Berapa ", "Berapakah ").replace("Apa ", "Jelaskan "), a))

print(f"Kesehatan: {len(lines)} entries")

# ── 4. Agama Islam ───────────────────────────────────────────────────────────
islam_qa = [
    ("Apa itu rukun Islam?", "Rukun Islam ada 5: 1) Syahadat (bersaksi tiada Tuhan selain Allah dan Muhammad rasul-Nya), 2) Shalat (5 waktu sehari), 3) Zakat (2.5% harta), 4) Puasa Ramadan, 5) Haji (bagi yang mampu)."),
    ("Apa itu rukun iman?", "Rukun Iman ada 6: 1) Iman kepada Allah, 2) Iman kepada Malaikat, 3) Iman kepada Kitab-kitab Allah, 4) Iman kepada Rasul, 5) Iman kepada Hari Kiamat, 6) Iman kepada Qada dan Qadar."),
    ("Berapa jumlah surat dalam Al-Quran?", "Al-Quran terdiri dari 114 surat, 6.236 ayat, 30 juz. Surat terpanjang adalah Al-Baqarah (286 ayat), surat terpendek adalah Al-Kautsar (3 ayat)."),
    ("Apa itu shalat 5 waktu?", "Shalat 5 waktu: 1) Subuh (2 rakaat, sebelum matahari terbit), 2) Dzuhur (4 rakaat, tengah hari), 3) Ashar (4 rakaat, sore), 4) Maghrib (3 rakaat, setelah matahari terbenam), 5) Isya (4 rakaat, malam)."),
    ("Apa itu puasa Ramadan?", "Puasa Ramadan adalah ibadah menahan makan, minum, dan hal-hal yang membatalkan puasa dari terbit fajar hingga terbenam matahari selama bulan Ramadan. Wajib bagi Muslim yang mampu."),
    ("Apa itu zakat?", "Zakat adalah kewajiban mengeluarkan sebagian harta untuk diberikan kepada yang berhak. Ada zakat fitrah (dibayar sebelum Idul Fitri) dan zakat mal (2.5% dari harta yang mencapai nisab)."),
    ("Apa itu haji?", "Haji adalah ibadah ke Makkah yang wajib dilakukan sekali seumur hidup bagi Muslim yang mampu. Dilaksanakan pada bulan Dzulhijjah. Rangkaian: ihram, tawaf, sa'i, wukuf di Arafah, mabit di Muzdalifah dan Mina, lempar jumrah."),
    ("Apa itu Idul Fitri?", "Idul Fitri adalah hari raya Islam yang dirayakan pada 1 Syawal setelah selesai puasa Ramadan. Dikenal sebagai Lebaran di Indonesia. Diisi dengan shalat Id, silaturahmi, dan saling memaafkan."),
    ("Apa itu Idul Adha?", "Idul Adha adalah hari raya Islam pada 10 Dzulhijjah, memperingati pengorbanan Nabi Ibrahim. Diisi dengan shalat Id dan penyembelihan hewan kurban (sapi, kambing, domba) yang dagingnya dibagikan."),
    ("Apa itu Al-Quran?", "Al-Quran adalah kitab suci umat Islam, wahyu Allah yang diturunkan kepada Nabi Muhammad SAW melalui Malaikat Jibril selama 23 tahun. Ditulis dalam bahasa Arab dan menjadi pedoman hidup umat Islam."),
    ("Siapa Nabi Muhammad SAW?", "Nabi Muhammad SAW (570-632 M) adalah nabi dan rasul terakhir dalam Islam. Lahir di Makkah, menerima wahyu pertama di Gua Hira pada usia 40 tahun. Mendirikan komunitas Muslim di Madinah dan menyebarkan Islam ke seluruh Jazirah Arab."),
    ("Apa itu masjid?", "Masjid adalah tempat ibadah umat Islam. Masjid terbesar dan tersuci adalah Masjidil Haram di Makkah (tempat Ka'bah), diikuti Masjid Nabawi di Madinah. Di Indonesia, masjid juga berfungsi sebagai pusat kegiatan sosial dan pendidikan."),
    ("Apa itu Ka'bah?", "Ka'bah adalah bangunan berbentuk kubus di tengah Masjidil Haram, Makkah. Dianggap sebagai rumah Allah dan kiblat shalat umat Islam di seluruh dunia. Dibangun oleh Nabi Ibrahim dan putranya Ismail."),
    ("Apa itu wudhu?", "Wudhu adalah bersuci dengan air sebelum shalat. Caranya: niat, cuci tangan, berkumur, cuci hidung, cuci muka, cuci tangan hingga siku, usap kepala, cuci telinga, cuci kaki hingga mata kaki. Batal jika buang air, kentut, atau tidur."),
    ("Apa itu halal dan haram?", "Halal adalah sesuatu yang diperbolehkan dalam Islam, haram adalah yang dilarang. Makanan haram: babi, darah, bangkai, alkohol. Makanan halal harus disembelih dengan cara Islam. Konsep halal-haram juga berlaku untuk perilaku dan transaksi."),
]
for q, a in islam_qa:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Jelaskan tentang ").replace("Siapa ", "Ceritakan tentang ").replace("Berapa ", "Berapakah "), a))

print(f"Agama: {len(lines)} entries")

# ── 5. Olahraga ──────────────────────────────────────────────────────────────
olahraga_qa = [
    ("Apa itu sepak bola?", "Sepak bola adalah olahraga tim yang dimainkan 11 pemain per tim, tujuannya memasukkan bola ke gawang lawan. Lapangan berukuran 100-110 x 64-75 meter. Pertandingan 2x45 menit. Olahraga paling populer di dunia."),
    ("Apa itu bulu tangkis?", "Bulu tangkis (badminton) adalah olahraga raket yang dimainkan 1 vs 1 atau 2 vs 2, memukul shuttlecock melewati net. Indonesia adalah kekuatan besar bulu tangkis dunia dengan banyak medali olimpiade."),
    ("Apa itu basket?", "Basket (basketball) adalah olahraga tim 5 vs 5 yang tujuannya memasukkan bola ke ring lawan. Lapangan 28x15 meter. Pertandingan 4x10 menit (FIBA) atau 4x12 menit (NBA)."),
    ("Apa itu voli?", "Voli (volleyball) adalah olahraga tim 6 vs 6 yang memukul bola melewati net tanpa menyentuh lantai. Sistem skor rally point hingga 25 poin (3 set kemenangan dari 5 set)."),
    ("Apa itu renang?", "Renang adalah olahraga air yang menggunakan gerakan tubuh untuk bergerak di air. Gaya renang: gaya bebas (crawl), gaya punggung, gaya dada, gaya kupu-kupu. Manfaat: melatih seluruh otot tubuh, baik untuk jantung."),
    ("Apa itu lari maraton?", "Maraton adalah lomba lari sejauh 42,195 km. Berasal dari legenda Pheidippides yang berlari dari Marathon ke Athena. Rekor dunia: 2 jam 0 menit 35 detik (Kelvin Kiptum, 2023)."),
    ("Apa itu olimpiade?", "Olimpiade adalah ajang olahraga internasional terbesar yang diadakan setiap 4 tahun. Ada Olimpiade Musim Panas dan Musim Dingin. Pertama kali modern diadakan di Athena 1896. Indonesia pertama kali ikut olimpiade 1952."),
    ("Siapa Lionel Messi?", "Lionel Messi adalah pesepakbola Argentina, dianggap salah satu pemain terbaik sepanjang masa. Meraih 8 Ballon d'Or, juara Piala Dunia 2022 bersama Argentina. Bermain untuk Barcelona, PSG, dan Inter Miami."),
    ("Siapa Cristiano Ronaldo?", "Cristiano Ronaldo adalah pesepakbola Portugal, salah satu pemain terbaik dunia. Meraih 5 Ballon d'Or, juara Liga Champions 5 kali. Bermain untuk Manchester United, Real Madrid, Juventus, dan Al Nassr."),
    ("Apa itu Piala Dunia FIFA?", "Piala Dunia FIFA adalah turnamen sepak bola internasional terbesar, diadakan setiap 4 tahun. Diikuti 32 tim (akan jadi 48 tim mulai 2026). Juara terbanyak: Brasil (5 kali). Indonesia belum pernah lolos ke Piala Dunia."),
    ("Apa itu SEA Games?", "SEA Games (Southeast Asian Games) adalah ajang olahraga multi-cabang negara-negara Asia Tenggara, diadakan setiap 2 tahun. Indonesia sering menjadi tuan rumah dan meraih banyak medali."),
    ("Apa itu Thomas Cup?", "Thomas Cup adalah kejuaraan bulu tangkis beregu putra paling bergengsi di dunia. Indonesia adalah negara tersukses dengan 14 gelar juara. Diadakan setiap 2 tahun."),
    ("Siapa Kevin Sanjaya?", "Kevin Sanjaya Sukamuljo adalah pemain bulu tangkis ganda putra Indonesia. Bersama Marcus Fernaldi Gideon, pernah menjadi pasangan ganda putra nomor 1 dunia. Dikenal dengan permainan agresif dan cepat."),
    ("Apa itu MotoGP?", "MotoGP adalah kejuaraan balap motor paling bergengsi di dunia, menggunakan motor prototipe berkapasitas 1000cc. Sirkuit Mandalika di Lombok, Indonesia menjadi tuan rumah MotoGP sejak 2022."),
    ("Apa itu Formula 1?", "Formula 1 (F1) adalah kejuaraan balap mobil paling bergengsi di dunia. Mobil F1 bisa mencapai kecepatan 350+ km/jam. Juara terbanyak: Lewis Hamilton dan Michael Schumacher (7 gelar masing-masing)."),
]
for q, a in olahraga_qa:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Ceritakan tentang ").replace("Siapa ", "Siapakah "), a))

print(f"Olahraga: {len(lines)} entries")

# ── 6. Motivasi & pengembangan diri ─────────────────────────────────────────
motivasi = [
    ("Bagaimana cara belajar efektif?", "Tips belajar efektif: 1) Buat jadwal belajar rutin, 2) Gunakan teknik Pomodoro (25 menit fokus, 5 menit istirahat), 3) Buat catatan dengan kata-kata sendiri, 4) Ajarkan materi ke orang lain, 5) Istirahat cukup dan tidur teratur, 6) Hindari multitasking."),
    ("Bagaimana cara mengatasi prokrastinasi?", "Cara mengatasi prokrastinasi: 1) Pecah tugas besar menjadi langkah kecil, 2) Mulai dengan 2 menit saja, 3) Hilangkan gangguan (HP, media sosial), 4) Buat deadline yang jelas, 5) Reward diri setelah menyelesaikan tugas, 6) Cari teman belajar/kerja."),
    ("Bagaimana cara meningkatkan kepercayaan diri?", "Tips meningkatkan kepercayaan diri: 1) Kenali kelebihan dan kekurangan diri, 2) Tetapkan tujuan kecil dan capai, 3) Jaga penampilan dan kesehatan, 4) Berhenti membandingkan diri dengan orang lain, 5) Kelilingi diri dengan orang positif, 6) Belajar dari kegagalan."),
    ("Bagaimana cara manajemen waktu?", "Tips manajemen waktu: 1) Buat to-do list harian, 2) Prioritaskan tugas (penting vs mendesak), 3) Gunakan kalender/planner, 4) Batasi waktu untuk setiap tugas, 5) Delegasikan jika bisa, 6) Evaluasi penggunaan waktu setiap minggu."),
    ("Bagaimana cara mengatasi stres?", "Cara mengatasi stres: 1) Olahraga rutin, 2) Meditasi atau pernapasan dalam, 3) Tidur cukup, 4) Cerita ke orang terpercaya, 5) Batasi konsumsi berita negatif, 6) Lakukan hobi yang menyenangkan, 7) Jangan ragu minta bantuan profesional jika perlu."),
    ("Apa itu growth mindset?", "Growth mindset (Carol Dweck) adalah keyakinan bahwa kemampuan bisa dikembangkan melalui usaha dan belajar. Kebalikannya adalah fixed mindset (kemampuan bawaan, tidak bisa berubah). Dengan growth mindset, kegagalan dilihat sebagai kesempatan belajar."),
    ("Bagaimana cara membangun kebiasaan baik?", "Cara membangun kebiasaan (James Clear - Atomic Habits): 1) Mulai sangat kecil (2 menit rule), 2) Tumpuk kebiasaan baru pada yang sudah ada, 3) Buat lingkungan yang mendukung, 4) Lacak progress, 5) Jangan lewatkan 2 hari berturut-turut, 6) Fokus pada identitas, bukan hasil."),
    ("Apa itu mindfulness?", "Mindfulness adalah praktik memusatkan perhatian pada momen saat ini tanpa menghakimi. Manfaat: mengurangi stres, meningkatkan fokus, memperbaiki kesehatan mental. Cara: meditasi, pernapasan sadar, makan dengan penuh perhatian."),
    ("Bagaimana cara public speaking yang baik?", "Tips public speaking: 1) Persiapkan materi dengan baik, 2) Latihan berulang kali, 3) Kenali audiens, 4) Mulai dengan pembuka yang menarik, 5) Gunakan kontak mata, 6) Variasikan intonasi suara, 7) Gunakan gestur tangan, 8) Jangan takut jeda, 9) Tutup dengan kuat."),
    ("Bagaimana cara belajar bahasa Inggris?", "Tips belajar bahasa Inggris: 1) Dengarkan podcast/lagu Inggris setiap hari, 2) Tonton film/series dengan subtitle Inggris, 3) Baca artikel/buku Inggris, 4) Praktik berbicara (dengan teman atau AI), 5) Catat kosakata baru, 6) Gunakan aplikasi seperti Duolingo, 7) Jangan takut salah."),
]
for q, a in motivasi:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Bagaimana cara ", "Apa tips untuk ").replace("Apa itu ", "Jelaskan "), a))

print(f"Motivasi: {len(lines)} entries")

# ── 7. Teknologi & gadget ────────────────────────────────────────────────────
teknologi = [
    ("Apa itu smartphone?", "Smartphone adalah telepon genggam canggih dengan sistem operasi (Android/iOS), layar sentuh, koneksi internet, dan kemampuan menjalankan aplikasi. Fitur utama: kamera, GPS, sensor, dan akses ke jutaan aplikasi."),
    ("Apa perbedaan Android dan iOS?", "Android (Google): open source, banyak merek (Samsung, Xiaomi, dll), lebih fleksibel, harga bervariasi. iOS (Apple): eksklusif untuk iPhone, lebih tertutup, update lebih lama, ekosistem Apple yang terintegrasi. Keduanya memiliki jutaan aplikasi."),
    ("Apa itu RAM?", "RAM (Random Access Memory) adalah memori sementara yang digunakan komputer/HP untuk menjalankan program aktif. Semakin besar RAM, semakin banyak aplikasi yang bisa berjalan bersamaan. RAM berbeda dengan storage (penyimpanan permanen)."),
    ("Apa itu SSD?", "SSD (Solid State Drive) adalah media penyimpanan data yang menggunakan chip flash, jauh lebih cepat dari HDD (Hard Disk Drive) yang menggunakan piringan magnetik. SSD membuat komputer booting dan loading lebih cepat."),
    ("Apa itu WiFi?", "WiFi adalah teknologi jaringan nirkabel yang memungkinkan perangkat terhubung ke internet tanpa kabel. Menggunakan frekuensi radio 2.4 GHz atau 5 GHz. WiFi 6 (802.11ax) adalah standar terbaru dengan kecepatan lebih tinggi."),
    ("Apa itu Bluetooth?", "Bluetooth adalah teknologi komunikasi nirkabel jarak pendek (sekitar 10 meter) untuk menghubungkan perangkat seperti headphone, speaker, keyboard, dan mouse tanpa kabel."),
    ("Apa itu VPN?", "VPN (Virtual Private Network) adalah layanan yang mengenkripsi koneksi internet dan menyembunyikan alamat IP. Digunakan untuk privasi, keamanan di WiFi publik, dan mengakses konten yang diblokir secara geografis."),
    ("Apa itu CPU?", "CPU (Central Processing Unit) adalah 'otak' komputer yang menjalankan instruksi program. Kecepatan diukur dalam GHz. Merek utama: Intel (Core i3/i5/i7/i9) dan AMD (Ryzen). Semakin banyak core, semakin baik untuk multitasking."),
    ("Apa itu GPU?", "GPU (Graphics Processing Unit) adalah prosesor khusus untuk mengolah grafis. Penting untuk gaming, desain grafis, dan AI/machine learning. Merek utama: NVIDIA (GeForce) dan AMD (Radeon)."),
    ("Apa itu cloud storage?", "Cloud storage adalah layanan penyimpanan data di server internet. Contoh: Google Drive, Dropbox, iCloud, OneDrive. Keuntungan: akses dari mana saja, backup otomatis, berbagi mudah. Kekurangan: butuh internet, privasi."),
    ("Apa itu ChatGPT?", "ChatGPT adalah chatbot AI buatan OpenAI yang menggunakan model bahasa besar (LLM) GPT. Bisa menjawab pertanyaan, menulis teks, membuat kode, dan banyak lagi. Diluncurkan November 2022 dan langsung viral."),
    ("Apa itu metaverse?", "Metaverse adalah konsep dunia virtual 3D yang imersif di mana orang bisa berinteraksi, bekerja, bermain, dan berbelanja menggunakan avatar. Menggunakan teknologi VR/AR. Masih dalam tahap pengembangan awal."),
    ("Apa itu NFT?", "NFT (Non-Fungible Token) adalah aset digital unik yang diverifikasi menggunakan blockchain. Bisa berupa karya seni digital, musik, atau item game. Setiap NFT memiliki kepemilikan yang tercatat di blockchain."),
    ("Apa itu cryptocurrency?", "Cryptocurrency adalah mata uang digital yang menggunakan kriptografi untuk keamanan dan blockchain untuk pencatatan transaksi. Contoh: Bitcoin (BTC), Ethereum (ETH). Nilainya sangat fluktuatif dan tidak dijamin pemerintah."),
    ("Apa itu Bitcoin?", "Bitcoin adalah cryptocurrency pertama dan terbesar, diciptakan oleh Satoshi Nakamoto pada 2009. Berjalan di jaringan blockchain terdesentralisasi. Jumlah maksimal 21 juta BTC. Digunakan sebagai investasi dan alat pembayaran di beberapa tempat."),
]
for q, a in teknologi:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Tolong jelaskan ").replace("Apa perbedaan ", "Bedakan "), a))

print(f"Teknologi: {len(lines)} entries")

# ── 8. Resep masakan ─────────────────────────────────────────────────────────
resep = [
    ("Bagaimana cara membuat nasi goreng?", "Bahan: nasi putih 2 piring, telur 2 butir, bawang merah 3 siung, bawang putih 2 siung, kecap manis 2 sdm, garam, merica. Cara: tumis bawang hingga harum, masukkan telur orak-arik, masukkan nasi, tambahkan kecap, garam, merica. Aduk rata. Sajikan dengan kerupuk."),
    ("Bagaimana cara membuat mie goreng?", "Bahan: mie telur 200g, telur 1 butir, sawi, wortel, bawang putih, kecap manis, saus tiram, garam. Cara: rebus mie hingga matang, tiriskan. Tumis bawang putih, masukkan sayuran, telur orak-arik, masukkan mie, tambahkan bumbu. Aduk rata."),
    ("Bagaimana cara membuat soto ayam?", "Bahan: ayam 1/2 ekor, kunyit, jahe, serai, daun salam, bawang merah, bawang putih, garam. Cara: rebus ayam dengan bumbu hingga matang. Suwir ayam. Sajikan kuah dengan mie, tauge, telur rebus, dan suwiran ayam. Taburi bawang goreng."),
    ("Bagaimana cara membuat rendang?", "Bahan: daging sapi 1 kg, santan kental 1 liter, cabai merah, bawang merah, bawang putih, jahe, lengkuas, serai, daun jeruk, daun kunyit. Cara: haluskan bumbu, masak daging dengan santan dan bumbu di api sedang sambil diaduk hingga santan mengering dan daging berwarna coklat kehitaman (3-4 jam)."),
    ("Bagaimana cara membuat bakso?", "Bahan: daging sapi giling 500g, tepung tapioka 100g, putih telur 2, bawang putih, garam, merica. Cara: haluskan daging dengan bumbu, campur tepung dan putih telur, bentuk bulat, rebus dalam air mendidih hingga mengapung. Sajikan dengan kuah kaldu, mie, dan tahu."),
    ("Bagaimana cara membuat es teh?", "Cara: seduh 2 kantong teh celup dalam 200ml air panas selama 3-5 menit. Tambahkan gula sesuai selera, aduk. Tuang ke gelas berisi es batu. Bisa tambahkan perasan jeruk nipis untuk es teh lemon."),
    ("Bagaimana cara membuat pisang goreng?", "Bahan: pisang kepok/raja 5 buah, tepung terigu 150g, tepung beras 50g, gula 1 sdm, garam, air secukupnya, minyak goreng. Cara: kupas pisang, belah atau geprek. Buat adonan tepung dengan air hingga kental. Celupkan pisang, goreng hingga keemasan."),
    ("Bagaimana cara membuat tempe goreng?", "Bahan: tempe 1 papan, bawang putih 3 siung, ketumbar 1/2 sdt, kunyit 1/4 sdt, garam, minyak goreng. Cara: haluskan bumbu, campur dengan sedikit air. Lumuri tempe dengan bumbu, diamkan 15 menit. Goreng hingga keemasan dan renyah."),
    ("Bagaimana cara membuat sambal terasi?", "Bahan: cabai merah 10 buah, cabai rawit 5 buah, bawang merah 5 siung, bawang putih 2 siung, terasi 1 sdt, tomat 1 buah, garam, gula. Cara: goreng/bakar semua bahan, ulek kasar atau halus sesuai selera. Tambahkan garam dan gula."),
    ("Bagaimana cara membuat kopi susu?", "Cara: seduh 1-2 sdt kopi bubuk dengan 100ml air panas. Tambahkan gula sesuai selera. Tuang susu kental manis 2-3 sdm atau susu cair 100ml. Aduk rata. Untuk kopi susu kekinian, tambahkan es batu dan bisa pakai susu oat/almond."),
]
for q, a in resep:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Bagaimana cara membuat ", "Resep "), a))
    lines.append(pair(q.replace("Bagaimana cara membuat ", "Cara masak "), a))

print(f"Resep: {len(lines)} entries")

# ── 9. Matematika lanjutan ───────────────────────────────────────────────────
# Konversi satuan
konversi = [
    ("1 km berapa meter?", "1 kilometer = 1.000 meter"),
    ("1 meter berapa cm?", "1 meter = 100 sentimeter"),
    ("1 kg berapa gram?", "1 kilogram = 1.000 gram"),
    ("1 ton berapa kg?", "1 ton = 1.000 kilogram"),
    ("1 liter berapa ml?", "1 liter = 1.000 mililiter"),
    ("1 jam berapa menit?", "1 jam = 60 menit"),
    ("1 menit berapa detik?", "1 menit = 60 detik"),
    ("1 hari berapa jam?", "1 hari = 24 jam"),
    ("1 minggu berapa hari?", "1 minggu = 7 hari"),
    ("1 bulan berapa hari?", "1 bulan rata-rata 30 hari (28-31 hari tergantung bulan)"),
    ("1 tahun berapa bulan?", "1 tahun = 12 bulan"),
    ("1 tahun berapa hari?", "1 tahun = 365 hari (tahun kabisat 366 hari)"),
    ("1 dekade berapa tahun?", "1 dekade = 10 tahun"),
    ("1 abad berapa tahun?", "1 abad = 100 tahun"),
    ("1 milenium berapa tahun?", "1 milenium = 1.000 tahun"),
    ("1 hektar berapa m2?", "1 hektar = 10.000 meter persegi (m²)"),
    ("1 km2 berapa hektar?", "1 km² = 100 hektar"),
    ("1 inci berapa cm?", "1 inci = 2,54 sentimeter"),
    ("1 kaki berapa meter?", "1 kaki (feet) = 0,3048 meter"),
    ("1 mil berapa km?", "1 mil = 1,609 kilometer"),
]
for q, a in konversi:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("berapa", "sama dengan berapa"), a))
    lines.append(pair("Konversi: " + q, a))

# Rumus matematika
rumus = [
    ("Rumus luas persegi?", "Luas persegi = sisi × sisi = s²\nContoh: sisi 5 cm → Luas = 5² = 25 cm²"),
    ("Rumus luas persegi panjang?", "Luas persegi panjang = panjang × lebar\nContoh: p=10 cm, l=5 cm → Luas = 10 × 5 = 50 cm²"),
    ("Rumus luas segitiga?", "Luas segitiga = ½ × alas × tinggi\nContoh: alas=8 cm, tinggi=6 cm → Luas = ½ × 8 × 6 = 24 cm²"),
    ("Rumus luas lingkaran?", "Luas lingkaran = π × r²\nContoh: r=7 cm → Luas = 3,14 × 7² = 3,14 × 49 ≈ 153,86 cm²"),
    ("Rumus keliling lingkaran?", "Keliling lingkaran = 2 × π × r = π × d\nContoh: r=7 cm → Keliling = 2 × 3,14 × 7 = 43,96 cm"),
    ("Rumus volume kubus?", "Volume kubus = sisi³ = s × s × s\nContoh: sisi 4 cm → Volume = 4³ = 64 cm³"),
    ("Rumus volume balok?", "Volume balok = panjang × lebar × tinggi\nContoh: 5×4×3 cm → Volume = 60 cm³"),
    ("Rumus volume bola?", "Volume bola = (4/3) × π × r³\nContoh: r=3 cm → Volume = (4/3) × 3,14 × 27 ≈ 113,04 cm³"),
    ("Rumus Pythagoras?", "Teorema Pythagoras: a² + b² = c²\nDi mana c adalah sisi miring (hipotenusa).\nContoh: a=3, b=4 → c = √(9+16) = √25 = 5"),
    ("Rumus kecepatan?", "Kecepatan = Jarak ÷ Waktu (v = s/t)\nContoh: jarak 120 km, waktu 2 jam → v = 120/2 = 60 km/jam"),
    ("Rumus bunga sederhana?", "Bunga = Pokok × Suku Bunga × Waktu\nContoh: Rp1.000.000 × 10% × 2 tahun = Rp200.000"),
    ("Rumus rata-rata?", "Rata-rata = Jumlah semua nilai ÷ Banyak data\nContoh: nilai 70, 80, 90 → Rata-rata = (70+80+90)/3 = 80"),
]
for q, a in rumus:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Rumus ", "Apa rumus "), a))
    lines.append(pair(q.replace("Rumus ", "Bagaimana rumus "), a))

# Soal cerita matematika
soal_cerita = []
for harga in [5000, 10000, 15000, 20000, 25000, 50000, 100000]:
    for jumlah in [2, 3, 4, 5, 6, 10]:
        total = harga * jumlah
        soal_cerita.append((
            f"Jika harga 1 barang Rp{harga:,}, berapa harga {jumlah} barang?",
            f"Harga {jumlah} barang = {jumlah} × Rp{harga:,} = Rp{total:,}"
        ))

for q, a in soal_cerita[:100]:
    lines.append(pair(q, a))

print(f"Matematika lanjutan: {len(lines)} entries")

# ── 10. Bahasa Inggris dasar ─────────────────────────────────────────────────
english_basic = [
    ("How do you say 'terima kasih' in English?", "'Terima kasih' in English is 'Thank you'."),
    ("How do you say 'selamat pagi' in English?", "'Selamat pagi' in English is 'Good morning'."),
    ("How do you say 'selamat siang' in English?", "'Selamat siang' in English is 'Good afternoon'."),
    ("How do you say 'selamat malam' in English?", "'Selamat malam' in English is 'Good evening' or 'Good night'."),
    ("How do you say 'apa kabar' in English?", "'Apa kabar' in English is 'How are you?'"),
    ("How do you say 'saya tidak mengerti' in English?", "'Saya tidak mengerti' in English is 'I don't understand'."),
    ("How do you say 'tolong bantu saya' in English?", "'Tolong bantu saya' in English is 'Please help me'."),
    ("How do you say 'di mana toilet' in English?", "'Di mana toilet' in English is 'Where is the bathroom/toilet?'"),
    ("How do you say 'berapa harganya' in English?", "'Berapa harganya' in English is 'How much does it cost?'"),
    ("How do you say 'saya lapar' in English?", "'Saya lapar' in English is 'I am hungry'."),
    ("Apa arti 'beautiful' dalam bahasa Indonesia?", "'Beautiful' dalam bahasa Indonesia artinya 'cantik' atau 'indah'."),
    ("Apa arti 'knowledge' dalam bahasa Indonesia?", "'Knowledge' dalam bahasa Indonesia artinya 'pengetahuan'."),
    ("Apa arti 'freedom' dalam bahasa Indonesia?", "'Freedom' dalam bahasa Indonesia artinya 'kebebasan'."),
    ("Apa arti 'challenge' dalam bahasa Indonesia?", "'Challenge' dalam bahasa Indonesia artinya 'tantangan'."),
    ("Apa arti 'opportunity' dalam bahasa Indonesia?", "'Opportunity' dalam bahasa Indonesia artinya 'kesempatan' atau 'peluang'."),
    ("Apa arti 'success' dalam bahasa Indonesia?", "'Success' dalam bahasa Indonesia artinya 'kesuksesan' atau 'keberhasilan'."),
    ("Apa arti 'experience' dalam bahasa Indonesia?", "'Experience' dalam bahasa Indonesia artinya 'pengalaman'."),
    ("Apa arti 'technology' dalam bahasa Indonesia?", "'Technology' dalam bahasa Indonesia artinya 'teknologi'."),
    ("Apa arti 'environment' dalam bahasa Indonesia?", "'Environment' dalam bahasa Indonesia artinya 'lingkungan'."),
    ("Apa arti 'government' dalam bahasa Indonesia?", "'Government' dalam bahasa Indonesia artinya 'pemerintah'."),
]
for q, a in english_basic:
    lines.append(pair(q, a))

# Terjemahan angka
for i in range(1, 101):
    en_words = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",
                11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",
                18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"forty",50:"fifty",60:"sixty",
                70:"seventy",80:"eighty",90:"ninety",100:"one hundred"}
    if i in en_words:
        lines.append(pair(f"Angka {i} dalam bahasa Inggris?", f"Angka {i} dalam bahasa Inggris adalah '{en_words[i]}'."))
        lines.append(pair(f"How do you say {i} in Indonesian?", f"{i} in Indonesian is '{['nol','satu','dua','tiga','empat','lima','enam','tujuh','delapan','sembilan','sepuluh'][i]}'" if i <= 10 else f"The number {i} in Indonesian."))

print(f"Bahasa Inggris: {len(lines)} entries")

# ── 11. Variasi pertanyaan ALand-AI ─────────────────────────────────────────
aland_variants = [
    ("Siapa yang membuat kamu?", "Saya dibuat oleh ALand, seorang developer yang membangun sistem AI lokal ini."),
    ("Kamu buatan siapa?", "Saya adalah ALand-AI, dibuat oleh ALand."),
    ("Apa nama AI ini?", "Nama saya ALand-AI, asisten AI lokal buatan ALand."),
    ("Apakah kamu bisa offline?", "Ya! ALand-AI berjalan 100% lokal di perangkat kamu, tidak membutuhkan koneksi internet setelah model didownload."),
    ("Apakah data saya aman?", "Ya, semua percakapan berjalan lokal di perangkat kamu. Tidak ada data yang dikirim ke server eksternal."),
    ("Apa kelebihan ALand-AI?", "Kelebihan ALand-AI: 1) Berjalan 100% lokal tanpa internet, 2) Privasi terjaga, 3) Bisa dikustomisasi, 4) Mendukung bahasa Indonesia dengan baik, 5) Gratis dan open source."),
    ("Bagaimana cara menggunakan ALand-AI?", "Cara menggunakan ALand-AI: 1) Install dengan 'pip install -e .', 2) Download model dengan 'aland-ai pull <model>', 3) Jalankan server dengan 'aland-ai serve', 4) Buka browser ke http://localhost:3000."),
    ("Model apa yang tersedia?", "Model yang tersedia: tinyllama (669MB, ringan), llama3.2 (2GB, bagus untuk chat), qwen2.5 (2GB, bagus bahasa Indonesia), mistral (4.1GB, bagus untuk coding)."),
    ("Apakah ALand-AI gratis?", "Ya, ALand-AI sepenuhnya gratis dan open source. Kamu bisa menggunakannya tanpa biaya apapun."),
    ("Apa itu aland-ai serve?", "'aland-ai serve' adalah perintah untuk menjalankan API server ALand-AI di port 11435. Server ini kompatibel dengan format API Ollama."),
    ("Bagaimana cara download model?", "Gunakan perintah: 'aland-ai pull <nama-model>'. Contoh: 'aland-ai pull tinyllama' atau 'aland-ai pull llama3.2'."),
    ("Bagaimana cara chat di terminal?", "Gunakan perintah: 'aland-ai run <nama-model>'. Contoh: 'aland-ai run llama3.2' untuk chat interaktif di terminal."),
    ("Bagaimana cara lihat model yang ada?", "Gunakan perintah: 'aland-ai list' untuk melihat semua model yang sudah didownload."),
    ("Bagaimana cara hapus model?", "Gunakan perintah: 'aland-ai rm <nama-model>'. Contoh: 'aland-ai rm tinyllama'."),
    ("Di mana model disimpan?", "Model disimpan di direktori ~/.aland-ai/models/ di komputer kamu."),
    ("Apa itu aland-ai train?", "'aland-ai train' adalah perintah untuk melatih model dengan dataset bahasa Indonesia. Gunakan '--export' untuk mengekspor hasil ke format GGUF."),
    ("Bagaimana cara training model?", "Cara training: 1) Install dependencies: 'pip install transformers peft datasets torch', 2) Jalankan: 'aland-ai train --epochs 3', 3) Export: 'aland-ai train --export'."),
    ("Apa format dataset training?", "Format dataset training adalah JSONL, setiap baris berisi:\n{\"messages\": [{\"role\": \"user\", \"content\": \"...\"}, {\"role\": \"assistant\", \"content\": \"...\"}]}"),
    ("Di mana file dataset training?", "Dataset training ada di 'aland-ai/training/dataset.jsonl'. Kamu bisa menambahkan data sendiri dengan format JSONL."),
    ("Apa itu GGUF?", "GGUF adalah format file model AI yang dioptimalkan untuk inferensi lokal menggunakan llama.cpp. Format ini efisien dan mendukung berbagai tingkat kuantisasi."),
]
for q, a in aland_variants:
    lines.append(pair(q, a))

print(f"ALand variants: {len(lines)} entries")

# ── 12. Tulis ke dataset ─────────────────────────────────────────────────────
with open(DATASET, "a", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

print(f"\n✅ Total {len(lines)} entri baru ditambahkan ke dataset")
print(f"📁 Dataset: {DATASET}")
