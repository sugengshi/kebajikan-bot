# handlers/conversation.py
import logging
import os
import re
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from utils.database import (
    get_user, create_user, update_user,
    save_catatan, get_catatan_hari_ini, save_tambahan_malam,
    get_tambahan_malam, set_pending, get_pending, clear_pending,
    get_user_lang
)
from utils.messages import (
    format_pertanyaan_refleksi, format_konfirmasi_sesi,
    format_ringkasan_positif, format_pertanyaan_tambahan_malam,
    format_laporan_ringkas, format_laporan_lengkap,
    format_sambutan, format_tujuan_smart, format_smart_revisi,
    format_onboarding_selesai, format_rekomendasi,
    format_pagi_ganti_tanya, format_pagi_lanjut_konfirmasi,
)
from utils.i18n import T, COMMANDS, TIMEZONE_MAP, cmd
from utils.smart_evaluator import evaluasi_smart, rekomendasikan_kebajikan
from data.kebajikan import KEBAJIKAN, LEVEL_CONFIG, get_mahir_virtues_for_day

logger = logging.getLogger(__name__)

# ─── STATES ──────────────────────────────────────────────────────────────────
(
    PILIH_BAHASA,
    PILIH_TIMEZONE,
    PILIH_LEVEL,
    ONBOARDING_GOAL,
    ONBOARDING_GOAL_REVISI,
    ONBOARDING_KONFIRMASI_KEBAJIKAN,
    REFLEKSI_POSITIF,
    REFLEKSI_NEGATIF,
    REFLEKSI_RENCANA,
    TAMBAHAN_MALAM_INPUT,
    GANTI_PILIH,
    UPGRADE_PASSWORD,
    PILIH_VOW_AWAL,
    PILIH_JAM_VOW,
    SETJAM_SEQUENTIAL,
    PILIH_REFLEKSI,
    PILIH_SESI_REFLEKSI,
    SUMPAH_REFLEKSI_POSITIF,
    SUMPAH_REFLEKSI_NEGATIF,
    SUMPAH_REFLEKSI_RENCANA,
    PILIH_HARI_ROTASI,
) = range(21)

SETJAM_DB_KEYS    = ["jam_fokus","jam_pagi","jam_siang","jam_sore","jam_malam","jam_ringkasan","jam_cofmed"]
SETJAM_DEFAULTS   = ["06:00","07:00","12:00","18:00","20:00","21:00","21:30"]

VOW_JAM_DEFAULTS  = ["07:00","09:30","12:00","14:30","17:00","19:30"]

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _sesi_sekarang() -> str:
    import pytz
    from datetime import datetime
    jam = datetime.now(pytz.timezone("Asia/Jakarta")).hour
    if jam < 12:   return "pagi"
    elif jam < 17: return "siang"
    else:          return "sore"


def _today_for_user(db_user: dict):
    """Return today's date in the user's local timezone (avoids UTC midnight bugs)."""
    import pytz
    from datetime import datetime
    tz_str = (db_user or {}).get("timezone") or "Asia/Jakarta"
    try:
        tz = pytz.timezone(tz_str)
    except Exception:
        tz = pytz.timezone("Asia/Jakarta")
    return datetime.now(tz).date()


def _day_number_for_user(db_user: dict) -> int:
    """Compute today's day-number in the user's own timezone."""
    from datetime import date as dt_date
    join_date_raw = (db_user or {}).get("join_date")
    today = _today_for_user(db_user)
    if join_date_raw:
        jd = join_date_raw if isinstance(join_date_raw, dt_date) else today
        # datetime subclasses date — convert if needed
        if hasattr(jd, "date"):
            jd = jd.date()
        return (today - jd).days + 1
    return 1


async def _lang(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> str:
    if "lang" in context.user_data:
        return context.user_data["lang"]
    lang = await get_user_lang(user_id)
    context.user_data["lang"] = lang
    return lang


def _valid_time(t: str) -> bool:
    if not re.match(r"^\d{2}:\d{2}$", t):
        return False
    h, m = t.split(":")
    return 0 <= int(h) <= 23 and 0 <= int(m) <= 59


# ─── KEYBOARDS ───────────────────────────────────────────────────────────────

def kb_bahasa():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="lang_id")],
        [InlineKeyboardButton("🇬🇧 English",          callback_data="lang_en")],
    ])

def kb_timezone():
    keys = ["WIB","WITA","WIT","SGT","MYT","IST","AEST","GMT","CET","EST","PST"]
    rows = [[InlineKeyboardButton(
        f"{'Asia/Jakarta' if k=='WIB' else TIMEZONE_MAP[k]} ({k})",
        callback_data=f"tz_{k}"
    )] for k in keys]
    return InlineKeyboardMarkup(rows)

def kb_level(lang: str = "id"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T("level_pemula_label",   lang), callback_data="level_pemula")],
        [InlineKeyboardButton(T("level_menengah_label", lang), callback_data="level_menengah")],
        [InlineKeyboardButton(T("level_mahir_label",    lang), callback_data="level_mahir")],
        [InlineKeyboardButton(T("level_advanced_label", lang), callback_data="level_advanced")],
        [InlineKeyboardButton(T("level_super_label",    lang), callback_data="level_super_advanced")],
    ])

def kb_smart(lang: str = "id"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T("smart_lanjut_label", lang), callback_data="goal_lanjut"),
        InlineKeyboardButton(T("smart_revisi_label", lang), callback_data="goal_revisi"),
    ]])

def kb_kebajikan_konfirmasi(lang: str = "id"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T("setuju_label",        lang), callback_data="kebajikan_setuju"),
        InlineKeyboardButton(T("pilih_sendiri_label", lang), callback_data="kebajikan_sendiri"),
    ]])

def kb_kebajikan_manual(level: str, dipilih: list, lang: str = "id"):
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    rows = []
    for k_id, data in KEBAJIKAN.items():
        cek = "✅ " if k_id in dipilih else ""
        rows.append([InlineKeyboardButton(
            f"{cek}{data['emoji']} {k_id}. {data['nama']}",
            callback_data=f"pilih_k_{k_id}"
        )])
    if len(dipilih) >= jumlah:
        rows.append([InlineKeyboardButton(T("selesai_pilih_label", lang), callback_data="selesai_pilih")])
    return InlineKeyboardMarkup(rows)

def kb_pagi_ganti(lang: str = "id"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T("pagi_ganti_ya_label",    lang), callback_data="pagi_ganti_ya"),
        InlineKeyboardButton(T("pagi_ganti_tidak_label", lang), callback_data="pagi_ganti_tidak"),
    ]])

def kb_upgrade_level(lang: str = "id"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T("level_pemula_label",   lang), callback_data="upgrade_pemula")],
        [InlineKeyboardButton(T("level_menengah_label", lang), callback_data="upgrade_menengah")],
        [InlineKeyboardButton(T("level_mahir_label",    lang), callback_data="upgrade_mahir")],
        [InlineKeyboardButton(T("level_advanced_label", lang), callback_data="upgrade_advanced")],
        [InlineKeyboardButton(T("level_super_label",    lang), callback_data="upgrade_super_advanced")],
    ])

def kb_vow_jam_konfirmasi(lang: str = "id"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T("vow_konfirmasi_jam",  lang), callback_data="atur_jam_vow"),
    ]])

def kb_setjam_lewati(lang: str = "id"):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T("setjam_lewati_label", lang), callback_data="setjam_lewati"),
    ]])


# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_user(user.id, user.username or user.first_name)
    context.user_data.clear()
    # Full reset
    await update_user(user.id, onboarding_selesai=0, level="pemula",
                      kebajikan_fokus="[]", tujuan_smart="", join_date=None)
    await update.message.reply_text(
        T("pilih_bahasa", "id"),
        parse_mode="Markdown",
        reply_markup=kb_bahasa()
    )
    return PILIH_BAHASA


# ─── LANGUAGE ────────────────────────────────────────────────────────────────

async def pilih_bahasa_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await update_user(query.from_user.id, bahasa=lang)
    await query.edit_message_text(T("bahasa_dipilih", lang), parse_mode="Markdown")
    # Show timezone selection
    await query.message.reply_text(
        T("pilih_timezone", lang), parse_mode="Markdown",
        reply_markup=kb_timezone()
    )
    return PILIH_TIMEZONE


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(
        T("language_prompt", lang), parse_mode="Markdown", reply_markup=kb_bahasa()
    )
    return PILIH_BAHASA


async def ganti_bahasa_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await update_user(query.from_user.id, bahasa=lang)
    await query.edit_message_text(T("language_changed", lang), parse_mode="Markdown")
    return ConversationHandler.END


# ─── TIMEZONE ────────────────────────────────────────────────────────────────

async def pilih_timezone_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    tz_key = query.data.replace("tz_", "")
    tz_value = TIMEZONE_MAP.get(tz_key, "Asia/Jakarta")
    context.user_data["timezone"] = tz_value
    await update_user(query.from_user.id, timezone=tz_value)
    await query.edit_message_text(
        T("timezone_dipilih", lang, tz=f"{tz_key} ({tz_value})"), parse_mode="Markdown"
    )
    await query.message.reply_text(
        format_sambutan(lang), parse_mode="Markdown", reply_markup=kb_level(lang)
    )
    return PILIH_LEVEL


