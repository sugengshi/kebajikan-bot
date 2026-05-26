# utils/messages.py
# All message formatting now uses i18n.T() for bilingual output.

from datetime import datetime
import pytz
from utils.i18n import T
from data.kebajikan import KEBAJIKAN, get_kebajikan_by_id

WIB = pytz.timezone("Asia/Jakarta")

SESI_KEY = {
    "pagi":  "sesi_pagi_label",
    "siang": "sesi_siang_label",
    "sore":  "sesi_sore_label",
}


def _sesi_label(sesi: str, lang: str) -> str:
    return T(SESI_KEY.get(sesi, "sesi_pagi_label"), lang)


def format_sambutan(lang: str = "id") -> str:
    return T("sambutan", lang)


def format_sambutan_kembali(name: str, lang: str = "id") -> str:
    return T("sambutan_kembali", lang, name=name)


def format_pilih_level(lang: str = "id") -> str:
    return T("pilih_level", lang)


def format_tujuan_smart(lang: str = "id") -> str:
    return T("tujuan_smart_prompt", lang)


def format_smart_revisi(lang: str = "id") -> str:
    return T("smart_revisi_prompt", lang)


def format_rekomendasi(level: str, alasan_id: str, alasan_en: str, lang: str = "id") -> str:
    level_key = f"rekomendasi_level_{level}" if level in ("pemula","menengah","mahir") else "rekomendasi_level_pemula"
    level_text = T(level_key, lang)
    alasan = alasan_id if lang == "id" else alasan_en
    return T("rekomendasi_intro", lang, level_text=level_text, alasan=alasan)


def format_onboarding_selesai(name: str, fokus: list, lang: str = "id", tz: str = "Asia/Jakarta") -> str:
    lines = []
    for i, k_id in enumerate(fokus):
        k = KEBAJIKAN.get(k_id, {})
        if k:
            nama = k["nama"] if lang == "id" else k.get("nama_en", k["nama"])
            lines.append(f"{k['emoji']} {nama}")
    daftar = "\n".join(lines)
    jadwal = T("jadwal_harian", lang)
    return T("onboarding_selesai", lang, name=name, daftar=daftar, tz=tz, jadwal=jadwal)


def format_pagi_ganti_tanya(fokus: list, lang: str = "id") -> str:
    lines = []
    for k_id in fokus:
        k = KEBAJIKAN.get(k_id, {})
        if k:
            nama = k["nama"] if lang == "id" else k.get("nama_en", k["nama"])
            lines.append(f"{k['emoji']} {nama}")
    daftar = "\n".join(lines)
    return T("pagi_ganti_tanya", lang, daftar=daftar)


def format_pagi_lanjut_konfirmasi(fokus: list, lang: str = "id") -> str:
    lines = []
    for k_id in fokus:
        k = KEBAJIKAN.get(k_id, {})
        if k:
            nama = k["nama"] if lang == "id" else k.get("nama_en", k["nama"])
            lines.append(f"{k['emoji']} {nama}")
    daftar = "\n".join(lines)
    return T("pagi_lanjut_konfirmasi", lang, daftar=daftar)


def format_pertanyaan_refleksi(sesi: str, k_id: int, step: str, lang: str = "id") -> str:
    k = get_kebajikan_by_id(k_id)
    if not k:
        return ""
    sesi_label = _sesi_label(sesi, lang)
    nama = k["nama"] if lang == "id" else k.get("nama_en", k["nama"])
    pertanyaan = k["pertanyaan_asosiasi"] if lang == "id" else k.get("pertanyaan_asosiasi_en", k["pertanyaan_asosiasi"])
    key = f"refleksi_{step}"
    return T(key, lang,
             sesi=sesi_label, emoji=k["emoji"],
             nama=nama, nama_en=nama,
             pertanyaan=pertanyaan)


