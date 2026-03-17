"""
Manual corrections for IDSpider1 translation dictionary.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from .schema_translator import (
    extract_identifiers_from_tables_json,
    build_identifier_translation_dict,
    split_identifier,
    detect_per_table_collisions,
    detect_table_name_collisions,
    detect_db_id_collisions,
    build_collision_fixes,
)
from .config import SPIDER_TABLES_JSON, SQL_KEYWORDS, NEVER_TRANSLATE_TOKENS



# WORD-LEVEL TRANSLATION FIXES


WORD_FIXES = {
    #  Core structural words 
    "date": "tanggal",
    "time": "waktu",
    "year": "tahun",
    "month": "bulan",
    "day": "hari",
    "hour": "jam",
    "minute": "menit",
    "second": "detik",
    "week": "minggu",
    "name": "nama",
    "title": "judul",
    "code": "kode",
    "number": "nomor",
    "count": "jumlah",
    "type": "tipe",
    "status": "status",
    "level": "tingkat",
    "class": "kelas",
    "category": "kategori",
    "description": "deskripsi",
    "details": "rincian",
    "note": "catatan",
    "notes": "catatan",
    "comment": "komentar",
    "comments": "komentar",
    "value": "nilai",  # FIX: was "nilai_data"
    "amount": "jumlah_uang",
    "quantity": "kuantitas",
    "total": "total",
    "price": "harga",
    "cost": "biaya",
    "fee": "biaya_tambahan",
    "rate": "tarif",
    "size": "ukuran",
    "length": "panjang",
    "width": "lebar",
    "height": "tinggi",
    "weight": "berat",
    "age": "usia",
    "score": "skor",
    "point": "poin",
    "points": "poin",
    "rank": "peringkat",
    "ranking": "peringkat",
    "position": "posisi",
    "grade": "nilai_rapor",
    "rating": "peringkat_nilai",
    "result": "hasil",
    "outcome": "hasil_akhir",
    "record": "catatan",  # FIX: was "rekaman" (that means audio recording)
    "entry": "entri",
    "section": "bagian",
    "part": "komponen",  # FIX: was "bagian_dari"
    "role": "peran",
    "order": "pesanan",
    "address": "alamat",
    "location": "lokasi",
    "place": "tempat",
    "area": "area",
    "region": "wilayah",
    "zone": "zona",
    "percentage": "persentase",
    "percent": "persen",

    #  People & roles 
    "people": "orang",
    "person": "individu",
    "member": "anggota",
    "group": "kelompok",
    "team": "tim",
    "staff": "staf",
    "employee": "karyawan",
    "employees": "karyawan",
    "manager": "manajer",
    "director": "direktur",
    "president": "presiden",
    "customer": "pelanggan",
    "client": "klien",
    "user": "pengguna",
    "author": "penulis",
    "artist": "seniman",
    "singer": "penyanyi",
    "player": "pemain",
    "doctor": "dokter",
    "patient": "pasien",
    "nurse": "perawat",
    "teacher": "guru",
    "student": "mahasiswa",
    "professor": "profesor",
    "instructor": "instruktur",
    "coach": "pelatih",
    "captain": "kapten",
    "judge": "hakim",
    "referee": "wasit",
    "owner": "pemilik",
    "voter": "pemilih",
    "candidate": "kandidat",
    "winner": "pemenang",
    "loser": "pecundang",
    "guest": "tamu",
    "host": "tuan_rumah",
    "pilot": "pilot",
    "driver": "pengemudi",
    "engineer": "insinyur",
    "technician": "teknisi",
    "scientist": "ilmuwan",
    "researcher": "peneliti",
    "agent": "agen",
    "representative": "perwakilan",
    "delegate": "delegasi",
    "official": "resmi",  # FIX: was "pejabat" (noun, not adj)
    "principal": "utama",  # FIX: was "kepala_sekolah"
    "parent": "induk",  # FIX: was "orang_tua" (biological parent, not hierarchical)
    "individual": "individu",
    "professional": "profesional",
    "expert": "ahli",
    "specialist": "spesialis",
    "advisor": "penasihat",
    "chairman": "ketua",
    "founder": "pendiri",
    "entrepreneur": "pengusaha",
    "investor": "investor",
    "tourist": "wisatawan",
    "visitor": "pengunjung",
    "passenger": "penumpang",
    "swimmer": "perenang",
    "wrestler": "pegulat",
    "gymnast": "pesenam",
    "cyclist": "pesepeda",
    "climber": "pendaki",
    "builder": "pembangun",
    "maker": "pembuat",
    "conductor": "konduktor",
    "composer": "komposer",
    "writer": "penulis",
    "editor": "editor",
    "reviewer": "penilai",
    "nominee": "nominasi",
    "spokesman": "juru_bicara",
    "perpetrator": "pelaku",
    "journalist": "jurnalis",
    "photographer": "fotografer",
    "volunteer": "sukarelawan",

    #  Organizations & places 
    "company": "perusahaan",
    "organization": "organisasi",
    "organisation": "organisasi",
    "department": "departemen",
    "school": "sekolah",
    "college": "perguruan_tinggi",
    "university": "universitas",
    "institute": "institut",
    "institution": "institusi",
    "academy": "akademi",
    "library": "perpustakaan",
    "hospital": "rumah_sakit",
    "clinic": "klinik",
    "restaurant": "restoran",
    "hotel": "hotel",
    "shop": "toko",  # FIX: was "toko_belanja"
    "store": "toko",
    "market": "pasar",
    "bank": "bank",
    "office": "kantor",
    "factory": "pabrik",
    "warehouse": "gudang",
    "museum": "museum",
    "church": "gereja",
    "temple": "kuil",
    "stadium": "stadion",
    "airport": "bandara",
    "station": "stasiun",
    "port": "pelabuhan",
    "bridge": "jembatan",
    "park": "taman",
    "farm": "pertanian",
    "camp": "kemah",
    "lab": "laboratorium",
    "campus": "kampus",
    "dormitory": "asrama",
    "headquarter": "kantor_pusat",
    "headquarters": "kantor_pusat",
    "branch": "cabang",
    "franchise": "waralaba",
    "chain": "jaringan_toko",
    "gallery": "galeri",
    "theater": "teater",
    "theatre": "teater",
    "cinema": "bioskop",

    #  Geography 
    "country": "negara",
    "state": "negara_bagian",
    "province": "provinsi",
    "county": "kabupaten",
    "city": "kota",
    "town": "kota_kecil",
    "village": "desa",
    "district": "distrik",
    "continent": "benua",
    "island": "pulau",
    "mountain": "gunung",
    "river": "sungai",
    "lake": "danau",
    "ocean": "samudra",
    "sea": "laut",
    "coast": "pantai",
    "border": "perbatasan",
    "capital": "ibu_kota",
    "nation": "bangsa",
    "road": "jalan",
    "street": "jalan_raya",
    "route": "rute",
    "highway": "jalan_tol",
    "neighborhood": "lingkungan",
    "latitude": "lintang",
    "longitude": "bujur",
    "elevation": "ketinggian",
    "altitude": "ketinggian",
    "surface": "permukaan",

    #  Education 
    "semester": "semester",
    "degree": "gelar",
    "faculty": "fakultas",
    "curriculum": "kurikulum",
    "course": "kursus",
    "subject": "subjek",
    "lesson": "pelajaran",
    "exam": "ujian",
    "exams": "ujian",
    "test": "ujian",
    "assignment": "tugas",
    "homework": "pekerjaan_rumah",
    "enrollment": "pendaftaran",
    "registration": "registrasi",
    "certificate": "sertifikat",
    "transcript": "transkrip",
    "graduation": "kelulusan",
    "scholarship": "beasiswa",
    "major": "jurusan",
    "minor": "minor",
    "credit": "sks",
    "credits": "sks",

    #  Time & dates 
    "birth": "lahir",
    "death": "kematian",
    "born": "lahir",
    "died": "meninggal",
    "created": "dibuat",
    "updated": "diperbarui",
    "deleted": "dihapus",
    "modified": "diubah",
    "submitted": "dikirim",
    "approved": "disetujui",
    "rejected": "ditolak",
    "completed": "selesai",
    "pending": "tertunda",
    "cancelled": "dibatalkan",
    "closed": "ditutup",
    "opened": "dibuka",
    "ended": "berakhir",
    "started": "dimulai",
    "reached": "tercapai",
    "assigned": "ditugaskan",
    "released": "dirilis",
    "published": "diterbitkan",
    "expired": "kedaluwarsa",
    "effective": "efektif",
    "scheduled": "dijadwalkan",
    "duration": "durasi",
    "season": "musim",
    "annual": "tahunan",
    "daily": "harian",
    "weekly": "mingguan",
    "monthly": "bulanan",
    "quarterly": "triwulanan",
    "calendar": "kalender",

    #  Finance 
    "salary": "gaji",
    "income": "pendapatan",
    "budget": "anggaran",
    "revenue": "pendapatan",
    "profit": "keuntungan",
    "loss": "kerugian",
    "debt": "utang",
    "payment": "pembayaran",
    "expense": "pengeluaran",
    "tax": "pajak",
    "discount": "diskon",
    "currency": "mata_uang",
    "exchange": "pertukaran",
    "deposit": "deposito",
    "balance": "saldo",
    "invoice": "faktur",
    "account": "akun",
    "transaction": "transaksi",
    "purchase": "pembelian",
    "sales": "penjualan",
    "billing": "penagihan",
    "premium": "premi",
    "insurance": "asuransi",
    "policy": "polis",
    "claim": "klaim",
    "refund": "pengembalian_dana",
    "bonus": "bonus",
    "commission": "komisi",
    "earnings": "penghasilan",
    "investment": "investasi",
    "share": "saham",
    "stock": "stok",
    "asset": "aset",
    "equity": "ekuitas",
    "dividend": "dividen",
    "interest": "bunga",

    #  Products & commerce 
    "product": "produk",
    "products": "produk",
    "item": "barang",
    "items": "barang",
    "brand": "merek",
    "model": "model",
    "version": "versi",
    "color": "warna",
    "colors": "warna",
    "material": "bahan",
    "style": "gaya",
    "feature": "fitur",
    "specification": "spesifikasi",
    "manufacturer": "pabrikan",
    "warranty": "garansi",
    "shipping": "pengiriman",
    "delivery": "pengiriman_barang",
    "return": "pengembalian",
    "complaint": "keluhan",
    "review": "ulasan",
    "feedback": "umpan_balik",
    "catalog": "katalog",
    "inventory": "inventaris",
    "supply": "pasokan",
    "supplier": "pemasok",
    "rental": "sewa",
    "rentals": "penyewaan",
    "booking": "pemesanan",
    "reservation": "reservasi",

    #  Transport 
    "flight": "penerbangan",
    "airline": "maskapai",
    "aircraft": "pesawat",
    "vehicle": "kendaraan",
    "car": "mobil",
    "bus": "bus",
    "train": "kereta",
    "ship": "kapal",
    "boat": "perahu",
    "bike": "sepeda",
    "truck": "truk",
    "engine": "mesin",
    "fuel": "bahan_bakar",
    "speed": "kecepatan",
    "distance": "jarak",
    "departure": "keberangkatan",
    "arrival": "kedatangan",
    "destination": "tujuan",
    "ticket": "tiket",
    "seat": "kursi",
    "boarding": "naik",
    "railway": "kereta_api",

    #  Health 
    "medicine": "obat",
    "medication": "pengobatan",
    "prescription": "resep",
    "diagnosis": "diagnosis",
    "symptom": "gejala",
    "surgery": "operasi",
    "recovery": "pemulihan",
    "treatment": "perawatan",
    "vaccine": "vaksin",
    "allergy": "alergi",
    "dose": "dosis",
    "therapy": "terapi",

    #  Entertainment & sports 
    "movie": "film",
    "actor": "aktor",
    "actress": "aktris",
    "producer": "produser",
    "screenplay": "skenario",
    "genre": "genre",
    "show": "pertunjukan",
    "performance": "pertunjukan",
    "episode": "episode",
    "album": "album",
    "song": "lagu",
    "concert": "konser",
    "music": "musik",
    "instrument": "instrumen",
    "band": "band",
    "match": "pertandingan",
    "game": "permainan",
    "event": "acara",
    "round": "putaran",
    "win": "menang",
    "draw": "seri",
    "goal": "gol",
    "assist": "assist",
    "penalty": "penalti",
    "tournament": "turnamen",
    "champion": "juara",
    "championship": "kejuaraan",
    "league": "liga",
    "competition": "kompetisi",
    "sport": "olahraga",
    "sports": "olahraga",
    "race": "balapan",  # FIX: was "ras" (ethnicity)
    "track": "lintasan",
    "marathon": "maraton",
    "medal": "medali",
    "trophy": "trofi",
    "award": "penghargaan",
    "nomination": "nominasi",
    "cartoon": "kartun",
    "drama": "drama",

    #  Nature & weather 
    "weather": "cuaca",
    "temperature": "suhu",
    "humidity": "kelembaban",
    "wind": "angin",
    "rain": "hujan",
    "storm": "badai",
    "flood": "banjir",
    "earthquake": "gempa",
    "forest": "hutan",
    "garden": "kebun",
    "plant": "tanaman",
    "animal": "hewan",
    "dog": "anjing",
    "cat": "kucing",
    "horse": "kuda",
    "bird": "burung",
    "fish": "ikan",
    "pet": "hewan_peliharaan",
    "pets": "hewan_peliharaan",
    "breed": "ras_hewan",
    "species": "spesies",

    #  Technology 
    "software": "perangkat_lunak",
    "hardware": "perangkat_keras",
    "network": "jaringan",
    "channel": "saluran",
    "platform": "platform",
    "device": "perangkat",
    "screen": "layar",
    "display": "tampilan",
    "browser": "peramban",
    "website": "situs_web",
    "email": "email",
    "phone": "telepon",
    "mobile": "ponsel",
    "fax": "faks",
    "connection": "koneksi",
    "interface": "antarmuka",
    "system": "sistem",
    "program": "program",
    "application": "aplikasi",
    "download": "unduhan",
    "upload": "unggahan",
    "file": "berkas",
    "folder": "folder",
    "database": "basis_data",
    "server": "server",
    "memory": "memori",
    "storage": "penyimpanan",
    "processor": "prosesor",
    "pixel": "piksel",
    "resolution": "resolusi",
    "format": "format",
    "image": "gambar",
    "photo": "foto",
    "photos": "foto",
    "video": "video",
    "audio": "audio",

    #  Government & politics 
    "government": "pemerintah",
    "election": "pemilihan",
    "vote": "suara",
    "citizen": "warga",
    "population": "populasi",
    "independence": "kemerdekaan",
    "military": "militer",
    "political": "politik",
    "party": "pihak",  # FIX: was "pesta" (celebration). In DB context, it's business party
    "law": "hukum",
    "legal": "hukum",
    "court": "pengadilan",
    "prison": "penjara",
    "crime": "kejahatan",
    "security": "keamanan",
    "safety": "keamanan",
    "minister": "menteri",
    "governor": "gubernur",
    "mayor": "walikota",
    "senator": "senator",
    "council": "dewan",
    "committee": "komite",
    "parliament": "parlemen",
    "republic": "republik",
    "embassy": "kedutaan",
    "consulate": "konsulat",
    "treaty": "perjanjian",

    #  Actions / states 
    "active": "aktif",
    "available": "tersedia",
    "married": "menikah",
    "single": "lajang",
    "male": "pria",
    "female": "wanita",
    "first": "pertama",
    "last": "terakhir",
    "middle": "tengah",
    "home": "rumah",
    "highest": "tertinggi",
    "lowest": "terendah",
    "average": "rata_rata",
    "maximum": "maksimum",
    "minimum": "minimum",
    "open": "buka",
    "close": "tutup",
    "start": "mulai",
    "end": "akhir",
    "begin": "awal",
    "finish": "selesai",
    "new": "baru",
    "old": "lama",
    "big": "besar",
    "small": "kecil",
    "long": "panjang",
    "short": "pendek",
    "high": "tinggi",
    "low": "rendah",
    "full": "penuh",
    "empty": "kosong",
    "free": "gratis",
    "paid": "berbayar",
    "actual": "aktual",
    "original": "asli",
    "current": "saat_ini",
    "previous": "sebelumnya",
    "next": "selanjutnya",
    "main": "utama",
    "primary": "primer",
    "secondary": "sekunder",
    "other": "lain",
    "additional": "tambahan",
    "special": "khusus",
    "general": "umum",
    "common": "umum",
    "public": "publik",
    "private": "pribadi",
    "local": "lokal",
    "global": "global",
    "international": "internasional",
    "national": "nasional",
    "domestic": "domestik",
    "foreign": "asing",
    "permanent": "permanen",
    "temporary": "sementara",
    "regular": "reguler",

    #  Materials & properties 
    "gold": "emas",
    "silver": "perak",
    "bronze": "perunggu",
    "iron": "besi",
    "steel": "baja",
    "wood": "kayu",
    "glass": "kaca",
    "plastic": "plastik",
    "paper": "makalah",
    "fabric": "kain",
    "cotton": "katun",
    "leather": "kulit",
    "rubber": "karet",
    "oil": "minyak",
    "gas": "gas",
    "water": "air",
    "wine": "anggur",
    "beer": "bir",
    "coffee": "kopi",
    "food": "makanan",
    "meal": "makanan",
    "drink": "minuman",
    "menu": "menu",
    "recipe": "resep",
    "ingredient": "bahan",
    "flavor": "rasa",
    "taste": "rasa",
    "dish": "hidangan",

    #  Relationships & actions 
    "contact": "kontak",
    "connection": "koneksi",
    "appointment": "janji_temu",
    "meeting": "rapat",
    "schedule": "jadwal",
    "invitation": "undangan",
    "wedding": "pernikahan",
    "ceremony": "upacara",
    "gift": "hadiah",
    "donation": "donasi",
    "charity": "amal",
    "benefit": "tunjangan",
    "training": "pelatihan",
    "promotion": "promosi",
    "contract": "kontrak",
    "agreement": "perjanjian",
    "interview": "wawancara",
    "experience": "pengalaman",
    "skill": "keterampilan",
    "qualification": "kualifikasi",
    "achievement": "pencapaian",
    "accomplishment": "prestasi",
    "progress": "kemajuan",
    "report": "laporan",
    "analysis": "analisis",
    "survey": "survei",
    "proposal": "proposal",
    "project": "proyek",
    "mission": "misi",
    "task": "tugas",
    "issue": "masalah",
    "problem": "masalah",
    "solution": "solusi",
    "decision": "keputusan",
    "approval": "persetujuan",
    "request": "permintaan",
    "response": "respons",
    "notification": "notifikasi",
    "message": "pesan",
    "letter": "surat",
    "document": "dokumen",
    "form": "formulir",
    "template": "templat",
    "sample": "sampel",
    "source": "sumber",
    "target": "target",
    "reference": "referensi",
    "label": "label",
    "tag": "tag",
    "flag": "penanda",
    "option": "opsi",
    "preference": "preferensi",
    "setting": "pengaturan",
    "configuration": "konfigurasi",
    "parameter": "parameter",
    "attribute": "atribut",
    "property": "properti",
    "characteristic": "karakteristik",
    "criteria": "kriteria",
    "condition": "kondisi",
    "requirement": "persyaratan",
    "constraint": "batasan",
    "limit": "batas",
    "threshold": "ambang_batas",
    "range": "rentang",
    "scope": "cakupan",

    #  Publishing & research 
    "publication": "publikasi",
    "journal": "jurnal",
    "conference": "konferensi",
    "abstract": "abstrak",
    "keyword": "kata_kunci",
    "citation": "kutipan",
    "research": "penelitian",

    #  Miscellaneous important words 
    "capacity": "kapasitas",
    "gender": "jenis_kelamin",
    "sex": "jenis_kelamin",
    "nationality": "kewarganegaraan",
    "citizenship": "kewarganegaraan",
    "language": "bahasa",
    "religion": "agama",
    "belief": "kepercayaan",
    "culture": "budaya",
    "tradition": "tradisi",
    "heritage": "warisan",
    "history": "sejarah",
    "origin": "asal",
    "background": "latar_belakang",
    "identity": "identitas",
    "logo": "logo",
    "symbol": "simbol",
    "mascot": "maskot",
    "motto": "moto",
    "theme": "tema",
    "decoration": "dekorasi",
    "pattern": "pola",
    "design": "desain",
    "layout": "tata_letak",
    "structure": "struktur",
    "architecture": "arsitektur",
    "construction": "konstruksi",
    "renovation": "renovasi",
    "maintenance": "pemeliharaan",
    "repair": "perbaikan",
    "inspection": "inspeksi",
    "assessment": "penilaian",
    "evaluation": "evaluasi",
    "measurement": "pengukuran",
    "monitoring": "pemantauan",
    "tracking": "pelacakan",
    "recording": "perekaman",
    "collection": "koleksi",
    "exhibition": "pameran",
    "display": "tampilan",
    "presentation": "presentasi",
    "entertainment": "hiburan",
    "recreation": "rekreasi",
    "tourism": "pariwisata",
    "adventure": "petualangan",
    "activity": "aktivitas",
    "exercise": "latihan",
    "practice": "praktik",
    "routine": "rutinitas",
    "habit": "kebiasaan",
    "lifestyle": "gaya_hidup",

    #  Words found untranslated in current dict 
    "incident": "insiden",
    "attraction": "atraksi",
    "battle": "pertempuran",
    "kill": "membunuh",
    "killed": "terbunuh",
    "injured": "terluka",
    "damage": "kerusakan",
    "accident": "kecelakaan",
    "emergency": "darurat",
    "rescue": "penyelamatan",
    "victim": "korban",
    "suspect": "tersangka",
    "witness": "saksi",
    "evidence": "bukti",
    "arrest": "penangkapan",
    "trial": "persidangan",
    "sentence": "hukuman",
    "charges": "dakwaan",
    "charge": "penanggung_jawab",  # FIX: "in charge of" meaning, not "tarif"
    "fine": "denda",
    "violation": "pelanggaran",

    #  Fix common abbreviation-like words 
    "ssn": "ssn",
    "stuid": "stuid",
    "lname": "lname",
    "fname": "fname",
    "num": "num",
    "ref": "ref",
    "apt": "apt",
    "emp": "emp",
    "dept": "dept",
    "cid": "cid",
    "msid": "msid",
    "yn": "yn",
    "cmi": "cmi",
    "did": "did",
    "hr": "hr",
    "stu": "stu",
    "aid": "aid",
    "bio": "bio",
    "to": "ke",
    "in": "dalam",
    "for": "untuk",
    "of": "dari",
    "by": "oleh",
    "the": "the",
    "and": "dan",
    "or": "atau",
    "with": "dengan",
    "from": "dari",
    "at": "di",
    "on": "pada",

    #  Words specific to DB column contexts 
    "login": "login",
    "password": "kata_sandi",
    "username": "nama_pengguna",
    "email": "email",
    "log": "log",
    "meter": "meter",
    "minimum": "minimum",
    "maximum": "maksimum",
    "genre": "genre",
    "semester": "semester",
    "hotel": "hotel",
    "diagnosis": "diagnosis",
    "menu": "menu",
    "band": "band",
    "album": "album",
    "platform": "platform",
    "format": "format",
    "model": "model",
    "status": "status",
    "video": "video",
    "audio": "audio",
    "server": "server",
    "data": "data",
    "pilot": "pilot",
    "label": "label",
    "tag": "tag",
    "parameter": "parameter",
    "bonus": "bonus",
    "investor": "investor",
    "drama": "drama",
    "logo": "logo",
    "proposal": "proposal",
    "program": "program",
    "target": "target",
    "folder": "folder",
    "sampel": "sampel",

    #  Household / real estate 
    "apartment": "apartemen",
    "room": "kamar",
    "bedroom": "kamar_tidur",
    "bathroom": "kamar_mandi",
    "kitchen": "dapur",
    "floor": "lantai",
    "building": "bangunan",
    "furniture": "furnitur",
    "amenity": "fasilitas",
    "property": "properti",
    "estate": "real_estate",
    "rent": "sewa",
    "lease": "sewa_kontrak",
    "mortgage": "hipotek",
    "hire": "sewa",  # FIX: was "perekrutan" (recruitment), but in product context means rental

    #  Working / employment 
    "working": "bekerja",
    "work": "kerja",
    "works": "bekerja",
    "job": "pekerjaan",
    "occupation": "pekerjaan",
    "career": "karier",
    "retirement": "pensiun",
    "resignation": "pengunduran_diri",
    "termination": "pemutusan",
    "hiring": "perekrutan",
    "fired": "dipecat",

    # Additional context-dependent fixes
    "opening": "pembukaan",
    "closing": "penutupan",
    "access": "akses",
    "approval": "persetujuan",
    "rejection": "penolakan",
    "acceptance": "penerimaan",
    "submission": "pengajuan",
    "announcement": "pengumuman",
    "celebration": "perayaan",
    "festival": "festival",
    "exhibition": "pameran",
    "ceremony": "upacara",
    "reception": "resepsi",
    "congress": "kongres",
    "symposium": "simposium",
    "seminar": "seminar",
    "workshop": "lokakarya",

    # More missing words from the audit
    "dock": "dermaga",
    "docks": "dermaga",
    "booked": "dipesan",
    "wins": "kemenangan",

    #  Missing plural forms appearing in identifiers 
    "movements": "pergerakan",
    "bookings": "pemesanan",
    "buildings": "bangunan",
    "facilities": "fasilitas",
    "processes": "proses",
    "outcomes": "hasil",
    "officers": "petugas",
    "policies": "kebijakan",
    "definitions": "definisi",
    "attractions": "atraksi",
    "features": "fitur",
    "characteristics": "karakteristik",
    "categories": "kategori",
    "groups": "kelompok",
    "sections": "bagian",
    "structures": "struktur",
    "members": "anggota",
    "interactions": "interaksi",
    "payments": "pembayaran",
    "courses": "kursus",
    "collections": "koleksi",
    "questions": "pertanyaan",
    "profits": "keuntungan",
    "readers": "pembaca",
    "meetings": "rapat",
    "students": "mahasiswa",
    "channels": "saluran",
    "services": "layanan",
    "events": "acara",
    "pieces": "potongan",
    "factories": "pabrik",
    "hosts": "tuan_rumah",
    "matches": "pertandingan",
    "championships": "kejuaraan",
    "stories": "cerita",
    "platforms": "platform",
    "apartments": "apartemen",
    "activities": "aktivitas",
    "accounts": "akun",
    "applications": "aplikasi",
    "assessments": "penilaian",
    "assignments": "penugasan",
    "albums": "album",
    "artists": "seniman",
    "attributes": "atribut",
    "authors": "penulis",
    "tutors": "tutor",
    "participants": "peserta",
    "performers": "penampil",
    "agents": "agen",
    "agencies": "lembaga",
    "agreements": "perjanjian",
    "appearances": "penampilan",
    "achievements": "pencapaian",
    "notes": "catatan",
    "deaths": "kematian",
    "cities": "kota",
    "products": "produk",
    "customers": "pelanggan",
    "systems": "sistem",
    "invoices": "faktur",
    "contacts": "kontak",
    "transactions": "transaksi",
    "campaigns": "kampanye",
    "addresses": "alamat",
    "loans": "pinjaman",
    "episodes": "episode",
    "seasons": "musim",
    "shops": "toko",

    #  Missing common words appearing in identifiers 
    "settlement": "penyelesaian",
    "destruction": "pemusnahan",
    "disposition": "disposisi",
    "detention": "penahanan",
    "accreditation": "akreditasi",
    "enrolment": "pendaftaran",
    "completion": "penyelesaian",
    "attendance": "kehadiran",
    "publication": "publikasi",
    "registration": "registrasi",
    "revision": "revisi",
    "transcript": "transkrip",
    "treatment": "perawatan",
    "answer": "jawaban",
    "answers": "jawaban",
    "editor": "editor",
    "fame": "ketenaran",
    "measure": "ukuran",
    "purpose": "tujuan",
    "audience": "penonton",
    "memory": "memori",
    "workflow": "alur_kerja",
    "information": "informasi",
    "doc": "dokumen",

    #  Numbers and units 
    "billion": "miliar",
    "billions": "miliar",
    "million": "juta",
    "millions": "juta",
    "dollar": "dolar",
    "dollars": "dolar",
    "percent": "persen",
    "gross": "bruto",

    #  Untranslated adjectives/verbs 
    "affected": "terdampak",
    "acquired": "diperoleh",
    "disposed": "dibuang",
    "planned": "direncanakan",
    "assisting": "pendamping",
    "worldwide": "seluruh_dunia",
    "authorised": "diotorisasi",
    "authorized": "diotorisasi",
    "good": "baik",
    "bad": "buruk",
    "latest": "terbaru",
    "full": "penuh",

    #  Legal/Governance 
    "attorney": "jaksa",

    #  Context words for connectors 
    "boys": "laki_laki",
    "girls": "perempuan",
    "boy": "laki_laki",
    "girl": "perempuan",
    "boarding": "asrama",
    "sheep": "domba",
    "goats": "kambing",
    "goat": "kambing",
    "round": "putaran",
    "series": "seri",
    "thing": "hal",
    "things": "hal",
    "powertrain": "penggerak",
    "hall": "aula",
    "there": "sana",
    "num": "jumlah",
    "no": "jumlah",
    "locaton": "lokasi",  # typo in original Spider data

    
    # MASSIVE BATCH: All remaining self-mapped words from word map
    

    #  A: nouns, adjectives, verbs 
    "abandoned": "ditinggalkan",
    "abbreviation": "singkatan",
    "accelerate": "mempercepat",
    "acceleration": "percepatan",
    "accelerator": "akselerator",
    "accession": "aksesi",
    "accuracy": "akurasi",
    "acting": "penjabat",
    "adopted": "diadopsi",
    "adress": "alamat",
    "adults": "dewasa",
    "advertising": "periklanan",
    "affiliated": "berafiliasi",
    "affiliation": "afiliasi",
    "affirmative": "afirmatif",
    "agency": "lembaga",
    "aggression": "agresi",
    "agility": "kelincahan",
    "agree": "setuju",
    "agreed": "disetujui",
    "air": "udara",
    "airdate": "tanggal_tayang",
    "airlines": "maskapai",
    "airports": "bandara",
    "allowed": "diizinkan",
    "analogue": "analog",
    "analytical": "analitis",
    "aperture": "apertur",
    "appelation": "sebutan",
    "appellations": "sebutan",
    "apps": "aplikasi",
    "architect": "arsitek",
    "areas": "area",
    "arrange": "mengatur",
    "arrears": "tunggakan",
    "arrived": "tiba",
    "art": "seni",
    "artwork": "karya_seni",
    "asessment": "penilaian",
    "asian": "asia",
    "aspect": "aspek",
    "attacking": "penyerangan",
    "authority": "otoritas",
    "authorship": "kepenulisan",
    "availability": "ketersediaan",
    "awarded": "dianugerahi",
    "away": "tandang",

    #  B: nouns, adjectives, verbs 
    "bakery": "toko_roti",
    "ball": "bola",
    "ballots": "surat_suara",
    "bandmate": "rekan_band",
    "bars": "bar",
    "base": "basis",
    "bats": "pukulan",
    "batting": "pukulan",
    "became": "menjadi",
    "bed": "tempat_tidur",
    "beds": "tempat_tidur",
    "behaviour": "perilaku",
    "benefits": "tunjangan",
    "best": "terbaik",
    "bikes": "sepeda",
    "billable": "dapat_ditagih",
    "bills": "tagihan",
    "birthday": "ulang_tahun",
    "black": "hitam",
    "block": "blok",
    "boats": "perahu",
    "books": "buku",
    "boxes": "kotak",
    "breeds": "ras_hewan",
    "broadcast": "siaran",
    "budgeted": "dianggarkan",
    "build": "membangun",
    "built": "dibangun",
    "bulgarian": "bulgaria",
    "bulls": "banteng",
    "burden": "beban",
    "buyer": "pembeli",
    "buying": "pembelian",
    "bytes": "byte",

    #  C: nouns, adjectives, verbs 
    "call": "panggilan",
    "camera": "kamera",
    "campuses": "kampus",
    "candidates": "kandidat",
    "cards": "kartu",
    "carrier": "pengangkut",
    "cars": "mobil",
    "cases": "kasus",
    "catalogs": "katalog",
    "catalogue": "katalog",
    "cattle": "ternak",
    "caused": "disebabkan",
    "cells": "sel",
    "census": "sensus",
    "certification": "sertifikasi",
    "chair": "kursi",
    "chance": "peluang",
    "change": "perubahan",
    "chapters": "bab",
    "character": "karakter",
    "chargeable": "dikenakan_biaya",
    "chassis": "sasis",
    "checkin": "check_in",
    "checking": "pengecekan",
    "chromosome": "kromosom",
    "circuit": "sirkuit",
    "circuits": "sirkuit",
    "circulation": "sirkulasi",
    "claimed": "diklaim",
    "claims": "klaim",
    "classes": "kelas",
    "classification": "klasifikasi",
    "clean": "bersih",
    "clearance": "izin",
    "clients": "klien",
    "closure": "penutupan",
    "coaster": "wahana",
    "codes": "kode",
    "colours": "warna",
    "combined": "gabungan",
    "commander": "komandan",
    "commerce": "perdagangan",
    "companies": "perusahaan",
    "compatible": "kompatibel",
    "component": "komponen",
    "comptroller": "pengawas_keuangan",
    "consider": "mempertimbangkan",
    "constructor": "konstruktor",
    "constructors": "konstruktor",
    "content": "konten",
    "contents": "isi",
    "contest": "kontes",
    "contestant": "peserta",
    "contestants": "peserta",
    "continents": "benua",
    "continuation": "kelanjutan",
    "contracts": "kontrak",
    "coordinates": "koordinat",
    "copies": "salinan",
    "copy": "salinan",
    "copyright": "hak_cipta",
    "counties": "kabupaten",
    "countries": "negara",
    "coupon": "kupon",
    "coupons": "kupon",
    "cover": "sampul",
    "cows": "sapi",
    "creation": "pembuatan",
    "crossing": "perlintasan",
    "curve": "kurva",
    "cycle": "siklus",
    "cyclists": "pesepeda",
    "cylinders": "silinder",

    #  D: nouns, adjectives, verbs 
    "damaged": "rusak",
    "dates": "tanggal",
    "days": "hari",
    "decor": "dekorasi",
    "defence": "pertahanan",
    "defender": "bek",
    "defense": "pertahanan",
    "defensive": "bertahan",
    "definition": "definisi",
    "degrees": "gelar",
    "delivered": "dikirim",
    "denomination": "denominasi",
    "density": "kepadatan",
    "departed": "berangkat",
    "departments": "departemen",
    "dependent": "tanggungan",
    "derived": "turunan",
    "destroyed": "dimusnahkan",
    "developers": "pengembang",
    "dimensions": "dimensi",
    "direct": "langsung",
    "directed": "disutradarai",
    "discipline": "disiplin",
    "discontinued": "dihentikan",
    "distributer": "distributor",
    "divergence": "divergensi",
    "diving": "selam",
    "division": "divisi",
    "dogs": "anjing",
    "doubles": "ganda",
    "draft": "draf",
    "drafts": "draf",
    "dribbling": "dribel",
    "drivers": "pengemudi",
    "due": "jatuh_tempo",

    #  E: nouns, adjectives, verbs 
    "economics": "ekonomi",
    "economy": "ekonomi",
    "education": "pendidikan",
    "elected": "terpilih",
    "electoral": "pemilihan",
    "eliminated": "dieliminasi",
    "elimination": "eliminasi",
    "employer": "pemberi_kerja",
    "employment": "pekerjaan",
    "endowment": "sumbangan",
    "engineers": "insinyur",
    "enrolled": "terdaftar",
    "enrollments": "pendaftaran",
    "entered": "masuk",
    "entrant": "peserta",
    "enzyme": "enzim",
    "estimate": "estimasi",
    "estimation": "estimasi",
    "euros": "euro",
    "exit": "keluar",
    "expectancy": "harapan",
    "expires": "kedaluwarsa",
    "extension": "ekstensi",

    #  F: nouns, adjectives, verbs 
    "facility": "fasilitas",
    "family": "keluarga",
    "famous": "terkenal",
    "fastest": "tercepat",
    "fate": "nasib",
    "faults": "kesalahan",
    "fees": "biaya",
    "feet": "kaki",
    "filename": "nama_berkas",
    "files": "berkas",
    "finances": "keuangan",
    "financial": "finansial",
    "fines": "denda",
    "finishing": "penyelesaian",
    "fleet": "armada",
    "flights": "penerbangan",
    "floors": "lantai",
    "followers": "pengikut",
    "follows": "mengikuti",
    "foot": "kaki",
    "force": "kekuatan",
    "forename": "nama_depan",
    "formats": "format",
    "formed": "dibentuk",
    "forms": "formulir",
    "founded": "didirikan",
    "freight": "kargo",
    "fully": "sepenuhnya",
    "functional": "fungsional",

    #  G: nouns, adjectives, verbs 
    "garage": "garasi",
    "genres": "genre",
    "geographic": "geografis",
    "get": "mendapatkan",
    "given": "diberikan",
    "goals": "gol",
    "goods": "barang",
    "graduate": "lulusan",
    "grape": "anggur",
    "grapes": "anggur",
    "graphics": "grafis",
    "guests": "tamu",
    "gust": "hembusan",

    #  H: nouns, adjectives, verbs 
    "half": "setengah",
    "hand": "tangan",
    "handling": "penanganan",
    "happy": "bahagia",
    "headquartered": "berkantor_pusat",
    "heading": "menuju",
    "health": "kesehatan",
    "heat": "panas",
    "held": "diadakan",
    "highschooler": "siswa_sma",
    "hight": "tinggi",
    "hired": "dipekerjakan",
    "hispanic": "hispanik",
    "homepage": "beranda",
    "hometown": "kota_asal",
    "horsepower": "tenaga_kuda",
    "horses": "kuda",
    "hosting": "penyelenggaraan",
    "hotels": "hotel",
    "hours": "jam",
    "house": "rumah",
    "how": "cara",
    "human": "manusia",

    #  I: nouns, adjectives, verbs 
    "images": "gambar",
    "inches": "inci",
    "incorporated": "didirikan",
    "individuals": "individu",
    "inducted": "dilantik",
    "initial": "awal",
    "installation": "instalasi",
    "instruments": "instrumen",
    "integration": "integrasi",
    "interaction": "interaksi",
    "interceptions": "intersepsi",
    "interchanges": "persimpangan",
    "invested": "diinvestasikan",
    "investors": "investor",
    "issued": "diterbitkan",
    "issues": "masalah",

    #  J-K: nouns, adjectives, verbs 
    "jerk": "angkatan",
    "jobs": "pekerjaan",
    "joined": "bergabung",
    "jumping": "lompat",
    "justice": "keadilan",
    "kick": "tendangan",
    "kicking": "menendang",
    "kid": "anak",
    "kids": "anak",
    "knots": "knot",

    #  L: nouns, adjectives, verbs 
    "languages": "bahasa",
    "lap": "putaran",
    "laps": "putaran",
    "late": "terlambat",
    "launched": "diluncurkan",
    "layer": "lapisan",
    "learning": "pembelajaran",
    "lens": "lensa",
    "lessons": "pelajaran",
    "licence": "lisensi",
    "lieutenant": "letnan",
    "life": "kehidupan",
    "lifespan": "masa_hidup",
    "liked": "disukai",
    "likes": "suka",
    "lineage": "keturunan",
    "lines": "jalur",
    "list": "daftar",
    "lives": "tinggal",
    "loading": "pemuatan",
    "locality": "lokalitas",
    "losses": "kekalahan",
    "lost": "hilang",
    "lyric": "lirik",

    #  M: nouns, adjectives, verbs 
    "made": "dibuat",
    "mailed": "dikirimkan",
    "mailing": "pengiriman_surat",
    "make": "merek",
    "makers": "pembuat",
    "making": "pembuatan",
    "manage": "mengelola",
    "management": "manajemen",
    "manufacturers": "pabrikan",
    "marketing": "pemasaran",
    "markets": "pasar",
    "marking": "penilaian",
    "matched": "cocok",
    "mean": "rata_rata",
    "medium": "sedang",
    "meters": "meter",
    "methods": "metode",
    "metric": "metrik",
    "miles": "mil",
    "mill": "pabrik_penggilingan",
    "milliseconds": "milidetik",
    "minutes": "menit",
    "money": "uang",
    "most": "paling",
    "move": "gerakan",
    "moved": "dipindahkan",
    "movies": "film",
    "museums": "museum",

    #  N: nouns, adjectives, verbs 
    "names": "nama",
    "native": "asli",
    "needed": "dibutuhkan",
    "negative": "negatif",
    "neighbourhood": "lingkungan",
    "neutral": "netral",
    "nickname": "julukan",

    #  O: nouns, adjectives, verbs 
    "object": "objek",
    "objectives": "tujuan",
    "objects": "objek",
    "occupancy": "okupansi",
    "offered": "ditawarkan",
    "officer": "petugas",
    "openings": "lowongan",
    "openning": "pembukaan",
    "operate": "mengoperasikan",
    "operating": "operasional",
    "oppose": "melawan",
    "organisations": "organisasi",
    "organizations": "organisasi",
    "organized": "terorganisir",
    "outfield": "luar_lapangan",
    "outstanding": "luar_biasa",
    "overall": "keseluruhan",
    "overpayments": "kelebihan_bayar",
    "own": "milik",
    "owned": "dimiliki",
    "owners": "pemilik",
    "oxen": "lembu",

    #  P: nouns, adjectives, verbs 
    "package": "paket",
    "page": "halaman",
    "pages": "halaman",
    "painter": "pelukis",
    "painting": "lukisan",
    "paintings": "lukisan",
    "papers": "makalah",
    "paragraph": "paragraf",
    "paragraphs": "paragraf",
    "parallel": "paralel",
    "parking": "parkir",
    "parks": "taman",
    "participant": "peserta",
    "participates": "berpartisipasi",
    "participation": "partisipasi",
    "parties": "pihak",
    "parts": "bagian",
    "passengers": "penumpang",
    "passing": "operan",
    "pay": "bayar",
    "payable": "terutang",
    "penalties": "penalti",
    "performer": "penampil",
    "personal": "pribadi",
    "physician": "dokter",
    "picture": "gambar",
    "pigs": "babi",
    "pixels": "piksel",
    "placed": "ditempatkan",
    "plane": "pesawat",
    "play": "bermain",
    "played": "dimainkan",
    "players": "pemain",
    "playlist": "daftar_putar",
    "playlists": "daftar_putar",
    "plays": "bermain",
    "pole": "tiang",
    "politics": "politik",
    "popular": "populer",
    "popularity": "popularitas",
    "positioning": "penentuan_posisi",
    "postal": "pos",
    "potential": "potensi",
    "pounds": "pon",
    "power": "daya",
    "precipitation": "curah_hujan",
    "preferred": "diutamakan",
    "premise": "tempat_usaha",
    "premises": "tempat_usaha",
    "presence": "kehadiran",
    "press": "pers",
    "pressure": "tekanan",
    "procedures": "prosedur",
    "process": "proses",
    "processing": "pemrosesan",
    "professionals": "profesional",
    "profiles": "profil",
    "programs": "program",
    "projects": "proyek",
    "prominence": "ketinggian",
    "propulsion": "propulsi",
    "provided": "disediakan",
    "publisher": "penerbit",
    "purchased": "dibeli",
    "purchases": "pembelian",

    #  Q-R: nouns, adjectives, verbs 
    "qualify": "lolos",
    "qualifying": "kualifikasi",
    "question": "pertanyaan",
    "races": "balapan",
    "racing": "balap",
    "raised": "terkumpul",
    "rankings": "peringkat",
    "rates": "tarif",
    "ratings": "peringkat",
    "ratio": "rasio",
    "reactions": "reaksi",
    "receipt": "kwitansi",
    "receipts": "kwitansi",
    "received": "diterima",
    "recipient": "penerima",
    "recognition": "pengakuan",
    "recommendations": "rekomendasi",
    "recorded": "dicatat",
    "reflexes": "refleks",
    "regions": "wilayah",
    "register": "daftar",
    "registered": "terdaftar",
    "registrations": "registrasi",
    "reign": "pemerintahan",
    "related": "terkait",
    "relationship": "hubungan",
    "release": "rilis",
    "remarks": "keterangan",
    "renting": "penyewaan",
    "replacement": "penggantian",
    "reported": "dilaporkan",
    "reports": "laporan",
    "represented": "diwakili",
    "reputation": "reputasi",
    "requested": "diminta",
    "required": "wajib",
    "reservations": "reservasi",
    "reserves": "cadangan",
    "residence": "tempat_tinggal",
    "resident": "penduduk",
    "residents": "penduduk",
    "restaurants": "restoran",
    "results": "hasil",
    "returned": "dikembalikan",
    "rhythm": "ritme",
    "riding": "berkuda",
    "rings": "cincin",
    "roles": "peran",
    "rooms": "kamar",
    "routes": "rute",

    #  S: nouns, adjectives, verbs 
    "sailors": "pelaut",
    "sale": "penjualan",
    "satisfactory": "memuaskan",
    "savings": "tabungan",
    "scientists": "ilmuwan",
    "scores": "skor",
    "sculptor": "pematung",
    "sculpture": "patung",
    "sculptures": "patung",
    "search": "pencarian",
    "searches": "pencarian",
    "seating": "tempat_duduk",
    "seats": "kursi",
    "secretary": "sekretaris",
    "seed": "unggulan",
    "seller": "penjual",
    "selling": "penjualan",
    "semesters": "semester",
    "senate": "senat",
    "sender": "pengirim",
    "sent": "dikirim",
    "sequence": "urutan",
    "settled": "diselesaikan",
    "settlements": "penyelesaian",
    "shareholding": "kepemilikan_saham",
    "shipment": "pengiriman",
    "shipments": "pengiriman",
    "shooting": "menembak",
    "shot": "tembakan",
    "shots": "tembakan",
    "shows": "acara",
    "since": "sejak",
    "singles": "tunggal",
    "sizes": "ukuran",
    "skills": "keterampilan",
    "snatch": "angkatan",
    "sold": "terjual",
    "songs": "lagu",
    "sound": "suara",
    "span": "rentang",
    "speach": "pidato",
    "spent": "dihabiskan",
    "stage": "panggung",
    "stages": "tahapan",
    "standing": "klasemen",
    "standings": "klasemen",
    "star": "bintang",
    "staring": "membintangi",
    "stars": "bintang",
    "starting": "awal",
    "starts": "dimulai",
    "statement": "pernyataan",
    "statements": "pernyataan",
    "stay": "menginap",
    "stint": "babak",
    "stop": "perhentian",
    "stops": "perhentian",
    "stored": "disimpan",
    "stores": "toko",
    "strength": "kekuatan",
    "subjects": "mata_pelajaran",
    "subscription": "langganan",
    "summary": "ringkasan",
    "supplied": "dipasok",
    "suppliers": "pemasok",
    "support": "dukungan",
    "surname": "nama_keluarga",

    #  T: nouns, adjectives, verbs 
    "tackle": "tekel",
    "taken": "diambil",
    "takes": "mengambil",
    "tallest": "tertinggi",
    "tasks": "tugas",
    "teachers": "guru",
    "teaches": "mengajar",
    "templates": "templat",
    "terrestrial": "terestrial",
    "tests": "ujian",
    "theaters": "teater",
    "third": "ketiga",
    "throws": "lemparan",
    "tie": "seri",
    "ties": "seri",
    "timed": "berjangka",
    "times": "waktu",
    "tonnage": "tonase",
    "tonnes": "ton",
    "took": "diambil",
    "top": "teratas",
    "tours": "tur",
    "tracks": "lintasan",
    "trained": "terlatih",
    "translation": "terjemahan",
    "transmitter": "pemancar",
    "traverse": "lintasan",
    "treasurer": "bendahara",
    "treatments": "perawatan",
    "tries": "percobaan",
    "trip": "perjalanan",
    "triple": "tiga_kali",
    "trucks": "truk",
    "tryout": "seleksi",
    "tweets": "cuitan",
    "typical": "tipikal",

    #  U-Z: nouns, adjectives, verbs 
    "unavailable": "tidak_tersedia",
    "undergoes": "menjalani",
    "undergraduate": "sarjana",
    "units": "unit",
    "used": "digunakan",
    "users": "pengguna",
    "vault": "lompat_kuda",
    "vehicles": "kendaraan",
    "velocity": "kecepatan",
    "venue": "tempat",
    "vice": "wakil",
    "viewers": "penonton",
    "visibility": "jarak_pandang",
    "visitors": "pengunjung",
    "visits": "kunjungan",
    "vocals": "vokal",
    "voice": "suara",
    "volleys": "voli",
    "votes": "suara",
    "voting": "pemungutan_suara",
    "warehouses": "gudang",
    "weeks": "minggu",
    "wheels": "roda",
    "white": "putih",
    "winery": "kilang_anggur",
    "winning": "kemenangan",
    "winnings": "hadiah",
    "won": "menang",
    "worth": "bernilai",
    "writes": "menulis",
    "written": "ditulis",
    "years": "tahun",
}




# SQL KEYWORD TRANSLATIONS


SQL_KEYWORD_TRANSLATIONS = {
    "date": "tanggal",
    "order": "pesanan",
    "end": "akhir",
    "time": "waktu",
    "count": "jumlah",
    "total": "total",       # Loanword in Indonesian, keep as-is
    "create": "buat",
    "check": "periksa",
    "key": "kunci",
    "set": "himpunan",
    "group": "kelompok",
    "cast": "pemeran",
    "match": "pertandingan",
    "round": "babak",
    "interval": "interval",
    "text": "teks",
    "status": "status",
    "label": "label",
    "length": "panjang",
}




# CONNECTOR REPLACEMENTS


CONNECTOR_REPLACEMENTS = {
    "_of_": "_",        # "of" is dropped in Indonesian DM word order
    "_the_": "_",       # "the" has no Indonesian equivalent
    "_and_": "_dan_",
    "_or_": "_atau_",
    "_in_": "_dalam_",
    "_to_": "_ke_",
    "_for_": "_untuk_",
    "_by_": "_oleh_",
    "_from_": "_dari_",
}




# HEAD NOUNS (Indonesian DM word order)


HEAD_NOUNS_SHOULD_BE_FIRST = {
    "nama": True,       # name → nama_X
    "kode": True,       # code → kode_X
    "nomor": True,      # number → nomor_X
    "tipe": True,       # type → tipe_X
    "tanggal": True,    # date → tanggal_X
    "waktu": True,      # time → waktu_X
    "tahun": True,      # year → tahun_X
    "bulan": True,      # month → bulan_X
    "hari": True,       # day → hari_X
    "jam": True,        # hour → jam_X
    "harga": True,      # price → harga_X
    "biaya": True,      # cost → biaya_X
    "tarif": True,      # rate → tarif_X
    "alamat": True,     # address → alamat_X
    "lokasi": True,     # location → lokasi_X
    "tempat": True,     # place → tempat_X
    "jumlah": True,     # count/amount → jumlah_X
    "deskripsi": True,  # description → deskripsi_X
    "rincian": True,    # details → rincian_X
    "ukuran": True,     # size → ukuran_X
    "tingkat": True,    # level → tingkat_X
    "peringkat": True,  # rank → peringkat_X
    "posisi": True,     # position → posisi_X
    "skor": True,       # score → skor_X
    "poin": True,       # point → poin_X
    "nilai": True,      # value → nilai_X
    "hasil": True,      # result → hasil_X
    "catatan": True,    # record/note → catatan_X
    "tema": True,       # theme → tema_X
    "warna": True,      # color → warna_X
}




# IDENTIFIER OVERRIDES


IDENT_OVERRIDES = {
    #  DB_IDs 
    "concert_singer": "penyanyi_konser",
    "dog_kennels": "kandang_anjing",
    "battle_death": "kematian_pertempuran",
    "department_store": "toko_departemen",
    "employee_hire_evaluation": "evaluasi_perekrutan_karyawan",
    "student_transcripts_tracking": "pelacakan_transkrip_mahasiswa",
    "county_public_safety": "keamanan_publik_kabupaten",
    "mountain_photos": "foto_gunung",
    "museum_visit": "kunjungan_museum",
    "shop_membership": "keanggotaan_toko",
    "school_bus": "bus_sekolah",
    "train_station": "stasiun_kereta",
    "body_builder": "binaragawan",
    "storm_record": "catatan_badai",
    "real_estate_properties": "properti_real_estate",
    "coffee_shop": "kedai_kopi",
    "flight_company": "perusahaan_penerbangan",
    "city_record": "catatan_kota",
    "company_employee": "karyawan_perusahaan",
    "company_office": "kantor_perusahaan",
    "election_representative": "perwakilan_pemilihan",
    "entertainment_awards": "penghargaan_hiburan",
    "game_injury": "cedera_permainan",
    "gas_company": "perusahaan_gas",
    "machine_repair": "perbaikan_mesin",
    "match_season": "musim_pertandingan",
    "medicine_enzyme_interaction": "interaksi_enzim_obat",
    "news_report": "laporan_berita",
    "party_host": "tuan_rumah_pihak",
    "party_people": "orang_pihak",
    "performance_attendance": "kehadiran_pertunjukan",
    "phone_market": "pasar_telepon",
    "pilot_record": "catatan_pilot",
    "products_for_hire": "produk_untuk_disewa",
    "products_gen_characteristics": "karakteristik_umum_produk",
    "product_catalog": "katalog_produk",
    "program_share": "pembagian_program",
    "protein_institute": "institut_protein",
    "race_track": "lintasan_balapan",
    "school_finance": "keuangan_sekolah",
    "school_player": "pemain_sekolah",
    "ship_mission": "misi_kapal",
    "sports_competition": "kompetisi_olahraga",
    "store_product": "produk_toko",
    "student_assessment": "penilaian_mahasiswa",
    "theme_gallery": "galeri_tema",
    "tracking_grants_for_research": "pelacakan_hibah_untuk_penelitian",
    "tracking_orders": "pelacakan_pesanan",
    "tracking_share_transactions": "pelacakan_transaksi_saham",
    "tracking_software_problems": "pelacakan_masalah_perangkat_lunak",
    "university_basketball": "bola_basket_universitas",
    "workshop_paper": "makalah_lokakarya",
    "decoration_competition": "kompetisi_dekorasi",
    "film_rank": "peringkat_film",
    "customers_and_addresses": "pelanggan_dan_alamat",
    "customers_and_invoices": "pelanggan_dan_faktur",
    "customers_and_products_contacts": "pelanggan_dan_kontak_produk",
    "customers_campaigns_ecommerce": "kampanye_pelanggan_ecommerce",
    "customers_card_transactions": "transaksi_kartu_pelanggan",
    "customer_complaints": "keluhan_pelanggan",
    "customer_deliveries": "pengiriman_pelanggan",
    "insurance_and_eClaims": "asuransi_dan_eklaim",
    "insurance_fnol": "asuransi_fnol",
    "insurance_policies": "polis_asuransi",
    "cre_Docs_and_Epenses": "cre_dokumen_dan_pengeluaran",
    "cre_Doc_Control_Systems": "cre_sistem_kontrol_dokumen",
    "cre_Doc_Template_Mgt": "cre_manajemen_templat_dokumen",
    "cre_Doc_Tracking_DB": "cre_pelacakan_dokumen_db",
    "cre_Drama_Workshop_Groups": "cre_kelompok_lokakarya_drama",
    "cre_Theme_park": "cre_taman_tema",
    "e_government": "e_pemerintah",
    "e_learning": "e_pembelajaran",
    "local_govt_and_lot": "pemerintah_lokal_dan_lot",
    "local_govt_in_alabama": "pemerintah_lokal_di_alabama",
    "local_govt_mdm": "pemerintah_lokal_mdm",
    "culture_company": "perusahaan_budaya",
    "document_management": "manajemen_dokumen",
    "department_management": "manajemen_departemen",
    "riding_club": "klub_berkuda",
    "driving_school": "sekolah_mengemudi",
    "small_bank_1": "bank_kecil_1",
    "apartment_rentals": "penyewaan_apartemen",
    "assets_maintenance": "pemeliharaan_aset",
    "behavior_monitoring": "pemantauan_perilaku",
    "candidate_poll": "jajak_pendapat_kandidat",
    "journal_committee": "komite_jurnal",
    "poker_player": "pemain_poker",
    "station_weather": "stasiun_cuaca",
    "course_teach": "kursus_mengajar",
    "singer_in_concert": "penyanyi_dalam_konser",
    "network_1": "jaringan_1",
    "network_2": "jaringan_2",
    "browser_web": "peramban_web",
    "activity_1": "aktivitas_1",
    "phone_1": "telepon_1",
    "store_1": "toko_1",
    "ship_1": "kapal_1",
    "bike_1": "sepeda_1",
    "book_2": "buku_2",
    "game_1": "permainan_1",
    "inn_1": "penginapan_1",
    "loan_1": "pinjaman_1",
    "voter_2": "pemilih_2",
    "farm": "pertanian",
    "restaurants": "restoran",
    "singer": "penyanyi",
    "perpetrator": "pelaku",
    "world_1": "dunia_1",
    "soccer_1": "sepak_bola_1",
    "soccer_2": "sepak_bola_2",
    "car_1": "mobil_1",
    "pets_1": "hewan_peliharaan_1",
    "dog_kennels": "kandang_anjing",

    # Abbreviation DBs that stay unchanged
    "chinook_1": "chinook_1",
    "formula_1": "formula_1",
    "geo": "geo",
    "csu_1": "csu_1",
    "hr_1": "hr_1",
    "icfp_1": "icfp_1",
    "imdb": "imdb",
    "epinions_1": "epinions_1",
    "sakila_1": "sakila_1",
    "tvshow": "tvshow",
    "twitter_1": "twitter_1",
    "wta_1": "wta_1",
    "yelp": "yelp",
    "roller_coaster": "roller_coaster",

    #  Column name / table name word-order fixes 
    # _name suffix → nama_ prefix
    "Official_Name": "nama_resmi",
    "Official_native_language": "bahasa_asli_resmi",
    "official_languages": "bahasa_resmi",

    # Birth/Death place
    "Birth_Place": "tempat_lahir",
    "birth_place": "tempat_lahir",
    "Death_Place": "tempat_kematian",
    "Home_city": "kota_asal",
    "Hometown": "kota_asal",
    "Home_town": "kota_asal",
    "home_city": "kota_asal",

    # Price/Cost
    "Ticket_Price": "harga_tiket",
    "Product_Price": "harga_produk",
    "product_price": "harga_produk",
    "PurchasePrice": "harga_pembelian",
    "SalePrice": "harga_jual",
    "UnitPrice": "harga_satuan",
    "unit_price": "harga_satuan",
    "basePrice": "harga_dasar",
    "daily_hire_cost": "biaya_sewa_harian",
    "Annual_fuel_cost": "biaya_bahan_bakar_tahunan",
    "CampusFee": "biaya_kampus",

    # Address
    "STREET_ADDRESS": "alamat_jalan_raya",
    "Street_address": "alamat_jalan_raya",
    "street_address": "alamat_jalan_raya",
    "BillingAddress": "alamat_penagihan",
    "Customer_Email_Address": "alamat_email_pelanggan",
    "Store_Email_Address": "alamat_email_toko",
    "email_address": "alamat_email",

    # Location
    "College_Location": "lokasi_perguruan_tinggi",
    "Office_locations": "lokasi_kantor",
    "ClubLocation": "lokasi_klub",

    # Theme
    "Decoration_Theme": "tema_dekorasi",
    "Party_Theme": "tema_pihak",

    # First/Last name (Indonesian: nama_depan, nama_belakang)
    "customer_first_name": "nama_depan_pelanggan",
    "customer_last_name": "nama_belakang_pelanggan",
    "staff_first_name": "nama_depan_staf",
    "staff_last_name": "nama_belakang_staf",
    "individual_first_name": "nama_depan_individu",
    "individual_last_name": "nama_belakang_individu",
    "individual_middle_name": "nama_tengah_individu",
    "guest_first_name": "nama_depan_tamu",
    "guest_last_name": "nama_belakang_tamu",
    "first_name": "nama_depan",
    "last_name": "nama_belakang",
    "middle_name": "nama_tengah",
    "Firstname": "nama_depan",
    "Lastname": "nama_belakang",
    "fname": "fname",
    "lname": "lname",

    # Description suffixes
    "Attraction_Type_Description": "deskripsi_tipe_atraksi",
    "Budget_Type_Description": "deskripsi_tipe_anggaran",
    "Claim_Status_Description": "deskripsi_status_klaim",
    "Document_Type_Description": "deskripsi_tipe_dokumen",
    "Service_Type_Description": "deskripsi_tipe_layanan",
    "Template_Type_Description": "deskripsi_tipe_templat",

    # Details suffixes
    "Feature_Details": "rincian_fitur",
    "Channel_Details": "rincian_saluran",
    "Customer_Details": "rincian_pelanggan",
    "Event_Details": "rincian_acara",
    "Market_Details": "rincian_pasar",
    "Other_Details": "rincian_lainnya",
    "Staff_Details": "rincian_staf",
    "Visit_Details": "rincian_kunjungan",
    "Account_Details": "rincian_akun",
    "Shop_Details": "rincian_toko",
    "Statement_Details": "rincian_pernyataan",
    "Party_Details": "rincian_pihak",
    "Theme_Park_Details": "rincian_taman_tema",

    # Position/Rank
    "Highest_Position": "posisi_tertinggi",
    "Rank_position": "posisi_peringkat",
    "Pole_Position": "posisi_pole",
    "StagePosition": "posisi_panggung",

    # Silver medals with adjective
    "Big_Silver": "perak_besar",
    "Small_Silver": "perak_kecil",

    # Home/Away
    "Home_team": "tim_tuan_rumah",
    "Away_team": "tim_tamu",
    "Home_Phone": "telepon_rumah",
    "home_phone": "telepon_rumah",
    "Home_Conference": "konferensi_rumah",

    # Time patterns
    "CLASS_TIME": "waktu_kelas",
    "lesson_time": "waktu_pelajaran",
    "Time_of_day": "waktu_dalam_sehari",
    "Time_of_purchase": "waktu_pembelian",
    "end_date_time": "waktu_tanggal_akhir",
    "start_date_time": "waktu_tanggal_mulai",

    # Count patterns (jumlah_X)
    "access_count": "jumlah_akses",
    "booked_count": "jumlah_dipesan",
    "bathroom_count": "jumlah_kamar_mandi",
    "bedroom_count": "jumlah_kamar_tidur",
    "dock_count": "jumlah_dermaga",
    "review_count": "jumlah_ulasan",
    "room_count": "jumlah_kamar",
    "share_count": "jumlah_saham",
    "Wins_count": "jumlah_kemenangan",

    # Year patterns (tahun_X)
    "opening_year": "tahun_pembukaan",
    "Openning_year": "tahun_pembukaan",
    "purchase_year": "tahun_pembelian",
    "release_year": "tahun_rilis",
    "Song_release_year": "tahun_rilis_lagu",
    "birth_year": "tahun_lahir",
    "death_year": "tahun_kematian",
    "founded_year": "tahun_didirikan",
    "graduation_year": "tahun_kelulusan",
    "hire_year": "tahun_perekrutan",
    "start_year": "tahun_mulai",
    "end_year": "tahun_akhir",
    "years_working": "tahun_bekerja",
    "Years_Working": "tahun_bekerja",
    "Years_working": "tahun_bekerja",

    # Month/Day patterns
    "birth_month": "bulan_lahir",
    "death_month": "bulan_kematian",
    "birth_day": "hari_lahir",
    "death_day": "hari_kematian",
    "Day_Number": "nomor_hari",

    # "Party" as business entity, not celebration
    "Party": "pihak",
    "party": "pihak",
    "Party_Addresses": "alamat_pihak",
    "Party_Details": "rincian_pihak",
    "Party_Forms": "formulir_pihak",
    "Party_ID": "id_pihak",
    "party_id": "id_pihak",
    "Party_Services": "layanan_pihak",
    "Party_name": "nama_pihak",
    "party_email": "email_pihak",
    "party_phone": "telepon_pihak",
    "Third_Party_Companies": "perusahaan_pihak_ketiga",

    # "Parent" as hierarchical, not biological
    "Parent_Collection_ID": "id_koleksi_induk",
    "Parent_Document_Object_ID": "id_objek_dokumen_induk",
    "Parent_Service_Type_Code": "kode_tipe_layanan_induk",
    "parent_document_structure_code": "kode_struktur_dokumen_induk",
    "parent_entry_id": "id_entri_induk",
    "parent_functional_area_code": "kode_area_fungsional_induk",
    "parent_organization_id": "id_organisasi_induk",
    "parent_product_id": "id_produk_induk",

    # "Race" as competition, not ethnicity
    "Race_ID": "id_balapan",
    "Race_Name": "nama_balapan",
    "raceId": "id_balapan",
    "race_id": "id_balapan",

    # "Record" as catatan (notes), not rekaman (audio recording)
    "Record_Company": "perusahaan_rekaman",  # this one IS audio recording context
    "Record_ID": "id_catatan",
    "competition_record": "catatan_kompetisi",
    "Voting_record": "catatan_pemungutan_suara",

    # Body_Builder → binaragawan
    "Body_Builder": "binaragawan",
    "Body_Builder_ID": "id_binaragawan",

    # HeadOfState
    "HeadOfState": "kepala_negara",

    # Part → komponen
    "part_id": "id_komponen",
    "part_name": "nama_komponen",
    "part_fault_id": "id_kesalahan_komponen",
    "Part_Faults": "kesalahan_komponen",

    # Value → nilai (not nilai_data)
    "Value": "nilai",
    "value": "nilai",
    "Market_Value": "nilai_pasar",
    "Market_Value_billion": "nilai_pasar_miliar",
    "Market_Value_in_Billion": "nilai_pasar_dalam_miliar",
    "attribute_value": "nilai_atribut",
    "feature_value": "nilai_fitur",
    "product_characteristic_value": "nilai_karakteristik_produk",
    "total_value_purchased": "total_nilai_dibeli",
    "value_points": "poin_nilai",

    # "charge" in context of "in charge of"
    "Is_Main_in_Charge": "adalah_utama_penanggung_jawab",
    "Member_in_charge_ID": "id_anggota_penanggung_jawab",
    "Num_of_shaff_in_charge": "jumlah_staf_penanggung_jawab",

    # "Principal" as primary/main
    "Principal_activities": "aktivitas_utama",

    # Hours/Per patterns
    "HoursPerWeek": "jam_per_minggu",
    "Show_times_per_day": "waktu_pertunjukan_per_hari",

    # Assessment/Notes
    "Assessment_Notes": "catatan_penilaian",

    # Census/Rankings
    "Census_Ranking": "peringkat_sensus",

    # Economy rates
    "City_fuel_economy_rate": "tarif_ekonomi_bahan_bakar_kota",

    # ACC patterns
    "ACC_Regular_Season": "acc_musim_reguler",

    # "Official" as adjective
    "Official_ratings_(millions)": "peringkat_resmi_jutaan",

    # Shop → toko (not toko_belanja)
    "Shop_ID": "id_toko",
    "shop_id": "id_toko",

    # Claim processing
    "Claim_Processing_ID": "id_pemrosesan_klaim",
    "Claim_Stage_ID": "id_tahap_klaim",
    "Claims_Processing": "pemrosesan_klaim",
    "Claims_Processing_Stages": "tahapan_pemrosesan_klaim",

    # Specific compound columns with "by" patterns
    "Created_by_Staff_ID": "id_staf_pembuat",
    "Destroyed_by_Employee_ID": "id_karyawan_perusak",
    "Destruction_Authorised_by_Employee_ID": "id_karyawan_otorisasi_pemusnahan",
    "closure_authorised_by_staff_id": "id_staf_otorisasi_penutupan",
    "recorded_by_staff_id": "id_staf_pencatat",
    "reported_by_staff_id": "id_staf_pelapor",
    "caused_by_ship_id": "id_kapal_penyebab",

    # Fix compound IDs that got mangled
    "Customer_Event_ID": "id_acara_pelanggan",
    "Customer_Event_Note_ID": "id_catatan_acara_pelanggan",
    "Customer_Interaction_ID": "id_interaksi_pelanggan",
    "Customer_Policy_ID": "id_polis_pelanggan",
    "Customers_and_Services_ID": "id_pelanggan_dan_layanan",
    "Document_Object_ID": "id_objek_dokumen",
    "Document_Subset_ID": "id_subset_dokumen",
    "Host_city_ID": "id_kota_tuan_rumah",
    "Invoice_Item_ID": "id_barang_faktur",
    "Next_Claim_Stage_ID": "id_tahap_klaim_selanjutnya",
    "Order_Item_ID": "id_barang_pesanan",
    "Poker_Player_ID": "id_pemain_poker",
    "Product_in_Event_ID": "id_produk_dalam_acara",
    "Related_Document_Object_ID": "id_objek_dokumen_terkait",
    "Royal_Family_ID": "id_keluarga_kerajaan",
    "Student_Answer_ID": "id_jawaban_mahasiswa",
    "Theme_Park_ID": "id_taman_tema",
    "Tourist_Attraction_ID": "id_atraksi_wisata",
    "Workshop_Group_ID": "id_kelompok_lokakarya",

    # City_channel_ID
    "City_channel_ID": "id_saluran_kota",

    # Various specific compound columns
    "actual_order_id": "id_pesanan_aktual",
    "book_club_id": "id_klub_buku",
    "business_rates_id": "id_tarif_bisnis",
    "catalog_entry_id": "id_entri_katalog",
    "contact_staff_id": "id_staf_kontak",
    "council_tax_id": "id_pajak_dewan",
    "current_address_id": "id_alamat_saat_ini",
    "customer_address_id": "id_alamat_pelanggan",
    "degree_program_id": "id_program_gelar",
    "dept_store_chain_id": "id_jaringan_toko_departemen",
    "dept_store_id": "id_toko_departemen",
    "driver_employee_id": "id_karyawan_pengemudi",
    "employee_address_id": "id_alamat_karyawan",
    "employer_organisation_id": "id_organisasi_pemberi_kerja",
    "end_station_id": "id_stasiun_akhir",
    "engineer_visit_id": "id_kunjungan_insinyur",
    "fault_log_entry_id": "id_entri_log_kesalahan",
    "location_address_id": "id_alamat_lokasi",
    "mailed_to_address_id": "id_alamat_pengiriman",
    "maintenance_contract_company_id": "id_perusahaan_kontrak_pemeliharaan",
    "maintenance_contract_id": "id_kontrak_pemeliharaan",
    "manager_staff_id": "id_staf_manajer",
    "master_customer_id": "id_pelanggan_utama",
    "media_type_id": "id_tipe_media",
    "original_language_id": "id_bahasa_asli",
    "owner_user_id": "id_pengguna_pemilik",
    "permanent_address_id": "id_alamat_permanen",
    "person_address_id": "id_alamat_individu",
    "player_api_id": "id_api_pemain",
    "player_fifa_api_id": "id_api_fifa_pemain",
    "previous_entry_id": "id_entri_sebelumnya",
    "purchase_transaction_id": "id_transaksi_pembelian",
    "sales_transaction_id": "id_transaksi_penjualan",
    "start_station_id": "id_stasiun_mulai",
    "student_address_id": "id_alamat_mahasiswa",
    "student_course_id": "id_kursus_mahasiswa",
    "student_enrolment_id": "id_pendaftaran_mahasiswa",
    "student_loan_id": "id_pinjaman_mahasiswa",
    "supplier_company_id": "id_perusahaan_pemasok",
    "staff_address_id": "id_alamat_staf",
    "user_address_id": "id_alamat_pengguna",
    "team_api_id": "id_api_tim",
    "team_fifa_api_id": "id_api_fifa_tim",
    "tv_show_ID": "id_acara_tv",

    # Specific table names
    "Party_Addresses": "alamat_pihak",
    "Party_Forms": "formulir_pihak",
    "Party_Services": "layanan_pihak",
    "Theme_Park_Details": "rincian_taman_tema",

    # "Hire" in rental context
    "Products_for_Hire": "produk_untuk_disewa",
    "date_last_hire": "tanggal_sewa_terakhir",

    #  "_of_" connector patterns (drop "of" in Indonesian) 
    "Date_of_Answer": "tanggal_jawaban",
    "Date_of_Birth": "tanggal_lahir",
    "Date_of_Claim": "tanggal_klaim",
    "Date_of_Settlement": "tanggal_penyelesaian",
    "Date_of_ceremony": "tanggal_upacara",
    "date_of_attendance": "tanggal_kehadiran",
    "date_of_birth": "tanggal_lahir",
    "date_of_completion": "tanggal_penyelesaian",
    "date_of_enrolment": "tanggal_pendaftaran",
    "date_of_latest_logon": "tanggal_masuk_terbaru",
    "date_of_latest_revision": "tanggal_revisi_terbaru",
    "date_of_loan": "tanggal_pinjaman",
    "date_of_notes": "tanggal_catatan",
    "date_of_publication": "tanggal_publikasi",
    "date_of_registration": "tanggal_registrasi",
    "date_of_transaction": "tanggal_transaksi",
    "date_of_transcript": "tanggal_transkrip",
    "date_of_treatment": "tanggal_perawatan",
    "day_of_week": "hari_dalam_minggu",
    "First_Notification_of_Loss": "notifikasi_pertama_kerugian",
    "Level_of_Membership": "tingkat_keanggotaan",
    "Level_of_membership": "tingkat_keanggotaan",
    "Location_of_office": "lokasi_kantor",
    "Member_of_club": "anggota_klub",
    "Num_of_Audience": "jumlah_penonton",
    "Num_of_Component": "jumlah_komponen",
    "Num_of_Factories": "jumlah_pabrik",
    "Num_of_Pieces": "jumlah_potongan",
    "Num_of_Shops": "jumlah_toko",
    "Num_of_Staff": "jumlah_staf",
    "Num_of_Ticket": "jumlah_tiket",
    "Num_of_employees": "jumlah_karyawan",
    "Num_of_shops": "jumlah_toko",
    "Num_of_staff": "jumlah_staf",
    "Num_of_stock": "jumlah_stok",
    "Num_Employees": "jumlah_karyawan",
    "Number_of_Championships": "jumlah_kejuaraan",
    "Number_of_Platforms": "jumlah_platform",
    "Number_of_Stories": "jumlah_lantai",
    "Number_of_hosts": "jumlah_tuan_rumah",
    "Number_of_matches": "jumlah_pertandingan",
    "Number_of_product_category": "jumlah_kategori_produk",
    "Number_Deaths": "jumlah_kematian",
    "Number_cities": "jumlah_kota",
    "Number_city_affected": "jumlah_kota_terdampak",
    "Number_products": "jumlah_produk",
    "Number_in_season": "nomor_dalam_musim",
    "Rank_of_the_Year": "peringkat_tahun_ini",
    "Rank_of_the_year": "peringkat_tahun_ini",
    "Status_of_Thing_Code": "kode_status_hal",
    "Timed_Locations_of_Things": "lokasi_berwaktu_hal",
    "Timed_Status_of_Things": "status_berwaktu_hal",
    "Type_Of_Restaurant": "tipe_restoran",
    "Type_of_Question_Code": "kode_tipe_pertanyaan",
    "Type_of_Thing_Code": "kode_tipe_hal",
    "Type_of_powertrain": "tipe_penggerak",
    "Year_of_Founded": "tahun_didirikan",
    "Year_of_Work": "tahun_kerja",
    "amount_of_discount": "jumlah_diskon",
    "amount_of_loan": "jumlah_pinjaman",
    "amount_of_refund": "jumlah_pengembalian_dana",
    "amount_of_transaction": "jumlah_transaksi",
    "cost_of_treatment": "biaya_perawatan",
    "disposition_of_ship": "disposisi_kapal",
    "hall_of_fame": "aula_ketenaran",
    "no_of_customers": "jumlah_pelanggan",
    "no_of_loans": "jumlah_pinjaman",
    "num_of_episodes": "jumlah_episode",
    "num_of_seasons": "jumlah_musim",
    "purpose_of_meeting": "tujuan_rapat",
    "text_of_notes": "teks_catatan",
    "unit_of_measure": "satuan_ukuran",

    #  "_in_" connector patterns (in → dalam/di) 
    "Assets_in_Billion": "aset_dalam_miliar",
    "Assets_in_Events": "aset_dalam_acara",
    "Budget_in_Billions": "anggaran_dalam_miliar",
    "Date_in_Location_From": "tanggal_di_lokasi_dari",
    "Date_in_Locaton_To": "tanggal_di_lokasi_ke",
    "Documents_in_Collections": "dokumen_dalam_koleksi",
    "Memory_in_G": "memori_dalam_g",
    "Participants_in_Events": "peserta_dalam_acara",
    "Parties_in_Events": "pihak_dalam_acara",
    "Performers_in_Bookings": "penampil_dalam_pemesanan",
    "Price_in_Dollar": "harga_dalam_dolar",
    "Products_in_Events": "produk_dalam_acara",
    "Profits_in_Billion": "keuntungan_dalam_miliar",
    "Questions_in_Exams": "pertanyaan_dalam_ujian",
    "Rank_in_Round": "peringkat_dalam_putaran",
    "Rank_in_series": "peringkat_dalam_seri",
    "Rating_in_percent": "peringkat_nilai_dalam_persen",
    "Readers_in_Million": "pembaca_dalam_juta",
    "Sales_in_Billion": "penjualan_dalam_miliar",
    "Share_in_percent": "saham_dalam_persen",
    "Staff_in_Meetings": "staf_dalam_rapat",
    "Staff_in_Processes": "staf_dalam_proses",
    "Students_in_Detention": "mahasiswa_dalam_penahanan",
    "Gross_in_dollar": "bruto_dalam_dolar",
    "amount_paid_in_full_yn": "jumlah_dibayar_penuh_yn",

    #  "_and_" connector patterns (and → dan) 
    "Date_and_Date": "tanggal_dan_tanggal",
    "Date_and_Time": "tanggal_dan_waktu",
    "Course_Authors_and_Tutors": "penulis_dan_tutor_kursus",
    "Customers_and_Services": "pelanggan_dan_layanan",
    "Customers_and_Services_Details": "rincian_pelanggan_dan_layanan",
    "Services_and_Channels_Details": "rincian_layanan_dan_saluran",
    "Sheep_and_Goats": "domba_dan_kambing",
    "cre_Doc_and_collections": "cre_dokumen_dan_koleksi",

    #  "_or_" connector patterns (or → atau) 
    "Author_or_Editor": "penulis_atau_editor",
    "Boys_or_Girls": "laki_laki_atau_perempuan",
    "Day_or_Boarding": "harian_atau_asrama",
    "good_or_bad_customer": "pelanggan_baik_atau_buruk",

    #  "_to_" connector patterns (to → untuk/ke/hingga) 
    "Documents_to_be_Destroyed": "dokumen_untuk_dimusnahkan",
    "How_to_Get_There": "cara_menuju_ke_sana",
    "active_to_date": "aktif_hingga_tanggal",
    "assigned_to_staff_id": "id_staf_ditugaskan",

    #  "_with_" connector patterns 
    "Affiliated_With": "berafiliasi_dengan",
    "Documents_with_Expenses": "dokumen_dengan_pengeluaran",

    #  "_by_" connector patterns 
    "Directed_by": "disutradarai_oleh",
    "directed_by": "disutradarai_oleh",
    "Eliminated_By": "dieliminasi_oleh",
    "Organized_by": "diselenggarakan_oleh",
    "Written_by": "ditulis_oleh",
    "written_by": "ditulis_oleh",
    "made_by": "dibuat_oleh",
    "numCitedBy": "jumlah_dikutip_oleh",

    #  "_in_" trailing patterns 
    "Enrolled_in": "terdaftar_di",
    "Faculty_Participates_in": "fakultas_berpartisipasi_di",
    "Incorporated_in": "didirikan_di",
    "Lives_in": "tinggal_di",
    "Participates_in": "berpartisipasi_di",
    "Trained_In": "terlatih_di",
    "most_popular_in": "paling_populer_di",
    "date_moved_in": "tanggal_pindah_masuk",
    "checkin": "checkin",

    #  "_from_" patterns 
    "Start_from": "mulai_dari",
    "Date_Effective_From": "tanggal_efektif_dari",
    "date_address_from": "tanggal_alamat_dari",
    "date_assigned_from": "tanggal_ditugaskan_dari",
    "date_contact_from": "tanggal_kontak_dari",
    "date_supplied_from": "tanggal_dipasok_dari",

    #  "is_" prefix patterns 
    "IsOfficial": "apakah_resmi",
    "Is_Male": "apakah_pria",
    "Is_male": "apakah_pria",
    "Is_first_director": "apakah_direktur_pertama",
    "Is_free": "apakah_gratis",
    "is_buyer": "apakah_pembeli",
    "is_open": "apakah_buka",
    "is_seller": "apakah_penjual",

    #  "has_" prefix patterns 
    "Has_Allergy": "memiliki_alergi",
    "Has_Clearance": "memiliki_izin",
    "Has_Pet": "memiliki_hewan_peliharaan",
    "Has_amenity": "memiliki_fasilitas",

    #  "all_" prefix patterns 
    "All_Documents": "semua_dokumen",
    "All_Games": "semua_permainan",
    "All_Games_Percent": "persen_semua_permainan",
    "All_Home": "semua_kandang",
    "All_Neutral": "semua_netral",
    "All_Road": "semua_tandang",
    "all_star": "bintang_semua",

    #  Misc remaining English fragments 
    "Continuation_of": "kelanjutan",
    "Member_of": "anggota",
    "best_of": "terbaik",
    "FlightNo": "nomor_penerbangan",

    #  Special compound translations 
    "Attorney_General": "jaksa_agung",
    "Apartment_Bookings": "pemesanan_apartemen",
    "Apartment_Buildings": "bangunan_apartemen",
    "Apartment_Facilities": "fasilitas_apartemen",
    "Aircraft_Movements": "pergerakan_pesawat",
    "Gross_worldwide": "bruto_seluruh_dunia",
    "cre_Doc_Workflow": "cre_alur_kerja_dokumen",
    "cre_Students_Information_Systems": "cre_sistem_informasi_mahasiswa",

    #  SQLite internal tables — MUST keep as-is 
    "sqlite_sequence": "sqlite_sequence",

    #  Additional missing overrides (connector patterns) 
    "active_from_date": "tanggal_mulai_aktif",
    "move_in_year": "tahun_pindah",
    "divergence_from_human_lineage": "divergensi_dari_garis_keturunan_manusia",
    "sequence_identity_to_human_protein": "identitas_urutan_protein_manusia",
    "price_in_dollars": "harga_dalam_dolar",
    "price_in_euros": "harga_dalam_euro",
    "price_in_pounds": "harga_dalam_poundsterling",
    "customers_and_orders": "pelanggan_dan_pesanan",
    "lost_in_battle": "kalah_dalam_pertempuran",

    #  Previously untranslated compound identifiers (SQL keyword words) 
    "CheckIn": "checkin",
    "CheckOut": "checkout",
    "DateExped": "tanggal_ekspedisi",
    "DateOrder": "tanggal_pesanan",
    "Order_Date": "tanggal_pesanan",
    "order_date": "tanggal_pesanan",
    "End_Date": "tanggal_akhir",
    "end_date": "tanggal_akhir",
    "END_DATE": "tanggal_akhir",
    "create_date": "tanggal_buat",
    "createdate": "tanggal_buat",
    "Date": "tanggal",
    "date": "tanggal",
    "date_from": "tanggal_dari",
    "date_left": "tanggal_keluar",
    "date_valid_from": "tanggal_berlaku_dari",
    "datestamp": "cap_tanggal",
    "releasedate": "tanggal_rilis",
    "status_date": "tanggal_status",
    "time": "waktu",
    "time_slot": "slot_waktu",
    "time_slot_id": "id_slot_waktu",
    "order_id": "id_pesanan",
    "Order_ID": "id_pesanan",
    "order_status": "status_pesanan",
    "EMP_DOB": "tanggal_lahir_karyawan",
    "EMP_FNAME": "nama_depan_karyawan",
    "EMP_LNAME": "nama_belakang_karyawan",
    "EMP_HIREDATE": "tanggal_rekrut_karyawan",
    "EMP_JOBCODE": "kode_pekerjaan_karyawan",
    "STU_DOB": "tanggal_lahir_mahasiswa",
    "STU_FNAME": "nama_depan_mahasiswa",
    "STU_LNAME": "nama_belakang_mahasiswa",
    "STU_GPA": "ipk_mahasiswa",
    "STU_HRS": "jam_mahasiswa",
    "STU_INIT": "inisial_mahasiswa",
    "EMAIL": "email",
    "Email": "email",
    "email": "email",
    "IdOrder": "id_pesanan",
    "Editor_ID": "id_editor",
    "Film_ID": "id_film",
    "Festival_ID": "id_festival",
    "Headphone_ID": "id_headphone",
    "HH_ID": "id_hh",
    "Match_ID": "id_pertandingan",
    "Museum_ID": "id_museum",
    "Pilot_ID": "id_pilot",
    "Pilot_Id": "id_pilot",
    "PlanetID": "id_planet",
    "Platform_ID": "id_platform",
    "Program_ID": "id_program",
    "Radio_ID": "id_radio",
    "Round_ID": "id_babak",
    "Volume_ID": "id_volume",
    "FNOL_ID": "id_fnol",
    "album_id": "id_album",
    "film_id": "id_film",
    "genre_id": "id_genre",
    "hotel_id": "id_hotel",
    "investor_id": "id_investor",
    "lot_id": "id_lot",
    "tip_id": "id_tip",
    "tourney_id": "id_turnamen",
    "tourney_date": "tanggal_turnamen",
    "transaction_date": "tanggal_transaksi",
    "transaction_id": "id_transaksi",
    "If_full_time": "apakah_penuh_waktu",
    "Is_full_time": "apakah_penuh_waktu",
    "Is_online": "apakah_daring",
    "Round": "babak",
    "round": "babak",
    "Length": "panjang",
    "length": "panjang",
    "text": "teks",
    "cast": "pemeran",
    "match": "pertandingan",
    "count": "jumlah",
    "total": "total",
    "Total": "total",
    "film": "film",
    "film_text": "teks_film",
    "pilot": "pilot",
    "museum": "museum",
    "platform": "platform",
    "program": "program",
    "headphone": "headphone",
    "editor": "editor",
    "debut": "debut",
    "era": "era",
    "bank": "bank",
    "dataset": "dataset",
    "protein": "protein",
    "Episode": "episode",
    "Label": "label",
    "Model": "model",
    "Pilot": "pilot",
    "Investor": "investor",
    "Slots": "slot",
    "Sub_tittle": "sub_judul",
    "Gradeconversion": "konversi_nilai",
    "Tracklists": "daftar_lagu",
    "View_Unit_Status": "status_tampilan_unit",
    "Total_WL": "total_wl",
    "Total_disk_area": "total_area_disk",
    "CMI_Cross_References": "referensi_silang_cmi",
    "cmi_cross_ref_id": "id_referensi_silang_cmi",
    "Minor_in": "minor_di",
    "Prescribes": "meresepkan",
    "Earpads": "bantalan_telinga",
    "bio_data": "data_biografi",
    "chip_model": "model_chip",
    "codeshare": "berbagi_kode",
    "festival_detail": "detail_festival",
    "inseason": "dalam_musim",
    "postseason": "pasca_musim",
    "fielding": "penjagaan",
    "fielding_postseason": "penjagaan_pasca_musim",
    "pitching": "lemparan",
    "pitching_postseason": "lemparan_pasca_musim",
    "Has_Allergy": "memiliki_alergi",
    "callsign": "tanda_panggil",
    "countrylanguage": "bahasa_negara",
    "focal_length_mm": "panjang_fokus_mm",
    "keyphrase": "frasa_kunci",
    "highlow": "tinggi_rendah",
    "isAVA": "apakah_ava",
    "gradepoint": "nilai_poin",
    "lettergrade": "nilai_huruf",
    "ENROLL": "pendaftaran",
    "FTE_AY": "fte_ay",
    "TotalEnrollment_AY": "total_pendaftaran_ay",
    "Porphyria": "porfiria",
    "Amerindian": "amerindian",
    "Multiracial": "multirasial",
    "Hanyu_Pinyin": "hanyu_pinyin",
    "Hanzi": "hanzi",
    "Area": "luas",
    "Area_km": "luas_km",
    "Area_km_2": "luas_km_2",
    "roller_coaster": "roller_coaster",

    #  Compound _id entries with _id in the middle 
    "Club_ID_1": "id_klub_1",
    "Club_ID_2": "id_klub_2",
    "league_id_loser": "id_liga_pecundang",
    "league_id_winner": "id_liga_pemenang",
    "team_id_br": "id_tim_br",
    "team_id_lahman45": "id_tim_lahman45",
    "team_id_loser": "id_tim_pecundang",
    "team_id_retro": "id_tim_retro",
    "team_id_winner": "id_tim_pemenang",

    #  Fix remaining _id suffix entries 
    "Address_ID": "id_alamat",
    "address_id": "id_alamat",
    "LOCATION_ID": "id_lokasi",
    "Location_ID": "id_lokasi",
    "Show_ID": "id_pertunjukan",
    "Performance_ID": "id_penampilan",
    "Performance": "penampilan",
    "performance": "penampilan",
    "school_performance": "kinerja_sekolah",

    #  Fix table name collisions 
    # restaurant_1: Type_Of_Restaurant vs Restaurant_Type
    "Type_Of_Restaurant": "jenis_restoran",
    "Restaurant_Type": "tipe_restoran",
    # wine_1: grapes vs wine
    "grapes": "buah_anggur",
    "wine": "anggur",
    # bakery_1 (test_database): goods vs items both -> barang
    "items": "item",
    "notes_id": "id_catatan",
    "resultId": "id_hasil",
    "venueId": "id_tempat",

    
    # CONSISTENCY FIXES — ensure same lowercased key → same translation
    
    # first_name variants → all must be nama_depan
    "first_name": "nama_depan",
    "First_Name": "nama_depan",
    "FIRST_NAME": "nama_depan",
    "FirstName": "nama_depan",
    "Firstname": "nama_depan",
    # last_name variants → all must be nama_belakang
    "last_name": "nama_belakang",
    "Last_Name": "nama_belakang",
    "LAST_NAME": "nama_belakang",
    "LastName": "nama_belakang",
    "Lastname": "nama_belakang",
    # other_details variants → all must be rincian_lain
    "other_details": "rincian_lain",
    "Other_Details": "rincian_lain",
    # lname/fname → proper translations
    "LName": "nama_belakang",
    "Lname": "nama_belakang",
    "lname": "nama_belakang",
    "FName": "nama_depan",
    "Fname": "nama_depan",
    "fname": "nama_depan",
    # area → luas (geographic area)
    "Area": "luas",
    "area": "luas",
    # dname → nama_d (keep abbreviated form since it's DB-specific)
    "DName": "nama_d",
    "Dname": "nama_d",
    # document_type_description → consistent
    "Document_Type_Description": "deskripsi_tipe_dokumen",
    "document_type_description": "deskripsi_tipe_dokumen",
    # order_item_id → consistent
    "Order_Item_ID": "id_barang_pesanan",
    "order_item_id": "id_barang_pesanan",
    # pname → consistent
    "Pname": "nama_p",
    "pName": "nama_p",
    # time variants
    "Time": "waktu",
    "time": "waktu",

    
    # DB_ID FIXES — Indonesian word order & linguistic correctness
    

    #  Untranslated db_ids that need translation 
    "tvshow": "acara_tv",

    #  Wrong word order (must follow DM: head noun first, modifier second) 
    "advertising_agencies": "agensi_periklanan",
    "bbc_channels": "saluran_bbc",
    "bike_racing": "balap_sepeda",
    "book_press": "percetakan_buku",
    "book_review": "ulasan_buku",
    "car_racing": "balap_mobil",
    "car_road_race": "balapan_jalan_mobil",
    "club_leader": "pemimpin_klub",
    "concert_singer": "penyanyi_konser",
    "country_language": "bahasa_negara",
    "district_spokesman": "juru_bicara_distrik",
    "government_shift": "pergeseran_pemerintah",
    "headphone_store": "toko_headphone",
    "online_exams": "ujian_daring",
    "real_estate_rentals": "penyewaan_real_estate",
    "region_building": "bangunan_wilayah",
    "restaurant_bills": "tagihan_restoran",
    "sing_contest": "kontes_menyanyi",
    "tv_shows": "tayangan_tv",
    "vehicle_driver": "pengemudi_kendaraan",
    "vehicle_rent": "sewa_kendaraan",
    "video_game": "permainan_video",

    #  Semantic fixes for db_ids 
    "party_host": "tuan_rumah_pesta",
    "party_people": "orang_partai",
    "e_commerce": "e_niaga",

    
    # WORD ORDER FIXES — 3+ word compounds & special multi-word cases
    

    # Table names with 3+ words (wrong DM order)
    "Actual_Order_Products": "produk_pesanan_aktual",
    "Catalog_Contents_Additional_Attributes": "atribut_tambahan_isi_katalog",
    "Customer_Address_History": "riwayat_alamat_pelanggan",
    "Customer_Contact_Channels": "saluran_kontak_pelanggan",
    "Customer_Event_Notes": "catatan_acara_pelanggan",
    "Customer_Master_Index": "indeks_master_pelanggan",
    "Delivery_Route_Locations": "lokasi_rute_pengiriman",
    "Delivery_Routes": "rute_pengiriman",
    "Department_Store_Chain": "jaringan_toko_departemen",
    "Document_Functional_Areas": "area_fungsional_dokumen",
    "Document_Sections_Images": "gambar_bagian_dokumen",
    "Fault_Log_Parts": "bagian_log_kesalahan",
    "Invoice_Line_Items": "barang_baris_faktur",
    "Mailshot_Campaigns": "kampanye_surat_massal",
    "Mailshot_Customers": "pelanggan_surat_massal",
    "Other_Available_Features": "fitur_tersedia_lainnya",
    "Other_Property_Features": "fitur_properti_lainnya",
    "Problem_Category_Codes": "kode_kategori_masalah",
    "Problem_Status_Codes": "kode_status_masalah",
    "Ref_Document_Status": "ref_status_dokumen",
    "Ref_Payment_Methods": "ref_metode_pembayaran",
    "Ref_Product_Categories": "ref_kategori_produk",
    "Ref_Shipping_Agents": "ref_agen_pengiriman",
    "Regular_Order_Products": "produk_pesanan_reguler",
    "Staff_Department_Assignments": "penugasan_departemen_staf",
    "Student_Course_Attendance": "kehadiran_kursus_mahasiswa",
    "Student_Course_Enrolment": "pendaftaran_kursus_mahasiswa",
    "Student_Course_Registrations": "registrasi_kursus_mahasiswa",
    "Student_Enrolment_Courses": "kursus_pendaftaran_mahasiswa",
    "Student_Tests_Taken": "ujian_diambil_mahasiswa",
    "Tourist_Attraction_Features": "fitur_atraksi_wisata",
    "View_Product_Availability": "tampilan_ketersediaan_produk",
    "Web_client_accelerator": "akselerator_klien_web",
    "accelerator_compatible_browser": "peramban_kompatibel_akselerator",

    # Table names where English→Indonesian word count differs
    "basketball_match": "pertandingan_bola_basket",
    "TV_Channel": "saluran_tv",
    "TV_series": "seri_tv",
    "Video_Games": "permainan_video",
    "Tourist_Attractions": "atraksi_wisata",
    "Theme_Parks": "taman_tema",
    "Royal_Family": "keluarga_kerajaan",
    "Street_Markets": "pasar_jalanan",
    "Skills_Required_To_Fix": "keterampilan_wajib_untuk_perbaikan",

    # Additional 2-word table names that auto-fix might miss
    "Dorm_amenity": "fasilitas_asrama",
    "dorm_amenity": "fasilitas_asrama",
    "Electoral_Register": "daftar_pemilihan",
    "Maintenance_Contracts": "kontrak_pemeliharaan",
    "Maintenance_Engineers": "insinyur_pemeliharaan",
    "Marketing_Regions": "wilayah_pemasaran",
    "On_Call": "panggilan_siaga",
    "Parking_Fines": "denda_parkir",
    "Rent_Arrears": "tunggakan_sewa",
    "Research_Staff": "staf_penelitian",
    "CLASS_ROOM": "ruang_kelas",

    # Column names with wrong order (not caught by auto-fix)
    "market_share": "pangsa_pasar",
    "broadcast_share": "pangsa_siaran",
    "parking_lots": "lahan_parkir",

    #  Preserve correct order (false positives of auto-fix) 
    "Date_Opened": "tanggal_dibuka",
    "date_opened": "tanggal_dibuka",
    "Year_Opened": "tahun_dibuka",
    "year_opened": "tahun_dibuka",
    "date_registered": "tanggal_terdaftar",
    "Date_registered": "tanggal_terdaftar",
    "Total_Attendance": "total_kehadiran",
    "total_attendance": "total_kehadiran",
    "Total_spent": "total_dihabiskan",
    "total_spent": "total_dihabiskan",
    "Visits_Restaurant": "kunjungan_restoran",
    "Class_A": "kelas_a",
    "Class_AA": "kelas_aa",
    "Counties_Represented": "kabupaten_diwakili",
    "Clean_Jerk": "angkat_bersih",
    "all_star": "semua_bintang",
}




# MAIN FIX FUNCTION


def run_manual_corrections(
    dict_path: Path,
    words_path: Path,
    tables_json_path: Path = None,
) -> dict:
    """Apply all manual corrections to the translation dictionary.

    Steps:
        1. Apply WORD_FIXES to the word map
        2. Rebuild identifier dict from updated word map
        2.1. Fix SQL-keyword words in compound identifiers
        2.5. Strip English connectors from translated values
        3. Fix _id suffix → id_ prefix (Indonesian word order)
        4. Apply IDENT_OVERRIDES
        5. Auto-fix word order using HEAD_NOUNS
        6. Detect and fix collisions
        7. Save results

    Returns dict with stats.
    """
    if tables_json_path is None:
        tables_json_path = SPIDER_TABLES_JSON

    # Load data
    with open(words_path, "r", encoding="utf-8") as f:
        wm = json.load(f)
    with open(dict_path, "r", encoding="utf-8") as f:
        td = json.load(f)

    print(f"Loaded word map: {len(wm)} entries")
    print(f"Loaded dict: {len(td)} entries")

    stats = {}

    #  Step 1: Apply word fixes 
    fixed_words = 0
    for word, translation in WORD_FIXES.items():
        if word in wm:
            if wm[word] != translation:
                wm[word] = translation
                fixed_words += 1
        else:
            wm[word] = translation
            fixed_words += 1
    stats["words_fixed"] = fixed_words
    print(f"\nStep 1: Fixed/added {fixed_words} words in word map")

    with open(words_path, "w", encoding="utf-8") as f:
        json.dump(wm, f, ensure_ascii=False, indent=2)

    #  Step 2: Rebuild identifier dict 
    extracted = extract_identifiers_from_tables_json(tables_json_path)
    all_idents = set(extracted["all_identifiers"].keys())
    test_tables = tables_json_path.parent / "test_data" / "tables.json"
    if test_tables.exists():
        test_extracted = extract_identifiers_from_tables_json(test_tables)
        all_idents |= set(test_extracted["all_identifiers"].keys())

    td = build_identifier_translation_dict(all_idents, wm)
    changed = sum(1 for k, v in td.items() if k != v)
    stats["identifiers_translated"] = changed
    print(f"\nStep 2: Rebuilt dict: {changed}/{len(td)} identifiers translated")

    #  Step 2.1: Fix SQL-keyword words 
    sql_kw_fixes = 0
    for key, val in list(td.items()):
        if key.lower() != val.lower():
            parts = val.split("_")
            new_parts = []
            changed_any = False
            for part in parts:
                low = part.lower()
                if low in SQL_KEYWORD_TRANSLATIONS and low == part:
                    replacement = SQL_KEYWORD_TRANSLATIONS[low]
                    if replacement != low:
                        new_parts.append(replacement)
                        changed_any = True
                    else:
                        new_parts.append(part)
                else:
                    new_parts.append(part)
            if changed_any:
                td[key] = "_".join(new_parts)
                sql_kw_fixes += 1
        else:
            words = split_identifier(key)
            if len(words) <= 1:
                continue
            new_words = []
            any_changed = False
            for word in words:
                low = word.lower()
                if low in wm and wm[low] != low:
                    new_words.append(wm[low])
                    any_changed = True
                elif low in SQL_KEYWORD_TRANSLATIONS:
                    new_words.append(SQL_KEYWORD_TRANSLATIONS[low])
                    if SQL_KEYWORD_TRANSLATIONS[low] != low:
                        any_changed = True
                else:
                    new_words.append(low)
            if any_changed:
                td[key] = "_".join(new_words)
                sql_kw_fixes += 1
    stats["sql_keyword_fixes"] = sql_kw_fixes
    print(f"\nStep 2.1: Fixed {sql_kw_fixes} SQL-keyword words in identifiers")

    #  Step 2.5: Strip English connectors 
    connector_fixes = 0
    for key, val in list(td.items()):
        if key.lower() == val.lower():
            continue
        new_val = val
        for eng_conn, idn_conn in CONNECTOR_REPLACEMENTS.items():
            if eng_conn in new_val:
                new_val = new_val.replace(eng_conn, idn_conn)
        for eng_conn in ["of_", "the_", "and_", "or_", "in_", "to_", "for_", "by_", "from_"]:
            if new_val.startswith(eng_conn):
                new_val = new_val[len(eng_conn):]
        while "__" in new_val:
            new_val = new_val.replace("__", "_")
        new_val = new_val.strip("_")
        if new_val != val:
            td[key] = new_val
            connector_fixes += 1
    stats["connector_fixes"] = connector_fixes
    print(f"\nStep 2.5: Fixed {connector_fixes} leftover English connectors")

    #  Step 3: Fix _id suffix → id_ prefix 
    id_fixes = 0
    for key, val in list(td.items()):
        if val.lower().endswith("_id") and val.lower() != "id" and key.lower() != val.lower():
            base = val[:-3]
            if base:
                new_val = f"id_{base}"
                if new_val != val:
                    td[key] = new_val
                    id_fixes += 1
    stats["id_prefix_fixes"] = id_fixes
    print(f"\nStep 3: Fixed {id_fixes} _id suffix -> id_ prefix entries")

    #  Step 4: Apply IDENT_OVERRIDES 
    override_count = 0
    for ident, new_val in IDENT_OVERRIDES.items():
        if ident in td:
            if td[ident] != new_val:
                td[ident] = new_val
                override_count += 1
    stats["overrides_applied"] = override_count
    print(f"\nStep 4: Applied {override_count} identifier overrides")

    #  Step 5: Auto word-order fix (comprehensive) 
    # Build word-level map from WORD_FIXES + Google Translate word map
    word_level_map = {}
    for w, t in WORD_FIXES.items():
        word_level_map[w.lower()] = t.lower()
    for w, t in wm.items():
        if '_' not in w and '_' not in t:
            if w.lower() not in word_level_map:
                word_level_map[w.lower()] = t.lower()

    preps = {'of', 'in', 'for', 'to', 'and', 'with', 'on', 'at', 'by', 'from',
             'di', 'ke', 'dari', 'untuk', 'dan', 'dengan', 'pada', 'oleh', 'atau'}
    unit_suffixes = {'billion', 'million', 'percent', 'thousand', 'hundred',
                     'm', 'km', 'mm', 'pct'}

    auto_fixes = 0
    for key, val in list(td.items()):
        if key.lower() == val.lower() or key in IDENT_OVERRIDES:
            continue

        eng_parts = [p.lower() for p in key.replace(' ', '_').split('_') if p]
        idn_parts = [p.lower() for p in val.split('_') if p]

        # Only handle 2-word compounds with matching word count
        if len(eng_parts) != 2 or len(idn_parts) != 2:
            continue
        # Skip prepositions/connectors
        if any(p in preps for p in eng_parts + idn_parts):
            continue
        # Skip if first Indonesian word is already a known head noun (correct DM)
        if idn_parts[0] in HEAD_NOUNS_SHOULD_BE_FIRST:
            continue
        # Skip unit/measurement suffixes (Assets_billion, Budget_million)
        if eng_parts[1] in unit_suffixes:
            continue
        # Skip past participle second words (Date_Opened = head + modifier)
        if eng_parts[1].endswith('ed'):
            continue

        t1 = word_level_map.get(eng_parts[0], '')
        t2 = word_level_map.get(eng_parts[1], '')

        if not t1 or not t2:
            continue

        # Check if translation preserves English word order (wrong for Indonesian)
        if idn_parts[0] == t1 and idn_parts[1] == t2:
            new_val = f"{t2}_{t1}"
            td[key] = new_val
            auto_fixes += 1
    stats["word_order_fixes"] = auto_fixes
    print(f"\nStep 5: Auto-fixed word order for {auto_fixes} identifiers")

    #  Step 6: Collision detection and fixing 
    print("\nStep 6: Checking for collisions...")
    col_collisions = detect_per_table_collisions(tables_json_path, td)
    tbl_collisions = detect_table_name_collisions(tables_json_path, td)
    db_collisions = detect_db_id_collisions(tables_json_path, td)
    print(f"  Column collisions: {len(col_collisions)}")
    print(f"  Table name collisions: {len(tbl_collisions)}")
    print(f"  DB ID collisions: {len(db_collisions)}")

    all_collisions = col_collisions + tbl_collisions + db_collisions
    if all_collisions:
        fixes = build_collision_fixes(td, tables_json_path, wm)
        print(f"\n  Auto-fixing {len(fixes)} collisions:")
        for en, idn in sorted(fixes.items()):
            td[en] = idn
            print(f"    {en} -> {idn}")
        # Re-check
        col2 = detect_per_table_collisions(tables_json_path, td)
        tbl2 = detect_table_name_collisions(tables_json_path, td)
        db2 = detect_db_id_collisions(tables_json_path, td)
        print(f"  After fix — col: {len(col2)}, tbl: {len(tbl2)}, db: {len(db2)}")
        stats["collisions_fixed"] = len(fixes)
    else:
        stats["collisions_fixed"] = 0

    #  Step 7: Save 
    with open(dict_path, "w", encoding="utf-8") as f:
        json.dump(td, f, ensure_ascii=False, indent=2, sort_keys=True)

    translated = sum(1 for k, v in td.items() if k.lower() != v.lower())
    unchanged = len(td) - translated
    stats["total"] = len(td)
    stats["translated"] = translated
    stats["unchanged"] = unchanged

    print(f"\n{'='*60}")
    print(f"FINAL RESULT: {len(td)} entries, {translated} translated, {unchanged} unchanged")
    print(f"{'='*60}")

    return stats


if __name__ == "__main__":
    from .config import SCHEMA_DICT_PATH, SCHEMA_DICT_WORDS_PATH
    run_manual_corrections(SCHEMA_DICT_PATH, SCHEMA_DICT_WORDS_PATH)