# ─── PILIH LEVEL ─────────────────────────────────────────────────────────────

async def pilih_level_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    level = query.data.replace("level_", "")
    context.user_data["level"] = level
    context.user_data["upgrade_target"] = level
    lang = await _lang(query.from_user.id, context)
    cfg = LEVEL_CONFIG.get(level, {})
    from utils.i18n import STRINGS
    label_key = f"level_{level}_label"
    label = T(label_key, lang) if label_key in STRINGS else cfg.get("label", level)

    await query.edit_message_text(
        T("level_dipilih", lang, label=label, desc=cfg.get("deskripsi", "")),
        parse_mode="Markdown"
    )
    if level in ("advanced", "super_advanced"):
        label_key2 = "level_advanced_label" if level == "advanced" else "level_super_label"
        await query.message.reply_text(
            T("password_prompt", lang, label=T(label_key2, lang)),
            parse_mode="Markdown"
        )
        return UPGRADE_PASSWORD

    # Mahir: skip SMART goal — auto-assign Day 1 virtues, then set 6 reflection times
    if level == "mahir":
        dipilih = get_mahir_virtues_for_day(1)
        context.user_data["kebajikan_dipilih"] = dipilih
        context.user_data["goal"] = ""
        context.user_data["mahir_onboarding"] = True
        tz = context.user_data.get("timezone", "Asia/Jakarta")
        from datetime import date as _date
        await update_user(query.from_user.id, level="mahir", kebajikan_fokus=dipilih,
                          tujuan_smart="", onboarding_selesai=1, timezone=tz,
                          join_date=_date.today())
        await query.edit_message_text(T("mahir_sambutan_jam", lang), parse_mode="Markdown")
        context.user_data["vow_times_new"] = list(VOW_JAM_DEFAULTS)
        return await _vow_jam_next_slot(query.message, context, lang, slot=0)

    await query.message.reply_text(format_tujuan_smart(lang), parse_mode="Markdown")
    return ONBOARDING_GOAL


# ─── SMART GOAL ──────────────────────────────────────────────────────────────

async def terima_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    context.user_data["goal"] = update.message.text
    hasil = evaluasi_smart(update.message.text)
    await update.message.reply_text(hasil["feedback"], parse_mode="Markdown",
                                    reply_markup=kb_smart(lang))
    return ONBOARDING_GOAL_REVISI


async def goal_lanjut_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    lang = await _lang(query.from_user.id, context)
    return await _tampilkan_rekomendasi(query.message, context, lang)


async def goal_revisi_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    lang = await _lang(query.from_user.id, context)
    await query.message.reply_text(format_smart_revisi(lang), parse_mode="Markdown")
    return ONBOARDING_GOAL


async def _tampilkan_rekomendasi(message, context, lang: str):
    goal = context.user_data.get("goal", "")
    rekomendasi = rekomendasikan_kebajikan(goal)
    context.user_data["rekomendasi"] = rekomendasi
    level = context.user_data.get("level", "pemula")
    dipilih = [rekomendasi["utama"]] if level == "pemula" else rekomendasi["semua"]
    context.user_data["kebajikan_dipilih"] = dipilih
    await message.reply_text(
        format_rekomendasi(level, rekomendasi["alasan"], rekomendasi["alasan"], lang),
        parse_mode="Markdown", reply_markup=kb_kebajikan_konfirmasi(lang)
    )
    return ONBOARDING_KONFIRMASI_KEBAJIKAN


# ─── KEBAJIKAN SELECTION ─────────────────────────────────────────────────────

async def kebajikan_setuju_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    lang = await _lang(query.from_user.id, context)
    return await _simpan_dan_selesai(query, context, lang)


async def kebajikan_sendiri_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    lang = await _lang(query.from_user.id, context)
    level = context.user_data.get("level", "pemula")
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    context.user_data["kebajikan_dipilih"] = []
    await query.message.reply_text(
        T("ganti_judul", lang, jumlah=jumlah), parse_mode="Markdown",
        reply_markup=kb_kebajikan_manual(level, [], lang)
    )
    return GANTI_PILIH


async def pilih_kebajikan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)

    if query.data == "selesai_pilih":
        dipilih = context.user_data.get("kebajikan_dipilih", [])
        if not dipilih:
            await query.answer(T("pilih_minimal", lang), show_alert=True)
            return GANTI_PILIH
        return await _simpan_dan_selesai(query, context, lang)

    k_id = int(query.data.replace("pilih_k_", ""))
    level = context.user_data.get("level", "pemula")
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    dipilih = context.user_data.get("kebajikan_dipilih", [])

    if k_id in dipilih:
        dipilih.remove(k_id)
    elif len(dipilih) < jumlah:
        dipilih.append(k_id)
    else:
        await query.answer(T("sudah_penuh_alert", lang, jumlah=jumlah), show_alert=True)
        return GANTI_PILIH

    context.user_data["kebajikan_dipilih"] = dipilih
    if len(dipilih) == jumlah:
        return await _simpan_dan_selesai(query, context, lang)
    await query.edit_message_reply_markup(
        reply_markup=kb_kebajikan_manual(level, dipilih, lang)
    )
    return GANTI_PILIH


async def _simpan_dan_selesai(query, context, lang: str):
    user_id = query.from_user.id
    level = context.user_data.get("level", "pemula")
    dipilih = context.user_data.get("kebajikan_dipilih", [])
    goal = context.user_data.get("goal", "")
    tz = context.user_data.get("timezone", "Asia/Jakarta")
    await update_user(user_id, level=level, kebajikan_fokus=dipilih,
                      tujuan_smart=goal, onboarding_selesai=1, timezone=tz)
    nama = query.from_user.first_name
    await query.message.reply_text(
        format_onboarding_selesai(nama, dipilih, lang, tz), parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─── /refleksi ───────────────────────────────────────────────────────────────

async def cmd_refleksi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user or not db_user.get("onboarding_selesai"):
        await update.message.reply_text(T("silakan_start", "id"))
        return ConversationHandler.END
    lang = db_user.get("bahasa", "id")
    context.user_data["lang"] = lang
    level = db_user.get("level", "pemula")

    # ── Advanced / Super Advanced: show today's vow schedule ──
    if level in ("advanced", "super_advanced"):
        return await _tampilkan_pilihan_sumpah(update.message, context, lang, db_user)

    # ── Mahir: show 6 refleksi slots with status ──
    if level == "mahir":
        return await _tampilkan_pilihan_refleksi_mahir(update.message, context, lang, db_user)

    # ── Standard levels: show kebajikan ──
    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        await update.message.reply_text(T("kebajikan_belum_ada", lang))
        return ConversationHandler.END

    catatan_hari_ini = await get_catatan_hari_ini(user_id)
    filled = {(c["kebajikan_id"], c["sesi"]) for c in catatan_hari_ini}
    sesi_list = ["pagi", "siang", "sore"]

    if len(fokus) == 1:
        k_id = fokus[0]
        sesi = _sesi_sekarang()
        for s in sesi_list:
            if (k_id, s) not in filled:
                sesi = s
                break
        await set_pending(user_id, sesi, k_id)
        await update.message.reply_text(
            format_pertanyaan_refleksi(sesi, k_id, "positif", lang),
            parse_mode="Markdown"
        )
        return REFLEKSI_POSITIF

    return await _tampilkan_pilihan_refleksi(update.message, context, lang, fokus, filled)


async def reflect_vow_from_scheduler_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User tapped 'Reflect' on a scheduler vow message — start Q1 directly."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await _lang(user_id, context)

    # Parse: reflect_vow_{slot_index}_{jam_no_colon}
    parts = query.data.replace("reflect_vow_", "").split("_")
    slot_index = int(parts[0])
    jam_raw = parts[1] if len(parts) > 1 else "0700"
    jam = jam_raw[:2] + ":" + jam_raw[2:]  # "0700" → "07:00"

    # Rebuild vow data from DB
    db_user = await get_user(user_id)
    if not db_user:
        await query.message.reply_text(T("silakan_start", lang))
        return ConversationHandler.END

    level = db_user.get("level", "advanced")
    from data.vows import (get_adv_vows_for_day, get_sa_vows_for_day,
                           ADVANCED_VOWS, SUPER_ADVANCED_VOWS, ADV_TIMES, SA_TIMES)
    day_number = _day_number_for_user(db_user)
    vows = get_adv_vows_for_day(day_number) if level == "advanced" else get_sa_vows_for_day(day_number)
    times = ADV_TIMES if level == "advanced" else SA_TIMES
    vow_dict = ADVANCED_VOWS if level == "advanced" else SUPER_ADVANCED_VOWS

    if slot_index >= len(vows):
        await query.message.reply_text(T("silakan_start", lang))
        return ConversationHandler.END

    vow_raw = vows[slot_index]
    label_key = "sumpah_label_advanced" if level == "advanced" else "sumpah_label_super"
    label = T(label_key, lang)

    p = _build_vow_params(vow_raw, vow_dict)
    context.user_data["lang"]                = lang
    context.user_data["sumpah_vow_num"]      = p["vow_num"]
    context.user_data["sumpah_vow_en"]       = p["en"]
    context.user_data["sumpah_vow_id"]       = p["id_"]
    context.user_data["sumpah_vow_nums_str"] = p["nums_str"]
    context.user_data["sumpah_vow_block"]    = p["vow_block"]
    context.user_data["sumpah_vow_jam"]      = jam
    context.user_data["sumpah_vow_label"]    = label
    context.user_data["sumpah_vows_today"]   = vows
    context.user_data["sumpah_times_today"]  = times
    context.user_data["sumpah_level"]        = level
    context.user_data["sumpah_pair_next"]    = p["pair_next"]
    context.user_data["sumpah_was_pair"]     = p["pair_next"] is not None

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(T("sumpah_order_pos_label", lang), callback_data="sumpah_order_pos_first"),
        InlineKeyboardButton(T("sumpah_order_neg_label", lang), callback_data="sumpah_order_neg_first"),
    ]])
    if p["pair_next"]:
        prompt = T("sumpah_pilih_urutan_pair_intro", lang,
                   **_vow_ctx(context), first_num=p["nums_str"])
    else:
        prompt = T("sumpah_pilih_urutan", lang, **_vow_ctx(context))
    await query.message.reply_text(prompt, parse_mode="Markdown", reply_markup=kb)
    return PILIH_REFLEKSI


