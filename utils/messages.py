# utils/messages.py
from data.kebajikan import KEBAJIKAN, get_kebajikan_by_id
from datetime import datetime
import pytz

WIB = pytz.timezone("Asia/Jakarta")

SESI_LABEL = {
    "pagi": "🌅 Pagi (07:00)",
    "siang": "☀️ Siang (12:00)",
    "sore": "🌇 Sore (18:00)",
}


def format_sambutan():
    return (
        "🙏 *Selamat datang di Bot Kebajikan Harian*\n\n"
        "Bot ini akan memandu Anda memantau dan mengembangkan kebajikan "
        "setiap hari — berdasarkan *10 Bibit Baik Utama* dari kebijaksanaan Tibet kuno.\n\n"
        "Mari kita mulai dengan mengenal diri Anda lebih baik.\n\n"
        "_Pertama, pilih level praktik Anda:_"
    )


def format_pilih_level():
    return (
        "📊 *Pilih Level Praktik Anda:*\n\n"
        "🌱 *Pemula*\n"
        "Fokus pada 1 kebajikan per hari hingga Anda siap berganti.\n\n"
        "🌿 *Praktisi Menengah*\n"
        "Fokus pada 3 kebajikan per hari secara bersamaan.\n\n"
        "🌳 *Praktisi Mahir*\n"
        "Memantau semua 10 kebajikan dengan sistem rotasi harian.\n\n"
        "_Pilih yang terasa paling sesuai dengan kondisi Anda saat ini:_"
    )


def format_onboarding_tujuan():
    return (
        "🎯 *Langkah 1 dari 4 — Tujuan SMART Anda*\n\n"
        "Tuliskan tujuan yang ingin Anda capai melalui praktik kebajikan ini.\n\n"
        "Pastikan tujuan Anda *SMART:*\n"
        "• *S*pesifik — jelas dan konkret\n"
        "• *M*easurable — bisa diukur\n"
        "• *A*chievable — bisa dicapai\n"
        "• *R*elevant — sesuai dengan nilai Anda\n"
        "• *T*ime-bound — ada batas waktunya\n\n"
        "_Contoh: Dalam 30 hari ke depan, saya ingin lebih sabar dalam berbicara dengan keluarga saya._\n\n"
        "✏️ *Tuliskan tujuan SMART Anda:*"
    )


def format_onboarding_siapa():
    return (
        "👥 *Langkah 2 dari 4 — Siapa yang Akan Anda Bantu?*\n\n"
        "Kebajikan yang kita tanam selalu terhubung dengan orang-orang di sekitar kita.\n\n"
        "Pikirkan: siapa yang paling akan merasakan manfaat dari perubahan Anda?\n\n"
        "_Contoh: Keluarga saya di rumah, terutama anak-anak saya. Juga rekan kerja yang sering berinteraksi dengan saya._\n\n"
        "✏️ *Tuliskan siapa yang ingin Anda bantu:*"
    )


def format_onboarding_pelaksanaan():
    return (
        "📋 *Langkah 3 dari 4 — Rencana Pelaksanaan*\n\n"
        "Bagaimana Anda berencana menjalani praktik ini setiap hari?\n\n"
        "_Contoh: Saya akan mengisi refleksi pagi, siang, dan sore dengan jujur. "
        "Saya berkomitmen untuk tidak melewatkan satu pun sesi selama 30 hari._\n\n"
        "✏️ *Tuliskan rencana pelaksanaan Anda:*"
    )


def format_onboarding_cofmed():
    return (
        "☕ *Langkah 4 dari 4 — Coffee Meditation (CofMed)*\n\n"
        "Setiap malam pukul 21:30, bot akan mengirimkan *rangkuman semua hal positif* "
        "yang sudah Anda catat sepanjang hari.\n\n"
        "Ini adalah momen untuk duduk tenang, membaca ulang semua kebaikan yang sudah "
        "Anda lakukan — dan membiarkan bibit-bibit itu meresap.\n\n"
        "Tidak ada yang perlu dijawab. Cukup baca dan rasakan. 🙏\n\n"
        "─────────────────────\n"
        "Sekarang mari pilih kebajikan fokus Anda untuk mulai!\n\n"
        "Ketuk tombol di bawah untuk melanjutkan:"
    )


def format_daftar_kebajikan(untuk_pilih: bool = False):
    lines = ["📿 *10 Kebajikan Utama:*\n"]
    current_group = ""
    for k_id, data in KEBAJIKAN.items():
        if data["kelompok"] != current_group:
            current_group = data["kelompok"]
            lines.append(f"\n*{current_group}*")
        lines.append(f"{data['emoji']} {k_id}. {data['nama']}")
    if untuk_pilih:
        lines.append("\n\n_Ketuk nomor kebajikan yang ingin Anda pilih:_")
    return "\n".join(lines)