def format_konfirmasi_sesi(positif: str, negatif: str, rencana: str, k_id: int, lang: str = "id") -> str:
    k = get_kebajikan_by_id(k_id)
    nama = k["nama"] if k else "Kebajikan"
    if lang == "en" and k:
        nama = k.get("nama_en", nama)
    return T("refleksi_konfirmasi", lang, nama=nama, positif=positif, negatif=negatif, rencana=rencana)


def format_pertanyaan_tambahan_malam(lang: str = "id") -> str:
    return T("tambahan_malam_prompt", lang)


def format_ringkasan_positif(catatan_list: list, tambahan_list: list, lang: str = "id") -> str:
    now = datetime.now(WIB).strftime("%d %B %Y")
    lines = [T("ringkasan_judul", lang, tanggal=now)]

    ada_isi = False
    for c in catatan_list:
        positif = c.get("catatan_positif", "").strip()
        if not positif:
            continue
        ada_isi = True
        sesi = c.get("sesi", "")
        k_id = c.get("kebajikan_id", 0)
        # Advanced/Super Advanced: sesi = "slot_HH:MM", k_id = vow number
        if sesi.startswith("slot_"):
            jam = sesi.replace("slot_", "")
            from data.vows import ADVANCED_VOWS, SUPER_ADVANCED_VOWS
            vow_text = (ADVANCED_VOWS.get(k_id) or SUPER_ADVANCED_VOWS.get(k_id))
            if vow_text:
                en_t, id_t = vow_text
                vow_label = id_t if lang == "id" else en_t
                short = vow_label[:50] + "..." if len(vow_label) > 50 else vow_label
                lines.append(f"*{jam}* — *#{k_id}* _{short}_")
            else:
                lines.append(f"*{jam}* — *#{k_id}*")
        else:
            k = get_kebajikan_by_id(k_id)
            nama = k["nama"] if k else "Kebajikan"
            if lang == "en" and k:
                nama = k.get("nama_en", nama)
            emoji = k["emoji"] if k else "•"
            sesi_label = _sesi_label(sesi, lang)
            lines.append(f"*{sesi_label}* — {emoji} _{nama}_")
        lines.append(f"✅ {positif}\n")

    if tambahan_list:
        ada_isi = True
        lines.append(T("tambahan_malam_label", lang))
        for t in tambahan_list:
            lines.append(f"✅ {t}\n")

    if not ada_isi:
        return T("ringkasan_kosong", lang)

    lines.append("─────────────────────")
    lines.append("─────────────────────")
    return "\n".join(lines)


def _get_entry_header(c: dict, lang: str, hide_sesi_label: bool = False) -> str:
    """Return display header for a catatan entry (works for both slot_ and standard sesi)."""
    sesi = c.get("sesi", "")
    k_id = c.get("kebajikan_id", 0)
    if sesi.startswith("slot_"):
        jam = sesi.replace("slot_", "")
        from data.vows import ADVANCED_VOWS, SUPER_ADVANCED_VOWS
        vow_text = ADVANCED_VOWS.get(k_id) or SUPER_ADVANCED_VOWS.get(k_id)
        if vow_text:
            en_t, id_t = vow_text
            short = (id_t if lang == "id" else en_t)[:55]
            if len(id_t if lang == "id" else en_t) > 55:
                short += "..."
            return f"*{jam}* — 📿 *#{k_id}* _{short}_"
        return f"*{jam}* — 📿 *#{k_id}*"
    else:
        # Check if k_id is actually a vow number (>10) stored with wrong sesi
        from data.vows import ADVANCED_VOWS, SUPER_ADVANCED_VOWS
        vow_text = ADVANCED_VOWS.get(k_id) or SUPER_ADVANCED_VOWS.get(k_id)
        if vow_text:
            en_t, id_t = vow_text
            short = (id_t if lang == "id" else en_t)[:55]
            if len(id_t if lang == "id" else en_t) > 55:
                short += "..."
            # Show time from sesi if it contains time info, else just vow
            if ":" in sesi:
                return f"*{sesi}* — 📿 *#{k_id}* _{short}_"
            return f"📿 *#{k_id}* _{short}_"
        # Standard kebajikan (id 1-10)
        k = get_kebajikan_by_id(k_id)
        if not k or not k.get("nama"):
            return f"📿 *#{k_id}*"
        nama = k["nama"]
        if lang == "en":
            nama = k.get("nama_en", nama)
        emoji = k.get("emoji", "•")
        if hide_sesi_label:
            return f"{emoji} *{nama}*"
        sesi_label = _sesi_label(sesi, lang)
        return f"*{sesi_label}* — {emoji} _{nama}_"