async def rewrite_vow_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle yes/no from the 'all done, want to rewrite?' prompt."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    user_id = query.from_user.id

    if query.data == "rewrite_vow_no":
        await query.edit_message_text(T("sumpah_sudah_semua_tidak", lang), parse_mode="Markdown")
        return ConversationHandler.END

    # Yes — show the full vow schedule to pick from (same as /reflect)
    db_user = await get_user(user_id)
    if not db_user:
        await query.message.reply_text(T("silakan_start", lang))
        return ConversationHandler.END
    await query.edit_message_reply_markup(reply_markup=None)
    return await _tampilkan_pilihan_sumpah(query.message, context, lang, db_user)


async def _tampilkan_pilihan_sumpah(message, context, lang: str, db_user: dict):
    """For Advanced/Super Advanced: show today's vow schedule as selectable buttons."""
    from data.vows import (get_adv_vows_for_day, get_sa_vows_for_day,
                           ADVANCED_VOWS, SUPER_ADVANCED_VOWS, ADV_TIMES, SA_TIMES)

    level = db_user.get("level", "advanced")
    day_number = _day_number_for_user(db_user)

    times = ADV_TIMES if level == "advanced" else SA_TIMES
    vows = get_adv_vows_for_day(day_number) if level == "advanced" else get_sa_vows_for_day(day_number)
    vow_dict = ADVANCED_VOWS if level == "advanced" else SUPER_ADVANCED_VOWS

    # Check which vow slots already have a catatan today
    # We store vow number as kebajikan_id in save_catatan for advanced levels
    from utils.database import get_catatan_hari_ini as _get_cat
    catatan_today = await _get_cat(db_user.get("user_id", 0) if isinstance(db_user, dict) else 0)
    # get user_id from message
    try:
        uid = message.chat.id
        catatan_today = await _get_cat(uid)
    except Exception:
        catatan_today = []
    filled_vows = {c["kebajikan_id"] for c in catatan_today}

    rows = []
    for i, (t, v) in enumerate(zip(times, vows)):
        if isinstance(v, list):
            nums = " & ".join(str(n) for n in v)
            status = "✅ " if all(vi in filled_vows for vi in v) else "○ "
            label = f"{status}{t} — #{nums}"
            cb = f"sumpah_slot_{i}"
        else:
            en, id_ = vow_dict.get(v, ("?", "?"))
            text = id_ if lang == "id" else en
            short = text[:38] + "..." if len(text) > 38 else text
            status = "✅ " if v in filled_vows else "○ "
            label = f"{status}{t} — #{v} {short}"
            cb = f"sumpah_slot_{i}"
        rows.append([InlineKeyboardButton(label, callback_data=cb)])

    # Store today's vow list in context for the callback
    context.user_data["sumpah_vows_today"] = vows
    context.user_data["sumpah_times_today"] = times
    context.user_data["sumpah_level"] = level

    await message.reply_text(
        T("refleksi_pilih_sumpah", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return PILIH_REFLEKSI


async def pilih_sumpah_slot_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User selected a vow slot — start 3-question reflection flow."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await _lang(user_id, context)
    slot_index = int(query.data.replace("sumpah_slot_", ""))

    vows = context.user_data.get("sumpah_vows_today", [])
    times = context.user_data.get("sumpah_times_today", [])
    level = context.user_data.get("sumpah_level", "")

    # Rebuild from DB if context was lost (e.g. bot restart)
    if not vows or not level:
        db_user = await get_user(user_id)
        if not db_user:
            await query.message.reply_text(T("silakan_start", lang))
            return ConversationHandler.END
        level = db_user.get("level", "advanced")
        from data.vows import (get_adv_vows_for_day, get_sa_vows_for_day,
                               ADV_TIMES, SA_TIMES)
        day_number = _day_number_for_user(db_user)
        vows = get_adv_vows_for_day(day_number) if level == "advanced" else get_sa_vows_for_day(day_number)
        times = ADV_TIMES if level == "advanced" else SA_TIMES
        context.user_data["sumpah_vows_today"] = vows
        context.user_data["sumpah_times_today"] = times
        context.user_data["sumpah_level"] = level

    if slot_index >= len(vows):
        await query.message.reply_text(T("silakan_start", lang))
        return ConversationHandler.END

    vow_raw = vows[slot_index]
    jam = times[slot_index] if slot_index < len(times) else "?"
    from data.vows import ADVANCED_VOWS, SUPER_ADVANCED_VOWS
    vow_dict = ADVANCED_VOWS if level == "advanced" else SUPER_ADVANCED_VOWS
    label_key = "sumpah_label_advanced" if level == "advanced" else "sumpah_label_super"
    label = T(label_key, lang)

    p = _build_vow_params(vow_raw, vow_dict)
    context.user_data["sumpah_vow_num"]      = p["vow_num"]
    context.user_data["sumpah_vow_en"]       = p["en"]
    context.user_data["sumpah_vow_id"]       = p["id_"]
    context.user_data["sumpah_vow_nums_str"] = p["nums_str"]
    context.user_data["sumpah_vow_block"]    = p["vow_block"]
    context.user_data["sumpah_vow_jam"]      = jam
    context.user_data["sumpah_vow_label"]    = label
    context.user_data["sumpah_pair_next"]    = p["pair_next"]   # None for single vows
    context.user_data["sumpah_was_pair"]     = p["pair_next"] is not None

    await query.edit_message_reply_markup(reply_markup=None)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(T("sumpah_order_pos_label", lang), callback_data="sumpah_order_pos_first"),
        InlineKeyboardButton(T("sumpah_order_neg_label", lang), callback_data="sumpah_order_neg_first"),
    ]])
    if p["pair_next"]:
        prompt = T("sumpah_pilih_urutan_pair_intro", lang,
                   **_vow_ctx(context), first_num=p["nums_str"])
    else:
        prompt = T("sumpah_pilih_urutan", lang, **_vow_ctx(context))
    await query.message.reply_text(prompt, parse_mode="Markdown", reply_markup=kb)
    return PILIH_REFLEKSI


async def sumpah_urutan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose reflection order (positive-first or negative-first)."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    order = query.data.replace("sumpah_order_", "")  # "pos_first" or "neg_first"
    context.user_data["sumpah_order"] = order

    vow   = context.user_data.get("sumpah_vow_num", 0)
    en    = context.user_data.get("sumpah_vow_en", "")
    id_   = context.user_data.get("sumpah_vow_id", "")
    label = context.user_data.get("sumpah_vow_label", "")
    jam   = context.user_data.get("sumpah_vow_jam", "")

    # Narrow to single-vow display for Q1/Q2/Q3 (overview already showed both)
    context.user_data["sumpah_vow_nums_str"] = f"#{vow}"
    context.user_data["sumpah_vow_block"]    = f"🇬🇧 _{en}_\n\n🇮🇩 _{id_}_"

    await query.edit_message_reply_markup(reply_markup=None)
    if order == "neg_first":
        await query.message.reply_text(
            T("sumpah_refleksi_negatif_q1", lang, **_vow_ctx(context)),
            parse_mode="Markdown"
        )
        return SUMPAH_REFLEKSI_NEGATIF
    else:
        await query.message.reply_text(
            T("sumpah_refleksi_positif", lang, **_vow_ctx(context)),
            parse_mode="Markdown"
        )
        return SUMPAH_REFLEKSI_POSITIF


def _esc_md(text: str) -> str:
    """Escape Markdown v1 special characters in user-generated text."""
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


