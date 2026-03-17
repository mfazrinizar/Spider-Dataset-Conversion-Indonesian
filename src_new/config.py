"""
Configuration and constants for the IDSpider1 translation pipeline.
"""

from pathlib import Path

#  Paths 

# Root of the idspider1 project
IDSPIDER1_ROOT = Path(__file__).resolve().parent.parent

# Original Spider dataset
SPIDER_DIR = IDSPIDER1_ROOT / "data" / "spider"
SPIDER_TABLES_JSON = SPIDER_DIR / "tables.json"
SPIDER_DEV_JSON = SPIDER_DIR / "dev.json"
SPIDER_TRAIN_SPIDER_JSON = SPIDER_DIR / "train_spider.json"
SPIDER_TRAIN_OTHERS_JSON = SPIDER_DIR / "train_others.json"
SPIDER_DEV_GOLD_SQL = SPIDER_DIR / "dev_gold.sql"
SPIDER_TRAIN_GOLD_SQL = SPIDER_DIR / "train_gold.sql"
SPIDER_DATABASE_DIR = SPIDER_DIR / "database"

SPIDER_TEST_DATA_DIR = SPIDER_DIR / "test_data"
SPIDER_TEST_DATABASE_DIR = SPIDER_DIR / "test_database"

# SQL keywords file
SQL_KEYWORDS_FILE = SPIDER_DIR / "sql_keywords.txt"

# Output: translated Indonesian dataset
OUTPUT_DIR = IDSPIDER1_ROOT / "data" / "idspider"
OUTPUT_TABLES_JSON = OUTPUT_DIR / "tables.json"
OUTPUT_DEV_JSON = OUTPUT_DIR / "dev.json"
OUTPUT_TRAIN_SPIDER_JSON = OUTPUT_DIR / "train_spider.json"
OUTPUT_TRAIN_OTHERS_JSON = OUTPUT_DIR / "train_others.json"
OUTPUT_TRAIN_JSON = OUTPUT_DIR / "train.json"
OUTPUT_DEV_GOLD_SQL = OUTPUT_DIR / "dev_gold.sql"
OUTPUT_TRAIN_GOLD_SQL = OUTPUT_DIR / "train_gold.sql"
OUTPUT_DATABASE_DIR = OUTPUT_DIR / "database"

OUTPUT_TEST_DATA_DIR = OUTPUT_DIR / "test_data"
OUTPUT_TEST_DATABASE_DIR = OUTPUT_DIR / "test_database"

# Intermediate files
INTERMEDIATE_DIR = IDSPIDER1_ROOT / "data" / "intermediate"
SCHEMA_DICT_PATH = INTERMEDIATE_DIR / "schema_translation_dict.json"
SCHEMA_DICT_WORDS_PATH = INTERMEDIATE_DIR / "schema_translation_dict_words.json"
COLLISION_REPORT_PATH = INTERMEDIATE_DIR / "collision_report.json"
TRANSLATED_QUESTIONS_DIR = INTERMEDIATE_DIR / "translated_questions"

#  SQL Keywords 

# Core SQL keywords that must never be translated
SQL_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE",
    "IS", "NULL", "EXISTS", "HAVING", "GROUP", "BY", "ORDER", "ASC", "DESC",
    "LIMIT", "OFFSET", "JOIN", "INNER", "LEFT", "RIGHT", "OUTER", "CROSS",
    "ON", "AS", "DISTINCT", "ALL", "UNION", "INTERSECT", "EXCEPT", "INSERT",
    "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "ALTER",
    "DROP", "INDEX", "VIEW", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
    "CONSTRAINT", "CHECK", "DEFAULT", "UNIQUE", "CASCADE", "CASE", "WHEN",
    "THEN", "ELSE", "END", "CAST", "INTEGER", "INT", "REAL", "FLOAT",
    "DOUBLE", "DECIMAL", "NUMERIC", "CHAR", "VARCHAR", "TEXT", "BLOB",
    "BOOLEAN", "DATE", "TIME", "TIMESTAMP", "DATETIME", "BIGINT", "SMALLINT",
    "TINYINT", "COUNT", "SUM", "AVG", "MIN", "MAX", "ABS", "ROUND",
    "UPPER", "LOWER", "LENGTH", "SUBSTR", "TRIM", "COALESCE", "IFNULL",
    "NULLIF", "REPLACE", "GROUP_CONCAT", "TOTAL", "TYPEOF", "INSTR",
    "HEX", "ZEROBLOB", "LIKELIHOOD", "UNLIKELY", "UNICODE", "QUOTE",
    "AUTOINCREMENT", "PRAGMA", "BEGIN", "COMMIT", "ROLLBACK", "TRANSACTION",
    "ABORT", "FAIL", "IGNORE", "EXPLAIN", "ATTACH", "DETACH", "REINDEX",
    "VACUUM", "ANALYZE", "WITH", "RECURSIVE", "IF", "TEMP", "TEMPORARY",
    "TRIGGER", "AFTER", "BEFORE", "INSTEAD", "OF", "FOR", "EACH", "ROW",
    "TRUE", "FALSE", "GLOB", "REGEXP", "MATCH", "ESCAPE", "NATURAL",
    "USING", "FULL", "CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP",
    "COLLATE", "NOCASE", "BINARY", "RTRIM", "NO", "ACTION", "RESTRICT",
    "DEFERRABLE", "DEFERRED", "IMMEDIATE", "INITIALLY",
}

