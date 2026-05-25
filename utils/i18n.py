# utils/i18n.py
# All bot messages in English and Indonesian.
# Usage: T("key", lang) — returns the string in the user's language.

STRINGS = {

    # ─── ONBOARDING ──────────────────────────────────────────────────────────

    "pilih_bahasa": {
        "id": (
            "🌏 *Selamat datang di Bot Kebajikan Harian!*\n\n"
            "Silakan pilih bahasa yang ingin Anda gunakan:"
        ),
        "en": (
            "🌏 *Welcome to the Daily Virtue Bot!*\n\n"
            "Please choose your preferred language:"
        ),
    },
    "bahasa_dipilih": {
        "id": "✅ Bahasa Indonesia dipilih. Mari mulai!",
        "en": "✅ English selected. Let's begin!",
    },
    "sambutan": {
        "id": (
            "🙏 *Selamat datang di Bot Kebajikan Harian*\n\n"
            "Bot ini memandu Anda memantau dan mengembangkan kebajikan setiap hari "
            "berdasarkan *10 Bibit Baik Utama*.\n\n"
            "Pertama, pilih level praktik Anda:"
        ),
        "en": (
            "🙏 *Welcome to the Daily Virtue Bot*\n\n"
            "This bot guides you in monitoring and developing virtues every day "
            "based on the *10 Main Virtue Seeds*.\n\n"
            "First, please choose your practice level:"
        ),
    },
    "sambutan_kembali": {
        "id": (
            "🙏 Selamat datang kembali, *{name}*!\n\n"
            "Gunakan /kebajikan untuk melihat fokus hari ini, "
            "/refleksi untuk mengisi refleksi, atau /bantuan untuk daftar perintah."
        ),
        "en": (
            "🙏 Welcome back, *{name}*!\n\n"
            "Use /kebajikan to see today's focus, "
            "/refleksi to fill in your reflection, or /bantuan for the command list."
        ),
    },

    # ─── LEVEL SELECTION ─────────────────────────────────────────────────────

    "pilih_level": {
        "id": "📊 *Pilih Level Praktik Anda:*",
        "en": "📊 *Choose Your Practice Level:*",
    },
    "level_pemula_label":        {"id": "🌱 Pemula",                          "en": "🌱 Beginner"},
    "level_menengah_label":      {"id": "🌿 Praktisi Menengah",               "en": "🌿 Intermediate Practitioner"},
    "level_mahir_label":         {"id": "🌳 Praktisi Mahir",                  "en": "🌳 Advanced Practitioner"},
    "level_advanced_label":      {"id": "🪷 Advanced (Sumpah Bodhisattva)",   "en": "🪷 Advanced (Bodhisattva Vows)"},
    "level_super_label":         {"id": "💎 Super Advanced (Sumpah Tantra)",  "en": "💎 Super Advanced (Tantric Vows)"},
    "level_dipilih": {
        "id": "👍 Level Anda: *{label}*\n_{desc}_",
        "en": "👍 Your level: *{label}*\n_{desc}_",
    },

    # ─── SMART GOAL ──────────────────────────────────────────────────────────

    "tujuan_smart_prompt": {
        "id": (
            "🎯 *Langkah 1 — Tujuan SMART Anda*\n\n"
            "Tuliskan satu tujuan yang ingin Anda capai melalui praktik kebajikan ini.\n\n"
            "Bot akan mengevaluasi apakah tujuan Anda memenuhi kriteria *SMART:*\n"
            "• *S*pesifik — jelas dan konkret\n"
            "• *M*easurable — bisa diukur\n"
            "• *A*chievable — bisa dicapai\n"
            "• *R*elevant — bermakna bagi Anda\n"
            "• *T*ime-bound — ada batas waktunya\n\n"
            "_Contoh: Dalam 30 hari ke depan, saya ingin lebih sabar berbicara "
            "dengan anak-anak saya._\n\n"
            "✏️ *Tuliskan tujuan Anda:*"
        ),
        "en": (
            "🎯 *Step 1 — Your SMART Goal*\n\n"
            "Write one goal you want to achieve through this virtue practice.\n\n"
            "The bot will evaluate whether your goal meets the *SMART* criteria:\n"
            "• *S*pecific — clear and concrete\n"
            "• *M*easurable — can be measured\n"
            "• *A*chievable — can be accomplished\n"
            "• *R*elevant — meaningful to you\n"
            "• *T*ime-bound — has a deadline\n\n"
            "_Example: In the next 30 days, I want to speak more patiently "
            "with my children._\n\n"
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
    "rekomendasi_level_pemula": {
        "id": "Sebagai Pemula, bot merekomendasikan *1 kebajikan utama* untuk Anda fokusi:",
        "en": "As a Beginner, the bot recommends *1 main virtue* for you to focus on:",
    },
    "rekomendasi_level_menengah": {
        "id": "Sebagai Praktisi Menengah, bot merekomendasikan *3 kebajikan* (1 utama + 2 pendukung):",
        "en": "As an Intermediate Practitioner, the bot recommends *3 virtues* (1 main + 2 supporting):",
    },
    "rekomendasi_level_mahir": {
        "id": "Sebagai Praktisi Mahir, ini *titik masuk* yang direkomendasikan:",
        "en": "As an Advanced Practitioner, here is the recommended *entry point*:",
    },
    "setuju_label":       {"id": "✅ Mulai Sekarang!", "en": "✅ Start Now!"},
    "pilih_sendiri_label":{"id": "🔄 Pilih sendiri",  "en": "🔄 Choose myself"},

    # ─── ONBOARDING COMPLETE ─────────────────────────────────────────────────

    "onboarding_selesai": {
        "id": (
            "🎉 *Selamat, {name}!*\n\n"
            "Anda telah resmi memulai perjalanan kebajikan Anda.\n\n"
            "*Fokus kebajikan Anda:*\n{daftar}\n\n"
            "*Jadwal harian (WIB):*\n"
            "06:00 — Pilihan fokus hari ini\n"
            "07:00 — Refleksi pagi\n"
            "12:00 — Refleksi siang\n"
            "18:00 — Refleksi sore\n"
            "20:00 — Tambahan perbuatan baik\n"
            "21:00 — Ringkasan positif\n"
            "21:30 — Arsip pribadi\n\n"
            "Gunakan /setjam untuk melakukan pengaturan waktu notifikasi. 🙏"
        ),
        "en": (
            "🎉 *Congratulations, {name}!*\n\n"
            "You have officially started your virtue journey.\n\n"
            "*Your virtue focus:*\n{daftar}\n\n"
            "*Daily schedule (WIB):*\n"
            "06:00 — Today's focus check\n"
            "07:00 — Morning reflection\n"
            "12:00 — Midday reflection\n"
            "18:00 — Afternoon reflection\n"
            "20:00 — Additional good deeds\n"
            "21:00 — Positive summary\n"
            "21:30 — Personal archive\n\n"
            "Use /setjam to set your notification times. 🙏"
        ),
    },

    # ─── 06:00 FOCUS CHECK ───────────────────────────────────────────────────

    "pagi_ganti_tanya": {
        "id": "🌅 *Selamat pagi!*\n\nFokus kebajikan Anda saat ini:\n\n{daftar}\n\nApakah ingin *mengganti* fokus kebajikan hari ini?",
        "en": "🌅 *Good morning!*\n\nYour current virtue focus:\n\n{daftar}\n\nWould you like to *change* your virtue focus for today?",
    },
    "pagi_ganti_ya_label":    {"id": "🔄 Ya, ganti",   "en": "🔄 Yes, change"},
    "pagi_ganti_tidak_label": {"id": "✅ Lanjutkan",    "en": "✅ Continue"},
    "pagi_lanjut_konfirmasi": {
        "id": "✅ *Fokus kebajikan hari ini tetap:*\n\n{daftar}\n\nRefleksi pagi akan dimulai sesuai jadwal Anda. 🙏",
        "en": "✅ *Today's virtue focus remains:*\n\n{daftar}\n\nMorning reflection will begin on schedule. 🙏",
    },
    "pagi_ganti_instruksi": {
        "id": "🔄 Gunakan /ganti untuk memilih kebajikan fokus baru hari ini.",
        "en": "🔄 Use /ganti to choose a new virtue focus for today.",
    },

    # ─── REFLEKSI ────────────────────────────────────────────────────────────

    "sesi_pagi_label":  {"id": "🌅 Pagi (07:00)",   "en": "🌅 Morning (07:00)"},
    "sesi_siang_label": {"id": "☀️ Siang (12:00)",  "en": "☀️ Midday (12:00)"},
    "sesi_sore_label":  {"id": "🌇 Sore (18:00)",   "en": "🌇 Afternoon (18:00)"},

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
            "{sesi}\n{emoji} *{nama_en}*\n\n"
            "🔍 *Question 1 of 3*\n\n"
            "Over the *last 24 hours*, expanding the meaning of this virtue:\n\n"
            "_{pertanyaan}_\n\n"
            "✅ *What did you do or think that is IN LINE with this virtue?*\n\n"
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
            "{sesi}\n{emoji} *{nama_en}*\n\n"
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
            "{sesi}\n{emoji} *{nama_en}*\n\n"
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
            "Thank you for being honest and thorough! These notes are saved. 🙏"
        ),
    },

    # ─── 20:00 TAMBAHAN ──────────────────────────────────────────────────────

    "tambahan_malam_prompt": {
        "id": (
            "🌙 *Laporan Malam*\n\n"
            "Sebelum hari berakhir — adakah *perbuatan baik lainnya* yang sudah Anda lakukan "
            "hari ini yang belum tercatat?\n\n"
            "Ceritakan di sini, seberapapun kecilnya. 🙏\n\n"
            "_Ketuk 'Tidak ada' jika sudah lengkap._"
        ),
        "en": (
            "🌙 *Evening Report*\n\n"
            "Before the day ends — are there any *other good deeds* you did today "
            "that haven't been recorded yet?\n\n"
            "Share them here, no matter how small. 🙏\n\n"
            "_Tap 'None' if you're all done._"
        ),
    },
    "tambahan_tidak_ada_label": {"id": "✅ Tidak ada tambahan", "en": "✅ None"},
    "tambahan_tersimpan": {
        "id": "✨ Catatan tersimpan. Terima kasih! 🙏\nKetuk /tambahan lagi jika ingin menambah.",
        "en": "✨ Notes saved. Thank you! 🙏\nTap /tambahan again if you want to add more.",
    },
    "tambahan_selesai": {
        "id": "✅ Baik! Arsip akan dikirim pukul 21:30. 🙏",
        "en": "✅ Great! The archive will be sent at 21:30. 🙏",
    },

    # ─── 21:00 RINGKASAN POSITIF ─────────────────────────────────────────────

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

    # ─── 21:30 ARSIP PRIBADI ─────────────────────────────────────────────────

    "arsip_judul": {
        "id": "📁 *Arsip Pribadi Harian{sapaan}*\n_{tanggal}_\n\n═════════════════════\n",
        "en": "📁 *Daily Personal Archive{sapaan}*\n_{tanggal}_\n\n═════════════════════\n",
    },
    "arsip_kosong": {
        "id": "📁 *Arsip Pribadi*\n\nBelum ada entri untuk hari ini.\nIstirahatlah dengan tenang. 🙏",
        "en": "📁 *Personal Archive*\n\nNo entries for today.\nRest well. 🙏",
    },
    "arsip_positif_label":  {"id": "✅ *Sesuai kebajikan:*\n",      "en": "✅ *In line with virtue:*\n"},
    "arsip_negatif_label":  {"id": "⚠️ *Perlu diseimbangkan:*\n",  "en": "⚠️ *To balance:*\n"},
    "arsip_rencana_label":  {"id": "🌱 *Rencana 24 jam ke depan:*\n","en": "🌱 *Plan for next 24 hours:*\n"},
    "arsip_tambahan_label": {"id": "🌙 *Tambahan Perbuatan Baik (20:00)*\n", "en": "🌙 *Additional Good Deeds (20:00)*\n"},
    "arsip_penutup": {
        "id": "_Arsip ini adalah catatan integritas Anda. Setiap bibit yang dicatat dengan jujur akan tumbuh. Istirahatlah dengan tenang._ 🙏",
        "en": "_This archive is a record of your integrity. Every seed honestly noted will grow. Rest well._ 🙏",
    },

    # ─── PENGINGAT ───────────────────────────────────────────────────────────

    "pengingat": {
        "id": "⏰ *Pengingat*\n\nRefleksi {sesi} untuk {emoji} *{nama}* Anda belum terisi.\nKetuk /refleksi untuk mulai mengisi sekarang. 🙏",
        "en": "⏰ *Reminder*\n\nYour {sesi} reflection for {emoji} *{nama}* hasn't been filled in yet.\nTap /refleksi to fill it in now. 🙏",
    },

    # ─── SUMPAH (ADVANCED/SUPER ADVANCED) ────────────────────────────────────

    "sumpah_label_advanced":      {"id": "Sumpah Bodhisattva 🪷", "en": "Bodhisattva Vow 🪷"},
    "sumpah_label_super":         {"id": "Sumpah Tantra 💎",       "en": "Tantric Vow 💎"},
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
        "id": "❌ Kata sandi salah. Gunakan /level untuk mencoba lagi.",
        "en": "❌ Wrong password. Use /level to try again.",
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
            "✅ *Konfirmasi:*\n\n"
            "Level: *{label}*\n"
            "Mulai dari sumpah: *#{vow_num}*\n"
            "(Hari ke-{day_number} dalam rotasi)\n\n"
            "Apakah sudah benar?"
        ),
        "en": (
            "✅ *Confirmation:*\n\n"
            "Level: *{label}*\n"
            "Starting from vow: *#{vow_num}*\n"
            "(Day {day_number} in the rotation)\n\n"
            "Is this correct?"
        ),
    },
    "vow_konfirmasi_ya":   {"id": "✅ Ya, mulai!", "en": "✅ Yes, start!"},
    "vow_konfirmasi_ubah": {"id": "✏️ Ubah",       "en": "✏️ Change"},
    "vow_ubah_prompt":     {"id": "Ketik ulang nomor sumpah awal:", "en": "Type the starting vow number again:"},
    "upgrade_berhasil_advanced": {
        "id": (
            "✅ Level berhasil diubah ke *{label}*!\n\n"
            "🪷 *Sumpah Bodhisattva* akan dikirim 6 kali sehari:\n"
            "07:00 · 09:30 · 12:00 · 14:30 · 17:00 · 19:30\n"
            "Rotasi 147 hari — setiap sumpah muncul sekali per siklus.\n\n"
            "_Semoga praktik Anda semakin mendalam._ 🙏"
        ),
        "en": (
            "✅ Level successfully changed to *{label}*!\n\n"
            "🪷 *Bodhisattva Vows* will be sent 6 times a day:\n"
            "07:00 · 09:30 · 12:00 · 14:30 · 17:00 · 19:30\n"
            "147-day rotation — each vow appears once per cycle.\n\n"
            "_May your practice deepen._ 🙏"
        ),
    },
    "upgrade_berhasil_super": {
        "id": (
            "✅ Level berhasil diubah ke *{label}*!\n\n"
            "💎 *Sumpah Tantra* akan dikirim 6 kali sehari:\n"
            "07:00 · 09:30 · 12:00 · 14:30 · 17:00 · 19:30\n"
            "Rotasi 44 hari — 265 sumpah dalam satu siklus.\n\n"
            "_Semoga praktik Anda semakin mendalam._ 🙏"
        ),
        "en": (
            "✅ Level successfully changed to *{label}*!\n\n"
            "💎 *Tantric Vows* will be sent 6 times a day:\n"
            "07:00 · 09:30 · 12:00 · 14:30 · 17:00 · 19:30\n"
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
    "kebajikan_utama_label":    {"id": "Utama",    "en": "Main"},
    "kebajikan_pendukung_label":{"id": "Pendukung","en": "Supporting"},
    "kebajikan_belum_ada": {
        "id": "Belum ada kebajikan fokus. Gunakan /ganti.",
        "en": "No virtue focus yet. Use /ganti.",
    },

    # ─── GANTI KEBAJIKAN ─────────────────────────────────────────────────────

    "ganti_judul": {
        "id": "🔄 *Ganti Fokus Kebajikan*\n\nPilih {jumlah} kebajikan baru:",
        "en": "🔄 *Change Virtue Focus*\n\nChoose {jumlah} new virtue(s):",
    },
    "selesai_pilih_label": {"id": "✅ Selesai", "en": "✅ Done"},
    "sudah_penuh_alert": {
        "id": "Sudah memilih {jumlah} kebajikan. Batalkan salah satu dulu.",
        "en": "You've already chosen {jumlah} virtues. Cancel one first.",
    },

    # ─── LAPORAN & BANTUAN ───────────────────────────────────────────────────

    "laporan_kosong": {
        "id": "📋 Belum ada catatan hari ini.\nGunakan /refleksi untuk mulai.",
        "en": "📋 No notes for today yet.\nUse /refleksi to start.",
    },
    "bantuan": {
        "id": (
            "📖 *Daftar Perintah:*\n\n"
            "/start — Mulai atau restart\n"
            "/kebajikan — Fokus kebajikan hari ini\n"
            "/refleksi — Isi refleksi sekarang\n"
            "/ganti — Ganti fokus kebajikan\n"
            "/tambahan — Tambah perbuatan baik\n"
            "/laporan — Ringkasan hari ini\n"
            "/level — Ubah level praktik\n"
            "/language — Ganti bahasa\n"
            "/setjam — Atur jam notifikasi\n"
            "/bantuan — Tampilkan menu ini"
        ),
        "en": (
            "📖 *Command List:*\n\n"
            "/start — Start or restart\n"
            "/kebajikan — Today's virtue focus\n"
            "/refleksi — Fill in reflection now\n"
            "/ganti — Change virtue focus\n"
            "/tambahan — Add good deeds\n"
            "/laporan — Today's summary\n"
            "/level — Change practice level\n"
            "/language — Change language\n"
            "/setjam — Set notification times\n"
            "/bantuan — Show this menu"
        ),
    },
    "setjam_bantuan": {
        "id": (
            "⏰ *Atur Jam Notifikasi*\n\n"
            "Kirim pesan dalam format berikut:\n\n"
            "`/setjam pagi 07:30`\n"
            "`/setjam siang 13:00`\n"
            "`/setjam sore 17:00`\n"
            "`/setjam malam 19:30`\n"
            "`/setjam cofmed 22:00`\n\n"
            "Semua waktu dalam WIB (UTC+7)."
        ),
        "en": (
            "⏰ *Set Notification Times*\n\n"
            "Send a message in the following format:\n\n"
            "`/setjam pagi 07:30`\n"
            "`/setjam siang 13:00`\n"
            "`/setjam sore 17:00`\n"
            "`/setjam malam 19:30`\n"
            "`/setjam cofmed 22:00`\n\n"
            "All times are in WIB (UTC+7)."
        ),
    },
    "setjam_berhasil": {
        "id": "✅ Jam {sesi} berhasil diubah ke *{jam}* WIB.",
        "en": "✅ {sesi} time successfully changed to *{jam}* WIB.",
    },
    "setjam_format_salah": {
        "id": "Format jam tidak valid. Gunakan HH:MM, contoh: 07:30",
        "en": "Invalid time format. Use HH:MM, example: 07:30",
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
}


def T(key: str, lang: str, **kwargs) -> str:
    """
    Translate a key to the user's language.
    lang: 'id' or 'en' (defaults to 'id' if unknown)
    kwargs: format variables substituted into the string
    """
    lang = lang if lang in ("id", "en") else "id"
    entry = STRINGS.get(key, {})
    text = entry.get(lang, entry.get("id", f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