def _build_vow_params(vow_raw, vow_dict: dict) -> dict:
    """Return nums_str, vow_block, and optional pair_next for a single or pair vow."""
    if isinstance(vow_raw, list):
        nums_str = " & ".join(f"#{v}" for v in vow_raw)
        # Show each vow in full with a visual separator between them
        blocks = []
        for v in vow_raw:
            en_v, id_v = vow_dict.get(v, ("?", "?"))
            blocks.append(f"*#{v}*\n🇬🇧 _{en_v}_\n🇮🇩 _{id_v}_")
        vow_block = "\n\n— — —\n\n".join(blocks)
        # First vow is what we reflect on first
        vow_num = vow_raw[0]
        en, id_ = vow_dict.get(vow_num, ("?", "?"))
        # Build "next" params for the second vow (single-vow style)
        next_num = vow_raw[1]
        next_en, next_id = vow_dict.get(next_num, ("?", "?"))
        pair_next = {
            "vow_num":   next_num,
            "nums_str":  f"#{next_num}",
            "vow_block": f"🇬🇧 _{next_en}_\n\n🇮🇩 _{next_id}_",
            "en":        next_en,
            "id_":       next_id,
        }
    else:
        vow_num = vow_raw
        en, id_ = vow_dict.get(vow_num, ("?", "?"))
        nums_str = f"#{vow_num}"
        vow_block = f"🇬🇧 _{en}_\n\n🇮🇩 _{id_}_"
        pair_next = None
    return {"vow_num": vow_num, "nums_str": nums_str, "vow_block": vow_block,
            "en": en, "id_": id_, "pair_next": pair_next}


async def _maybe_transition_pair(message, context, lang: str, saved_vow: int, saved_nums: str) -> bool:
    """If a pair-next vow is pending, transition to it. Returns True if transitioning."""
    pair_next = context.user_data.pop("sumpah_pair_next", None)
    if not pair_next:
        return False
    # Brief save confirmation for first vow
    await message.reply_text(
        T("sumpah_pair_transisi", lang,
          saved_num=saved_nums, next_num=pair_next["nums_str"])
    )
    # Load second vow into context
    context.user_data["sumpah_vow_num"]      = pair_next["vow_num"]
    context.user_data["sumpah_vow_en"]       = pair_next["en"]
    context.user_data["sumpah_vow_id"]       = pair_next["id_"]
    context.user_data["sumpah_vow_nums_str"] = pair_next["nums_str"]
    context.user_data["sumpah_vow_block"]    = pair_next["vow_block"]
    # Clear previous answers and order choice
    for key in ["sumpah_positif", "sumpah_negatif", "sumpah_rencana", "sumpah_order"]:
        context.user_data.pop(key, None)
    # Show order choice for second vow
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(T("sumpah_order_pos_label", lang), callback_data="sumpah_order_pos_first"),
        InlineKeyboardButton(T("sumpah_order_neg_label", lang), callback_data="sumpah_order_neg_first"),
    ]])
    await message.reply_text(
        T("sumpah_pilih_urutan", lang, **_vow_ctx(context)),
        parse_mode="Markdown", reply_markup=kb
    )
    return True


def _vow_ctx(context) -> dict:
    """Read stored vow params from context for T() calls."""
    vow = context.user_data.get("sumpah_vow_num", 0)
    return {
        "vow": vow,
        "nums_str": context.user_data.get("sumpah_vow_nums_str", f"#{vow}"),
        "vow_block": context.user_data.get("sumpah_vow_block", ""),
        "label": context.user_data.get("sumpah_vow_label", ""),
        "jam": context.user_data.get("sumpah_vow_jam", ""),
        "en": context.user_data.get("sumpah_vow_en", ""),
        "id_": context.user_data.get("sumpah_vow_id", ""),
    }


async def terima_sumpah_positif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    order = context.user_data.get("sumpah_order", "pos_first")

    if order == "neg_first":
        # Positive is Q3 (final) — save everything now
        user_id = update.effective_user.id
        positif = update.message.text
        negatif = context.user_data.get("sumpah_negatif", "")
        rencana = context.user_data.get("sumpah_rencana", "")
        vow = context.user_data.get("sumpah_vow_num", 0)
        nums_str = context.user_data.get("sumpah_vow_nums_str", f"#{vow}")
        jam = context.user_data.get("sumpah_vow_jam", "")
        sesi = f"slot_{jam}_{vow}" if jam else _sesi_sekarang()
        await save_catatan(user_id, sesi, vow, positif, negatif, rencana)
        if await _maybe_transition_pair(update.message, context, lang, vow, nums_str):
            return PILIH_REFLEKSI
        await update.message.reply_text(
            T("sumpah_refleksi_konfirmasi", lang, vow=vow, nums_str=nums_str,
              positif=positif, negatif=negatif, rencana=rencana),
            parse_mode="Markdown"
        )
        for key in ["sumpah_positif","sumpah_negatif","sumpah_rencana","sumpah_vow_num",
                    "sumpah_vow_en","sumpah_vow_id","sumpah_vow_nums_str","sumpah_vow_block",
                    "sumpah_vow_jam","sumpah_vow_label","sumpah_order","sumpah_was_pair"]:
            context.user_data.pop(key, None)
        return ConversationHandler.END
    else:
        # Positive is Q1 — now ask Q2 (negative), show vow again
        context.user_data["sumpah_positif"] = update.message.text
        await update.message.reply_text(
            T("sumpah_refleksi_negatif", lang, **_vow_ctx(context)),
            parse_mode="Markdown"
        )
        return SUMPAH_REFLEKSI_NEGATIF


async def terima_sumpah_negatif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    negatif = update.message.text
    context.user_data["sumpah_negatif"] = negatif
    order = context.user_data.get("sumpah_order", "pos_first")
    vow = context.user_data.get("sumpah_vow_num", 0)
    en  = context.user_data.get("sumpah_vow_en", "")
    id_ = context.user_data.get("sumpah_vow_id", "")

    if order == "neg_first":
        # Negative was Q1 — now ask Q2 (plan/todo), show the negative
        await update.message.reply_text(
            T("sumpah_refleksi_rencana_q2", lang, negatif=_esc_md(negatif)),
            parse_mode="Markdown"
        )
        return SUMPAH_REFLEKSI_RENCANA
    else:
        # Negative was Q2 — now ask Q3 (plan), show the negative
        await update.message.reply_text(
            T("sumpah_refleksi_rencana", lang, negatif=_esc_md(negatif)),
            parse_mode="Markdown"
        )
        return SUMPAH_REFLEKSI_RENCANA


async def terima_sumpah_rencana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    rencana = update.message.text
    order = context.user_data.get("sumpah_order", "pos_first")

    if order == "neg_first":
        # Plan was Q2 — save rencana to context, now ask Q3 (positive), show vow
        context.user_data["sumpah_rencana"] = rencana
        await update.message.reply_text(
            T("sumpah_refleksi_positif_q3", lang, **_vow_ctx(context)),
            parse_mode="Markdown"
        )
        return SUMPAH_REFLEKSI_POSITIF

    # pos_first: plan was Q3 — save everything now
    vow = context.user_data.get("sumpah_vow_num", 0)
    nums_str = context.user_data.get("sumpah_vow_nums_str", f"#{vow}")
    positif = context.user_data.get("sumpah_positif", "")
    negatif = context.user_data.get("sumpah_negatif", "")
    jam = context.user_data.get("sumpah_vow_jam", "")
    sesi = f"slot_{jam}_{vow}" if jam else _sesi_sekarang()
    await save_catatan(user_id, sesi, vow, positif, negatif, rencana)
    if await _maybe_transition_pair(update.message, context, lang, vow, nums_str):
        return PILIH_REFLEKSI
    await update.message.reply_text(
        T("sumpah_refleksi_konfirmasi", lang, vow=vow, nums_str=nums_str,
          positif=positif, negatif=negatif, rencana=rencana),
        parse_mode="Markdown"
    )
    for key in ["sumpah_positif","sumpah_negatif","sumpah_rencana","sumpah_vow_num",
                "sumpah_vow_en","sumpah_vow_id","sumpah_vow_nums_str","sumpah_vow_block",
                "sumpah_vow_jam","sumpah_vow_label","sumpah_order","sumpah_was_pair"]:
        context.user_data.pop(key, None)
    return ConversationHandler.END


def _format_vow_pair_for_reflect(vow_list: list, vow_dict: dict, label: str, jam: str, lang: str) -> str:
    lines = [f"📿 *{label}*\n*{jam}*\n"]
    for v in vow_list:
        en, id_ = vow_dict.get(v, ("?", "?"))
        lines.append(f"*Vow #{v}*")
        lines.append(f"🇬🇧 _{en}_")
        lines.append(f"🇮🇩 _{id_}_\n")
    lines.append("─────────────────────")
    lines.append(f"_{T('sumpah_renungan', lang)}_")
    return "\n".join(lines)