# Tokens that should never be translated (technical abbreviations)
NEVER_TRANSLATE_TOKENS = {
    "id", "url", "api", "pk", "fk", "uuid", "uid", "gid", "pid",
    "ip", "tcp", "udp", "http", "https", "ftp", "ssh", "ssl", "tls",
    "html", "css", "js", "sql", "xml", "json", "csv", "pdf", "png",
    "jpg", "gif", "svg", "mp3", "mp4", "avi", "iso", "zip", "tar",
    "gzip", "utf", "ascii", "rgb", "hex", "md5", "sha", "rsa",
    "cpu", "gpu", "ram", "rom", "ssd", "hdd", "usb", "hdmi",
    "wifi", "lan", "wan", "dns", "dhcp", "smtp", "imap", "pop",
    "iot", "ai", "ml", "nlp", "gps", "nfc", "rfid", "qr",
    "ok", "vs", "etc", "misc", "info", "no", "t", "f", "n",
}

#  Known Disambiguation Rules 
# Maps frozenset of English identifiers → {english: indonesian} disambiguation
# Used when multiple English words translate to the same Indonesian word

KNOWN_DISAMBIGUATIONS = {
    # state/country → negara conflicts
    frozenset({"state", "country"}): {"state": "negara_bagian", "country": "negara"},
    frozenset({"state", "province"}): {"state": "negara_bagian", "province": "provinsi"},
    frozenset({"country", "nation"}): {"country": "negara", "nation": "bangsa"},
    frozenset({"state", "status"}): {"state": "negara_bagian", "status": "status"},
    frozenset({"state", "condition"}): {"state": "keadaan", "condition": "kondisi"},

    # district/county/area/region/zone conflicts
    frozenset({"district", "county"}): {"district": "distrik", "county": "kabupaten"},
    frozenset({"district", "area"}): {"district": "distrik", "area": "area"},
    frozenset({"area", "region"}): {"area": "area", "region": "wilayah"},
    frozenset({"region", "zone"}): {"region": "wilayah", "zone": "zona"},
    frozenset({"district", "region"}): {"district": "distrik", "region": "wilayah"},

    # road/street/way/path
    frozenset({"road", "street"}): {"road": "jalan", "street": "jalan_raya"},
    frozenset({"road", "ramp"}): {"road": "jalan", "ramp": "jalur"},
    frozenset({"path", "route"}): {"path": "jalur", "route": "rute"},

    # fee/cost/price/charge
    frozenset({"fee", "cost"}): {"fee": "biaya", "cost": "ongkos"},
    frozenset({"fee", "price"}): {"fee": "biaya", "price": "harga"},
    frozenset({"cost", "price"}): {"cost": "biaya", "price": "harga"},
    frozenset({"charge", "fee"}): {"charge": "tarif", "fee": "biaya"},

    # name/title
    frozenset({"name", "title"}): {"name": "nama", "title": "judul"},

    # win/victory
    frozenset({"win", "won"}): {"win": "menang", "won": "dimenangkan"},

    # home/house
    frozenset({"home", "house"}): {"home": "rumah", "house": "tempat_tinggal"},

    # time/hour/period
    frozenset({"time", "hour"}): {"time": "waktu", "hour": "jam"},
    frozenset({"time", "period"}): {"time": "waktu", "period": "periode"},
    frozenset({"date", "time"}): {"date": "tanggal", "time": "waktu"},

    # match/game
    frozenset({"match", "game"}): {"match": "pertandingan", "game": "permainan"},

    # class/type/category
    frozenset({"class", "type"}): {"class": "kelas", "type": "tipe"},
    frozenset({"class", "category"}): {"class": "kelas", "category": "kategori"},
    frozenset({"type", "category"}): {"type": "tipe", "category": "kategori"},

    # people/person
    frozenset({"people", "person"}): {"people": "orang", "person": "individu"},

    # number/count
    frozenset({"number", "count"}): {"number": "nomor", "count": "jumlah"},

    # city/town
    frozenset({"city", "town"}): {"city": "kota", "town": "kota_kecil"},

    # description/detail
    frozenset({"description", "detail"}): {"description": "deskripsi", "detail": "rincian"},

    # start/begin
    frozenset({"start", "begin"}): {"start": "mulai", "begin": "awal"},

    # end/finish
    frozenset({"end", "finish"}): {"end": "akhir", "finish": "selesai"},

    # result/outcome
    frozenset({"result", "outcome"}): {"result": "hasil", "outcome": "keluaran"},

    # rank/position
    frozenset({"rank", "position"}): {"rank": "peringkat", "position": "posisi"},

    # score/point
    frozenset({"score", "point"}): {"score": "skor", "point": "poin"},

    # location/place
    frozenset({"location", "place"}): {"location": "lokasi", "place": "tempat"},

    # record/entry
    frozenset({"record", "entry"}): {"record": "rekaman", "entry": "entri"},

    # member/participant
    frozenset({"member", "participant"}): {"member": "anggota", "participant": "peserta"},

    # role/function
    frozenset({"role", "function"}): {"role": "peran", "function": "fungsi"},

    # amount/quantity
    frozenset({"amount", "quantity"}): {"amount": "jumlah", "quantity": "kuantitas"},

    # note/comment/remark
    frozenset({"note", "comment"}): {"note": "catatan", "comment": "komentar"},

    # section/part
    frozenset({"section", "part"}): {"section": "bagian", "part": "bagian_dari"},

    # year/annual
    frozenset({"year", "annual"}): {"year": "tahun", "annual": "tahunan"},

    # lost/loss
    frozenset({"lost", "loss"}): {"lost": "kalah", "loss": "kerugian"},
}

