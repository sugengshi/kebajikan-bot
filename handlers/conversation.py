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
    format_sambutan, format_sambutan_kembali, format_pilih_level,
    format_tujuan_smart, format_smart_revisi, format_onboarding_selesai,
    format_rekomendasi
)
from utils.i18n import T
from utils.smart_evaluator import evaluasi_smart, rekomendasikan_kebajikan
from data.kebajikan import KEBAJIKAN, LEVEL_CONFIG

logger = logging.getLogger(__name__)

# ─── STATES ──────────────────────────────────────────────────────────────────
(
    PILIH_BAHASA,
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
) = range(12)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _sesi_sekarang() -> str:
    import pytz
    from datetime import datetime
    jam = datetime.now(pytz.timezone("Asia/Jakarta")).hour
    if jam < 12:
        return "pagi"
    elif jam < 17:
        return "siang"
    else:
        return "sore"


async def _lang(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get user language from context cache or DB."""
    if "lang" in context.user_data:
        return context.user_data["lang"]
    lang = await get_user_lang(user_id)
    context.user_data["lang"] = lang
    return lang


# ─── KEYBOARDS ───────────────────────────────────────────────────────────────

def kb_bahasa():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="lang_id")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ])


def kb_level(lang: str = "id"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T("level_pemula_label", lang),   callback_data="level_pemula")],
        [InlineKeyboardButton(T("level_menengah_label", lang), callback_data="level_menengah")],
        [InlineKeyboardButton(T("level_mahir_label", lang),    callback_data="level_mahir")],
        [InlineKeyboardButton(T("level_advanced_label", lang), callback_data="level_advanced")],
        [InlineKeyboardButton(T("level_super_label", lang),    callback_data="level_super_advanced")],
    ])


def kb_smart(lang: str = "id"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(T("smart_lanjut_label", lang),  callback_data="goal_lanjut"),
            InlineKeyboardButton(T("smart_revisi_label", lang),  callback_data="goal_revisi"),
        ]
    ])


def kb_kebajikan_konfirmasi(lang: str = "id"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(T("setuju_label", lang),        callback_data="kebajikan_setuju"),
            InlineKeyboardButton(T("pilih_sendiri_label", lang), callback_data="kebajikan_sendiri"),
        ]
    ])


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
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(T("pagi_ganti_ya_label", lang),    callback_data="pagi_ganti_ya"),
            InlineKeyboardButton(T("pagi_ganti_tidak_label", lang), callback_data="pagi_ganti_tidak"),
        ]
    ])


def kb_upgrade_level(lang: str = "id"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T("level_pemula_label", lang),   callback_data="upgrade_pemula")],
        [InlineKeyboardButton(T("level_menengah_label", lang), callback_data="upgrade_menengah")],
        [InlineKeyboardButton(T("level_mahir_label", lang),    callback_data="upgrade_mahir")],
        [InlineKeyboardButton(T("level_advanced_label", lang), callback_data="upgrade_advanced")],
        [InlineKeyboardButton(T("level_super_label", lang),    callback_data="upgrade_super_advanced")],
    ])


def kb_vow_awal_konfirmasi(lang: str = "id"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(T("vow_konfirmasi_ya", lang),   callback_data="konfirmasi_vow_awal"),
            InlineKeyboardButton(T("vow_konfirmasi_ubah", lang), callback_data="ubah_vow_awal"),
        ]
    ])


# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_user(user.id, user.username or user.first_name)
    db_user = await get_user(user.id)

    if db_user and db_user.get("onboarding_selesai"):
        lang = db_user.get("bahasa", "id")
        context.user_data["lang"] = lang
        await update.message.reply_text(
            format_sambutan_kembali(user.first_name, lang),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        T("pilih_bahasa", "id"),
        parse_mode="Markdown",
        reply_markup=kb_bahasa()
    )
    return PILIH_BAHASA


# ─── PILIH BAHASA ────────────────────────────────────────────────────────────

async def pilih_bahasa_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await update_user(query.from_user.id, bahasa=lang)

    await query.edit_message_text(T("bahasa_dipilih", lang), parse_mode="Markdown")
    await query.message.reply_text(
        format_sambutan(lang),
        parse_mode="Markdown",
        reply_markup=kb_level(lang)
    )
    return PILIH_LEVEL


# ─── /language ───────────────────────────────────────────────────────────────

async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(
        T("language_prompt", lang),
        parse_mode="Markdown",
        reply_markup=kb_bahasa()
    )
    return PILIH_BAHASA


async def ganti_bahasa_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language change from /language command."""
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await update_user(query.from_user.id, bahasa=lang)
    await query.edit_message_text(T("language_changed", lang), parse_mode="Markdown")
    return ConversationHandler.END


# ─── PILIH LEVEL ─────────────────────────────────────────────────────────────

async def pilih_level_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    level = query.data.replace("level_", "")
    context.user_data["level"] = level
    lang = await _lang(query.from_user.id, context)
    cfg = LEVEL_CONFIG.get(level, {})
    label = T(f"level_{level}_label", lang) if f"level_{level}_label" in __import__("utils.i18n", fromlist=["STRINGS"]).STRINGS else cfg.get("label", level)

    await query.edit_message_text(
        T("level_dipilih", lang, label=label, desc=cfg.get("deskripsi", "")),
        parse_mode="Markdown"
    )
    await query.message.reply_text(format_tujuan_smart(lang), parse_mode="Markdown")
    return ONBOARDING_GOAL


# ─── SMART GOAL ──────────────────────────────────────────────────────────────

async def terima_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    teks_goal = update.message.text
    context.user_data["goal"] = teks_goal
    hasil = evaluasi_smart(teks_goal)
    await update.message.reply_text(
        hasil["feedback"],
        parse_mode="Markdown",
        reply_markup=kb_smart(lang)
    )
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
    cfg = LEVEL_CONFIG.get(level, {})

    if level == "pemula":
        dipilih = [rekomendasi["utama"]]
    else:
        dipilih = rekomendasi["semua"]

    context.user_data["kebajikan_dipilih"] = dipilih

    await message.reply_text(
        format_rekomendasi(level, rekomendasi["alasan"], rekomendasi["alasan"], lang),
        parse_mode="Markdown",
        reply_markup=kb_kebajikan_konfirmasi(lang)
    )
    return ONBOARDING_KONFIRMASI_KEBAJIKAN


# ─── KONFIRMASI KEBAJIKAN ────────────────────────────────────────────────────

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
        T("ganti_judul", lang, jumlah=jumlah),
        parse_mode="Markdown",
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
            await query.answer("Pilih minimal 1!", show_alert=True)
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

    if level == "mahir":
        dipilih = list(range(1, 11))

    await update_user(user_id, level=level, kebajikan_fokus=dipilih, tujuan_smart=goal, onboarding_selesai=1)

    nama = query.from_user.first_name
    await query.message.reply_text(
        format_onboarding_selesai(nama, dipilih, lang),
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─── /refleksi ───────────────────────────────────────────────────────────────

async def cmd_refleksi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    lang = db_user.get("bahasa", "id") if db_user else "id"
    context.user_data["lang"] = lang

    if not db_user or not db_user.get("onboarding_selesai"):
        await update.message.reply_text("Silakan mulai dengan /start.")
        return ConversationHandler.END

    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        await update.message.reply_text(T("kebajikan_belum_ada", lang))
        return ConversationHandler.END

    k_id = fokus[0]
    sesi = _sesi_sekarang()
    await set_pending(user_id, sesi, k_id)
    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "positif", lang),
        parse_mode="Markdown"
    )
    return REFLEKSI_POSITIF