async def _tampilkan_pilihan_refleksi_mahir(message, context, lang: str, db_user: dict):
    """Mahir /refleksi: show 6 slots with ✅/○ status and virtue name."""
    user_id = message.chat.id
    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus or len(fokus) < 6:
        await message.reply_text(T("kebajikan_belum_ada", lang))
        return ConversationHandler.END

    custom = db_user.get("vow_times", "")
    times = custom.split() if custom else list(VOW_JAM_DEFAULTS)

    catatan = await get_catatan_hari_ini(user_id)
    filled_sesi = {c["sesi"] for c in catatan}

    rows = []
    for i in range(6):
        sesi_key = f"refleksi_{i + 1}"
        is_filled = sesi_key in filled_sesi
        k_id = fokus[i] if i < len(fokus) else None
        k = KEBAJIKAN.get(k_id, {}) if k_id else {}
        slot_time = times[i] if i < len(times) else "—"
        status = "✅" if is_filled else "○"
        rows.append([InlineKeyboardButton(
            f"{status} {slot_time} — {k.get('emoji', '')}{k.get('nama', '?')}",
            callback_data=f"refleksi_mahir_{i}"
        )])

    await message.reply_text(
        T("refleksi_pilih_slot_mahir", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return PILIH_REFLEKSI


async def pilih_slot_mahir_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose a mahir refleksi slot — start reflection directly."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    user_id = query.from_user.id
    slot_idx = int(query.data.replace("refleksi_mahir_", ""))

    db_user = await get_user(user_id)
    if not db_user:
        return ConversationHandler.END
    fokus = db_user.get("kebajikan_fokus", [])
    k_id = fokus[slot_idx % len(fokus)]
    sesi = f"refleksi_{slot_idx + 1}"

    await set_pending(user_id, sesi, k_id)
    context.user_data["refleksi_k_id"] = k_id
    context.user_data["refleksi_sesi"]  = sesi
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "positif", lang),
        parse_mode="Markdown"
    )
    return REFLEKSI_POSITIF


async def _tampilkan_pilihan_refleksi(message, context, lang: str, fokus: list, filled: set):
    """Show inline keyboard of kebajikan with fill status."""
    sesi_list = ["pagi", "siang", "sore"]
    rows = []
    for k_id in fokus:
        k = KEBAJIKAN.get(k_id, {})
        if not k:
            continue
        # Count filled sesi for this kebajikan
        filled_count = sum(1 for s in sesi_list if (k_id, s) in filled)
        total = len(sesi_list)
        if filled_count == total:
            status = "✅"
        elif filled_count > 0:
            status = f"◐ {filled_count}/{total}"
        else:
            status = "○"
        rows.append([InlineKeyboardButton(
            f"{status} {k['emoji']} {k['nama']}",
            callback_data=f"refleksi_k_{k_id}"
        )])
    context.user_data["refleksi_filled"] = [(ki, s) for (ki, s) in filled]
    await message.reply_text(
        T("refleksi_pilih_kebajikan", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return PILIH_REFLEKSI


async def pilih_kebajikan_refleksi_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose which kebajikan to reflect on."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    k_id = int(query.data.replace("refleksi_k_", ""))
    context.user_data["refleksi_k_id"] = k_id
    k = KEBAJIKAN.get(k_id, {})
    nama = k.get("nama", "") if k else ""

    filled = set(context.user_data.get("refleksi_filled", []))
    sesi_list = ["pagi", "siang", "sore"]
    sesi_short_keys = {"pagi": "sesi_pagi_short", "siang": "sesi_siang_short", "sore": "sesi_sore_short"}

    rows = []
    for s in sesi_list:
        is_filled = (k_id, s) in filled
        label_key = sesi_short_keys[s]
        label = T(label_key, lang)
        status = "✅ " if is_filled else "○ "
        rows.append([InlineKeyboardButton(
            f"{status}{label}",
            callback_data=f"refleksi_sesi_{s}"
        )])

    await query.edit_message_text(
        T("refleksi_pilih_sesi", lang, nama=nama),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return PILIH_SESI_REFLEKSI


async def pilih_sesi_refleksi_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose which session to fill."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    sesi = query.data.replace("refleksi_sesi_", "")
    k_id = context.user_data.get("refleksi_k_id")
    if not k_id:
        await query.message.reply_text(T("silakan_start", lang))
        return ConversationHandler.END
    user_id = query.from_user.id
    await set_pending(user_id, sesi, k_id)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "positif", lang),
        parse_mode="Markdown"
    )
    return REFLEKSI_POSITIF


async def terima_refleksi_positif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    # Prefer context.user_data (set by pilih_slot_mahir_cb / pilih_sesi_refleksi_cb)
    # so the scheduler's set_pending for the *next* slot can't clobber an active session.
    k_id = context.user_data.get("refleksi_k_id")
    sesi = context.user_data.get("refleksi_sesi")
    if not k_id or not sesi:
        pending = await get_pending(user_id)
        if not pending:
            return ConversationHandler.END
        k_id = pending["kebajikan_id"]
        sesi = pending["sesi"]
    await set_pending(user_id, sesi, k_id, step="negatif", temp_positif=update.message.text)
    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "negatif", lang), parse_mode="Markdown"
    )
    return REFLEKSI_NEGATIF


async def terima_refleksi_negatif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    # Same: prefer context.user_data to avoid cross-slot contamination.
    k_id = context.user_data.get("refleksi_k_id")
    sesi = context.user_data.get("refleksi_sesi")
    pending = await get_pending(user_id)
    if not pending:
        return ConversationHandler.END
    if not k_id or not sesi:
        k_id = pending["kebajikan_id"]
        sesi = pending["sesi"]
    await set_pending(user_id, sesi, k_id, step="rencana",
                      temp_positif=pending.get("temp_positif", ""),
                      temp_negatif=update.message.text)
    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "rencana", lang), parse_mode="Markdown"
    )
    return REFLEKSI_RENCANA


async def terima_refleksi_rencana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    pending = await get_pending(user_id)
    if not pending:
        return ConversationHandler.END
    positif = pending.get("temp_positif", "")
    negatif = pending.get("temp_negatif", "")
    rencana = update.message.text
    # Prefer context.user_data for k_id/sesi consistency with Q1/Q2.
    k_id = context.user_data.pop("refleksi_k_id", None) or pending["kebajikan_id"]
    sesi = context.user_data.pop("refleksi_sesi", None) or pending["sesi"]
    await save_catatan(user_id, sesi, k_id, positif, negatif, rencana)
    await clear_pending(user_id)
    await update.message.reply_text(
        format_konfirmasi_sesi(positif, negatif, rencana, k_id, lang), parse_mode="Markdown"
    )
    return ConversationHandler.END


# ─── /ganti / /change ────────────────────────────────────────────────────────

async def cmd_ganti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text(T("silakan_start", "id"))
        return ConversationHandler.END
    lang = db_user.get("bahasa", "id")
    context.user_data["lang"] = lang
    level = db_user.get("level", "pemula")
    context.user_data["level"] = level

    # Mahir: allow setting which rotation day (1–5)
    if level == "mahir":
        context.user_data["upgrade_target"] = "mahir"
        prompt = (
            "📅 *Ganti hari rotasi Mahir*\n\nKetik angka hari ke berapa (1–5):\n"
            "Hari 1 = kebajikan 1–6\nHari 2 = 7–10,1–2\nHari 3 = 3–8\nHari 4 = 9–10,1–4\nHari 5 = 5–10"
            if lang == "id" else
            "📅 *Set Mahir rotation day*\n\nType a day number (1–5):\n"
            "Day 1 = virtues 1–6\nDay 2 = 7–10,1–2\nDay 3 = 3–8\nDay 4 = 9–10,1–4\nDay 5 = 5–10"
        )
        await update.message.reply_text(prompt, parse_mode="Markdown")
        return PILIH_HARI_ROTASI

    # Advanced/Super: offer two options — by vow number or by day number
    if level in ("advanced", "super_advanced"):
        context.user_data["upgrade_target"] = level
        context.user_data["upgrade_max_vow"] = 147 if level == "advanced" else 265
        await update.message.reply_text(
            T("ganti_advanced_pilihan", lang),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(T("ganti_dari_sumpah_label", lang), callback_data="ganti_adv_sumpah")],
                [InlineKeyboardButton(T("ganti_dari_hari_label",   lang), callback_data="ganti_adv_hari")],
            ])
        )
        return PILIH_VOW_AWAL

    jumlah = LEVEL_CONFIG[level]["jumlah"]
    context.user_data["kebajikan_dipilih"] = []
    await update.message.reply_text(
        T("ganti_judul", lang, jumlah=jumlah), parse_mode="Markdown",
        reply_markup=kb_kebajikan_manual(level, [], lang)
    )
    return GANTI_PILIH


# ─── /kebajikan / /virtue ────────────────────────────────────────────────────

async def ganti_adv_pilihan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle choice between change-by-vow and change-by-day."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)

    if query.data == "ganti_adv_sumpah":
        target = context.user_data.get("upgrade_target", "advanced")
        key = "vow_awal_prompt_advanced" if target == "advanced" else "vow_awal_prompt_super"
        await query.edit_message_text(T(key, lang), parse_mode="Markdown")
        return PILIH_VOW_AWAL

    # change-by-day
    await query.edit_message_text(T("ganti_dari_hari_prompt", lang), parse_mode="Markdown")
    return PILIH_HARI_ROTASI