def _is_advanced_list(catatan_list: list) -> bool:
    """Return True if the list contains any vow (slot_) entries."""
    return any(c.get("sesi", "").startswith("slot_") for c in catatan_list)


def format_laporan_ringkas(catatan_list: list, tambahan_list: list, lang: str = "id") -> str:
    """Show positives and plans only — for all filled slots."""
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %B %Y")

    if lang == "id":
        title = f"📋 *Ringkasan Hari Ini*\n_{now}_\n\n─────────────────────\n"
        penutup = "_Ketuk /report lagi untuk melihat semua entri lengkap._ 🙏"
    else:
        title = f"📋 *Today's Summary*\n_{now}_\n\n─────────────────────\n"
        penutup = "_Tap /report again to see all entries in full._ 🙏"

    lines = [title]
    ada_isi = False

    for c in catatan_list:
        positif = c.get("catatan_positif", "").strip()
        rencana = c.get("rencana_kedepan", "").strip()
        if not positif and not rencana:
            continue
        ada_isi = True
        hide = _is_advanced_list(catatan_list)
        header = _get_entry_header(c, lang, hide_sesi_label=hide)
        lines.append(header)
        if positif:
            lines.append(f"✅ {positif}")
        if rencana:
            todo_label = "🌱 *Plan:* " if lang == "en" else "🌱 *Rencana:* "
            lines.append(f"{todo_label}{rencana}")
        lines.append("")

    if tambahan_list:
        ada_isi = True
        label = "🌙 *Additional Good Deeds:*" if lang == "en" else "🌙 *Tambahan Perbuatan Baik:*"
        lines.append(label)
        for t in tambahan_list:
            lines.append(f"✅ {t}")
        lines.append("")

    if not ada_isi:
        return format_ringkasan_positif([], [], lang)

    lines.append("─────────────────────")
    lines.append(penutup)
    return "\n".join(lines)


def format_laporan_lengkap(catatan_list: list, tambahan_list: list, lang: str = "id", user_nama: str = "") -> str:
    """Show every field for every filled slot — positif, negatif, rencana."""
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%d %B %Y")
    sapaan = f" — {user_nama}" if user_nama else ""

    if lang == "id":
        title = f"📄 *Laporan Lengkap{sapaan}*\n_{now}_\n\n═════════════════════\n"
        penutup = "_Ini adalah semua entri yang sudah diisi hari ini._ 🙏"
    else:
        title = f"📄 *Full Report{sapaan}*\n_{now}_\n\n═════════════════════\n"
        penutup = "_These are all entries filled in today._ 🙏"

    lines = [title]

    if not catatan_list and not tambahan_list:
        no_entry = "Belum ada entri hari ini." if lang == "id" else "No entries yet today."
        return title + no_entry

    pos_label  = T("arsip_positif_label", lang)
    neg_label  = T("arsip_negatif_label", lang)
    plan_label = T("arsip_rencana_label", lang)

    hide = _is_advanced_list(catatan_list)
    for c in catatan_list:
        header = _get_entry_header(c, lang, hide_sesi_label=hide)
        lines.append(header)
        positif = c.get("catatan_positif", "").strip()
        negatif = c.get("catatan_negatif", "").strip()
        rencana = c.get("rencana_kedepan", "").strip()
        if positif:
            lines.append(pos_label + positif)
        if negatif and negatif.lower() not in ("tidak ada", "none", "-", ""):
            lines.append(neg_label + negatif)
        if rencana:
            lines.append(plan_label + rencana)
        lines.append("─────────────────────")

    if tambahan_list:
        add_label = T("arsip_tambahan_label", lang)
        lines.append(add_label)
        for t in tambahan_list:
            lines.append(f"✅ {t}")
        lines.append("─────────────────────")

    lines.append(penutup)
    return "\n".join(lines)


