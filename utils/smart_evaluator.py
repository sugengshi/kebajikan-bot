# utils/smart_evaluator.py
"""
Evaluasi SMART goal dan rekomendasi kebajikan menggunakan logika berbasis kata kunci.
Tidak memerlukan API eksternal — murni rule-based agar tetap ringan di Railway.
"""

import re
from data.kebajikan import KEBAJIKAN

# ─── SMART EVALUATION ────────────────────────────────────────────────────────

# Indikator per kriteria SMART
INDIKATOR_SMART = {
    "S": {
        "label": "Spesifik",
        "kata": [
            "saya", "saya akan", "saya ingin", "saya berkomitmen",
            "dengan cara", "melalui", "kepada", "bersama",
            "di rumah", "di kantor", "di keluarga", "di tempat kerja",
        ],
        "petunjuk": "Tambahkan *siapa*, *apa*, dan *di mana* yang lebih konkret.",
    },
    "M": {
        "label": "Terukur",
        "kata": [
            "kali", "x sehari", "x seminggu", "menit", "jam",
            "persen", "%", "orang", "hari", "minggu", "bulan",
            "lebih sering", "setiap", "minimal", "setidaknya",
        ],
        "petunjuk": "Tambahkan ukuran yang bisa dihitung — frekuensi, jumlah, atau durasi.",
    },
    "A": {
        "label": "Bisa Dicapai",
        "kata": [
            "mulai", "langkah", "satu", "kecil", "sedikit",
            "perlahan", "bertahap", "mencoba", "berlatih",
            "setiap hari", "rutin", "kebiasaan",
        ],
        "petunjuk": "Pastikan tujuan realistis — mulai dari langkah kecil yang bisa langsung dilakukan.",
    },
    "R": {
        "label": "Relevan",
        "kata": [
            "supaya", "agar", "karena", "demi", "untuk",
            "sehingga", "membantu", "bermanfaat", "berdampak",
            "penting", "berarti", "nilai", "prinsip",
        ],
        "petunjuk": "Jelaskan *mengapa* tujuan ini penting bagi Anda atau orang di sekitar Anda.",
    },
    "T": {
        "label": "Batas Waktu",
        "kata": [
            "hari", "minggu", "bulan", "tahun", "30", "60", "90",
            "dalam", "selama", "sampai", "hingga", "selesai",
            "januari", "februari", "maret", "april", "mei", "juni",
            "juli", "agustus", "september", "oktober", "november", "desember",
        ],
        "petunjuk": "Tambahkan batas waktu yang jelas — misalnya '30 hari ke depan' atau 'sampai akhir bulan ini'.",
    },
}

def evaluasi_smart(teks: str) -> dict:
    """
    Evaluasi teks goal terhadap 5 kriteria SMART.
    Return: {
        'skor': int (0-5),
        'lulus': bool,
        'detail': {'S': True/False, 'M': True/False, ...},
        'feedback': str (pesan lengkap),
    }
    """
    teks_lower = teks.lower()
    detail = {}

    for kode, info in INDIKATOR_SMART.items():
        cocok = any(kata in teks_lower for kata in info["kata"])
        detail[kode] = cocok

    skor = sum(1 for v in detail.values() if v)
    lulus = skor >= 4  # minimal 4 dari 5 kriteria

    # Bangun feedback
    baris = ["📊 *Evaluasi SMART Goal Anda:*\n"]
    for kode, info in INDIKATOR_SMART.items():
        icon = "✅" if detail[kode] else "⚠️"
        baris.append(f"{icon} *{kode} — {info['label']}*")
        if not detail[kode]:
            baris.append(f"   _{info['petunjuk']}_")

    baris.append(f"\n*Skor: {skor}/5*")

    if lulus:
        baris.append("\n✨ Goal Anda sudah memenuhi kriteria SMART!")
        baris.append("Mari kita temukan kebajikan yang paling sesuai.")
    else:
        baris.append(
            f"\n_Goal Anda memenuhi {skor} dari 5 kriteria. "
            "Apakah ingin memperbaikinya, atau lanjutkan saja?_"
        )

    return {
        "skor": skor,
        "lulus": lulus,
        "detail": detail,
        "feedback": "\n".join(baris),
    }