async def terima_hari_rotasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive day number directly and update join_date accordingly."""
    from data.vows import day_to_start_date, get_adv_vows_for_day, get_sa_vows_for_day
    from datetime import timedelta
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    target = context.user_data.get("upgrade_target", "advanced")

    # ── Mahir: day 1–5 cycle ──
    if target == "mahir":
        max_day = 5
        try:
            day_number = int(update.message.text.strip())
            if not 1 <= day_number <= max_day:
                raise ValueError
        except ValueError:
            err = f"Ketik angka 1–{max_day}." if lang == "id" else f"Type a number 1–{max_day}."
            await update.message.reply_text(err)
            return PILIH_HARI_ROTASI
        # join_date = today shifted back so that today is day_number
        join_date = date.today() - timedelta(days=day_number - 1)
        new_fokus = get_mahir_virtues_for_day(day_number)
        await update_user(user_id, join_date=join_date, kebajikan_fokus=new_fokus)
        k_names = ", ".join(
            f"{KEBAJIKAN.get(k, {}).get('emoji', '')} {KEBAJIKAN.get(k, {}).get('nama', '')}"
            for k in new_fokus
        )
        confirm = (
            f"✅ Hari ke-{day_number} disetel. Kebajikan hari ini:\n{k_names}"
            if lang == "id" else
            f"✅ Day {day_number} set. Today's virtues:\n{k_names}"
        )
        await update.message.reply_text(confirm, parse_mode="Markdown")
        context.user_data.pop("upgrade_target", None)
        return ConversationHandler.END

    max_day = 147 if target == "advanced" else 44

    try:
        day_number = int(update.message.text.strip())
        if not 1 <= day_number <= max_day:
            raise ValueError
    except ValueError:
        await update.message.reply_text(T("ganti_hari_invalid", lang, max_day=max_day))
        return PILIH_HARI_ROTASI

    join_date = day_to_start_date(day_number)
    await update_user(user_id, join_date=join_date)

    jadwal = _format_vow_schedule(target, day_number, lang)
    await update.message.reply_text(
        T("ganti_hari_konfirmasi", lang, day_number=day_number, jadwal=jadwal),
        parse_mode="Markdown"
    )
    context.user_data.pop("upgrade_target", None)
    context.user_data.pop("upgrade_max_vow", None)
    return ConversationHandler.END


async def cmd_kebajikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user or not db_user.get("onboarding_selesai"):
        await update.message.reply_text(T("silakan_start", "id"))
        return
    lang = db_user.get("bahasa", "id")
    level = db_user.get("level", "pemula")

    # Advanced/Super Advanced: show today's vow schedule
    if level in ("advanced", "super_advanced"):
        from data.vows import (get_adv_vows_for_day, get_sa_vows_for_day,
                               ADVANCED_VOWS, SUPER_ADVANCED_VOWS, ADV_TIMES, SA_TIMES)
        day_number = _day_number_for_user(db_user)
        times = ADV_TIMES if level == "advanced" else SA_TIMES
        vows = get_adv_vows_for_day(day_number) if level == "advanced" else get_sa_vows_for_day(day_number)
        vow_dict = ADVANCED_VOWS if level == "advanced" else SUPER_ADVANCED_VOWS
        label_key = "sumpah_label_advanced" if level == "advanced" else "sumpah_label_super"
        label = T(label_key, lang)
        sesi_word = "Jadwal Sumpah Hari Ini" if lang == "id" else "Today's Vow Schedule"
        lines = [f"📿 *{label}*\n_{sesi_word} (Day {day_number}):_\n"]
        for t, v in zip(times, vows):
            if isinstance(v, list):
                nums = " & ".join(f"#{n}" for n in v)
                lines.append(f"*{t}* — {nums}")
            else:
                en, id_ = vow_dict.get(v, ("?", "?"))
                text = id_ if lang == "id" else en
                short = text[:55] + "..." if len(text) > 55 else text
                lines.append(f"*{t}* — *#{v}* _{short}_")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    # Standard levels
    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        await update.message.reply_text(T("kebajikan_belum_ada", lang))
        return
    tujuan = db_user.get("tujuan_smart", "-") or "-"
    lines = [T("kebajikan_fokus_judul", lang, tujuan=tujuan[:100])]
    for i, k_id in enumerate(fokus):
        k = KEBAJIKAN.get(k_id, {})
        if k:
            label = T("kebajikan_utama_label", lang) if i == 0 else T("kebajikan_pendukung_label", lang)
            lines.append(f"{k['emoji']} *{k['nama']}* _{label}_")
            lines.append(f"_{k['pertanyaan_asosiasi']}_\n")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ─── /laporan / /report ──────────────────────────────────────────────────────

async def cmd_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)
    if not catatan and not tambahan:
        await update.message.reply_text(T("laporan_kosong", lang))
        return
    # Offer two view modes
    await update.message.reply_text(
        T("laporan_pilih_mode", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(T("laporan_mode_ringkas_label", lang), callback_data="laporan_ringkas")],
            [InlineKeyboardButton(T("laporan_mode_lengkap_label", lang), callback_data="laporan_lengkap")],
        ])
    )


async def laporan_mode_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await _lang(user_id, context)
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)
    db_user = await get_user(user_id)
    nama = db_user.get("username", "") if db_user else ""

    # Build vow-time map so legacy pagi/siang/sore entries show correct time
    from utils.messages import build_vow_time_map
    from datetime import date as dt_date
    vow_time_map = {}
    if db_user:
        level = db_user.get("level", "pemula")
        if level in ("advanced", "super_advanced"):
            join_date_raw = db_user.get("join_date")
            today = dt_date.today()
            jd = join_date_raw if (join_date_raw and isinstance(join_date_raw, dt_date)) else today
            day_number = (today - jd).days + 1
            vow_time_map = build_vow_time_map(level, day_number)

    await query.edit_message_reply_markup(reply_markup=None)

    if query.data == "laporan_ringkas":
        text = format_laporan_ringkas(catatan, tambahan, lang, vow_time_map=vow_time_map)
    else:
        text = format_laporan_lengkap(catatan, tambahan, lang, nama, vow_time_map=vow_time_map)

    await query.message.reply_text(text, parse_mode="Markdown")


# ─── /tambahan / /add ────────────────────────────────────────────────────────

async def cmd_tambahan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(
        format_pertanyaan_tambahan_malam(lang), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(T("tambahan_tidak_ada_label", lang), callback_data="tidak_ada_tambahan")
        ]])
    )
    return TAMBAHAN_MALAM_INPUT


async def mulai_tambahan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point when user taps '✏️ Tambah' button in the scheduled 20:00 message."""
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    await query.edit_message_text(
        format_pertanyaan_tambahan_malam(lang), parse_mode="Markdown"
    )
    return TAMBAHAN_MALAM_INPUT


async def terima_tambahan_malam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    await save_tambahan_malam(user_id, update.message.text)
    await update.message.reply_text(T("tambahan_tersimpan", lang))
    return ConversationHandler.END


async def tidak_ada_tambahan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    await query.edit_message_text(T("tambahan_selesai", lang))
    return ConversationHandler.END


# ─── /help ───────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(T("help", lang), parse_mode="Markdown")


# ─── /level ──────────────────────────────────────────────────────────────────

async def cmd_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text(T("silakan_start", "id"))
        return ConversationHandler.END
    lang = db_user.get("bahasa", "id")
    context.user_data["lang"] = lang
    current = db_user.get("level", "pemula")
    await update.message.reply_text(
        T("ubah_level_judul", lang, level=current), parse_mode="Markdown",
        reply_markup=kb_upgrade_level(lang)
    )
    return UPGRADE_PASSWORD


async def upgrade_level_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    target = query.data.replace("upgrade_", "")
    context.user_data["upgrade_target"] = target
    if target in ("pemula", "menengah", "mahir"):
        await _apply_level_upgrade(query, context, target)
        return ConversationHandler.END
    label_key = "level_advanced_label" if target == "advanced" else "level_super_label"
    await query.edit_message_text(
        T("password_prompt", lang, label=T(label_key, lang)), parse_mode="Markdown"
    )
    return UPGRADE_PASSWORD


async def terima_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    target = context.user_data.get("upgrade_target", "")
    entered = update.message.text.strip()
    env_key = "PASS_ADVANCED" if target == "advanced" else "PASS_SUPER"
    correct = os.environ.get(env_key, "")
    if not correct:
        await update.message.reply_text(T("password_belum_dikonfigurasi", lang))
        return ConversationHandler.END
    if entered != correct:
        await update.message.reply_text(T("password_salah", lang))
        context.user_data.clear()
        return ConversationHandler.END
    return await _tanya_vow_awal(update.message, context, target, lang)


async def _tanya_vow_awal(message, context, target, lang):
    key = "vow_awal_prompt_advanced" if target == "advanced" else "vow_awal_prompt_super"
    context.user_data["upgrade_max_vow"] = 147 if target == "advanced" else 265
    await message.reply_text(T(key, lang), parse_mode="Markdown")
    return PILIH_VOW_AWAL