def format_arsip_pribadi(catatan_list: list, tambahan_list: list, lang: str = "id", user_nama: str = "") -> str:
    now = datetime.now(WIB).strftime("%d %B %Y")
    sapaan = f" — {user_nama}" if user_nama else ""

    if not catatan_list and not tambahan_list:
        return T("arsip_kosong", lang)

    lines = [T("arsip_judul", lang, sapaan=sapaan, tanggal=now)]

    for c in catatan_list:
        sesi = c.get("sesi", "")
        k_id = c.get("kebajikan_id", 0)
        if sesi.startswith("slot_"):
            jam = sesi.replace("slot_", "")
            from data.vows import ADVANCED_VOWS, SUPER_ADVANCED_VOWS
            vow_text = (ADVANCED_VOWS.get(k_id) or SUPER_ADVANCED_VOWS.get(k_id))
            if vow_text:
                en_t, id_t = vow_text
                short = (id_t if lang == "id" else en_t)[:60]
                lines.append(f"*{jam}*")
                lines.append(f"📿 *#{k_id}* _{short}_\n")
            else:
                lines.append(f"*{jam}*")
                lines.append(f"📿 *#{k_id}*\n")
        else:
            k = get_kebajikan_by_id(k_id)
            nama = k["nama"] if k else "Kebajikan"
            if lang == "en" and k:
                nama = k.get("nama_en", nama)
            emoji = k["emoji"] if k else "•"
            sesi_label = _sesi_label(sesi, lang)
            lines.append(f"*{sesi_label}*")
            lines.append(f"{emoji} *{nama}*\n")

        positif = c.get("catatan_positif", "").strip()
        negatif = c.get("catatan_negatif", "").strip()
        rencana = c.get("rencana_kedepan", "").strip()

        if positif:
            lines.append(T("arsip_positif_label", lang) + positif + "\n")
        if negatif and negatif.lower() not in ("tidak ada", "none", "-", ""):
            lines.append(T("arsip_negatif_label", lang) + negatif + "\n")
        if rencana:
            lines.append(T("arsip_rencana_label", lang) + rencana + "\n")
        lines.append("─────────────────────\n")

    if tambahan_list:
        lines.append(T("arsip_tambahan_label", lang))
        for t in tambahan_list:
            lines.append(f"✅ {t}\n")
        lines.append("─────────────────────\n")

    lines.append(T("arsip_penutup", lang))
    return "\n".join(lines)


def format_pengingat(sesi: str, k_id: int, lang: str = "id") -> str:
    k = get_kebajikan_by_id(k_id)
    nama = k["nama"] if k else "kebajikan"
    if lang == "en" and k:
        nama = k.get("nama_en", nama)
    emoji = k["emoji"] if k else "•"
    sesi_label = _sesi_label(sesi, lang)
    return T("pengingat", lang, sesi=sesi_label, emoji=emoji, nama=nama)


# Alias kept for backward compat
def format_konfirmasi_laporan(catatan_list, tambahan_list, lang="id"):
    return format_ringkasan_positif(catatan_list, tambahan_list, lang)


def format_cofmed(catatan_list, tambahan_list, user_nama="", lang="id"):
    return format_arsip_pribadi(catatan_list, tambahan_list, lang, user_nama)
