# utils/smart_evaluator.py
"""
Evaluasi SMART goal dan rekomendasi kebajikan menggunakan logika berbasis kata kunci.
Tidak memerlukan API eksternal — murni rule-based agar tetap ringan di Railway.
"""

from data.kebajikan import KEBAJIKAN

# ─── SMART EVALUATION ────────────────────────────────────────────────────────

INDIKATOR_SMART = {
    "S": {
        "label": "Spesifik",
        "kata": [
            # Indonesian
            "saya", "aku", "kita", "akan", "ingin", "mau", "berkomitmen", "hendak", "berniat",
            "dengan cara", "melalui", "kepada", "bersama",
            "di rumah", "di kantor", "di keluarga", "di tempat kerja",
            "anak", "istri", "suami", "orang tua", "rekan", "teman",
            # English
            "i will", "i want", "i am", "i plan", "i commit", "i intend",
            "with", "through", "to my", "for my", "at home", "at work",
            "my child", "my wife", "my husband", "my partner", "my family",
            "my colleague", "my friend",
        ],
        "petunjuk": "Coba sebutkan *siapa* yang terlibat atau *apa* yang ingin Anda ubah.",
    },
    "M": {
        "label": "Terukur",
        "kata": [
            # Indonesian
            "kali", "sehari", "seminggu", "menit", "jam", "persen", "%",
            "orang", "hari", "minggu", "bulan", "lebih", "setiap",
            "minimal", "setidaknya", "tidak", "selalu", "rutin",
            "lebih sering", "lebih baik", "lebih sabar", "lebih ramah",
            # English
            "times", "per day", "per week", "minutes", "hours", "percent",
            "daily", "weekly", "monthly", "more", "every", "at least",
            "always", "regularly", "more often", "better", "more patient",
        ],
        "petunjuk": "Tambahkan ukuran sederhana — misalnya frekuensi atau perubahan yang bisa dirasakan.",
    },
    "A": {
        "label": "Bisa Dicapai",
        "kata": [
            # Indonesian
            "mulai", "langkah", "satu", "kecil", "sedikit", "perlahan",
            "bertahap", "mencoba", "berlatih", "setiap hari", "rutin",
            "kebiasaan", "bisa", "mampu", "berusaha", "ingin",
            "komitmen", "tekad", "niat", "usaha", "coba",
            # English
            "start", "step", "one", "small", "little", "gradually",
            "try", "practice", "each day", "routine", "habit", "able",
            "capable", "effort", "commit", "intend", "attempt",
        ],
        "petunjuk": "Pastikan tujuan terasa bisa dilakukan — tidak perlu sempurna, cukup nyata.",
    },
    "R": {
        "label": "Relevan",
        "kata": [
            # Indonesian
            "supaya", "agar", "karena", "demi", "untuk", "sehingga",
            "membantu", "bermanfaat", "berdampak", "penting", "berarti",
            "nilai", "prinsip", "perubahan", "lebih baik",
            "keluarga", "orang lain", "diri", "hidup", "ingin",
            # English
            "so that", "because", "in order to", "to help", "for the sake",
            "important", "meaningful", "impact", "value", "principle",
            "change", "improve", "family", "others", "myself", "life",
        ],
        "petunjuk": "Tuliskan *mengapa* ini penting bagi Anda — satu kalimat sudah cukup.",
    },
    "T": {
        "label": "Batas Waktu",
        "kata": [
            # Indonesian
            "hari", "minggu", "bulan", "tahun", "30", "60", "90", "7",
            "dalam", "selama", "sampai", "hingga", "selesai", "ke depan",
            "januari", "februari", "maret", "april", "mei", "juni",
            "juli", "agustus", "september", "oktober", "november", "desember",
            "besok", "pekan", "semester", "triwulan",
            # English
            "days", "weeks", "months", "years", "within", "during", "until",
            "by", "before", "deadline", "tomorrow", "next week", "next month",
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
            "quarter", "semester",
        ],
        "petunjuk": "Tambahkan batas waktu — misalnya '30 hari' atau 'bulan ini'.",
    },
}