# ─── REKOMENDASI KEBAJIKAN ───────────────────────────────────────────────────

# Kata kunci per kebajikan — dicocokkan dengan teks goal
KATA_KUNCI_KEBAJIKAN = {
    1: ["sehat", "kesehatan", "hidup", "sakit", "tubuh", "olahraga", "tidur",
        "makan", "minum", "jaga diri", "keselamatan", "cedera"],
    2: ["berbagi", "memberi", "murah hati", "dermawan", "sumbangan", "membantu",
        "uang", "harta", "rejeki", "keuangan", "investasi", "tabungan"],
    3: ["keluarga", "pasangan", "suami", "istri", "hubungan", "pernikahan",
        "setia", "kepercayaan", "komitmen", "anak", "orang tua"],
    4: ["jujur", "kejujuran", "janji", "komitmen", "integritas", "transparansi",
        "berbohong", "terbuka", "percaya", "kepercayaan"],
    5: ["konflik", "bertengkar", "damai", "harmonis", "hubungan", "orang lain",
        "bersama", "tim", "komunitas", "kelompok", "kebersamaan"],
    6: ["bicara", "kata-kata", "komunikasi", "berbicara", "perkataan",
        "ramah", "sopan", "lembut", "sabar", "nada", "amarah"],
    7: ["fokus", "produktif", "waktu", "efisien", "berguna", "bermanfaat",
        "konsentrasi", "tujuan", "rencana", "kerja"],
    8: ["syukur", "bersyukur", "bahagia", "senang", "gembira", "positif",
        "iri", "cemburu", "kepuasan", "apresiasi"],
    9: ["empati", "peduli", "simpati", "membantu", "orang lain", "perhatian",
        "mendukung", "mendengarkan", "kasih", "menolong"],
    10: ["belajar", "memahami", "mengerti", "wisdom", "bijak", "filosofi",
         "makna", "tujuan hidup", "prinsip", "nilai", "refleksi"],
}

# Pasangan pendukung alami per kebajikan utama
PASANGAN_PENDUKUNG = {
    1: [9, 2],   # Lindungi Hidup → Empati, Murah Hati
    2: [8, 9],   # Murah Hati → Syukur, Empati
    3: [4, 6],   # Hormati Hubungan → Jujur, Ramah
    4: [7, 5],   # Jujur → Berguna, Bawa Bersama
    5: [6, 9],   # Bawa Bersama → Ramah, Empati
    6: [5, 9],   # Ramah → Bawa Bersama, Empati
    7: [4, 10],  # Berguna → Jujur, Pandangan Benar
    8: [9, 10],  # Bahagia Org Lain → Empati, Pandangan Benar
    9: [8, 5],   # Empati → Bahagia Org Lain, Bawa Bersama
    10: [4, 8],  # Pandangan Benar → Jujur, Bahagia Org Lain
}

def rekomendasikan_kebajikan(teks_goal: str) -> dict:
    """
    Dari teks goal, rekomendasikan:
    - 1 kebajikan utama (paling relevan)
    - 2 kebajikan pendukung
    Return: {'utama': int, 'pendukung': [int, int], 'alasan': str}
    """
    teks_lower = teks_goal.lower()
    skor = {}

    for k_id, kata_list in KATA_KUNCI_KEBAJIKAN.items():
        cocok = sum(1 for kata in kata_list if kata in teks_lower)
        skor[k_id] = cocok

    # Kebajikan utama: skor tertinggi; fallback ke 10 (Pandangan Benar) jika semua 0
    utama = max(skor, key=lambda k: skor[k])
    if skor[utama] == 0:
        utama = 10  # Default: Pandangan Dunia yang Benar selalu relevan

    pendukung = PASANGAN_PENDUKUNG.get(utama, [8, 9])

    # Bangun teks rekomendasi
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