async def terima_refleksi_positif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    pending = await get_pending(user_id)
    if not pending:
        return ConversationHandler.END

    k_id = pending["kebajikan_id"]
    sesi = pending["sesi"]
    await set_pending(user_id, sesi, k_id, step="negatif", temp_positif=update.message.text)
    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "negatif", lang),
        parse_mode="Markdown"
    )
    return REFLEKSI_NEGATIF


async def terima_refleksi_negatif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    pending = await get_pending(user_id)
    if not pending:
        return ConversationHandler.END

    k_id = pending["kebajikan_id"]
    sesi = pending["sesi"]
    await set_pending(user_id, sesi, k_id, step="rencana",
                      temp_positif=pending.get("temp_positif", ""),
                      temp_negatif=update.message.text)
    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "rencana", lang),
        parse_mode="Markdown"
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
    k_id = pending["kebajikan_id"]
    sesi = pending["sesi"]

    await save_catatan(user_id, sesi, k_id, positif, negatif, rencana)
    await clear_pending(user_id)
    await update.message.reply_text(
        format_konfirmasi_sesi(positif, negatif, rencana, k_id, lang),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ─── /ganti ──────────────────────────────────────────────────────────────────

async def cmd_ganti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text("Silakan mulai dengan /start.")
        return ConversationHandler.END

    lang = db_user.get("bahasa", "id")
    context.user_data["lang"] = lang
    level = db_user.get("level", "pemula")
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    context.user_data["level"] = level
    context.user_data["kebajikan_dipilih"] = []

    await update.message.reply_text(
        T("ganti_judul", lang, jumlah=jumlah),
        parse_mode="Markdown",
        reply_markup=kb_kebajikan_manual(level, [], lang)
    )
    return GANTI_PILIH


# ─── /kebajikan ──────────────────────────────────────────────────────────────

async def cmd_kebajikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user or not db_user.get("onboarding_selesai"):
        await update.message.reply_text("Silakan mulai dengan /start.")
        return

    lang = db_user.get("bahasa", "id")
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


# ─── /laporan ────────────────────────────────────────────────────────────────

async def cmd_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)

    if not catatan and not tambahan:
        await update.message.reply_text(T("laporan_kosong", lang))
        return

    await update.message.reply_text(
        format_ringkasan_positif(catatan, tambahan, lang),
        parse_mode="Markdown"
    )


