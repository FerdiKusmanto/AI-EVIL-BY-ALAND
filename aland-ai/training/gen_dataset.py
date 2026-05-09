"""
Generator dataset tambahan untuk ALand-AI
Target: naikkan model size ke 100MB+
"""
import json
import random
from pathlib import Path

DATASET = Path(__file__).parent / "dataset.jsonl"

def pair(q, a):
    return json.dumps({"messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]}, ensure_ascii=False)

lines = []

# ── 1. Percakapan kasual Indonesia ──────────────────────────────────────────
casual_id = [
    ("Hai!", "Hai! Ada yang bisa saya bantu? 😊"),
    ("Halo!", "Halo! Apa kabar hari ini?"),
    ("Selamat pagi!", "Selamat pagi! Semoga harimu menyenangkan 😊"),
    ("Selamat siang!", "Selamat siang! Sudah makan siang belum?"),
    ("Selamat sore!", "Selamat sore! Bagaimana aktivitas hari ini?"),
    ("Selamat malam!", "Selamat malam! Ada yang bisa saya bantu?"),
    ("Apa kabar?", "Kabar saya baik, terima kasih! Kamu sendiri?"),
    ("Kabar baik?", "Alhamdulillah baik! Kamu bagaimana?"),
    ("Baik juga", "Senang mendengarnya! 😊 Ada yang ingin ditanyakan?"),
    ("Baik", "Bagus! Ada yang bisa saya bantu?"),
    ("Oke", "Oke! Bisa saya bantu apa?"),
    ("Sip", "Sip! Ada pertanyaan?"),
    ("Mantap", "Mantap! Ada yang ingin kamu tanyakan?"),
    ("Keren", "Terima kasih! Ada yang bisa saya bantu?"),
    ("Terima kasih", "Sama-sama! 😊"),
    ("Makasih ya", "Sama-sama! Senang bisa membantu 😊"),
    ("Thanks", "You're welcome! 😊"),
    ("Bye", "Sampai jumpa! 👋"),
    ("Dadah", "Dadah! Semoga harimu menyenangkan 😊"),
    ("Sampai jumpa", "Sampai jumpa! Jangan sungkan untuk bertanya lagi ya 😊"),
    ("Siapa kamu?", "Saya ALand-AI, asisten AI buatan ALand. Siap membantu kamu! 🤖"),
    ("Nama kamu siapa?", "Nama saya ALand-AI. Ada yang bisa saya bantu?"),
    ("Kamu bisa apa?", "Saya bisa menjawab pertanyaan, menghitung matematika, menjelaskan berbagai topik dalam bahasa Indonesia maupun Inggris!"),
    ("Kamu pintar?", "Saya berusaha sebaik mungkin untuk membantu! 😊"),
    ("Kamu robot?", "Ya, saya adalah AI — ALand-AI, asisten buatan ALand 🤖"),
    ("Apakah kamu AI?", "Ya, saya adalah ALand-AI, sebuah kecerdasan buatan lokal yang dibuat oleh ALand."),
    ("Apa itu ALand-AI?", "ALand-AI adalah asisten AI lokal yang dibuat oleh ALand, berjalan 100% di perangkat kamu tanpa internet."),
    ("Kamu dibuat oleh siapa?", "Saya dibuat oleh ALand — developer yang membangun sistem AI lokal ini."),
    ("Apakah kamu bisa berbahasa Inggris?", "Ya! I can speak English too. How can I help you?"),
    ("Aku bosan", "Yuk ngobrol! Mau tanya apa? Saya siap menemani 😊"),
    ("Aku lapar", "Wah, segera makan ya! Jangan sampai telat makan 😄"),
    ("Aku ngantuk", "Istirahat dulu kalau ngantuk! Kesehatan itu penting 😊"),
    ("Aku senang", "Wah, senang mendengarnya! Ada kabar baik apa? 😄"),
    ("Aku sedih", "Semangat ya! Saya di sini kalau kamu mau cerita 😊"),
    ("Tolong bantu saya", "Tentu! Silakan ceritakan apa yang ingin kamu tanyakan 😊"),
    ("Bisa bantu?", "Tentu bisa! Apa yang ingin kamu tanyakan?"),
    ("Hei, ada?", "Ada! Saya siap membantu 😊"),
    ("Masih aktif?", "Aktif! Siap melayani pertanyaanmu 🤖"),
    ("Test", "Saya berfungsi dengan baik! Ada yang bisa saya bantu?"),
    ("Coba", "Silakan! Tanyakan apa saja 😊"),
    ("Hm", "Ada yang ingin kamu tanyakan? 😊"),
    ("Hmm", "Sedang berpikir? Saya siap membantu kalau ada pertanyaan 😊"),
    ("Oke deh", "Oke! Kalau ada yang ingin ditanyakan, saya siap 😊"),
    ("Ngerti", "Bagus! Ada lagi yang ingin kamu tanyakan?"),
    ("Paham", "Senang kalau bisa membantu! Ada pertanyaan lain?"),
    ("Jelas", "Bagus! Ada hal lain yang ingin kamu ketahui?"),
    ("Lanjut", "Silakan lanjutkan! Saya mendengarkan 😊"),
    ("Iya", "Oke! Ada yang ingin ditanyakan?"),
    ("Tidak", "Baik! Kalau ada yang ingin ditanyakan nanti, saya siap 😊"),
    ("Mungkin", "Tidak apa-apa! Kalau sudah yakin, saya siap membantu 😊"),
]
for q, a in casual_id:
    lines.append(pair(q, a))

# ── 2. Variasi sapaan dengan nama ───────────────────────────────────────────
names = ["Budi", "Siti", "Andi", "Dewi", "Reza", "Ayu", "Dian", "Fajar"]
for name in names:
    lines.append(pair(f"Hai {name}!", f"Hai! Saya bukan {name}, tapi saya ALand-AI 😄 Ada yang bisa saya bantu?"))
    lines.append(pair(f"Halo {name}", f"Halo! Sepertinya kamu salah orang, saya ALand-AI 😊"))

print(f"Bagian 1 (casual): {len(lines)} entries")

# ── 3. Pengetahuan umum Indonesia ───────────────────────────────────────────
indo_facts = [
    ("Apa ibu kota Indonesia?", "Ibu kota Indonesia adalah Jakarta (saat ini), dan sedang dipindahkan ke Nusantara di Kalimantan Timur."),
    ("Apa ibu kota baru Indonesia?", "Ibu kota baru Indonesia adalah Nusantara, terletak di Kalimantan Timur."),
    ("Berapa jumlah pulau di Indonesia?", "Indonesia memiliki sekitar 17.000 pulau, menjadikannya negara kepulauan terbesar di dunia."),
    ("Apa bahasa resmi Indonesia?", "Bahasa resmi Indonesia adalah Bahasa Indonesia."),
    ("Apa mata uang Indonesia?", "Mata uang Indonesia adalah Rupiah (IDR)."),
    ("Siapa presiden pertama Indonesia?", "Presiden pertama Indonesia adalah Ir. Soekarno, menjabat dari 1945 hingga 1967."),
    ("Kapan Indonesia merdeka?", "Indonesia merdeka pada tanggal 17 Agustus 1945."),
    ("Siapa yang memproklamasikan kemerdekaan Indonesia?", "Kemerdekaan Indonesia diproklamasikan oleh Soekarno dan Mohammad Hatta pada 17 Agustus 1945."),
    ("Apa lagu kebangsaan Indonesia?", "Lagu kebangsaan Indonesia adalah Indonesia Raya, diciptakan oleh W.R. Supratman."),
    ("Apa lambang negara Indonesia?", "Lambang negara Indonesia adalah Garuda Pancasila."),
    ("Apa semboyan Indonesia?", "Semboyan Indonesia adalah Bhinneka Tunggal Ika, yang berarti Berbeda-beda tetapi tetap satu."),
    ("Berapa jumlah provinsi di Indonesia?", "Indonesia memiliki 38 provinsi."),
    ("Apa gunung tertinggi di Indonesia?", "Gunung tertinggi di Indonesia adalah Puncak Jaya (Carstensz Pyramid) di Papua, setinggi 4.884 meter."),
    ("Apa sungai terpanjang di Indonesia?", "Sungai terpanjang di Indonesia adalah Sungai Kapuas di Kalimantan Barat, sepanjang sekitar 1.143 km."),
    ("Apa danau terbesar di Indonesia?", "Danau terbesar di Indonesia adalah Danau Toba di Sumatera Utara."),
    ("Apa agama mayoritas di Indonesia?", "Agama mayoritas di Indonesia adalah Islam, dianut oleh sekitar 87% penduduk."),
    ("Berapa jumlah penduduk Indonesia?", "Jumlah penduduk Indonesia sekitar 270-280 juta jiwa, menjadikannya negara berpenduduk terbesar ke-4 di dunia."),
    ("Apa makanan nasional Indonesia?", "Indonesia memiliki banyak makanan khas, namun Nasi Goreng sering disebut sebagai makanan nasional."),
    ("Apa olahraga favorit Indonesia?", "Olahraga favorit Indonesia antara lain bulu tangkis (badminton), sepak bola, dan voli."),
    ("Berapa medali emas olimpiade Indonesia?", "Indonesia telah meraih puluhan medali emas olimpiade, mayoritas dari cabang bulu tangkis."),
    ("Apa itu Pancasila?", "Pancasila adalah dasar negara Indonesia yang terdiri dari 5 sila: Ketuhanan, Kemanusiaan, Persatuan, Kerakyatan, dan Keadilan."),
    ("Apa itu UUD 1945?", "UUD 1945 adalah Undang-Undang Dasar Negara Republik Indonesia yang menjadi konstitusi tertinggi negara."),
    ("Apa itu Bhinneka Tunggal Ika?", "Bhinneka Tunggal Ika adalah semboyan Indonesia yang berarti 'Berbeda-beda tetapi tetap satu jua', mencerminkan keberagaman bangsa."),
    ("Di mana letak Indonesia?", "Indonesia terletak di Asia Tenggara, di antara Samudra Hindia dan Samudra Pasifik, serta antara benua Asia dan Australia."),
    ("Apa iklim Indonesia?", "Indonesia beriklim tropis dengan dua musim: musim hujan dan musim kemarau."),
    ("Apa itu Batik?", "Batik adalah kain tradisional Indonesia dengan motif khas yang dibuat menggunakan teknik pewarnaan lilin. Diakui UNESCO sebagai warisan budaya."),
    ("Apa itu Wayang?", "Wayang adalah seni pertunjukan boneka tradisional Indonesia, biasanya menceritakan kisah Mahabharata atau Ramayana. Diakui UNESCO."),
    ("Apa itu Gamelan?", "Gamelan adalah ansambel musik tradisional Indonesia yang terdiri dari instrumen perkusi seperti gong, kenong, dan saron."),
    ("Apa itu Reog Ponorogo?", "Reog Ponorogo adalah kesenian tradisional dari Ponorogo, Jawa Timur, terkenal dengan topeng singa besar yang dihiasi bulu merak."),
    ("Apa itu Kecak?", "Kecak adalah tarian tradisional Bali yang menampilkan puluhan penari pria yang berteriak 'cak' secara berirama, menceritakan kisah Ramayana."),
]
for q, a in indo_facts:
    lines.append(pair(q, a))

# Variasi pertanyaan yang sama
for q, a in indo_facts[:10]:
    lines.append(pair(q.replace("Apa ", "Tolong jelaskan "), a))
    lines.append(pair(q.replace("Apa ", "Bisa ceritakan "), a))

print(f"Bagian 2 (Indonesia facts): {len(lines)} entries")

# ── 4. Kuliner Indonesia ─────────────────────────────────────────────────────
kuliner = [
    ("Apa itu Rendang?", "Rendang adalah masakan daging sapi khas Minangkabau yang dimasak lama dengan santan dan rempah-rempah hingga kering dan kaya rasa. Berasal dari Sumatera Barat."),
    ("Apa itu Nasi Goreng?", "Nasi Goreng adalah nasi yang digoreng dengan bumbu kecap, bawang, dan rempah. Sering disebut sebagai makanan nasional Indonesia."),
    ("Apa itu Soto?", "Soto adalah sup tradisional Indonesia dengan kuah kaldu, daging, dan berbagai pelengkap. Ada banyak variasi seperti Soto Ayam, Soto Betawi, dan Soto Lamongan."),
    ("Apa itu Gado-gado?", "Gado-gado adalah salad sayuran rebus khas Indonesia yang disajikan dengan saus kacang. Berasal dari Jakarta."),
    ("Apa itu Sate?", "Sate adalah daging yang ditusuk dengan tusukan bambu lalu dibakar, disajikan dengan saus kacang atau kecap. Ada sate ayam, sate kambing, dan lainnya."),
    ("Apa itu Bakso?", "Bakso adalah bola daging sapi yang disajikan dalam kuah kaldu panas dengan mie, tahu, dan pelengkap lainnya. Sangat populer di seluruh Indonesia."),
    ("Apa itu Mie Ayam?", "Mie Ayam adalah mie kuning dengan topping ayam cincang berbumbu, disajikan dengan kuah kaldu. Salah satu makanan favorit Indonesia."),
    ("Apa itu Pempek?", "Pempek adalah makanan khas Palembang dari tepung sagu dan ikan, disajikan dengan kuah cuka pedas manis yang disebut cuko."),
    ("Apa itu Gudeg?", "Gudeg adalah masakan khas Yogyakarta dari nangka muda yang dimasak dengan santan dan gula merah hingga berwarna coklat dan manis."),
    ("Apa itu Rawon?", "Rawon adalah sup daging sapi hitam khas Jawa Timur, warnanya hitam berasal dari kluwek. Disajikan dengan nasi, tauge, dan telur asin."),
    ("Apa itu Opor Ayam?", "Opor Ayam adalah ayam yang dimasak dalam kuah santan kuning berbumbu rempah. Sering disajikan saat Lebaran."),
    ("Apa itu Ketoprak?", "Ketoprak adalah makanan khas Jakarta berupa tahu, bihun, lontong, dan sayuran dengan saus kacang dan kecap."),
    ("Apa itu Martabak?", "Martabak adalah makanan populer Indonesia. Ada martabak manis (tebal, isi coklat/keju) dan martabak telur (tipis, isi daging dan telur)."),
    ("Apa itu Klepon?", "Klepon adalah kue tradisional Indonesia berbentuk bola hijau dari tepung ketan, berisi gula merah, dan dibalut kelapa parut."),
    ("Apa itu Onde-onde?", "Onde-onde adalah kue goreng berbentuk bola dari tepung ketan, berisi kacang hijau manis, dan dibalut wijen."),
    ("Apa itu Tempe?", "Tempe adalah makanan tradisional Indonesia dari kedelai yang difermentasi. Kaya protein dan sangat populer sebagai lauk."),
    ("Apa itu Tahu?", "Tahu adalah makanan dari kedelai yang dipadatkan. Bisa digoreng, direbus, atau dijadikan berbagai masakan."),
    ("Apa itu Kerupuk?", "Kerupuk adalah camilan renyah Indonesia yang dibuat dari tepung tapioka atau bahan lain, digoreng hingga mengembang."),
    ("Apa itu Sambal?", "Sambal adalah saus pedas khas Indonesia yang terbuat dari cabai, bawang, dan rempah. Ada ratusan jenis sambal di Indonesia."),
    ("Apa itu Nasi Padang?", "Nasi Padang adalah nasi dengan berbagai lauk khas Minangkabau seperti rendang, gulai, dan sambal hijau. Terkenal di seluruh Indonesia."),
    ("Apa itu Es Teler?", "Es Teler adalah minuman/dessert Indonesia berisi alpukat, kelapa muda, nangka, dan sirup manis dengan es serut."),
    ("Apa itu Cendol?", "Cendol adalah minuman tradisional Indonesia berisi jeli hijau dari tepung beras, santan, dan gula merah cair."),
    ("Apa itu Dawet?", "Dawet adalah minuman tradisional Jawa mirip cendol, berisi jeli hijau dengan santan dan gula merah."),
    ("Apa itu Lontong?", "Lontong adalah nasi yang dimasak dalam bungkus daun pisang hingga padat. Sering disajikan dengan sate atau opor."),
    ("Apa itu Ketupat?", "Ketupat adalah nasi yang dimasak dalam anyaman daun kelapa. Identik dengan perayaan Lebaran di Indonesia."),
]
for q, a in kuliner:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Ceritakan tentang "), a))
    lines.append(pair(q.replace("Apa itu ", "Jelaskan "), a))

print(f"Bagian 3 (kuliner): {len(lines)} entries")

# ── 5. Geografi dunia ────────────────────────────────────────────────────────
geo = [
    ("Ibu kota Amerika Serikat?", "Ibu kota Amerika Serikat adalah Washington, D.C."),
    ("Ibu kota Inggris?", "Ibu kota Inggris adalah London."),
    ("Ibu kota Prancis?", "Ibu kota Prancis adalah Paris."),
    ("Ibu kota Jerman?", "Ibu kota Jerman adalah Berlin."),
    ("Ibu kota Italia?", "Ibu kota Italia adalah Roma."),
    ("Ibu kota Spanyol?", "Ibu kota Spanyol adalah Madrid."),
    ("Ibu kota Rusia?", "Ibu kota Rusia adalah Moskow."),
    ("Ibu kota China?", "Ibu kota China adalah Beijing."),
    ("Ibu kota Jepang?", "Ibu kota Jepang adalah Tokyo."),
    ("Ibu kota Korea Selatan?", "Ibu kota Korea Selatan adalah Seoul."),
    ("Ibu kota India?", "Ibu kota India adalah New Delhi."),
    ("Ibu kota Australia?", "Ibu kota Australia adalah Canberra."),
    ("Ibu kota Brasil?", "Ibu kota Brasil adalah Brasília."),
    ("Ibu kota Kanada?", "Ibu kota Kanada adalah Ottawa."),
    ("Ibu kota Meksiko?", "Ibu kota Meksiko adalah Mexico City."),
    ("Ibu kota Argentina?", "Ibu kota Argentina adalah Buenos Aires."),
    ("Ibu kota Mesir?", "Ibu kota Mesir adalah Kairo."),
    ("Ibu kota Afrika Selatan?", "Ibu kota Afrika Selatan adalah Pretoria (eksekutif), Cape Town (legislatif), dan Bloemfontein (yudisial)."),
    ("Ibu kota Arab Saudi?", "Ibu kota Arab Saudi adalah Riyadh."),
    ("Ibu kota Turki?", "Ibu kota Turki adalah Ankara."),
    ("Ibu kota Malaysia?", "Ibu kota Malaysia adalah Kuala Lumpur."),
    ("Ibu kota Singapura?", "Singapura adalah negara kota, sehingga ibu kotanya adalah Singapura itu sendiri."),
    ("Ibu kota Thailand?", "Ibu kota Thailand adalah Bangkok."),
    ("Ibu kota Vietnam?", "Ibu kota Vietnam adalah Hanoi."),
    ("Ibu kota Filipina?", "Ibu kota Filipina adalah Manila."),
    ("Mata uang Amerika Serikat?", "Mata uang Amerika Serikat adalah Dolar (USD)."),
    ("Mata uang Inggris?", "Mata uang Inggris adalah Pound Sterling (GBP)."),
    ("Mata uang Eropa?", "Mata uang Eropa (zona euro) adalah Euro (EUR)."),
    ("Mata uang Jepang?", "Mata uang Jepang adalah Yen (JPY)."),
    ("Mata uang China?", "Mata uang China adalah Yuan atau Renminbi (CNY)."),
    ("Mata uang Korea Selatan?", "Mata uang Korea Selatan adalah Won (KRW)."),
    ("Mata uang Australia?", "Mata uang Australia adalah Dolar Australia (AUD)."),
    ("Mata uang India?", "Mata uang India adalah Rupee (INR)."),
    ("Mata uang Malaysia?", "Mata uang Malaysia adalah Ringgit (MYR)."),
    ("Mata uang Singapura?", "Mata uang Singapura adalah Dolar Singapura (SGD)."),
    ("Negara terbesar di dunia?", "Negara terbesar di dunia berdasarkan luas wilayah adalah Rusia, dengan luas sekitar 17,1 juta km²."),
    ("Negara terkecil di dunia?", "Negara terkecil di dunia adalah Vatikan, dengan luas hanya sekitar 0,44 km²."),
    ("Negara berpenduduk terbanyak?", "Negara berpenduduk terbanyak di dunia adalah India, mengalahkan China sejak 2023."),
    ("Benua terbesar di dunia?", "Benua terbesar di dunia adalah Asia."),
    ("Samudra terbesar di dunia?", "Samudra terbesar di dunia adalah Samudra Pasifik."),
    ("Gunung tertinggi di dunia?", "Gunung tertinggi di dunia adalah Gunung Everest di Nepal/Tibet, setinggi 8.849 meter."),
    ("Sungai terpanjang di dunia?", "Sungai terpanjang di dunia adalah Sungai Nil di Afrika, sepanjang sekitar 6.650 km."),
    ("Danau terbesar di dunia?", "Danau terbesar di dunia adalah Laut Kaspia (dianggap danau), diikuti Danau Superior di Amerika Utara."),
    ("Gurun terbesar di dunia?", "Gurun terbesar di dunia adalah Gurun Antartika, diikuti Gurun Arktik, lalu Gurun Sahara di Afrika."),
]
for q, a in geo:
    lines.append(pair(q, a))
    # variasi
    lines.append(pair("Apa " + q.lower(), a))

print(f"Bagian 4 (geografi): {len(lines)} entries")

# ── 6. Sains & teknologi ─────────────────────────────────────────────────────
sains = [
    ("Apa itu fotosintesis?", "Fotosintesis adalah proses tumbuhan mengubah cahaya matahari, air, dan CO₂ menjadi glukosa dan oksigen. Rumus: 6CO₂ + 6H₂O + cahaya → C₆H₁₂O₆ + 6O₂."),
    ("Apa itu gravitasi?", "Gravitasi adalah gaya tarik-menarik antara dua benda bermassa. Di Bumi, gravitasi menarik benda ke pusat bumi dengan percepatan sekitar 9,8 m/s²."),
    ("Apa itu atom?", "Atom adalah unit terkecil dari materi yang masih mempertahankan sifat kimia suatu unsur. Terdiri dari proton, neutron (di inti), dan elektron (di kulit)."),
    ("Apa itu DNA?", "DNA (Deoxyribonucleic Acid) adalah molekul yang membawa informasi genetik makhluk hidup. Berbentuk double helix dan terdapat di dalam inti sel."),
    ("Apa itu evolusi?", "Evolusi adalah perubahan bertahap pada sifat-sifat populasi makhluk hidup dari generasi ke generasi, dipengaruhi oleh seleksi alam."),
    ("Apa itu sel?", "Sel adalah unit terkecil kehidupan. Ada sel prokariotik (tanpa inti, seperti bakteri) dan sel eukariotik (dengan inti, seperti sel manusia)."),
    ("Apa itu ekosistem?", "Ekosistem adalah sistem yang terdiri dari makhluk hidup (biotik) dan lingkungan fisiknya (abiotik) yang saling berinteraksi."),
    ("Apa itu rantai makanan?", "Rantai makanan adalah urutan perpindahan energi dari satu organisme ke organisme lain melalui proses makan dan dimakan."),
    ("Apa itu kecepatan cahaya?", "Kecepatan cahaya di ruang hampa adalah sekitar 299.792.458 meter per detik, atau sekitar 300.000 km/s."),
    ("Apa itu energi?", "Energi adalah kemampuan untuk melakukan kerja. Ada berbagai bentuk energi: kinetik, potensial, panas, listrik, kimia, dan nuklir."),
    ("Apa itu AI?", "AI (Artificial Intelligence) atau Kecerdasan Buatan adalah simulasi kecerdasan manusia oleh mesin, terutama komputer, untuk belajar, bernalar, dan memecahkan masalah."),
    ("Apa itu machine learning?", "Machine Learning adalah cabang AI di mana komputer belajar dari data tanpa diprogram secara eksplisit. Contoh: rekomendasi Netflix, deteksi spam."),
    ("Apa itu internet?", "Internet adalah jaringan global komputer yang saling terhubung, memungkinkan pertukaran data dan komunikasi di seluruh dunia."),
    ("Apa itu cloud computing?", "Cloud computing adalah layanan komputasi (server, penyimpanan, database, software) melalui internet, tanpa perlu infrastruktur fisik sendiri."),
    ("Apa itu blockchain?", "Blockchain adalah teknologi penyimpanan data terdesentralisasi dalam bentuk rantai blok yang tidak bisa diubah, digunakan dalam cryptocurrency."),
    ("Apa itu Python?", "Python adalah bahasa pemrograman tingkat tinggi yang mudah dipelajari, populer untuk data science, AI, web development, dan otomasi."),
    ("Apa itu JavaScript?", "JavaScript adalah bahasa pemrograman yang digunakan untuk membuat halaman web interaktif. Berjalan di browser dan juga di server (Node.js)."),
    ("Apa itu API?", "API (Application Programming Interface) adalah antarmuka yang memungkinkan dua aplikasi berkomunikasi satu sama lain."),
    ("Apa itu database?", "Database adalah kumpulan data yang terorganisir dan dapat diakses, dikelola, serta diperbarui secara efisien. Contoh: MySQL, PostgreSQL, MongoDB."),
    ("Apa itu Linux?", "Linux adalah sistem operasi open-source berbasis Unix yang banyak digunakan di server, superkomputer, dan perangkat Android."),
]
for q, a in sains:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Jelaskan "), a))
    lines.append(pair(q.replace("Apa itu ", "Tolong jelaskan apa itu "), a))

print(f"Bagian 5 (sains & teknologi): {len(lines)} entries")

# ── 7. Matematika dasar ──────────────────────────────────────────────────────
# Tabel perkalian 1-20
for i in range(1, 21):
    for j in range(1, 21):
        result = i * j
        lines.append(pair(f"Berapa {i} kali {j}?", f"{i} × {j} = {result}"))
        lines.append(pair(f"Berapa {i} × {j}?", f"{i} × {j} = {result}"))
        if i != j:
            lines.append(pair(f"{i} times {j}?", f"{i} × {j} = {result}"))

# Tabel pembagian
for i in range(1, 21):
    for j in range(1, 11):
        result = i * j
        lines.append(pair(f"Berapa {result} dibagi {j}?", f"{result} ÷ {j} = {i}"))

# Persen umum
pct_data = [(10,100),(20,100),(25,100),(50,100),(75,100),(10,200),(20,200),(25,200),(50,200),(10,1000),(20,1000),(25,1000),(50,1000),(75,1000),(10,500),(20,500),(50,500)]
for p, n in pct_data:
    result = p * n // 100
    lines.append(pair(f"Berapa {p}% dari {n}?", f"{p}% dari {n} = {result}"))
    lines.append(pair(f"{p} persen dari {n}?", f"{p}% dari {n} = {result}"))

print(f"Bagian 6 (matematika): {len(lines)} entries")

# ── 8. Bahasa & kosakata Indonesia ──────────────────────────────────────────
antonim = [
    ("besar", "kecil"), ("tinggi", "rendah"), ("panjang", "pendek"),
    ("cepat", "lambat"), ("kuat", "lemah"), ("pintar", "bodoh"),
    ("kaya", "miskin"), ("tua", "muda"), ("panas", "dingin"),
    ("terang", "gelap"), ("keras", "lunak"), ("berat", "ringan"),
    ("lebar", "sempit"), ("dalam", "dangkal"), ("jauh", "dekat"),
    ("awal", "akhir"), ("naik", "turun"), ("masuk", "keluar"),
    ("datang", "pergi"), ("hidup", "mati"), ("benar", "salah"),
    ("baik", "buruk"), ("senang", "sedih"), ("rajin", "malas"),
    ("bersih", "kotor"), ("ramai", "sepi"), ("mudah", "sulit"),
    ("aman", "berbahaya"), ("cinta", "benci"), ("suka", "tidak suka"),
]
for kata, antonim_kata in antonim:
    lines.append(pair(f"Apa antonim dari {kata}?", f"Antonim dari '{kata}' adalah '{antonim_kata}'."))
    lines.append(pair(f"Lawan kata dari {kata}?", f"Lawan kata dari '{kata}' adalah '{antonim_kata}'."))
    lines.append(pair(f"Kebalikan dari {kata}?", f"Kebalikan dari '{kata}' adalah '{antonim_kata}'."))

sinonim = [
    ("bagus", ["baik", "indah", "cantik", "elok"]),
    ("besar", ["agung", "raya", "akbar"]),
    ("cepat", ["lekas", "segera", "kilat"]),
    ("senang", ["gembira", "bahagia", "suka"]),
    ("sedih", ["duka", "susah", "murung"]),
    ("pintar", ["cerdas", "pandai", "cerdik"]),
    ("cantik", ["indah", "elok", "molek"]),
    ("berani", ["gagah", "perkasa", "jantan"]),
    ("takut", ["gentar", "ngeri", "khawatir"]),
    ("marah", ["murka", "gusar", "berang"]),
]
for kata, sinonim_list in sinonim:
    sinonim_str = ", ".join(sinonim_list)
    lines.append(pair(f"Apa sinonim dari {kata}?", f"Sinonim dari '{kata}' antara lain: {sinonim_str}."))
    lines.append(pair(f"Persamaan kata dari {kata}?", f"Persamaan kata dari '{kata}' antara lain: {sinonim_str}."))

print(f"Bagian 7 (bahasa): {len(lines)} entries")

# ── 9. Sejarah & tokoh dunia ─────────────────────────────────────────────────
sejarah = [
    ("Siapa Albert Einstein?", "Albert Einstein (1879-1955) adalah fisikawan teoretis Jerman-Amerika yang mengembangkan teori relativitas. Meraih Nobel Fisika 1921."),
    ("Siapa Isaac Newton?", "Isaac Newton (1643-1727) adalah ilmuwan Inggris yang menemukan hukum gravitasi, hukum gerak, dan mengembangkan kalkulus."),
    ("Siapa Charles Darwin?", "Charles Darwin (1809-1882) adalah naturalis Inggris yang mengembangkan teori evolusi melalui seleksi alam dalam bukunya 'On the Origin of Species'."),
    ("Siapa Marie Curie?", "Marie Curie (1867-1934) adalah ilmuwan Polandia-Prancis, wanita pertama yang meraih Nobel, dan satu-satunya yang meraih Nobel di dua bidang berbeda (Fisika dan Kimia)."),
    ("Siapa Leonardo da Vinci?", "Leonardo da Vinci (1452-1519) adalah seniman, ilmuwan, dan penemu Italia Renaissance. Terkenal dengan lukisan Mona Lisa dan The Last Supper."),
    ("Siapa Napoleon Bonaparte?", "Napoleon Bonaparte (1769-1821) adalah pemimpin militer dan kaisar Prancis yang menaklukkan sebagian besar Eropa pada awal abad ke-19."),
    ("Siapa Abraham Lincoln?", "Abraham Lincoln (1809-1865) adalah presiden ke-16 Amerika Serikat yang memimpin negara selama Perang Saudara dan menghapus perbudakan."),
    ("Siapa Mahatma Gandhi?", "Mahatma Gandhi (1869-1948) adalah pemimpin kemerdekaan India yang terkenal dengan gerakan perlawanan tanpa kekerasan (non-violence)."),
    ("Siapa Nelson Mandela?", "Nelson Mandela (1918-2013) adalah pemimpin anti-apartheid Afrika Selatan yang dipenjara 27 tahun, lalu menjadi presiden pertama kulit hitam Afrika Selatan."),
    ("Siapa Soekarno?", "Ir. Soekarno (1901-1970) adalah proklamator dan presiden pertama Indonesia, pemimpin pergerakan kemerdekaan Indonesia dari penjajahan Belanda."),
    ("Siapa Mohammad Hatta?", "Mohammad Hatta (1902-1980) adalah wakil presiden pertama Indonesia, proklamator kemerdekaan bersama Soekarno, dan dikenal sebagai Bapak Koperasi Indonesia."),
    ("Siapa R.A. Kartini?", "R.A. Kartini (1879-1904) adalah pahlawan nasional Indonesia yang memperjuangkan emansipasi wanita dan pendidikan bagi perempuan Indonesia."),
    ("Siapa Diponegoro?", "Pangeran Diponegoro (1785-1855) adalah pahlawan nasional Indonesia yang memimpin Perang Diponegoro (1825-1830) melawan penjajahan Belanda."),
    ("Kapan Perang Dunia II berakhir?", "Perang Dunia II berakhir pada tahun 1945: di Eropa pada 8 Mei 1945 (V-E Day) dan di Pasifik pada 2 September 1945 (V-J Day)."),
    ("Kapan Perang Dunia I terjadi?", "Perang Dunia I terjadi dari tahun 1914 hingga 1918, melibatkan sebagian besar negara-negara Eropa dan sekutunya."),
    ("Apa itu Revolusi Industri?", "Revolusi Industri adalah periode transformasi besar dari ekonomi agraris ke industri manufaktur, dimulai di Inggris sekitar tahun 1760-1840."),
    ("Apa itu Perang Dingin?", "Perang Dingin adalah ketegangan geopolitik antara Amerika Serikat dan Uni Soviet dari 1947 hingga 1991, tanpa konflik militer langsung."),
    ("Kapan tembok Berlin runtuh?", "Tembok Berlin runtuh pada 9 November 1989, menandai berakhirnya pemisahan Jerman Timur dan Barat."),
    ("Apa itu Renaissance?", "Renaissance adalah periode kebangkitan seni, budaya, dan ilmu pengetahuan di Eropa dari abad ke-14 hingga ke-17, dimulai di Italia."),
    ("Siapa Christopher Columbus?", "Christopher Columbus (1451-1506) adalah penjelajah Italia yang berlayar untuk Spanyol dan menemukan benua Amerika pada tahun 1492."),
]
for q, a in sejarah:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Siapa ", "Ceritakan tentang ").replace("Kapan ", "Kapan tepatnya ").replace("Apa itu ", "Tolong jelaskan "), a))

print(f"Bagian 8 (sejarah): {len(lines)} entries")

# ── 10. Peribahasa & ungkapan Indonesia ─────────────────────────────────────
peribahasa = [
    ("Ada udang di balik batu", "Ada maksud tersembunyi di balik suatu perbuatan atau perkataan."),
    ("Air beriak tanda tak dalam", "Orang yang banyak bicara biasanya tidak berilmu tinggi."),
    ("Bagai air di daun talas", "Tidak tetap pendirian, mudah berubah-ubah."),
    ("Bersatu kita teguh bercerai kita runtuh", "Persatuan membuat kita kuat, perpecahan membuat kita lemah."),
    ("Buah jatuh tidak jauh dari pohonnya", "Sifat anak biasanya mirip dengan orang tuanya."),
    ("Di mana bumi dipijak di situ langit dijunjung", "Harus menghormati adat dan kebiasaan di tempat kita berada."),
    ("Habis manis sepah dibuang", "Setelah tidak berguna lagi, seseorang ditinggalkan begitu saja."),
    ("Hujan emas di negeri orang hujan batu di negeri sendiri lebih baik negeri sendiri", "Sebaik-baiknya tempat orang lain, tempat sendiri tetap lebih baik."),
    ("Karena nila setitik rusak susu sebelanga", "Karena kesalahan kecil, semua kebaikan yang telah dilakukan menjadi sia-sia."),
    ("Lebih baik mati berkalang tanah daripada hidup bercermin bangkai", "Lebih baik mati dengan kehormatan daripada hidup dengan menanggung malu."),
    ("Malu bertanya sesat di jalan", "Jika tidak mau bertanya, akan mengalami kesulitan atau kesalahan."),
    ("Nasi sudah menjadi bubur", "Sesuatu yang sudah terjadi tidak bisa diubah lagi."),
    ("Pagar makan tanaman", "Orang yang seharusnya melindungi malah merusak."),
    ("Sambil menyelam minum air", "Melakukan dua pekerjaan sekaligus dalam satu waktu."),
    ("Seperti katak dalam tempurung", "Orang yang wawasannya sempit karena tidak mau melihat dunia luar."),
    ("Tak ada rotan akar pun jadi", "Jika tidak ada yang terbaik, yang ada pun bisa digunakan."),
    ("Tong kosong nyaring bunyinya", "Orang yang kurang pengetahuan biasanya paling banyak bicara."),
]
for pb, arti in peribahasa:
    lines.append(pair(f"Apa arti peribahasa '{pb}'?", f"Peribahasa '{pb}' berarti: {arti}"))
    lines.append(pair(f"Jelaskan peribahasa {pb}", f"Peribahasa '{pb}' berarti: {arti}"))
    lines.append(pair(f"Apa maksud dari {pb}?", f"Maksud dari peribahasa '{pb}' adalah: {arti}"))

print(f"Bagian 9 (peribahasa): {len(lines)} entries")

# ── 11. Hewan & tumbuhan ─────────────────────────────────────────────────────
hewan = [
    ("Apa itu Komodo?", "Komodo (Varanus komodoensis) adalah kadal terbesar di dunia, hanya ada di Indonesia (Pulau Komodo, Rinca, Flores). Panjang bisa mencapai 3 meter."),
    ("Apa itu Orangutan?", "Orangutan adalah kera besar yang hanya ada di Kalimantan dan Sumatera. Nama 'orangutan' berasal dari bahasa Melayu yang berarti 'orang hutan'."),
    ("Apa itu Harimau Sumatera?", "Harimau Sumatera (Panthera tigris sumatrae) adalah subspesies harimau terkecil yang hanya ada di Pulau Sumatera, Indonesia. Status: kritis terancam punah."),
    ("Apa itu Cendrawasih?", "Cendrawasih adalah burung eksotis dari Papua yang terkenal dengan bulu indahnya. Sering disebut 'burung surga'. Ada sekitar 40 spesies di Papua."),
    ("Apa itu Badak Jawa?", "Badak Jawa (Rhinoceros sondaicus) adalah salah satu mamalia paling langka di dunia, hanya tersisa di Taman Nasional Ujung Kulon, Banten."),
    ("Apa itu Gajah Sumatera?", "Gajah Sumatera (Elephas maximus sumatranus) adalah subspesies gajah Asia yang lebih kecil, hanya ada di Sumatera. Status: kritis terancam punah."),
    ("Apa itu Anoa?", "Anoa adalah kerbau kerdil endemik Sulawesi, Indonesia. Merupakan bovid terkecil di dunia. Ada dua spesies: Anoa Dataran Rendah dan Anoa Pegunungan."),
    ("Apa itu Tapir?", "Tapir adalah mamalia herbivora dengan moncong panjang yang fleksibel. Di Indonesia, Tapir Malaya hidup di Sumatera."),
    ("Apa itu Rafflesia?", "Rafflesia arnoldii adalah bunga terbesar di dunia, berdiameter hingga 1 meter. Tumbuh di hutan Sumatera dan Kalimantan, tidak memiliki daun atau batang."),
    ("Apa itu Bunga Bangkai?", "Bunga Bangkai (Amorphophallus titanum) adalah tanaman dengan bunga majemuk terbesar di dunia. Mengeluarkan bau busuk untuk menarik serangga penyerbuk."),
]
for q, a in hewan:
    lines.append(pair(q, a))
    lines.append(pair(q.replace("Apa itu ", "Ceritakan tentang "), a))

print(f"Bagian 10 (hewan): {len(lines)} entries")

# ── 12. Tulis ke dataset ─────────────────────────────────────────────────────
with open(DATASET, "a", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

print(f"\n✅ Total {len(lines)} entri baru ditambahkan ke dataset")
print(f"📁 Dataset: {DATASET}")