def evaluasi_smart(teks: str) -> dict:
    """
    Evaluasi teks goal terhadap 5 kriteria SMART.
    Lulus jika memenuhi minimal 3 dari 5 kriteria (lebih lenient).
    """
    teks_lower = teks.lower()
    detail = {}

    for kode, info in INDIKATOR_SMART.items():
        cocok = any(kata in teks_lower for kata in info["kata"])
        detail[kode] = cocok

    skor = sum(1 for v in detail.values() if v)
    lulus = True  # Selalu lanjut — feedback hanya sebagai panduan

    baris = ["📊 *Evaluasi SMART Goal Anda:*\n"]
    for kode, info in INDIKATOR_SMART.items():
        icon = "✅" if detail[kode] else "💡"
        baris.append(f"{icon} *{kode} — {info['label']}*")
        if not detail[kode]:
            baris.append(f"   _{info['petunjuk']}_")

    baris.append(f"\n*Skor: {skor}/5*")

    if skor >= 4:
        baris.append("\n✨ Goal Anda sudah sangat jelas. Mari temukan kebajikan yang sesuai!")
    elif skor >= 2:
        baris.append("\n👍 Goal Anda sudah cukup untuk kita mulai.")
        baris.append("_Saran di atas bisa membantu memperkuat tujuan Anda ke depannya._")
    else:
        baris.append("\n💡 Goal Anda masih bisa diperkuat — tapi tidak apa-apa, kita tetap lanjutkan!")
        baris.append("_Saran di atas bisa Anda pertimbangkan sambil berjalan._")

    return {
        "skor": skor,
        "lulus": lulus,
        "detail": detail,
        "feedback": "\n".join(baris),
    }


# ─── REKOMENDASI KEBAJIKAN ───────────────────────────────────────────────────

# Kebajikan 10 dikecualikan dari rekomendasi otomatis
KEBAJIKAN_AKTIF = {k: v for k, v in KEBAJIKAN.items() if k != 10}

KATA_KUNCI_KEBAJIKAN = {
    1: [
        # Indonesian
        "sehat", "kesehatan", "hidup", "sakit", "tubuh", "olahraga", "tidur",
        "makan", "minum", "jaga diri", "keselamatan", "cedera", "istirahat",
        # English
        "health", "healthy", "body", "exercise", "sleep", "eat", "eating",
        "drink", "injury", "rest", "safety", "fitness", "wellbeing", "wellness",
    ],
    2: [
        # Indonesian
        "berbagi", "memberi", "murah hati", "dermawan", "sumbangan", "membantu",
        "uang", "harta", "rejeki", "keuangan", "investasi", "tabungan", "menabung",
        # English
        "give", "giving", "generous", "generosity", "donate", "donation", "share",
        "money", "wealth", "finance", "financial", "save", "saving", "budget",
        "spend", "charity",
    ],
    3: [
        # Indonesian
        "keluarga", "pasangan", "suami", "istri", "hubungan", "pernikahan",
        "setia", "kepercayaan", "komitmen", "anak", "orang tua", "rumah tangga",
        # English
        "family", "spouse", "husband", "wife", "relationship", "marriage",
        "faithful", "fidelity", "commitment", "child", "children", "parent",
        "parents", "home", "household", "partner",
    ],
    4: [
        # Indonesian
        "jujur", "kejujuran", "janji", "integritas", "transparansi",
        "terbuka", "percaya", "menepati", "amanah",
        # English
        "honest", "honesty", "promise", "integrity", "transparent", "transparency",
        "truthful", "truth", "trust", "trustworthy", "open", "sincere", "sincerity",
    ],
    5: [
        # Indonesian
        "konflik", "bertengkar", "damai", "harmonis", "orang lain",
        "bersama", "tim", "komunitas", "kelompok", "kebersamaan", "rukun",
        # English
        "conflict", "argue", "argument", "peace", "harmony", "harmonious",
        "team", "community", "group", "together", "cooperation", "collaborate",
        "cooperation", "unity",
    ],
    6: [
        # Indonesian
        "bicara", "kata-kata", "komunikasi", "berbicara", "perkataan",
        "ramah", "sopan", "lembut", "sabar", "nada", "amarah", "marah", "emosi",
        # English
        "speak", "speech", "talk", "communication", "communicate", "words",
        "kind", "kindness", "gentle", "patient", "patience", "tone", "anger",
        "angry", "emotion", "temper", "polite",
    ],
    7: [
        # Indonesian
        "fokus", "produktif", "efisien", "berguna", "bermanfaat",
        "konsentrasi", "rencana", "kerja", "tugas", "pekerjaan", "karir",
        # English
        "focus", "productive", "productivity", "efficient", "efficiency",
        "useful", "concentrate", "concentration", "plan", "work", "task",
        "job", "career", "goal", "achieve", "achievement",
    ],
    8: [
        # Indonesian
        "syukur", "bersyukur", "bahagia", "senang", "gembira", "positif",
        "iri", "cemburu", "kepuasan", "apresiasi", "terima kasih",
        # English
        "gratitude", "grateful", "thankful", "happy", "happiness", "joy",
        "joyful", "positive", "jealous", "jealousy", "envy", "satisfied",
        "satisfaction", "appreciate", "appreciation", "thank", "blessing",
    ],
    9: [
        # Indonesian
        "empati", "peduli", "simpati", "membantu", "perhatian",
        "mendukung", "mendengarkan", "kasih", "menolong", "sosial",
        # English
        "empathy", "empathize", "care", "compassion", "sympathy", "help",
        "helping", "attention", "support", "listen", "listening", "love",
        "loving", "social", "others", "people",
    ],
}