# Words that should use specific translations regardless of context
PREFERRED_TRANSLATIONS = {
    "people": "orang",
    "person": "individu",
    "state": "negara_bagian",
    "country": "negara",
    "county": "kabupaten",
    "district": "distrik",
    "region": "wilayah",
    "area": "area",
    "zone": "zona",
    "city": "kota",
    "town": "kota_kecil",
    "village": "desa",
    "location": "lokasi",
    "place": "tempat",
    "address": "alamat",
    "province": "provinsi",
    "name": "nama",
    "title": "judul",
    "description": "deskripsi",
    "type": "tipe",
    "category": "kategori",
    "class": "kelas",
    "status": "status",
    "code": "kode",
    "number": "nomor",
    "count": "jumlah",
    "amount": "jumlah_uang",
    "quantity": "kuantitas",
    "price": "harga",
    "cost": "biaya",
    "fee": "biaya_tambahan",
    "charge": "tarif",
    "date": "tanggal",
    "time": "waktu",
    "year": "tahun",
    "month": "bulan",
    "day": "hari",
    "hour": "jam",
    "minute": "menit",
    "second": "detik",
    "age": "usia",
    "size": "ukuran",
    "weight": "berat",
    "height": "tinggi",
    "length": "panjang",
    "width": "lebar",
    "score": "skor",
    "point": "poin",
    "rank": "peringkat",
    "position": "posisi",
    "level": "tingkat",
    "grade": "nilai",
    "rating": "peringkat_nilai",
    "result": "hasil",
    "record": "rekaman",
    "note": "catatan",
    "comment": "komentar",
    "section": "bagian",
    "part": "bagian_dari",
    "chapter": "bab",
    "role": "peran",
    "member": "anggota",
    "group": "kelompok",
    "team": "tim",
    "match": "pertandingan",
    "game": "permainan",
    "event": "acara",
    "show": "pertunjukan",
    "episode": "episode",
    "season": "musim",
    "round": "putaran",
    "win": "menang",
    "loss": "kalah",
    "draw": "seri",
    "road": "jalan",
    "street": "jalan_raya",
    "route": "rute",
    "flight": "penerbangan",
    "airline": "maskapai",
    "airport": "bandara",
    "station": "stasiun",
    "platform": "platform",
    "channel": "saluran",
    "network": "jaringan",
    "company": "perusahaan",
    "organization": "organisasi",
    "department": "departemen",
    "school": "sekolah",
    "college": "perguruan_tinggi",
    "university": "universitas",
    "student": "mahasiswa",
    "teacher": "guru",
    "professor": "profesor",
    "employee": "karyawan",
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
    "race": "ras",
    "gender": "jenis_kelamin",
    "sex": "jenis_kelamin",
    "born": "lahir",
    "death": "kematian",
    "population": "populasi",
    "continent": "benua",
    "language": "bahasa",
    "currency": "mata_uang",
    "budget": "anggaran",
    "salary": "gaji",
    "revenue": "pendapatan",
    "profit": "keuntungan",
    "tax": "pajak",
    "order": "pesanan",
    "product": "produk",
    "item": "barang",
    "stock": "stok",
    "brand": "merek",
    "model": "model",
    "version": "versi",
    "color": "warna",
    "material": "bahan",
    "style": "gaya",
}