def format_kebajikan_detail(k_id: int):
    k = get_kebajikan_by_id(k_id)
    if not k:
        return "Kebajikan tidak ditemukan."
    positif = "\n".join(f"  ✅ {c}" for c in k["contoh_positif"][:4])
    negatif = "\n".join(f"  ⚠️ {c}" for c in k["contoh_negatif"][:4])
    return (
        f"{k['emoji']} *{k['nama']}*\n"
        f"_{k['kelompok']}_\n\n"
        f"{k['deskripsi']}\n\n"
        f"*Contoh positif:*\n{positif}\n\n"
        f"*Contoh negatif:*\n{negatif}"
    )


def format_pertanyaan_pagi_ganti():
    return (
        "🌅 *Selamat pagi!*\n\n"
        "Hari baru telah tiba. Apakah Anda ingin *mengganti fokus kebajikan* hari ini, "
        "atau melanjutkan dengan yang sama?"
    )


def format_pertanyaan_refleksi(sesi: str, k_id: int, step: str):
    k = get_kebajikan_by_id(k_id)
    if not k:
        return ""
    label = SESI_LABEL.get(sesi, sesi)
    header = f"{label}\n{k['emoji']} *{k['nama']}*\n\n"

    if step == "positif":
        return (
            f"{header}"
            "🔍 *Pertanyaan 1 dari 3*\n\n"
            "Selama *24 jam terakhir*, dengan memperluas makna kebajikan ini ke semua yang "
            "terhubung dengannya — perbuatan, perkataan, bahkan niat dalam pikiran Anda:\n\n"
            f"_{k['pertanyaan_asosiasi']}_\n\n"
            "✅ *Apa yang sudah Anda lakukan atau pikirkan yang SESUAI dengan kebajikan ini?*\n\n"
            "_Tidak ada yang terlalu kecil untuk dicatat. Bahkan niat pun sudah menjadi bibit._"
        )
    elif step == "negatif":
        return (
            f"{header}"
            "🔍 *Pertanyaan 2 dari 3*\n\n"
            "⚠️ *Adakah perbuatan, perkataan, atau pikiran yang TIDAK SESUAI "
            "dengan kebajikan ini selama 24 jam terakhir?*\n\n"
            "_Jawab dengan jujur — ini bukan untuk dihakimi, tapi untuk disadari dan "
            "diseimbangkan. Anda bisa menulis 'tidak ada' jika memang tidak ada._"
        )
    elif step == "rencana":
        return (
            f"{header}"
            "🔍 *Pertanyaan 3 dari 3*\n\n"
            "🌱 *Untuk menyeimbangkan bibit negatif di atas, apa rencana konkret yang "
            "akan Anda lakukan dalam 24 jam ke depan?*\n\n"
            "_Satu tindakan kecil pun sudah cukup. Yang penting nyata dan bisa dilakukan._"
        )
    return ""


def format_konfirmasi_sesi(positif: str, negatif: str, rencana: str, k_id: int):
    k = get_kebajikan_by_id(k_id)
    nama = k["nama"] if k else "Kebajikan"
    return (
        f"✨ *Catatan Anda untuk {nama}:*\n\n"
        f"✅ *Positif:* {positif}\n\n"
        f"⚠️ *Perlu diseimbangkan:* {negatif}\n\n"
        f"🌱 *Rencana 24 jam ke depan:* {rencana}\n\n"
        "Terima kasih sudah jujur dan teliti! Catatan ini tersimpan. 🙏"
    )


def format_pertanyaan_tambahan_malam():
    return (
        "🌙 *Laporan Malam*\n\n"
        "Sebelum hari berakhir — adakah *perbuatan baik lainnya* yang sudah Anda lakukan "
        "hari ini yang belum tercatat di laporan pagi, siang, atau sore?\n\n"
        "Ceritakan di sini, seberapapun kecilnya. 🙏\n\n"
        "_Ketuk 'Tidak ada' jika sudah lengkap._"
    )