def _format_vow_schedule(target: str, day_number: int, lang: str) -> str:
    from data.vows import (get_adv_vows_for_day, get_sa_vows_for_day,
                           ADVANCED_VOWS, SUPER_ADVANCED_VOWS, ADV_TIMES, SA_TIMES)
    times = ADV_TIMES if target == "advanced" else SA_TIMES
    vows = get_adv_vows_for_day(day_number) if target == "advanced" else get_sa_vows_for_day(day_number)
    vow_dict = ADVANCED_VOWS if target == "advanced" else SUPER_ADVANCED_VOWS
    lines = []
    for t, v in zip(times, vows):
        if isinstance(v, list):
            nums = " & ".join(f"#{n}" for n in v)
            lines.append(f"{t} — {nums}")
        else:
            en, id_ = vow_dict.get(v, ("?", "?"))
            text = id_ if lang == "id" else en
            short = text[:55] + "..." if len(text) > 55 else text
            lines.append(f"{t} — *#{v}* _{short}_")
    return "\n".join(lines)


async def _apply_level_upgrade_direct(user_id: int, context, target: str, join_date):
    update_kwargs = {"level": target}
    if target == "mahir":
        jd = join_date
        if jd:
            jd = jd.date() if hasattr(jd, "date") else jd
            day_num = (date.today() - jd).days + 1
        else:
            day_num = 1
        update_kwargs["kebajikan_fokus"] = get_mahir_virtues_for_day(day_num)
    elif target in ("advanced", "super_advanced"):
        update_kwargs["join_date"] = join_date if join_date else date.today()
        update_kwargs["kebajikan_fokus"] = list(range(1, 11))
    db_user = await get_user(user_id)
    if db_user and not db_user.get("onboarding_selesai"):
        update_kwargs["onboarding_selesai"] = 1
    await update_user(user_id, **update_kwargs)


async def terima_vow_awal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from data.vows import adv_vow_to_day, sa_vow_to_day, day_to_start_date
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    target = context.user_data.get("upgrade_target", "")
    max_vow = context.user_data.get("upgrade_max_vow", 0)

    logger.info(f"terima_vow_awal: user={user_id} target={target!r} max_vow={max_vow}")

    if not target or not max_vow:
        await update.message.reply_text(T("silakan_start", lang))
        return ConversationHandler.END

    try:
        vow_num = int(update.message.text.strip())
        if not 1 <= vow_num <= max_vow:
            raise ValueError
    except ValueError:
        await update.message.reply_text(T("vow_awal_invalid", lang, max_vow=max_vow))
        return PILIH_VOW_AWAL

    day_number = adv_vow_to_day(vow_num) if target == "advanced" else sa_vow_to_day(vow_num)
    join_date = day_to_start_date(day_number)
    context.user_data["upgrade_join_date"] = join_date
    context.user_data["upgrade_day_number"] = day_number

    # Apply upgrade immediately
    await _apply_level_upgrade_direct(user_id, context, target, join_date)

    label_key = "level_advanced_label" if target == "advanced" else "level_super_label"
    label = T(label_key, lang)
    jadwal = _format_vow_schedule(target, day_number, lang)

    await update.message.reply_text(
        T("vow_awal_konfirmasi", lang, label=label, vow_num=vow_num,
          day_number=day_number, jadwal=jadwal),
        parse_mode="Markdown",
        reply_markup=kb_vow_jam_konfirmasi(lang)
    )
    return PILIH_JAM_VOW


async def konfirmasi_vow_awal_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await _lang(user_id, context)
    if query.data == "atur_jam_vow":
        # Seed vow_times_new from saved values so skipped slots keep current time
        db_user = await get_user(user_id)
        saved = (db_user.get("vow_times") or "") if db_user else ""
        saved_list = saved.split() if saved else []
        current_vow_times = [
            saved_list[i] if i < len(saved_list) else VOW_JAM_DEFAULTS[i]
            for i in range(6)
        ]
        context.user_data["vow_times_new"] = current_vow_times
        return await _vow_jam_next_slot(query.message, context, lang, slot=0)
    return ConversationHandler.END


# ─── VOW TIME — SEQUENTIAL ───────────────────────────────────────────────────

async def _vow_jam_next_slot(message, context, lang: str, slot: int):
    context.user_data["vow_jam_slot"] = slot
    slot_names = T("vow_jam_slot_names", lang)
    if isinstance(slot_names, str):
        import json
        slot_names = json.loads(slot_names)
    vow_times = context.user_data.get("vow_times_new", list(VOW_JAM_DEFAULTS))
    current = vow_times[slot]
    await message.reply_text(
        T("vow_jam_prompt", lang, n=slot + 1, nama_slot=slot_names[slot], jam_sekarang=current),
        parse_mode="Markdown",
        reply_markup=kb_setjam_lewati(lang)
    )
    return PILIH_JAM_VOW


async def terima_jam_vow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    teks = update.message.text.strip()
    if not _valid_time(teks):
        await update.message.reply_text(T("vow_jam_invalid", lang))
        return PILIH_JAM_VOW
    slot = context.user_data.get("vow_jam_slot", 0)
    vow_times = context.user_data.get("vow_times_new", list(VOW_JAM_DEFAULTS))
    vow_times[slot] = teks
    context.user_data["vow_times_new"] = vow_times
    return await _vow_jam_advance(update.message, context, lang, slot)


async def lewati_vow_jam_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    slot = context.user_data.get("vow_jam_slot", 0)
    vow_times = context.user_data.get("vow_times_new", list(VOW_JAM_DEFAULTS))
    context.user_data["vow_times_new"] = vow_times  # keep default
    return await _vow_jam_advance(query.message, context, lang, slot)


async def _vow_jam_advance(message, context, lang: str, slot: int):
    slot += 1
    if slot < 6:
        return await _vow_jam_next_slot(message, context, lang, slot)
    # All 6 slots done — save
    vow_times = context.user_data.get("vow_times_new", VOW_JAM_DEFAULTS)
    await update_user(message.chat.id, vow_times=" ".join(vow_times))
    slot_names = T("vow_jam_slot_names", lang)
    if isinstance(slot_names, str):
        import json
        slot_names = json.loads(slot_names)
    ringkasan = "\n".join(f"  {slot_names[i]}: {vow_times[i]}" for i in range(6))
    await message.reply_text(
        T("vow_jam_selesai", lang, ringkasan=ringkasan), parse_mode="Markdown"
    )
    # If coming from mahir onboarding, send the onboarding completion message
    if context.user_data.pop("mahir_onboarding", False):
        dipilih = context.user_data.get("kebajikan_dipilih", list(range(1, 7)))
        tz = context.user_data.get("timezone", "Asia/Jakarta")
        nama = getattr(message.chat, "first_name", "") or ""
        await message.reply_text(
            format_onboarding_selesai(nama, dipilih, lang, tz), parse_mode="Markdown"
        )
    context.user_data.pop("vow_times_new", None)
    return ConversationHandler.END


# ─── /setvowtime / /setjamsumpah ─────────────────────────────────────────────

