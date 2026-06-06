# utils/i18n.py
# Complete bilingual string table. T(key, lang, **kwargs) returns translated string.

STRINGS = {

    # ─── ONBOARDING ──────────────────────────────────────────────────────────

    "pilih_bahasa": {
        "id": "🌏 *Selamat datang! / Welcome!*\n\nSilakan pilih bahasa Anda. / Please choose your language:",
        "en": "🌏 *Selamat datang! / Welcome!*\n\nSilakan pilih bahasa Anda. / Please choose your language:",
    },
    "bahasa_dipilih": {
        "id": "✅ Bahasa Indonesia dipilih.",
        "en": "✅ English selected.",
    },

    # ─── TIMEZONE ────────────────────────────────────────────────────────────

    "pilih_timezone": {
        "id": (
            "🕐 *Pilih Zona Waktu Anda*\n\n"
            "Ini digunakan untuk jadwal notifikasi harian Anda."
        ),
        "en": (
            "🕐 *Choose Your Timezone*\n\n"
            "This is used for your daily notification schedule."
        ),
    },
    "timezone_dipilih": {
        "id": "✅ Zona waktu *{tz}* dipilih.",
        "en": "✅ Timezone *{tz}* selected.",
    },
    "tz_wib":   {"id": "🇮🇩 WIB (UTC+7) — Jakarta",        "en": "🇮🇩 WIB (UTC+7) — Jakarta"},
    "tz_wita":  {"id": "🇮🇩 WITA (UTC+8) — Bali/Makassar", "en": "🇮🇩 WITA (UTC+8) — Bali/Makassar"},
    "tz_wit":   {"id": "🇮🇩 WIT (UTC+9) — Papua",          "en": "🇮🇩 WIT (UTC+9) — Papua"},
    "tz_sgt":   {"id": "🇸🇬 SGT (UTC+8) — Singapore",      "en": "🇸🇬 SGT (UTC+8) — Singapore"},
    "tz_myt":   {"id": "🇲🇾 MYT (UTC+8) — Malaysia",       "en": "🇲🇾 MYT (UTC+8) — Malaysia"},
    "tz_ist":   {"id": "🇮🇳 IST (UTC+5:30) — India",       "en": "🇮🇳 IST (UTC+5:30) — India"},
    "tz_aest":  {"id": "🇦🇺 AEST (UTC+10) — Sydney",       "en": "🇦🇺 AEST (UTC+10) — Sydney"},
    "tz_gmt":   {"id": "🌍 GMT (UTC+0) — London",           "en": "🌍 GMT (UTC+0) — London"},
    "tz_cet":   {"id": "🇪🇺 CET (UTC+1) — Europe",         "en": "🇪🇺 CET (UTC+1) — Europe"},
    "tz_est":   {"id": "🇺🇸 EST (UTC-5) — New York",       "en": "🇺🇸 EST (UTC-5) — New York"},
    "tz_pst":   {"id": "🇺🇸 PST (UTC-8) — Los Angeles",    "en": "🇺🇸 PST (UTC-8) — Los Angeles"},

    # ─── SAMBUTAN ────────────────────────────────────────────────────────────

    "sambutan": {
        "id": (
            "🙏 *Selamat datang di Bot Kebajikan Harian*\n\n"
            "Bot ini memandu Anda memantau dan mengembangkan kebajikan setiap hari "
            "berdasarkan *10 Bibit Baik Utama*.\n\n"
            "Pilih level praktik Anda:"
        ),
        "en": (
            "🙏 *Welcome to the Daily Virtue Bot*\n\n"
            "This bot guides you in monitoring and developing virtues every day "
            "based on the *10 Main Virtue Seeds*.\n\n"
            "Choose your practice level:"
        ),
    },
    "sambutan_kembali": {
        "id": (
            "🙏 Selamat datang kembali, *{name}*!\n\n"
            "Gunakan /{cmd_kebajikan} untuk melihat fokus hari ini, "
            "/{cmd_refleksi} untuk refleksi, atau /{cmd_help} untuk daftar perintah."
        ),
        "en": (
            "🙏 Welcome back, *{name}*!\n\n"
            "Use /{cmd_kebajikan} to see today's focus, "
            "/{cmd_refleksi} for reflection, or /{cmd_help} for the command list."
        ),
    },
    "silakan_start": {
        "id": "Silakan mulai dengan /start.",
        "en": "Please start with /start.",
    },

    # ─── LEVEL SELECTION ─────────────────────────────────────────────────────

    "pilih_level": {
        "id": "📊 *Pilih Level Praktik Anda:*",
        "en": "📊 *Choose Your Practice Level:*",
    },
    "level_pemula_label":   {"id": "🌱 Pemula",                         "en": "🌱 Beginner"},
    "level_menengah_label": {"id": "🌿 Praktisi Menengah",              "en": "🌿 Intermediate Practitioner"},
    "level_mahir_label":    {"id": "🌳 Praktisi Mahir",                 "en": "🌳 Advanced Practitioner"},
    "level_advanced_label": {"id": "🪷 Advanced (Sumpah Bodhisattva)",  "en": "🪷 Advanced (Bodhisattva Vows)"},
    "level_super_label":    {"id": "💎 Super Advanced (Sumpah Tantra)", "en": "💎 Super Advanced (Tantric Vows)"},
    "level_dipilih": {
        "id": "👍 Level Anda: *{label}*\n_{desc}_",
        "en": "👍 Your level: *{label}*\n_{desc}_",
    },

    # ─── SMART GOAL ──────────────────────────────────────────────────────────

    "tujuan_smart_prompt": {
        "id": (
            "🎯 *Tujuan SMART Anda*\n\n"
            "Tuliskan satu tujuan yang ingin Anda capai melalui praktik kebajikan ini.\n\n"
            "Bot akan mengevaluasi apakah tujuan Anda memenuhi kriteria *SMART:*\n"
            "• *S*pesifik — jelas dan konkret\n"
            "• *M*easurable — bisa diukur\n"
            "• *A*chievable — bisa dicapai\n"
            "• *R*elevant — bermakna bagi Anda\n"
            "• *T*ime-bound — ada batas waktunya\n\n"
            "_Contoh: Dalam 30 hari ke depan, saya ingin lebih sabar berbicara dengan anak-anak saya._\n\n"
            "✏️ *Tuliskan tujuan Anda:*"
        ),
        "en": (
            "🎯 *Your SMART Goal*\n\n"
            "Write one goal you want to achieve through this virtue practice.\n\n"
            "The bot will evaluate whether your goal meets the *SMART* criteria:\n"
            "• *S*pecific — clear and concrete\n"
            "• *M*easurable — can be measured\n"
            "• *A*chievable — can be accomplished\n"
            "• *R*elevant — meaningful to you\n"
            "• *T*ime-bound — has a deadline\n\n"
            "_Example: In the next 30 days, I want to speak more patiently with my children._\n\n"
            "✏️ *Write your goal:*"
        ),
    },
    "smart_lanjut_label":  {"id": "✅ Lanjutkan",      "en": "✅ Continue"},
    "smart_revisi_label":  {"id": "✏️ Perbaiki Goal",  "en": "✏️ Improve Goal"},
    "smart_revisi_prompt": {
        "id": "✏️ *Tulis ulang tujuan SMART Anda:*\n\n_Ingat: sertakan siapa, apa, ukuran, relevansi, dan batas waktu._",
        "en": "✏️ *Rewrite your SMART goal:*\n\n_Remember: include who, what, measure, relevance, and time frame._",
    },

    # ─── KEBAJIKAN RECOMMENDATION ────────────────────────────────────────────

    "rekomendasi_intro": {
        "id": (
            "🔍 *Berdasarkan tujuan Anda, bot menemukan kebajikan yang paling sesuai:*\n\n"
            "{level_text}\n\n{alasan}\n"
            "─────────────────────\n"
            "Apakah Anda setuju dengan rekomendasi ini?"
        ),
        "en": (
            "🔍 *Based on your goal, the bot found the most suitable virtues:*\n\n"
            "{level_text}\n\n{alasan}\n"
            "─────────────────────\n"
            "Do you agree with this recommendation?"
        ),
    },
    "rekomendasi_level_pemula":   {"id": "Sebagai Pemula, bot merekomendasikan *1 kebajikan utama:*",             "en": "As a Beginner, the bot recommends *1 main virtue:*"},
    "rekomendasi_level_menengah": {"id": "Sebagai Praktisi Menengah, bot merekomendasikan *3 kebajikan:*",        "en": "As an Intermediate Practitioner, the bot recommends *3 virtues:*"},
    "rekomendasi_level_mahir":    {"id": "Sebagai Praktisi Mahir, ini *titik masuk* yang direkomendasikan:",      "en": "As an Advanced Practitioner, here is the recommended *entry point:*"},
    "setuju_label":        {"id": "✅ Mulai Sekarang!", "en": "✅ Start Now!"},
    "pilih_sendiri_label": {"id": "🔄 Pilih sendiri",  "en": "🔄 Choose myself"},

    # ─── ONBOARDING COMPLETE ─────────────────────────────────────────────────

    "onboarding_selesai": {
        "id": (
            "🎉 *Selamat, {name}!*\n\n"
            "Anda telah resmi memulai perjalanan kebajikan Anda.\n\n"
            "*Fokus kebajikan Anda:*\n{daftar}\n\n"
            "*Jadwal harian ({tz}):*\n{jadwal}\n\n"
            "Gunakan /setjam untuk mengatur ulang jam notifikasi. 🙏"
        ),
        "en": (
            "🎉 *Congratulations, {name}!*\n\n"
            "You have officially started your virtue journey.\n\n"
            "*Your virtue focus:*\n{daftar}\n\n"
            "*Daily schedule ({tz}):*\n{jadwal}\n\n"
            "Use /setjam to adjust notification times. 🙏"
        ),
    },
    "jadwal_harian": {
        "id": (
            "06:00 — Pilihan fokus hari ini\n"
            "07:00 — Refleksi pagi\n"
            "12:00 — Refleksi siang\n"
            "18:00 — Refleksi sore\n"
            "20:00 — Tambahan perbuatan baik\n"
            "21:00 — Ringkasan positif\n"
            "21:30 — Arsip pribadi"
        ),
        "en": (
            "06:00 — Today's focus check\n"
            "07:00 — Morning reflection\n"
            "12:00 — Midday reflection\n"
            "18:00 — Afternoon reflection\n"
            "20:00 — Additional good deeds\n"
            "21:00 — Positive summary\n"
            "21:30 — Personal archive"
        ),
    },

    # ─── 06:00 FOCUS CHECK ───────────────────────────────────────────────────

    "pagi_ganti_tanya": {
        "id": "🌅 *Selamat pagi!*\n\nFokus kebajikan Anda saat ini:\n\n{daftar}\n\nApakah ingin *mengganti* fokus kebajikan hari ini?",
        "en": "🌅 *Good morning!*\n\nYour current virtue focus:\n\n{daftar}\n\nWould you like to *change* your virtue focus for today?",
    },
    "pagi_ganti_ya_label":    {"id": "🔄 Ya, ganti",  "en": "🔄 Yes, change"},
    "pagi_ganti_tidak_label": {"id": "✅ Lanjutkan",   "en": "✅ Continue"},
    "pagi_lanjut_konfirmasi": {
        "id": "✅ *Fokus kebajikan hari ini tetap:*\n\n{daftar}\n\nRefleksi pagi akan dimulai sesuai jadwal. 🙏",
        "en": "✅ *Today's virtue focus remains:*\n\n{daftar}\n\nMorning reflection will begin on schedule. 🙏",
    },
    "pagi_ganti_instruksi": {
        "id": "🔄 Gunakan /{cmd_ganti} untuk memilih kebajikan fokus baru hari ini.",
        "en": "🔄 Use /{cmd_ganti} to choose a new virtue focus for today.",
    },

    # ─── SESI LABELS ─────────────────────────────────────────────────────────

    "sesi_pagi_label":  {"id": "🌅 Pagi (07:00)",  "en": "🌅 Morning (07:00)"},
    "sesi_siang_label": {"id": "☀️ Siang (12:00)", "en": "☀️ Midday (12:00)"},
    "sesi_sore_label":  {"id": "🌇 Sore (18:00)",  "en": "🌇 Afternoon (18:00)"},

    # ─── REFLEKSI ────────────────────────────────────────────────────────────

    "refleksi_positif": {
        "id": (
            "{sesi}\n{emoji} *{nama}*\n\n"
            "🔍 *Pertanyaan 1 dari 3*\n\n"
            "Selama *24 jam terakhir*, dengan memperluas makna kebajikan ini:\n\n"
            "_{pertanyaan}_\n\n"
            "✅ *Apa yang sudah Anda lakukan atau pikirkan yang SESUAI dengan kebajikan ini?*\n\n"
            "_Tidak ada yang terlalu kecil untuk dicatat. Bahkan niat pun sudah menjadi bibit._"
        ),
        "en": (
            "{sesi}\n{emoji} *{nama}*\n\n"
            "🔍 *Question 1 of 3*\n\n"
            "Over the *last 24 hours*, expanding the meaning of this virtue:\n\n"
            "_{pertanyaan}_\n\n"
            "✅ *What did you do or think that was IN LINE with this virtue?*\n\n"
            "_Nothing is too small to note. Even an intention is already a seed._"
        ),
    },
    "refleksi_negatif": {
        "id": (
            "{sesi}\n{emoji} *{nama}*\n\n"
            "🔍 *Pertanyaan 2 dari 3*\n\n"
            "⚠️ *Adakah perbuatan, perkataan, atau pikiran yang TIDAK SESUAI "
            "dengan kebajikan ini selama 24 jam terakhir?*\n\n"
            "_Jawab dengan jujur — ini bukan untuk dihakimi, tapi untuk disadari. "
            "Anda bisa menulis 'tidak ada' jika memang tidak ada._"
        ),
        "en": (
            "{sesi}\n{emoji} *{nama}*\n\n"
            "🔍 *Question 2 of 3*\n\n"
            "⚠️ *Were there any actions, words, or thoughts that were OUT OF LINE "
            "with this virtue in the last 24 hours?*\n\n"
            "_Answer honestly — this is not for judgment, but for awareness. "
            "You can write 'none' if there were none._"
        ),
    },
    "refleksi_rencana": {
        "id": (
            "{sesi}\n{emoji} *{nama}*\n\n"
            "🔍 *Pertanyaan 3 dari 3*\n\n"
            "🌱 *Untuk menyeimbangkan bibit negatif di atas, apa rencana konkret yang "
            "akan Anda lakukan dalam 24 jam ke depan?*\n\n"
            "_Satu tindakan kecil pun sudah cukup. Yang penting nyata dan bisa dilakukan._"
        ),
        "en": (
            "{sesi}\n{emoji} *{nama}*\n\n"
            "🔍 *Question 3 of 3*\n\n"
            "🌱 *To balance the negative seeds above, what concrete plan will "
            "you carry out in the next 24 hours?*\n\n"
            "_Even one small action is enough. What matters is that it is real and doable._"
        ),
    },
    "refleksi_konfirmasi": {
        "id": (
            "✨ *Catatan Anda untuk {nama}:*\n\n"
            "✅ *Positif:* {positif}\n\n"
            "⚠️ *Perlu diseimbangkan:* {negatif}\n\n"
            "🌱 *Rencana 24 jam ke depan:* {rencana}\n\n"
            "Terima kasih sudah jujur dan teliti! Catatan ini tersimpan. 🙏"
        ),
        "en": (
            "✨ *Your notes for {nama}:*\n\n"
            "✅ *Positive:* {positif}\n\n"
            "⚠️ *To balance:* {negatif}\n\n"
            "🌱 *Plan for next 24 hours:* {rencana}\n\n"
            "Thank you for being honest and thorough! Notes saved. 🙏"
        ),
    },
    "belum_mulai": {
        "id": "Silakan mulai dengan /start.",
        "en": "Please start with /start.",
    },
    "refleksi_pilih_sumpah": {
        "id": "📿 *Jadwal sumpah Anda hari ini:*\n\n_Ketuk sumpah yang ingin Anda renungkan._",
        "en": "📿 *Your vow schedule for today:*\n\n_Tap the vow you want to contemplate._",
    },
    "refleksi_pilih_sumpah_UNUSED": {
        "id": (
            "📿 *Pilih sumpah yang ingin Anda renungkan:*\n\n"
            "_(Ini adalah jadwal sumpah Anda hari ini)_"
        ),
        "en": (
            "📿 *Choose the vow you want to contemplate:*\n\n"
            "_(This is your vow schedule for today)_"
        ),
    },
    "refleksi_pilih_kebajikan": {
        "id": (
            "📝 *Pilih kebajikan yang ingin Anda refleksikan:*\n\n"
            "_(✅ = sudah diisi hari ini, ○ = belum diisi)_"
        ),
        "en": (
            "📝 *Choose the virtue you want to reflect on:*\n\n"
            "_(✅ = already filled today, ○ = not yet filled)_"
        ),
    },
    "refleksi_pilih_sesi": {
        "id": "📝 *Pilih sesi refleksi untuk* {nama}:",
        "en": "📝 *Choose the reflection session for* {nama}:",
    },
    "sesi_pagi_short":  {"id": "🌅 Pagi",  "en": "🌅 Morning"},
    "sesi_siang_short": {"id": "☀️ Siang", "en": "☀️ Midday"},
    "sesi_sore_short":  {"id": "🌇 Sore",  "en": "🌇 Afternoon"},
    "refleksi_belum": {
        "id": "Sesi refleksi tidak ditemukan. Gunakan /{cmd_refleksi} untuk memulai.",
        "en": "Reflection session not found. Use /{cmd_refleksi} to start.",
    },

    # ─── TAMBAHAN MALAM ──────────────────────────────────────────────────────

    "tambahan_malam_prompt": {
        "id": (
            "✨ *Catat Perbuatan Baik*\n\n"
            "Adakah *perbuatan baik* yang sudah Anda lakukan hari ini yang ingin dicatat?\n\n"
            "Ceritakan di sini, seberapapun kecilnya — setiap bibit berharga. 🙏\n\n"
            "_Catatan ini akan ditampilkan saat meditasi malam. Ketuk 'Tidak ada' jika tidak ada._"
        ),
        "en": (
            "✨ *Log Good Deeds*\n\n"
            "Are there any *good deeds* you've done today that you'd like to record?\n\n"
            "Share them here, no matter how small — every seed counts. 🙏\n\n"
            "_These will be shown during your evening meditation. Tap 'None' if there are none._"
        ),
    },
    "tambahan_tidak_ada_label": {"id": "✅ Tidak ada tambahan", "en": "✅ None"},
    "tambahan_tersimpan": {
        "id": "✨ Catatan tersimpan. Terima kasih! 🙏",
        "en": "✨ Notes saved. Thank you! 🙏",
    },
    "tambahan_selesai": {
        "id": "✅ Baik! Arsip akan dikirim pukul 21:30. 🙏",
        "en": "✅ Got it! The archive will be sent at 21:30. 🙏",
    },

    # ─── 21:00 RINGKASAN ─────────────────────────────────────────────────────

    "ringkasan_judul": {
        "id": "✨ *Perbuatan Baik Anda Hari Ini*\n_{tanggal}_\n\n─────────────────────\n",
        "en": "✨ *Your Good Deeds Today*\n_{tanggal}_\n\n─────────────────────\n",
    },
    "ringkasan_kosong": {
        "id": "✨ *Perbuatan Baik Hari Ini*\n\nBelum ada catatan yang masuk hari ini.\nTidak apa-apa — besok kita mulai lagi. 🙏",
        "en": "✨ *Good Deeds Today*\n\nNo notes recorded today.\nThat's okay — we start again tomorrow. 🙏",
    },
    "ringkasan_penutup": {
        "id": "_Bacalah perlahan. Rasakan setiap bibit yang sudah Anda tanam. Arsip lengkap akan dikirim pukul 21:30._ 🙏",
        "en": "_Read slowly. Feel every seed you have planted. The full archive will be sent at 21:30._ 🙏",
    },
    "tambahan_malam_label": {
        "id": "🌙 *Tambahan Perbuatan Baik:*\n",
        "en": "🌙 *Additional Good Deeds:*\n",
    },

    # ─── 21:30 ARSIP ─────────────────────────────────────────────────────────

    "arsip_judul": {
        "id": "📁 *Arsip Pribadi Harian{sapaan}*\n_{tanggal}_\n\n═════════════════════\n",
        "en": "📁 *Daily Personal Archive{sapaan}*\n_{tanggal}_\n\n═════════════════════\n",
    },
    "arsip_kosong": {
        "id": "📁 *Arsip Pribadi*\n\nBelum ada entri untuk hari ini.\nIstirahatlah dengan tenang. 🙏",
        "en": "📁 *Personal Archive*\n\nNo entries for today.\nRest well. 🙏",
    },
    "arsip_positif_label":  {"id": "✅ *Sesuai kebajikan:*\n",       "en": "✅ *In line with virtue:*\n"},
    "arsip_negatif_label":  {"id": "⚠️ *Perlu diseimbangkan:*\n",   "en": "⚠️ *To balance:*\n"},
    "arsip_rencana_label":  {"id": "🌱 *Rencana 24 jam ke depan:*\n","en": "🌱 *Plan for next 24 hours:*\n"},
    "arsip_tambahan_label": {"id": "🌙 *Tambahan Perbuatan Baik (20:00)*\n", "en": "🌙 *Additional Good Deeds (20:00)*\n"},
    "arsip_penutup": {
        "id": "_Arsip ini adalah catatan integritas Anda. Setiap bibit yang dicatat dengan jujur akan tumbuh. Istirahatlah dengan tenang._ 🙏",
        "en": "_This archive is a record of your integrity. Every seed honestly noted will grow. Rest well._ 🙏",
    },

    # ─── PENGINGAT ───────────────────────────────────────────────────────────

    "pengingat": {
        "id": "⏰ *Pengingat*\n\nRefleksi {sesi} untuk {emoji} *{nama}* Anda belum terisi.\nKetuk /{cmd_refleksi} untuk mulai mengisi sekarang. 🙏",
        "en": "⏰ *Reminder*\n\nYour {sesi} reflection for {emoji} *{nama}* hasn't been filled in yet.\nTap /{cmd_refleksi} to fill it in now. 🙏",
    },

    # ─── SUMPAH (ADVANCED/SUPER ADVANCED) ────────────────────────────────────

    "sumpah_label_advanced": {"id": "Sumpah Bodhisattva 🪷", "en": "Bodhisattva Vow 🪷"},
    "sumpah_label_super":    {"id": "Sumpah Tantra 💎",       "en": "Tantric Vow 💎"},
    "sumpah_pilih_urutan": {
        "id": (
            "📿 *{label}*\n"
            "*{jam} — Sumpah {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n"
            "_Anda akan menjawab 3 pertanyaan. Mulai dari mana?_"
        ),
        "en": (
            "📿 *{label}*\n"
            "*{jam} — Vow {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n"
            "_You will answer 3 questions. Where would you like to start?_"
        ),
    },
    "sumpah_order_pos_label": {"id": "✅ Mulai dari positif",  "en": "✅ Start with positives"},
    "sumpah_order_neg_label": {"id": "⚠️ Mulai dari negatif", "en": "⚠️ Start with negatives"},

    "sumpah_refleksi_positif": {
        "id": (
            "📿 *{label}*\n"
            "*{jam} — Sumpah {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n"
            "_Anda akan menjawab 3 pertanyaan terkait sumpah ini._\n\n"
            "✅ *Pertanyaan 1 dari 3*\n\n"
            "Selama 24 jam terakhir, adakah perbuatan, perkataan, atau pikiran yang "
            "SESUAI dengan sumpah ini?\n\n"
            "_Bahkan niat pun sudah menjadi bibit._"
        ),
        "en": (
            "📿 *{label}*\n"
            "*{jam} — Vow {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n"
            "_You will answer 3 questions related to this vow._\n\n"
            "✅ *Question 1 of 3*\n\n"
            "In the last 24 hours, were there any actions, words, or thoughts "
            "IN LINE with this vow?\n\n"
            "_Even an intention is already a seed._"
        ),
    },
    "sumpah_refleksi_negatif": {
        "id": (
            "📿 *Sumpah {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n\n"
            "⚠️ *Pertanyaan 2 dari 3*\n\n"
            "Adakah perbuatan, perkataan, atau pikiran yang TIDAK SESUAI dengan sumpah ini "
            "dalam 24 jam terakhir?\n\n"
            "_Jawab dengan jujur — ini bukan untuk dihakimi, tapi untuk disadari._"
        ),
        "en": (
            "📿 *Vow {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n\n"
            "⚠️ *Question 2 of 3*\n\n"
            "Were there any actions, words, or thoughts OUT OF LINE with this vow "
            "in the last 24 hours?\n\n"
            "_Answer honestly — this is not for judgment, but for awareness._"
        ),
    },
    "sumpah_refleksi_rencana": {
        "id": (
            "⚠️ *Catatan negatif Anda:*\n"
            "{negatif}\n\n"
            "─────────────────────\n\n"
            "🌱 *Pertanyaan 3 dari 3*\n\n"
            "Untuk menyeimbangkan catatan di atas, apa rencana konkret yang "
            "akan Anda lakukan dalam 24 jam ke depan?\n\n"
            "_Satu tindakan kecil pun sudah cukup._"
        ),
        "en": (
            "⚠️ *Your negative note:*\n"
            "{negatif}\n\n"
            "─────────────────────\n\n"
            "🌱 *Question 3 of 3*\n\n"
            "To balance the note above, what concrete plan will "
            "you carry out in the next 24 hours?\n\n"
            "_Even one small action is enough._"
        ),
    },
    # Neg-first order variants  (neg → plan → pos)
    "sumpah_refleksi_negatif_q1": {
        "id": (
            "📿 *Sumpah {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n"
            "_Anda akan menjawab 3 pertanyaan terkait sumpah ini._\n\n"
            "⚠️ *Pertanyaan 1 dari 3*\n\n"
            "Adakah perbuatan, perkataan, atau pikiran yang TIDAK SESUAI dengan sumpah ini "
            "dalam 24 jam terakhir?\n\n"
            "_Jawab dengan jujur — ini bukan untuk dihakimi, tapi untuk disadari._"
        ),
        "en": (
            "📿 *Vow {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n"
            "_You will answer 3 questions related to this vow._\n\n"
            "⚠️ *Question 1 of 3*\n\n"
            "Were there any actions, words, or thoughts OUT OF LINE with this vow "
            "in the last 24 hours?\n\n"
            "_Answer honestly — this is not for judgment, but for awareness._"
        ),
    },
    "sumpah_refleksi_rencana_q2": {
        "id": (
            "⚠️ *Catatan negatif Anda:*\n"
            "{negatif}\n\n"
            "─────────────────────\n\n"
            "🌱 *Pertanyaan 2 dari 3*\n\n"
            "Untuk menyeimbangkan catatan di atas, apa rencana konkret yang "
            "akan Anda lakukan dalam 24 jam ke depan?\n\n"
            "_Satu tindakan kecil pun sudah cukup._"
        ),
        "en": (
            "⚠️ *Your negative note:*\n"
            "{negatif}\n\n"
            "─────────────────────\n\n"
            "🌱 *Question 2 of 3*\n\n"
            "To balance the note above, what concrete plan will "
            "you carry out in the next 24 hours?\n\n"
            "_Even one small action is enough._"
        ),
    },
    "sumpah_refleksi_positif_q3": {
        "id": (
            "📿 *Sumpah {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n\n"
            "✅ *Pertanyaan 3 dari 3*\n\n"
            "Selama 24 jam terakhir, adakah perbuatan, perkataan, atau pikiran yang "
            "SESUAI dengan sumpah ini?\n\n"
            "_Bahkan niat pun sudah menjadi bibit._"
        ),
        "en": (
            "📿 *Vow {nums_str}*\n\n"
            "{vow_block}\n\n"
            "─────────────────────\n\n"
            "✅ *Question 3 of 3*\n\n"
            "In the last 24 hours, were there any actions, words, or thoughts "
            "IN LINE with this vow?\n\n"
            "_Even an intention is already a seed._"
        ),
    },

    "sumpah_refleksi_konfirmasi": {
        "id": (
            "✨ *Catatan Sumpah {nums_str} tersimpan:*\n\n"
            "✅ *Sesuai:* {positif}\n\n"
            "⚠️ *Perlu diseimbangkan:* {negatif}\n\n"
            "🌱 *Rencana:* {rencana}\n\n"
            "Terima kasih! 🙏"
        ),
        "en": (
            "✨ *Vow {nums_str} notes saved:*\n\n"
            "✅ *In line:* {positif}\n\n"
            "⚠️ *To balance:* {negatif}\n\n"
            "🌱 *Plan:* {rencana}\n\n"
            "Thank you! 🙏"
        ),
    },
    "ganti_advanced_pilihan": {
        "id": (
            "🔄 *Ganti Posisi Rotasi*\n\n"
            "Pilih cara mengganti posisi Anda dalam siklus sumpah:"
        ),
        "en": (
            "🔄 *Change Rotation Position*\n\n"
            "Choose how you want to change your position in the vow cycle:"
        ),
    },
    "ganti_dari_sumpah_label": {"id": "📿 Dari nomor sumpah", "en": "📿 From vow number"},
    "ganti_dari_hari_label":   {"id": "📅 Dari nomor hari",   "en": "📅 From day number"},
    "ganti_dari_hari_prompt": {
        "id": (
            "📅 *Masukkan nomor hari dalam siklus:*\n\n"
            "Advanced: 1–147\n"
            "Super Advanced: 1–44\n\n"
            "_Contoh: ketik *10* untuk memulai dari hari ke-10._"
        ),
        "en": (
            "📅 *Enter the day number in the cycle:*\n\n"
            "Advanced: 1–147\n"
            "Super Advanced: 1–44\n\n"
            "_Example: type *10* to start from day 10._"
        ),
    },
    "ganti_hari_invalid": {
        "id": "⚠️ Masukkan angka antara 1 dan {max_day}. Coba lagi:",
        "en": "⚠️ Please enter a number between 1 and {max_day}. Try again:",
    },
    "ganti_hari_konfirmasi": {
        "id": (
            "✅ *Posisi rotasi diperbarui!*\n\n"
            "Hari ke-*{day_number}* dalam siklus.\n\n"
            "*Jadwal sumpah hari ini:*\n{jadwal}"
        ),
        "en": (
            "✅ *Rotation position updated!*\n\n"
            "Day *{day_number}* in the cycle.\n\n"
            "*Today's vow schedule:*\n{jadwal}"
        ),
    },
    "kebajikan_belum_ada_ganti": {
        "id": "Gunakan /{cmd_ganti} untuk memilih kebajikan fokus.",
        "en": "Use /{cmd_ganti} to choose a virtue focus.",
    },
    "sumpah_semua_selesai": {
        "id": (
            "🎉 *Semua sumpah hari ini sudah direfleksikan!*\n\n"
            "Apakah Anda ingin menulis ulang salah satu sumpah?"
        ),
        "en": (
            "🎉 *All of today's vows have been reflected on!*\n\n"
            "Would you like to rewrite any vow?"
        ),
    },
    "sumpah_tulis_ulang_ya":   {"id": "✏️ Ya, tulis ulang",  "en": "✏️ Yes, rewrite one"},
    "sumpah_tulis_ulang_tidak":{"id": "✅ Tidak, sudah cukup","en": "✅ No, I'm done"},
    "sumpah_tulis_ulang_pilih":{
        "id": "📿 *Pilih sumpah yang ingin ditulis ulang:*",
        "en": "📿 *Choose the vow you want to rewrite:*",
    },
    "sumpah_sudah_semua_tidak":{
        "id": "✅ Baik! Refleksi hari ini selesai. Kerja bagus! 🙏",
        "en": "✅ Done! Today's reflection is complete. Well done! 🙏",
    },
    "sumpah_berikutnya": {
        "id": "📿 *Sumpah berikutnya yang belum direfleksikan:*",
        "en": "📿 *Next vow not yet reflected on:*",
    },
    "sumpah_mulai_refleksi_label": {
        "id": "✍️ Tulis refleksi sumpah ini",
        "en": "✍️ Reflect on this vow",
    },
    "sumpah_renungan": {
        "id": "_Renungkan sumpah ini dalam setiap tindakan, perkataan, dan pikiran Anda hari ini._ 🙏",
        "en": "_Contemplate this vow in every action, word, and thought today._ 🙏",
    },

    # ─── LEVEL UPGRADE ───────────────────────────────────────────────────────

    "ubah_level_judul": {
        "id": "📊 *Ubah Level Praktik*\n\nLevel Anda saat ini: *{level}*\n\nPilih level baru. Advanced dan Super Advanced memerlukan kata sandi.",
        "en": "📊 *Change Practice Level*\n\nYour current level: *{level}*\n\nChoose a new level. Advanced and Super Advanced require a password.",
    },
    "password_prompt": {
        "id": "🔐 *{label}*\n\nMasukkan kata sandi untuk mengakses level ini:",
        "en": "🔐 *{label}*\n\nEnter the password to access this level:",
    },
    "password_salah": {
        "id": "❌ Kata sandi salah. Gunakan /{cmd_level} untuk mencoba lagi.",
        "en": "❌ Wrong password. Use /{cmd_level} to try again.",
    },
    "password_belum_dikonfigurasi": {
        "id": "⚠️ Kata sandi belum dikonfigurasi. Hubungi administrator.",
        "en": "⚠️ Password not configured. Please contact the administrator.",
    },
    "vow_awal_prompt_advanced": {
        "id": (
            "🪷 *Kata sandi diterima!*\n\n"
            "Dari sumpah nomor berapa Anda ingin memulai?\n\n"
            "_Ketik angka 1–147. Contoh: ketik *32* untuk memulai dari hari ke-10._\n\n"
            "Atau ketik *1* untuk memulai dari awal."
        ),
        "en": (
            "🪷 *Password accepted!*\n\n"
            "Which vow number would you like to start from?\n\n"
            "_Type a number 1–147. Example: type *32* to start from day 10._\n\n"
            "Or type *1* to start from the beginning."
        ),
    },
    "vow_awal_prompt_super": {
        "id": (
            "💎 *Kata sandi diterima!*\n\n"
            "Dari sumpah nomor berapa Anda ingin memulai?\n\n"
            "_Ketik angka 1–265. Contoh: ketik *11* untuk memulai dari hari ke-11._\n\n"
            "Atau ketik *1* untuk memulai dari awal."
        ),
        "en": (
            "💎 *Password accepted!*\n\n"
            "Which vow number would you like to start from?\n\n"
            "_Type a number 1–265. Example: type *11* to start from day 11._\n\n"
            "Or type *1* to start from the beginning."
        ),
    },
    "vow_awal_invalid": {
        "id": "⚠️ Masukkan angka antara 1 dan {max_vow}. Coba lagi:",
        "en": "⚠️ Please enter a number between 1 and {max_vow}. Try again:",
    },
    "vow_awal_konfirmasi": {
        "id": (
            "✅ *Konfirmasi Mulai Sumpah*\n\n"
            "Level: *{label}*\n"
            "Mulai dari sumpah: *#{vow_num}* (Hari ke-{day_number})\n\n"
            "─────────────────────\n"
            "*Jadwal sumpah hari ini:*\n"
            "{jadwal}\n"
            "─────────────────────\n\n"
            "Anda siap memulai. Ketuk tombol di bawah untuk mengatur jam notifikasi jika diperlukan."
        ),
        "en": (
            "✅ *Vow Start Confirmation*\n\n"
            "Level: *{label}*\n"
            "Starting from vow: *#{vow_num}* (Day {day_number})\n\n"
            "─────────────────────\n"
            "*Today's vow schedule:*\n"
            "{jadwal}\n"
            "─────────────────────\n\n"
            "You're all set. Tap below to adjust notification times if needed."
        ),
    },
    "vow_konfirmasi_jam":     {"id": "⏰ Atur jam notifikasi", "en": "⏰ Set notification times"},
    "vow_jam_default_label":  {"id": "✅ Gunakan default",     "en": "✅ Use default"},
    "vow_jam_invalid": {
        "id": "⚠️ Format tidak valid. Ketik tepat 6 jam dalam format HH:MM, dipisah spasi:",
        "en": "⚠️ Invalid format. Type exactly 6 times in HH:MM format, separated by spaces:",
    },
    "vow_jam_dikonfirmasi": {
        "id": "✅ Jam notifikasi disimpan:\n{jadwal_jam}",
        "en": "✅ Notification times saved:\n{jadwal_jam}",
    },
    "upgrade_berhasil_advanced": {
        "id": (
            "✅ Level berhasil diubah ke *{label}*!\n\n"
            "🪷 *Sumpah Bodhisattva* akan dikirim 6 kali sehari.\n"
            "Rotasi 147 hari — setiap sumpah muncul sekali per siklus.\n\n"
            "_Semoga praktik Anda semakin mendalam._ 🙏"
        ),
        "en": (
            "✅ Level successfully changed to *{label}*!\n\n"
            "🪷 *Bodhisattva Vows* will be sent 6 times a day.\n"
            "147-day rotation — each vow appears once per cycle.\n\n"
            "_May your practice deepen._ 🙏"
        ),
    },
    "upgrade_berhasil_super": {
        "id": (
            "✅ Level berhasil diubah ke *{label}*!\n\n"
            "💎 *Sumpah Tantra* akan dikirim 6 kali sehari.\n"
            "Rotasi 44 hari — 265 sumpah dalam satu siklus.\n\n"
            "_Semoga praktik Anda semakin mendalam._ 🙏"
        ),
        "en": (
            "✅ Level successfully changed to *{label}*!\n\n"
            "💎 *Tantric Vows* will be sent 6 times a day.\n"
            "44-day rotation — 265 vows in one cycle.\n\n"
            "_May your practice deepen._ 🙏"
        ),
    },
    "upgrade_berhasil_standar": {
        "id": "✅ Level berhasil diubah ke *{label}*!\n\n_Semoga praktik Anda semakin mendalam._ 🙏",
        "en": "✅ Level successfully changed to *{label}*!\n\n_May your practice deepen._ 🙏",
    },

    # ─── KEBAJIKAN DISPLAY ───────────────────────────────────────────────────

    "kebajikan_fokus_judul": {
        "id": "🎯 *Fokus Kebajikan Anda*\n\n_Tujuan: {tujuan}_\n",
        "en": "🎯 *Your Virtue Focus*\n\n_Goal: {tujuan}_\n",
    },
    "kebajikan_utama_label":     {"id": "Utama",    "en": "Main"},
    "kebajikan_pendukung_label": {"id": "Pendukung","en": "Supporting"},
    "kebajikan_belum_ada": {
        "id": "Belum ada kebajikan fokus. Gunakan /{cmd_ganti}.",
        "en": "No virtue focus yet. Use /{cmd_ganti}.",
    },

    # ─── GANTI KEBAJIKAN ─────────────────────────────────────────────────────

    "ganti_judul": {
        "id": "🔄 *Ganti Fokus Kebajikan*\n\nPilih {jumlah} kebajikan baru:",
        "en": "🔄 *Change Virtue Focus*\n\nChoose {jumlah} new virtue(s):",
    },
    "selesai_pilih_label": {"id": "✅ Selesai", "en": "✅ Done"},
    "pilih_minimal":       {"id": "Pilih minimal 1!", "en": "Choose at least 1!"},
    "sudah_penuh_alert": {
        "id": "Sudah memilih {jumlah} kebajikan. Batalkan salah satu dulu.",
        "en": "You've already chosen {jumlah} virtues. Cancel one first.",
    },

    # ─── LAPORAN & HELP ──────────────────────────────────────────────────────

    "laporan_pilih_mode": {
        "id": "📋 *Pilih tampilan laporan:*",
        "en": "📋 *Choose report view:*",
    },
    "laporan_mode_ringkas_label": {
        "id": "✅ Positif & Rencana saja",
        "en": "✅ Positives & Plans only",
    },
    "laporan_mode_lengkap_label": {
        "id": "📄 Semua entri lengkap",
        "en": "📄 All entries in full",
    },
    "laporan_kosong": {
        "id": "📋 Belum ada catatan hari ini.\nGunakan /{cmd_refleksi} untuk mulai.",
        "en": "📋 No notes for today yet.\nUse /{cmd_refleksi} to start.",
    },
    "help": {
        "id": (
            "📖 *Daftar Perintah:*\n\n"
            "/start — Mulai ulang\n"
            "/help — Tampilkan menu ini\n"
            "/kebajikan — Fokus kebajikan hari ini\n"
            "/refleksi — Isi refleksi sekarang\n"
            "/ganti — Ganti fokus kebajikan\n"
            "/tambahan — Tambah perbuatan baik\n"
            "/laporan — Ringkasan hari ini\n"
            "/level — Ubah level praktik\n"
            "/language — Ganti bahasa\n"
            "/setjam — Atur jam notifikasi"
        ),
        "en": (
            "📖 *Command List:*\n\n"
            "/start — Restart\n"
            "/help — Show this menu\n"
            "/virtue — Today's virtue focus\n"
            "/reflect — Fill in reflection now\n"
            "/change — Change virtue focus\n"
            "/add — Add good deeds\n"
            "/report — Today's summary\n"
            "/level — Change practice level\n"
            "/language — Change language\n"
            "/settime — Set notification times"
        ),
    },

    # ─── SETJAM / SETTIME ────────────────────────────────────────────────────

    "setjam_slot_prompt": {
        "id": (
            "⏰ *Atur Jam Notifikasi — Slot {n} dari 7*\n\n"
            "*{nama_slot}*\n"
            "Jam saat ini: `{jam_sekarang}`\n\n"
            "Ketik jam baru dalam format *HH:MM*, atau ketuk *Lewati* untuk mempertahankan jam saat ini."
        ),
        "en": (
            "⏰ *Set Notification Times — Slot {n} of 7*\n\n"
            "*{nama_slot}*\n"
            "Current time: `{jam_sekarang}`\n\n"
            "Type the new time in *HH:MM* format, or tap *Skip* to keep the current time."
        ),
    },
    "setjam_lewati_label": {"id": "⏭ Lewati", "en": "⏭ Skip"},
    "setjam_format_salah": {
        "id": "Format tidak valid. Gunakan HH:MM, contoh: 07:30",
        "en": "Invalid format. Use HH:MM, example: 07:30",
    },
    "setjam_selesai": {
        "id": "✅ *Semua jam notifikasi tersimpan!*\n\n{ringkasan}\n\n_Perubahan berlaku mulai besok._ 🙏",
        "en": "✅ *All notification times saved!*\n\n{ringkasan}\n\n_Changes take effect from tomorrow._ 🙏",
    },
    "setjam_slot_names": {
        "id": ["Fokus pagi (06:00)", "Refleksi pagi (07:00)", "Refleksi siang (12:00)",
               "Refleksi sore (18:00)", "Tambahan malam (20:00)", "Ringkasan (21:00)", "Arsip pribadi (21:30)"],
        "en": ["Morning focus (06:00)", "Morning reflection (07:00)", "Midday reflection (12:00)",
               "Afternoon reflection (18:00)", "Evening addition (20:00)", "Summary (21:00)", "Personal archive (21:30)"],
    },
    "setjam_db_keys": {
        "id": ["jam_fokus", "jam_pagi", "jam_siang", "jam_sore", "jam_malam", "jam_ringkasan", "jam_cofmed"],
        "en": ["jam_fokus", "jam_pagi", "jam_siang", "jam_sore", "jam_malam", "jam_ringkasan", "jam_cofmed"],
    },
    "setjam_defaults": {
        "id": ["06:00", "07:00", "12:00", "18:00", "20:00", "21:00", "21:30"],
        "en": ["06:00", "07:00", "12:00", "18:00", "20:00", "21:00", "21:30"],
    },

    # ─── LANGUAGE COMMAND ────────────────────────────────────────────────────

    "language_prompt": {
        "id": "🌏 *Ganti Bahasa / Change Language*\n\nPilih bahasa Anda / Choose your language:",
        "en": "🌏 *Ganti Bahasa / Change Language*\n\nPilih bahasa Anda / Choose your language:",
    },
    "language_changed": {
        "id": "✅ Bahasa berhasil diubah ke *Bahasa Indonesia*.",
        "en": "✅ Language successfully changed to *English*.",
    },

    # ─── VOW JAM PROMPTS ─────────────────────────────────────────────────────

    "vow_jam_prompt": {
        "id": (
            "⏰ *Atur Jam Notifikasi Sumpah — Slot {n} dari 6*\n\n"
            "*{nama_slot}*\n"
            "Jam saat ini: `{jam_sekarang}`\n\n"
            "Ketik jam baru dalam format *HH:MM*, atau ketuk *Lewati*."
        ),
        "en": (
            "⏰ *Set Vow Notification Times — Slot {n} of 6*\n\n"
            "*{nama_slot}*\n"
            "Current time: `{jam_sekarang}`\n\n"
            "Type the new time in *HH:MM* format, or tap *Skip*."
        ),
    },
    "vow_jam_slot_names": {
        "id": ["Slot 1 (07:00)", "Slot 2 (09:30)", "Slot 3 (12:00)", "Slot 4 (14:30)", "Slot 5 (17:00)", "Slot 6 (19:30)"],
        "en": ["Slot 1 (07:00)", "Slot 2 (09:30)", "Slot 3 (12:00)", "Slot 4 (14:30)", "Slot 5 (17:00)", "Slot 6 (19:30)"],
    },
    "vow_jam_selesai": {
        "id": "✅ *Jam sumpah tersimpan!*\n\n{ringkasan}\n\n_Perubahan berlaku mulai besok._ 🙏",
        "en": "✅ *Vow times saved!*\n\n{ringkasan}\n\n_Changes take effect from tomorrow._ 🙏",
    },
    "setvowtime_only_advanced": {
        "id": "⚠️ Perintah ini hanya untuk level Advanced dan Super Advanced.",
        "en": "⚠️ This command is only available for Advanced and Super Advanced levels.",
    },
}