# Pasangan pendukung — tidak menggunakan kebajikan 10
PASANGAN_PENDUKUNG = {
    1: [9, 2],
    2: [8, 9],
    3: [4, 6],
    4: [7, 5],
    5: [6, 9],
    6: [5, 9],
    7: [4, 8],
    8: [9, 5],
    9: [8, 5],
}


def rekomendasikan_kebajikan(teks_goal: str) -> dict:
    """
    Dari teks goal, rekomendasikan 1 kebajikan utama + 2 pendukung.
    Kebajikan 10 dikecualikan dari rekomendasi otomatis.
    Fallback ke kebajikan 9 (Empati) jika tidak ada kata kunci yang cocok.
    """
    teks_lower = teks_goal.lower()
    skor = {}

    for k_id, kata_list in KATA_KUNCI_KEBAJIKAN.items():
        skor[k_id] = sum(1 for kata in kata_list if kata in teks_lower)

    utama = max(skor, key=lambda k: skor[k])
    if skor[utama] == 0:
        utama = 9  # Fallback: Empati — universal dan selalu relevan

    pendukung = PASANGAN_PENDUKUNG.get(utama, [8, 5])

    k_utama = KEBAJIKAN[utama]
    k_p1 = KEBAJIKAN[pendukung[0]]
    k_p2 = KEBAJIKAN[pendukung[1]]

    alasan = (
        f"🎯 *Kebajikan Utama yang Paling Sesuai:*\n"
        f"{k_utama['emoji']} *{k_utama['nama']}*\n"
        f"_{k_utama['deskripsi'][:120]}..._\n\n"
        f"🌿 *Dua Kebajikan Pendukung:*\n"
        f"{k_p1['emoji']} *{k_p1['nama']}*\n"
        f"_{k_p1['deskripsi'][:100]}..._\n\n"
        f"{k_p2['emoji']} *{k_p2['nama']}*\n"
        f"_{k_p2['deskripsi'][:100]}..._\n"
    )

    return {
        "utama": utama,
        "pendukung": pendukung,
        "semua": [utama] + pendukung,
        "alasan": alasan,
    }