def format_ringkasan_positif(catatan_list: list, tambahan_list: list):
    """
    21:00 — Tampilkan semua perbuatan baik hari ini (hanya sisi positif).
    Bukan konfirmasi, langsung tampil.
    """
    now = datetime.now(WIB).strftime("%d %B %Y")
    lines = [
        f"✨ *Perbuatan Baik Anda Hari Ini*",
        f"_{now}_\n",
        "─────────────────────\n",
    ]

    ada_isi = False
    for c in catatan_list:
        positif = c.get("catatan_positif", "").strip()
        if not positif:
            continue
        ada_isi = True
        k = get_kebajikan_by_id(c.get("kebajikan_id", 0))
        nama = k["nama"] if k else "Kebajikan"
        emoji = k["emoji"] if k else "•"
        sesi_label = SESI_LABEL.get(c["sesi"], c["sesi"])
        lines.append(f"*{sesi_label}* — {emoji} _{nama}_")
        lines.append(f"✅ {positif}\n")

    if tambahan_list:
        ada_isi = True
        lines.append("🌙 *Tambahan Perbuatan Baik:*\n")
        for t in tambahan_list:
            lines.append(f"✅ {t}\n")

    if not ada_isi:
        lines.append(
            "_Belum ada perbuatan baik yang tercatat hari ini.\n"
            "Tidak apa-apa — setiap hari adalah kesempatan baru._ 🙏"
        )
    else:
        lines.append("─────────────────────")
        lines.append(
            "_Bacalah perlahan. Rasakan setiap bibit yang sudah Anda tanam. "
            "Arsip lengkap akan dikirim pukul 21:30._ 🙏"
        )
    return "\n".join(lines)


def format_arsip_pribadi(catatan_list: list, tambahan_list: list, user_nama: str = ""):
    """
    21:30 — Arsip pribadi lengkap: semua entri refleksi pagi/siang/sore
    + tambahan perbuatan baik. Mencakup positif, negatif, dan rencana.
    """
    now = datetime.now(WIB).strftime("%d %B %Y")
    sapaan = f" — {user_nama}" if user_nama else ""
    lines = [
        f"📁 *Arsip Pribadi Harian{sapaan}*",
        f"_{now}_\n",
        "═════════════════════\n",
    ]

    if not catatan_list and not tambahan_list:
        lines.append(
            "_Tidak ada entri untuk hari ini.\n"
            "Mulai besok, setiap sesi yang terisi akan tersimpan di sini._ 🙏"
        )
        return "\n".join(lines)

    for c in catatan_list:
        k = get_kebajikan_by_id(c.get("kebajikan_id", 0))
        nama = k["nama"] if k else "Kebajikan"
        emoji = k["emoji"] if k else "•"
        sesi_label = SESI_LABEL.get(c["sesi"], c["sesi"])

        lines.append(f"*{sesi_label}*")
        lines.append(f"{emoji} *{nama}*\n")

        positif = c.get("catatan_positif", "").strip()
        negatif = c.get("catatan_negatif", "").strip()
        rencana = c.get("rencana_kedepan", "").strip()

        if positif:
            lines.append(f"✅ *Sesuai kebajikan:*\n{positif}\n")
        if negatif and negatif.lower() not in ("tidak ada", "-", ""):
            lines.append(f"⚠️ *Perlu diseimbangkan:*\n{negatif}\n")
        if rencana:
            lines.append(f"🌱 *Rencana 24 jam ke depan:*\n{rencana}\n")

        lines.append("─────────────────────\n")

    if tambahan_list:
        lines.append("🌙 *Tambahan Perbuatan Baik (20:00)*\n")
        for t in tambahan_list:
            lines.append(f"✅ {t}\n")
        lines.append("─────────────────────\n")

    lines.append(
        "_Arsip ini adalah catatan integritas Anda. "
        "Setiap bibit yang dicatat dengan jujur akan tumbuh. "
        "Istirahatlah dengan tenang._ 🙏"
    )
    return "\n".join(lines)


# Alias untuk backward compatibility
def format_konfirmasi_laporan(catatan_list: list, tambahan_list: list):
    return format_ringkasan_positif(catatan_list, tambahan_list)


def format_cofmed(catatan_list: list, tambahan_list: list, user_nama: str = ""):
    return format_arsip_pribadi(catatan_list, tambahan_list, user_nama)


def format_pengingat(sesi: str, k_id: int, attempt: int = 1):
    k = get_kebajikan_by_id(k_id)
    nama = k["nama"] if k else "kebajikan"
    emoji = k["emoji"] if k else "•"
    if attempt == 1:
        return (
            f"⏰ *Pengingat {SESI_LABEL.get(sesi, sesi)}*\n\n"
            f"Refleksi {emoji} *{nama}* Anda belum terisi.\n"
            "Butuh hanya beberapa menit — yuk kita isi bersama! 🙏"
        )
    return (
        f"🔔 *Pengingat ke-2*\n\n"
        f"Refleksi {sesi} untuk {emoji} *{nama}* masih menunggu.\n"
        "Ketuk /refleksi untuk mulai mengisi sekarang."
    )