# ─── COMMAND NAMES PER LANGUAGE ──────────────────────────────────────────────

COMMANDS = {
    "id": {
        "start":       "start",
        "help":        "help",
        "kebajikan":   "kebajikan",
        "refleksi":    "refleksi",
        "ganti":       "ganti",
        "tambahan":    "tambahan",
        "laporan":     "laporan",
        "level":       "level",
        "language":    "language",
        "setjam":      "setjam",
    },
    "en": {
        "start":       "start",
        "help":        "help",
        "kebajikan":   "virtue",
        "refleksi":    "reflect",
        "ganti":       "change",
        "tambahan":    "add",
        "laporan":     "report",
        "level":       "level",
        "language":    "language",
        "setjam":      "settime",
    },
}

TIMEZONE_MAP = {
    "WIB":  "Asia/Jakarta",
    "WITA": "Asia/Makassar",
    "WIT":  "Asia/Jayapura",
    "SGT":  "Asia/Singapore",
    "MYT":  "Asia/Kuala_Lumpur",
    "IST":  "Asia/Kolkata",
    "AEST": "Australia/Sydney",
    "GMT":  "UTC",
    "CET":  "Europe/Paris",
    "EST":  "America/New_York",
    "PST":  "America/Los_Angeles",
}


def T(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in ("id", "en") else "id"
    entry = STRINGS.get(key, {})
    text = entry.get(lang, entry.get("id", f"[{key}]"))
    # Inject localized command names
    cmds = COMMANDS.get(lang, COMMANDS["id"])
    kwargs.setdefault("cmd_kebajikan", cmds["kebajikan"])
    kwargs.setdefault("cmd_refleksi",  cmds["refleksi"])
    kwargs.setdefault("cmd_ganti",     cmds["ganti"])
    kwargs.setdefault("cmd_tambahan",  cmds["tambahan"])
    kwargs.setdefault("cmd_laporan",   cmds["laporan"])
    kwargs.setdefault("cmd_level",     cmds["level"])
    kwargs.setdefault("cmd_help",      cmds["help"])
    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def cmd(key: str, lang: str) -> str:
    """Return the command name for a given key and language."""
    return COMMANDS.get(lang, COMMANDS["id"]).get(key, key)