# ─── /tambahan ───────────────────────────────────────────────────────────────

async def cmd_tambahan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(
        format_pertanyaan_tambahan_malam(lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(T("tambahan_tidak_ada_label", lang), callback_data="tidak_ada_tambahan")]
        ])
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


# ─── /bantuan ────────────────────────────────────────────────────────────────

async def cmd_bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(T("bantuan", lang), parse_mode="Markdown")


# ─── /level ──────────────────────────────────────────────────────────────────

async def cmd_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text("Silakan mulai dengan /start.")
        return ConversationHandler.END

    lang = db_user.get("bahasa", "id")
    context.user_data["lang"] = lang
    current = db_user.get("level", "pemula")
    await update.message.reply_text(
        T("ubah_level_judul", lang, level=current),
        parse_mode="Markdown",
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
    label = T(label_key, lang)
    await query.edit_message_text(
        T("password_prompt", lang, label=label),
        parse_mode="Markdown"
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


async def terima_vow_awal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from data.vows import adv_vow_to_day, sa_vow_to_day, day_to_start_date
    user_id = update.effective_user.id
    lang = await _lang(user_id, context)
    target = context.user_data.get("upgrade_target", "")
    max_vow = context.user_data.get("upgrade_max_vow", 0)

    logger.info(f"terima_vow_awal: user={user_id} target={target!r} max_vow={max_vow} text={update.message.text!r}")

    # Guard: if target/max_vow missing, the state was entered incorrectly
    if not target or not max_vow:
        await update.message.reply_text(
            "⚠️ Sesi tidak ditemukan. Gunakan /level untuk memulai ulang." if lang == "id"
            else "⚠️ Session not found. Use /level to start over."
        )
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
    context.user_data["upgrade_start_vow"] = vow_num
    context.user_data["upgrade_day_number"] = day_number

    label_key = "level_advanced_label" if target == "advanced" else "level_super_label"
    label = T(label_key, lang)

    await update.message.reply_text(
        T("vow_awal_konfirmasi", lang, label=label, vow_num=vow_num, day_number=day_number),
        parse_mode="Markdown",
        reply_markup=kb_vow_awal_konfirmasi(lang)
    )
    return PILIH_VOW_AWAL


async def konfirmasi_vow_awal_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await _lang(query.from_user.id, context)

    if query.data == "ubah_vow_awal":
        await query.message.reply_text(T("vow_ubah_prompt", lang))
        return PILIH_VOW_AWAL

    join_date = context.user_data.get("upgrade_join_date")
    target = context.user_data.get("upgrade_target")
    await _apply_level_upgrade(query, context, target, join_date=join_date)
    return ConversationHandler.END


async def _apply_level_upgrade(source, context, target, join_date=None):
    user_id = source.from_user.id
    lang = await _lang(user_id, context)
    update_kwargs = {"level": target}

    if target in ("advanced", "super_advanced"):
        update_kwargs["join_date"] = join_date if join_date else date.today().isoformat()
        update_kwargs["kebajikan_fokus"] = list(range(1, 11))

    await update_user(user_id, **update_kwargs)

    label_map = {
        "pemula":         T("level_pemula_label", lang),
        "menengah":       T("level_menengah_label", lang),
        "mahir":          T("level_mahir_label", lang),
        "advanced":       T("level_advanced_label", lang),
        "super_advanced": T("level_super_label", lang),
    }
    label = label_map.get(target, target)

    if target == "advanced":
        text = T("upgrade_berhasil_advanced", lang, label=label)
    elif target == "super_advanced":
        text = T("upgrade_berhasil_super", lang, label=label)
    else:
        text = T("upgrade_berhasil_standar", lang, label=label)

    if hasattr(source, "edit_message_text"):
        await source.edit_message_text(text, parse_mode="Markdown")
    else:
        await source.reply_text(text, parse_mode="Markdown")

    context.user_data.clear()


# ─── 06:00 CALLBACK ──────────────────────────────────────────────────────────

async def callback_pagi_ganti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = await get_user(user_id)
    lang = db_user.get("bahasa", "id") if db_user else "id"

    if query.data == "pagi_ganti_ya":
        await query.edit_message_text(T("pagi_ganti_instruksi", lang), parse_mode="Markdown")
    else:
        fokus = db_user.get("kebajikan_fokus", []) if db_user else []
        from utils.messages import format_pagi_lanjut_konfirmasi
        await query.edit_message_text(
            format_pagi_lanjut_konfirmasi(fokus, lang),
            parse_mode="Markdown"
        )


# ─── /setjam ─────────────────────────────────────────────────────────────────

async def cmd_atur_jam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    await update.message.reply_text(T("setjam_bantuan", lang), parse_mode="Markdown")


async def cmd_setjam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await _lang(update.effective_user.id, context)
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("`/setjam pagi 07:30`", parse_mode="Markdown")
        return

    sesi_map = {"pagi":"jam_pagi","siang":"jam_siang","sore":"jam_sore","malam":"jam_malam","cofmed":"jam_cofmed"}
    sesi = args[0].lower()
    jam = args[1]

    if sesi not in sesi_map:
        await update.message.reply_text(f"Pilihan: pagi, siang, sore, malam, cofmed")
        return

    try:
        h, m = jam.split(":")
        assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except Exception:
        await update.message.reply_text(T("setjam_format_salah", lang))
        return

    await update_user(update.effective_user.id, **{sesi_map[sesi]: jam})
    await update.message.reply_text(T("setjam_berhasil", lang, sesi=sesi, jam=jam), parse_mode="Markdown")


# ─── CONVERSATION HANDLER ────────────────────────────────────────────────────

def build_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("refleksi", cmd_refleksi),
            CommandHandler("ganti", cmd_ganti),
            CommandHandler("tambahan", cmd_tambahan),
            CommandHandler("level", cmd_level),
            CommandHandler("language", cmd_language),
        ],
        states={
            PILIH_BAHASA: [
                CallbackQueryHandler(pilih_bahasa_cb, pattern="^lang_"),
                CallbackQueryHandler(ganti_bahasa_cb, pattern="^lang_"),
            ],
            PILIH_LEVEL: [
                CallbackQueryHandler(pilih_level_cb, pattern="^level_")
            ],
            ONBOARDING_GOAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_goal)
            ],
            ONBOARDING_GOAL_REVISI: [
                CallbackQueryHandler(goal_lanjut_cb, pattern="^goal_lanjut$"),
                CallbackQueryHandler(goal_revisi_cb, pattern="^goal_revisi$"),
            ],
            ONBOARDING_KONFIRMASI_KEBAJIKAN: [
                CallbackQueryHandler(kebajikan_setuju_cb, pattern="^kebajikan_setuju$"),
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
            ],
            UPGRADE_PASSWORD: [
                CallbackQueryHandler(upgrade_level_cb, pattern="^upgrade_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_password),
            ],
            PILIH_VOW_AWAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_vow_awal),
                CallbackQueryHandler(konfirmasi_vow_awal_cb, pattern="^konfirmasi_vow_awal$|^ubah_vow_awal$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
    )
