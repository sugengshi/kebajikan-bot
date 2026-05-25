# 🌱 Bot Kebajikan Harian — Seed System

Bot Telegram untuk memantau dan mengembangkan kebajikan setiap hari berdasarkan **10 Bibit Baik Utama**.

---

## Deploy ke Railway (PostgreSQL)

### 1. Buat Bot Telegram
1. Buka [@BotFather](https://t.me/BotFather) → `/newbot` → ikuti instruksi
2. Salin token yang diberikan

### 2. Push ke GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/username/kebajikan-bot.git
git push -u origin main
```

### 3. Deploy di Railway
1. Buka [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
2. Pilih repo Anda
3. Klik **+ New** → **Database → Add PostgreSQL**
4. Railway otomatis menambahkan `DATABASE_URL` ke environment
5. Di **Settings → Variables**, tambahkan satu variabel:
   ```
   BOT_TOKEN = token_dari_botfather_anda
   ```
6. Railway deploy otomatis — bot langsung berjalan

### 4. Test
Buka bot di Telegram → kirim `/start`

---

## Jadwal Harian (WIB default)

| Jam   | Aktivitas |
|-------|-----------|
| 06:00 | Ganti atau lanjutkan fokus kebajikan |
| 07:00 | Refleksi pagi |
| 12:00 | Refleksi siang |
| 18:00 | Refleksi sore |
| 20:00 | Tambahan perbuatan baik |
| 21:00 | Ringkasan perbuatan baik hari ini |
| 21:30 | Arsip pribadi lengkap |

Gunakan `/setjam pagi 07:30` untuk kustomisasi per pengguna.

---

## Perintah Bot

| Perintah | Fungsi |
|----------|--------|
| `/start` | Mulai onboarding |
| `/kebajikan` | Fokus kebajikan hari ini |
| `/refleksi` | Isi refleksi sekarang |
| `/ganti` | Ganti fokus kebajikan |
| `/tambahan` | Tambah perbuatan baik |
| `/laporan` | Ringkasan hari ini |
| `/setjam pagi 07:30` | Atur jam notifikasi |
| `/bantuan` | Daftar perintah |

---

## Struktur File

```
kebajikan-bot/
├── main.py                    # Entry point
├── requirements.txt
├── Procfile                   # Railway: web: python main.py
├── data/
│   └── kebajikan.py           # 10 Kebajikan Utama
├── handlers/
│   ├── conversation.py        # Onboarding & refleksi
│   └── scheduler.py           # Pesan terjadwal
└── utils/
    ├── database.py            # PostgreSQL via asyncpg
    ├── messages.py            # Template pesan
    └── smart_evaluator.py     # Evaluasi SMART + rekomendasi kebajikan
```

---

## Kapasitas

| Komponen | Batas |
|----------|-------|
| PostgreSQL (Railway Starter) | ~10.000 pengguna aktif |
| Telegram rate limit | 30 pesan/detik |
| Scheduler (APScheduler) | Tidak terbatas |

Bottleneck pertama adalah Telegram rate limit, bukan database.

---

_Seed System — Menanam bibit kebajikan setiap hari._ 🙏