async def cmd_setvowtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Let Advanced/Super Advanced users reset their 6 vow slot times."""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text(T("silakan_start", "id"))
        return ConversationHandler.END
    lang = db_user.get("bahasa", "id")
    context.user_data["lang"] = lang
    level = db_user.get("level", "pemula")
    if level not in ("advanced", "super_advanced", "mahir"):
        await update.message.reply_text(
            T("setvowtime_only_advanced", lang), parse_mode="Markdown"
        )
        return ConversationHandler.END
    # Seed from current saved vow_times
    saved = (db_user.get("vow_times") or "")
    saved_list = saved.split() if saved else []
    current = [
        saved_list[i] if i < len(saved_list) else VOW_JAM_DEFAULTS[i]
        for i in range(6)
    ]
    context.user_data["vow_times_new"] = current
    return await _vow_jam_next_slot(update.message, context, lang, slot=0)


# ─── SETJAM SEQUENTIAL ───────────────────────────────────────────────────────

async def cmd_setjam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.get("bahasa", "id") if db_user else "id"
    context.user_data["lang"] = lang
    context.user_data["setjam_slot"] = 0
    # Seed from user's saved values so skipped slots keep their current time
    current_times = [
        (db_user.get(key) if db_user else None) or default
        for key, default in zip(SETJAM_DB_KEYS, SETJAM_DEFAULTS)
    ]
    context.user_data["setjam_new"] = current_times
    return await _setjam_next_slot(update.message, context, lang, 0, db_user)


async def _setjam_next_slot(message, context, lang: str, slot: int, db_user=None):
    context.user_data["setjam_slot"] = slot
    slot_names = T("setjam_slot_names", lang)
    if isinstance(slot_names, list):
        name = slot_names[slot]
    else:
        name = SETJAM_DB_KEYS[slot]
    current = (db_user.get(SETJAM_DB_KEYS[slot]) if db_user else None) or SETJAM_DEFAULTS[slot]
    await message.reply_text(
        T("setjam_slot_prompt", lang, n=slot + 1, nama_slot=name, jam_sekarang=current),
        parse_mode="Markdown",
        reply_markup=kb_setjam_lewati(lang)
    )
    return SETJAM_SEQUENTIAL


async def terima_setjam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    teks = update.message.text.strip()
    if not _valid_time(teks):
        await update.message.reply_text(T("setjam_format_salah", lang))
        return SETJAM_SEQUENTIAL
    slot = context.user_data.get("setjam_slot", 0)
    new_times = context.user_data.get("setjam_new", list(SETJAM_DEFAULTS))
    new_times[slot] = teks
    context.user_data["setjam_new"] = new_times
    return await _setjam_advance(update.message, context, lang, slot)


async def lewati_setjam_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)
    slot = context.user_data.get("setjam_slot", 0)
    return await _setjam_advance(query.message, context, lang, slot)


async def _setjam_advance(message, context, lang: str, slot: int):
    slot += 1
    if slot < 7:
        db_user = None  # don't re-fetch, keep defaults for remaining
        return await _setjam_next_slot(message, context, lang, slot, db_user)
    # All 7 done — save
    user_id = message.chat.id
    new_times = context.user_data.get("setjam_new", SETJAM_DEFAULTS)
    save_kwargs = {SETJAM_DB_KEYS[i]: new_times[i] for i in range(7)}
    await update_user(user_id, **save_kwargs)
    slot_names = T("setjam_slot_names", lang)
    if not isinstance(slot_names, list):
        slot_names = SETJAM_DB_KEYS
    ringkasan = "\n".join(f"  {slot_names[i]}: {new_times[i]}" for i in range(7))
    await message.reply_text(
        T("setjam_selesai", lang, ringkasan=ringkasan), parse_mode="Markdown"
    )
    context.user_data.pop("setjam_new", None)
    return ConversationHandler.END


# ─── 06:00 CALLBACK ──────────────────────────────────────────────────────────

async def callback_pagi_ganti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = await get_user(user_id)
    lang = db_user.get("bahasa", "id") if db_user else "id"
    if query.data == "pagi_ganti_ya":
        await query.edit_message_text(
            T("pagi_ganti_instruksi", lang), parse_mode="Markdown"
        )
    else:
        fokus = db_user.get("kebajikan_fokus", []) if db_user else []
        await query.edit_message_text(
            format_pagi_lanjut_konfirmasi(fokus, lang), parse_mode="Markdown"
        )


# ─── /level UPGRADE APPLY ────────────────────────────────────────────────────

async def _apply_level_upgrade(source, context, target, join_date=None):
    user_id = source.from_user.id
    lang = await _lang(user_id, context)
    update_kwargs = {"level": target}
    if target == "mahir":
        db_user_pre = await get_user(user_id)
        jd = (db_user_pre or {}).get("join_date")
        if jd:
            jd = jd.date() if hasattr(jd, "date") else jd
            day_num = (date.today() - jd).days + 1
        else:
            # No prior join_date — start from Day 1 and save today as join_date
            jd = date.today()
            day_num = 1
            update_kwargs["join_date"] = jd
        update_kwargs["kebajikan_fokus"] = get_mahir_virtues_for_day(day_num)
    elif target in ("advanced", "super_advanced"):
        update_kwargs["join_date"] = join_date if join_date else date.today()
        update_kwargs["kebajikan_fokus"] = list(range(1, 11))
    db_user = await get_user(user_id)
    if db_user and not db_user.get("onboarding_selesai"):
        update_kwargs["onboarding_selesai"] = 1
    await update_user(user_id, **update_kwargs)
    label_map = {
        "pemula":         T("level_pemula_label",   lang),
        "menengah":       T("level_menengah_label", lang),
        "mahir":          T("level_mahir_label",    lang),
        "advanced":       T("level_advanced_label", lang),
        "super_advanced": T("level_super_label",    lang),
    }
    label = label_map.get(target, target)
    if target == "advanced":
        text = T("upgrade_berhasil_advanced", lang, label=label)
    elif target == "super_advanced":
        text = T("upgrade_berhasil_super", lang, label=label)
    else:
        text = T("upgrade_berhasil_standar", lang, label=label)
    try:
        if hasattr(source, "edit_message_text"):
            await source.edit_message_text(text, parse_mode="Markdown")
        else:
            await source.reply_text(text, parse_mode="Markdown")
    except Exception:
        await source.message.reply_text(text, parse_mode="Markdown")
    context.user_data.clear()


# ─── CONVERSATION HANDLER ────────────────────────────────────────────────────

def build_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start",    start),
            CommandHandler("refleksi", cmd_refleksi),
            CommandHandler("reflect",  cmd_refleksi),
            CallbackQueryHandler(reflect_vow_from_scheduler_cb, pattern="^reflect_vow_"),
            CallbackQueryHandler(rewrite_vow_cb, pattern="^rewrite_vow_"),
            CommandHandler("ganti",    cmd_ganti),
            CommandHandler("change",   cmd_ganti),
            CommandHandler("tambahan", cmd_tambahan),
            CommandHandler("add",      cmd_tambahan),
            CallbackQueryHandler(mulai_tambahan_cb, pattern="^mulai_tambahan$"),
            CommandHandler("level",    cmd_level),
            CommandHandler("language", cmd_language),
            CommandHandler("setjam",        cmd_setjam),
            CommandHandler("settime",       cmd_setjam),
            CommandHandler("setvowtime",    cmd_setvowtime),
            CommandHandler("setjamsumpah",  cmd_setvowtime),
        ],
        states={
            PILIH_BAHASA: [
                CallbackQueryHandler(pilih_bahasa_cb, pattern="^lang_"),
                CallbackQueryHandler(ganti_bahasa_cb, pattern="^lang_"),
            ],
            PILIH_TIMEZONE: [
                CallbackQueryHandler(pilih_timezone_cb, pattern="^tz_"),
            ],
            PILIH_LEVEL: [
                CallbackQueryHandler(pilih_level_cb, pattern="^level_"),
            ],
            ONBOARDING_GOAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_goal)
            ],
            ONBOARDING_GOAL_REVISI: [
                CallbackQueryHandler(goal_lanjut_cb,  pattern="^goal_lanjut$"),
                CallbackQueryHandler(goal_revisi_cb,  pattern="^goal_revisi$"),
            ],
            ONBOARDING_KONFIRMASI_KEBAJIKAN: [
                CallbackQueryHandler(kebajikan_setuju_cb,  pattern="^kebajikan_setuju$"),
                CallbackQueryHandler(kebajikan_sendiri_cb, pattern="^kebajikan_sendiri$"),
            ],
            GANTI_PILIH: [
                CallbackQueryHandler(pilih_kebajikan_cb, pattern="^pilih_k_|^selesai_pilih$"),
            ],
            REFLEKSI_POSITIF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_refleksi_positif)
            ],
            REFLEKSI_NEGATIF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_refleksi_negatif)
            ],
            REFLEKSI_RENCANA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_refleksi_rencana)
            ],
            TAMBAHAN_MALAM_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_tambahan_malam),
                CallbackQueryHandler(tidak_ada_tambahan_cb, pattern="^tidak_ada_tambahan$"),
                CallbackQueryHandler(mulai_tambahan_cb,    pattern="^mulai_tambahan$"),
            ],
            UPGRADE_PASSWORD: [
                CallbackQueryHandler(upgrade_level_cb, pattern="^upgrade_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_password),
            ],
            PILIH_VOW_AWAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_vow_awal),
                CallbackQueryHandler(ganti_adv_pilihan_cb, pattern="^ganti_adv_"),
            ],
            PILIH_HARI_ROTASI: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_hari_rotasi),
            ],
            PILIH_JAM_VOW: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_jam_vow),
                CallbackQueryHandler(konfirmasi_vow_awal_cb, pattern="^atur_jam_vow$"),
                CallbackQueryHandler(lewati_vow_jam_cb,       pattern="^setjam_lewati$"),
            ],
            SETJAM_SEQUENTIAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_setjam),
                CallbackQueryHandler(lewati_setjam_cb, pattern="^setjam_lewati$"),
            ],
            PILIH_REFLEKSI: [
                CallbackQueryHandler(pilih_kebajikan_refleksi_cb, pattern="^refleksi_k_"),
                CallbackQueryHandler(pilih_slot_mahir_cb,         pattern="^refleksi_mahir_"),
                CallbackQueryHandler(pilih_sumpah_slot_cb,        pattern="^sumpah_slot_"),
                CallbackQueryHandler(sumpah_urutan_cb,            pattern="^sumpah_order_"),
            ],
            PILIH_SESI_REFLEKSI: [
                CallbackQueryHandler(pilih_sesi_refleksi_cb, pattern="^refleksi_sesi_"),
            ],
            SUMPAH_REFLEKSI_POSITIF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_sumpah_positif),
            ],
            SUMPAH_REFLEKSI_NEGATIF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_sumpah_negatif),
            ],
            SUMPAH_REFLEKSI_RENCANA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_sumpah_rencana),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
        per_message=False,
        per_chat=True,
    )
