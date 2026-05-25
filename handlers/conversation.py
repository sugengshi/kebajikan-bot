# handlers/conversation.py
import logging
import os
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from utils.database import (
    get_user, create_user, update_user,
    save_catatan, get_catatan_hari_ini, save_tambahan_malam,
    get_tambahan_malam, set_pending, get_pending, clear_pending
)
from utils.messages import (
    format_pertanyaan_refleksi, format_konfirmasi_sesi,
    format_ringkasan_positif, format_pertanyaan_tambahan_malam
)
from utils.smart_evaluator import evaluasi_smart, rekomendasikan_kebajikan
from data.kebajikan import KEBAJIKAN, LEVEL_CONFIG

logger = logging.getLogger(__name__)

# ─── STATES ──────────────────────────────────────────────────────────────────
(
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
) = range(11)


# ─── KEYBOARDS ───────────────────────────────────────────────────────────────
def kb_level():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌱 Pemula", callback_data="level_pemula")],
        [InlineKeyboardButton("🌿 Praktisi Menengah", callback_data="level_menengah")],
        [InlineKeyboardButton("🌳 Praktisi Mahir", callback_data="level_mahir")],
    ])

def kb_lanjut_atau_revisi():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Lanjutkan", callback_data="goal_lanjut"),
            InlineKeyboardButton("✏️ Perbaiki Goal", callback_data="goal_revisi"),
        ]
    ])

def kb_konfirmasi_kebajikan():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Mulai dengan ini!", callback_data="kebajikan_setuju"),
            InlineKeyboardButton("🔄 Pilih sendiri", callback_data="kebajikan_sendiri"),
        ]
    ])

def kb_kebajikan_manual(level: str, dipilih: list = []):
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    rows = []
    for k_id, data in KEBAJIKAN.items():
        cek = "✅ " if k_id in dipilih else ""
        rows.append([InlineKeyboardButton(
            f"{cek}{data['emoji']} {k_id}. {data['nama']}",
            callback_data=f"pilih_k_{k_id}"
        )])
    if len(dipilih) >= jumlah:
        rows.append([InlineKeyboardButton("✅ Selesai", callback_data="selesai_pilih")])
    return InlineKeyboardMarkup(rows)


# ─── /start ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_user(user.id, user.username or user.first_name)
    db_user = await get_user(user.id)

    if db_user and db_user.get("onboarding_selesai"):
        await update.message.reply_text(
            f"🙏 Selamat datang kembali, *{user.first_name}*!\n\n"
            "Gunakan /kebajikan untuk melihat fokus hari ini, "
            "/refleksi untuk mengisi refleksi, atau /bantuan untuk daftar perintah.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🙏 *Selamat datang di Bot Kebajikan Harian*\n\n"
        "Bot ini memandu Anda memantau dan mengembangkan kebajikan setiap hari "
        "berdasarkan *10 Bibit Baik Utama*.\n\n"
        "Pertama, pilih level praktik Anda:",
        parse_mode="Markdown",
        reply_markup=kb_level()
    )
    return PILIH_LEVEL


# ─── PILIH LEVEL ─────────────────────────────────────────────────────────────
async def pilih_level_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    level = query.data.replace("level_", "")
    context.user_data["level"] = level
    cfg = LEVEL_CONFIG[level]

    await query.edit_message_text(
        f"👍 Level Anda: *{cfg['label']}*\n_{cfg['deskripsi']}_",
        parse_mode="Markdown"
    )
    await query.message.reply_text(
        "🎯 *Langkah 1 — Tujuan SMART Anda*\n\n"
        "Tuliskan satu tujuan yang ingin Anda capai melalui praktik kebajikan ini.\n\n"
        "Bot akan mengevaluasi apakah tujuan Anda memenuhi kriteria *SMART:*\n"
        "• *S*pesifik — jelas dan konkret\n"
        "• *M*easurable — bisa diukur\n"
        "• *A*chievable — bisa dicapai\n"
        "• *R*elevant — bermakna bagi Anda\n"
        "• *T*ime-bound — ada batas waktunya\n\n"
        "_Contoh: Dalam 30 hari ke depan, saya ingin lebih sabar berbicara "
        "dengan anak-anak saya — minimal tidak meninggikan nada suara saat "
        "menegur mereka._\n\n"
        "✏️ *Tuliskan tujuan Anda:*",
        parse_mode="Markdown"
    )
    return ONBOARDING_GOAL


# ─── TERIMA GOAL + EVALUASI SMART ────────────────────────────────────────────
async def terima_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks_goal = update.message.text
    context.user_data["goal"] = teks_goal

    # Evaluasi SMART
    hasil = evaluasi_smart(teks_goal)
    context.user_data["smart_hasil"] = hasil

    await update.message.reply_text(
        hasil["feedback"],
        parse_mode="Markdown",
        reply_markup=kb_lanjut_atau_revisi()
    )
    return ONBOARDING_GOAL_REVISI


async def goal_lanjut_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pengguna setuju lanjutkan — rekomendasikan kebajikan."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    return await _tampilkan_rekomendasi(query.message, context)


async def goal_revisi_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pengguna ingin memperbaiki goal."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        "✏️ *Tulis ulang tujuan SMART Anda:*\n\n"
        "_Ingat: sertakan siapa, apa, ukuran, relevansi, dan batas waktu._",
        parse_mode="Markdown"
    )
    return ONBOARDING_GOAL


async def _tampilkan_rekomendasi(message, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan rekomendasi kebajikan dari goal."""
    goal = context.user_data.get("goal", "")
    rekomendasi = rekomendasikan_kebajikan(goal)
    context.user_data["rekomendasi"] = rekomendasi

    level = context.user_data.get("level", "pemula")
    cfg = LEVEL_CONFIG[level]

    # Sesuaikan dengan level
    if level == "pemula":
        kebajikan_direkomendasikan = [rekomendasi["utama"]]
        teks_level = "Sebagai Pemula, bot merekomendasikan *1 kebajikan utama* untuk Anda fokusi:"
    elif level == "menengah":
        kebajikan_direkomendasikan = rekomendasi["semua"]  # utama + 2 pendukung
        teks_level = "Sebagai Praktisi Menengah, bot merekomendasikan *3 kebajikan* (1 utama + 2 pendukung):"
    else:
        kebajikan_direkomendasikan = rekomendasi["semua"]
        teks_level = "Sebagai Praktisi Mahir, Anda akan memantau semua 10 kebajikan. Ini *titik masuk* yang direkomendasikan:"

    context.user_data["kebajikan_dipilih"] = kebajikan_direkomendasikan

    await message.reply_text(
        f"🔍 *Berdasarkan tujuan Anda, bot menemukan kebajikan yang paling sesuai:*\n\n"
        f"{teks_level}\n\n"
        f"{rekomendasi['alasan']}\n"
        "─────────────────────\n"
        "Apakah Anda setuju dengan rekomendasi ini?",
        parse_mode="Markdown",
        reply_markup=kb_konfirmasi_kebajikan()
    )
    return ONBOARDING_KONFIRMASI_KEBAJIKAN


# ─── KONFIRMASI KEBAJIKAN ────────────────────────────────────────────────────
async def kebajikan_setuju_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    return await _simpan_dan_selesai(query, context)


async def kebajikan_sendiri_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pengguna ingin pilih kebajikan sendiri."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    level = context.user_data.get("level", "pemula")
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    context.user_data["kebajikan_dipilih"] = []

    await query.message.reply_text(
        f"Pilih *{jumlah} kebajikan* yang paling sesuai dengan tujuan Anda:",
        parse_mode="Markdown",
        reply_markup=kb_kebajikan_manual(level, [])
    )
    return GANTI_PILIH


async def pilih_kebajikan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "selesai_pilih":
        dipilih = context.user_data.get("kebajikan_dipilih", [])
        if not dipilih:
            await query.answer("Pilih minimal 1 kebajikan dulu!", show_alert=True)
            return GANTI_PILIH
        return await _simpan_dan_selesai(query, context)

    k_id = int(query.data.replace("pilih_k_", ""))
    level = context.user_data.get("level", "pemula")
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    dipilih = context.user_data.get("kebajikan_dipilih", [])

    if k_id in dipilih:
        dipilih.remove(k_id)
    elif len(dipilih) < jumlah:
        dipilih.append(k_id)
    else:
        await query.answer(
            f"Sudah memilih {jumlah} kebajikan. Batalkan salah satu dulu.",
            show_alert=True
        )
        return GANTI_PILIH

    context.user_data["kebajikan_dipilih"] = dipilih

    if len(dipilih) == jumlah:
        return await _simpan_dan_selesai(query, context)

    await query.edit_message_reply_markup(
        reply_markup=kb_kebajikan_manual(level, dipilih)
    )
    return GANTI_PILIH


async def _simpan_dan_selesai(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    level = context.user_data.get("level", "pemula")
    dipilih = context.user_data.get("kebajikan_dipilih", [])
    goal = context.user_data.get("goal", "")

    # Untuk level mahir, simpan semua 10 kebajikan
    if level == "mahir":
        dipilih = list(range(1, 11))

    await update_user(
        user_id,
        level=level,
        kebajikan_fokus=dipilih,
        tujuan_smart=goal,
        onboarding_selesai=1
    )

    lines = ["🎉 *Anda siap memulai perjalanan kebajikan!*\n"]
    lines.append("*Fokus kebajikan Anda:*")
    for k_id in dipilih:
        k = KEBAJIKAN.get(k_id, {})
        if k:
            lines.append(f"{k['emoji']} {k['nama']}")

    lines.append(
        "\n*Jadwal harian (WIB):*\n"
        "06:00 — Pilihan fokus hari ini\n"
        "07:00 — Refleksi pagi\n"
        "12:00 — Refleksi siang\n"
        "18:00 — Refleksi sore\n"
        "20:00 — Tambahan perbuatan baik\n"
        "21:00 — Ringkasan positif\n"
        "21:30 — Arsip pribadi\n\n"
        "Gunakan /setjam untuk melakukan pengaturan waktu notifikasi. 🙏"
    )

    await query.message.reply_text("\n".join(lines), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END


# ─── /refleksi ───────────────────────────────────────────────────────────────
async def cmd_refleksi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user or not db_user.get("onboarding_selesai"):
        await update.message.reply_text("Silakan mulai dengan /start terlebih dahulu.")
        return ConversationHandler.END

    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        await update.message.reply_text("Belum ada kebajikan fokus. Gunakan /ganti.")
        return ConversationHandler.END

    k_id = fokus[0]
    sesi = _sesi_sekarang()
    await set_pending(user_id, sesi, k_id)

    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "positif"),
        parse_mode="Markdown"
    )
    return REFLEKSI_POSITIF


async def terima_refleksi_positif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pending = await get_pending(user_id)
    if not pending:
        return ConversationHandler.END

    context.user_data["r_positif"] = update.message.text
    k_id = pending["kebajikan_id"]
    sesi = pending["sesi"]
    await set_pending(user_id, sesi, k_id, step="negatif", temp_positif=update.message.text)

    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "negatif"),
        parse_mode="Markdown"
    )
    return REFLEKSI_NEGATIF


async def terima_refleksi_negatif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pending = await get_pending(user_id)
    if not pending:
        return ConversationHandler.END

    k_id = pending["kebajikan_id"]
    sesi = pending["sesi"]
    await set_pending(
        user_id, sesi, k_id, step="rencana",
        temp_positif=pending.get("temp_positif", ""),
        temp_negatif=update.message.text
    )

    await update.message.reply_text(
        format_pertanyaan_refleksi(sesi, k_id, "rencana"),
        parse_mode="Markdown"
    )
    return REFLEKSI_RENCANA


async def terima_refleksi_rencana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
        format_konfirmasi_sesi(positif, negatif, rencana, k_id),
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

    level = db_user.get("level", "pemula")
    jumlah = LEVEL_CONFIG[level]["jumlah"]
    context.user_data["level"] = level
    context.user_data["kebajikan_dipilih"] = []

    await update.message.reply_text(
        f"🔄 *Ganti Fokus Kebajikan*\n\nPilih {jumlah} kebajikan baru:",
        parse_mode="Markdown",
        reply_markup=kb_kebajikan_manual(level, [])
    )
    return GANTI_PILIH


# ─── /kebajikan ──────────────────────────────────────────────────────────────
async def cmd_kebajikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user or not db_user.get("onboarding_selesai"):
        await update.message.reply_text("Silakan mulai dengan /start.")
        return

    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        await update.message.reply_text("Belum ada kebajikan fokus. Gunakan /ganti.")
        return

    lines = [
        f"🎯 *Fokus Kebajikan Anda*\n",
        f"_Tujuan: {db_user.get('tujuan_smart', '-')[:100]}_\n",
    ]
    for i, k_id in enumerate(fokus):
        k = KEBAJIKAN.get(k_id, {})
        if k:
            label = "Utama" if i == 0 else "Pendukung"
            lines.append(f"{k['emoji']} *{k['nama']}* _{label}_")
            lines.append(f"_{k['pertanyaan_asosiasi']}_\n")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ─── /laporan ────────────────────────────────────────────────────────────────
async def cmd_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)

    if not catatan and not tambahan:
        await update.message.reply_text(
            "📋 Belum ada catatan hari ini.\nGunakan /refleksi untuk mulai."
        )
        return

    await update.message.reply_text(
        format_ringkasan_positif(catatan, tambahan),
        parse_mode="Markdown"
    )


# ─── /tambahan ───────────────────────────────────────────────────────────────
async def cmd_tambahan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        format_pertanyaan_tambahan_malam(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Tidak ada tambahan", callback_data="tidak_ada_tambahan")]
        ])
    )
    return TAMBAHAN_MALAM_INPUT


async def terima_tambahan_malam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await save_tambahan_malam(user_id, update.message.text)
    await update.message.reply_text(
        "✨ Catatan tersimpan. Terima kasih! 🙏\n"
        "Ketuk /tambahan lagi jika ingin menambah."
    )
    return ConversationHandler.END


async def tidak_ada_tambahan_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Baik! Arsip akan dikirim pukul 21:30. 🙏")
    return ConversationHandler.END


# ─── /bantuan ────────────────────────────────────────────────────────────────
async def cmd_bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Daftar Perintah:*\n\n"
        "/start — Mulai atau restart\n"
        "/kebajikan — Fokus kebajikan hari ini\n"
        "/refleksi — Isi refleksi sekarang\n"
        "/ganti — Ganti fokus kebajikan\n"
        "/tambahan — Tambah perbuatan baik\n"
        "/laporan — Lihat ringkasan hari ini\n"
        "/setjam — Atur jam notifikasi\n"
        "/bantuan — Tampilkan menu ini",
        parse_mode="Markdown"
    )


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def _sesi_sekarang() -> str:
    from datetime import datetime
    import pytz
    jam = datetime.now(pytz.timezone("Asia/Jakarta")).hour
    if jam < 12:
        return "pagi"
    elif jam < 17:
        return "siang"
    else:
        return "sore"


# ─── LEVEL UPGRADE ───────────────────────────────────────────────────────────

async def cmd_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show level options and allow free upgrade to Menengah/Mahir, or password for Advanced/Super."""
    user_id = update.effective_user.id
    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text("Silakan mulai dengan /start.")
        return ConversationHandler.END

    current = db_user.get("level", "pemula")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌱 Pemula", callback_data="upgrade_pemula")],
        [InlineKeyboardButton("🌿 Praktisi Menengah", callback_data="upgrade_menengah")],
        [InlineKeyboardButton("🌳 Praktisi Mahir", callback_data="upgrade_mahir")],
        [InlineKeyboardButton("🪷 Advanced (Sumpah Bodhisattva)", callback_data="upgrade_advanced")],
        [InlineKeyboardButton("💎 Super Advanced (Sumpah Tantra)", callback_data="upgrade_super_advanced")],
    ])
    await update.message.reply_text(
        f"📊 *Ubah Level Praktik*\n\nLevel Anda saat ini: *{current}*\n\n"
        "Pilih level baru. Advanced dan Super Advanced memerlukan kata sandi.",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return UPGRADE_PASSWORD


async def upgrade_level_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    target = query.data.replace("upgrade_", "")
    context.user_data["upgrade_target"] = target

    # Free levels — no password needed
    if target in ("pemula", "menengah", "mahir"):
        await _apply_level_upgrade(query, context, target)
        return ConversationHandler.END

    # Password-protected levels
    label = "Advanced 🪷 (Sumpah Bodhisattva)" if target == "advanced" else "Super Advanced 💎 (Sumpah Tantra)"
    await query.edit_message_text(
        f"🔐 *{label}*\n\nMasukkan kata sandi untuk mengakses level ini:",
        parse_mode="Markdown"
    )
    return UPGRADE_PASSWORD


async def terima_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = context.user_data.get("upgrade_target", "")
    entered = update.message.text.strip()

    # Check password from environment variables
    env_key = "PASS_ADVANCED" if target == "advanced" else "PASS_SUPER"
    correct = os.environ.get(env_key, "")

    if not correct:
        await update.message.reply_text(
            "⚠️ Kata sandi belum dikonfigurasi. Hubungi administrator."
        )
        return ConversationHandler.END

    if entered != correct:
        await update.message.reply_text(
            "❌ Kata sandi salah. Gunakan /level untuk mencoba lagi."
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Correct password — ask for starting vow
    return await _tanya_vow_awal(update.message, context, target)


async def _tanya_vow_awal(message, context, target):
    """After correct password, ask which vow to start from."""
    if target == "advanced":
        max_vow = 147
        info = (
            "🪷 *Kata sandi diterima!*\n\n"
            "Dari sumpah nomor berapa Anda ingin memulai?\n\n"
            "_Ketik angka 1\u2013147. Contoh: ketik *32* untuk memulai dari hari ke-10 "
            "(di mana sumpah #32 muncul di slot pertama)._\n\n"
            "Atau ketik *1* untuk memulai dari awal."
        )
    else:
        max_vow = 265
        info = (
            "💎 *Kata sandi diterima!*\n\n"
            "Dari sumpah nomor berapa Anda ingin memulai?\n\n"
            "_Ketik angka 1\u2013265. Contoh: ketik *11* untuk memulai dari hari ke-11 "
            "(di mana sumpah #11 muncul di slot pertama)._\n\n"
            "Atau ketik *1* untuk memulai dari awal."
        )
    context.user_data["upgrade_target"] = target
    context.user_data["upgrade_max_vow"] = max_vow
    await message.reply_text(info, parse_mode="Markdown")
    return PILIH_VOW_AWAL


async def terima_vow_awal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive starting vow number and apply upgrade."""
    from data.vows import adv_vow_to_day, sa_vow_to_day, day_to_start_date
    target = context.user_data.get("upgrade_target", "advanced")
    max_vow = context.user_data.get("upgrade_max_vow", 147)

    try:
        vow_num = int(update.message.text.strip())
        if not 1 <= vow_num <= max_vow:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            f"⚠️ Masukkan angka antara 1 dan {max_vow}. Coba lagi:"
        )
        return PILIH_VOW_AWAL

    # Back-calculate day number and join_date
    if target == "advanced":
        day_number = adv_vow_to_day(vow_num)
    else:
        day_number = sa_vow_to_day(vow_num)

    join_date = day_to_start_date(day_number)
    context.user_data["upgrade_join_date"] = join_date
    context.user_data["upgrade_start_vow"] = vow_num
    context.user_data["upgrade_day_number"] = day_number

    label = "Advanced 🪷" if target == "advanced" else "Super Advanced 💎"
    await update.message.reply_text(
        f"✅ *Konfirmasi:*\n\n"
        f"Level: *{label}*\n"
        f"Mulai dari sumpah: *#{vow_num}*\n"
        f"(Hari ke-{day_number} dalam rotasi)\n\n"
        f"Apakah sudah benar?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Ya, mulai!", callback_data="konfirmasi_vow_awal"),
                InlineKeyboardButton("✏️ Ubah", callback_data="ubah_vow_awal"),
            ]
        ])
    )
    return PILIH_VOW_AWAL

    return PILIH_VOW_AWAL


async def konfirmasi_vow_awal_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "ubah_vow_awal":
        target = context.user_data.get("upgrade_target", "advanced")
        await query.message.reply_text("Ketik ulang nomor sumpah awal:")
        return PILIH_VOW_AWAL
    # Apply with custom join_date
    join_date = context.user_data.get("upgrade_join_date")
    target = context.user_data.get("upgrade_target")
    await _apply_level_upgrade(query, context, target, join_date=join_date)
    return ConversationHandler.END


async def _apply_level_upgrade(source, context, target, join_date=None):
    """Apply level change and set join_date for advanced levels."""
    from data.kebajikan import LEVEL_CONFIG
    cfg = LEVEL_CONFIG.get(target, {})

    user_id = source.from_user.id
    update_kwargs = {"level": target}

    if target in ("advanced", "super_advanced"):
        # Use provided join_date (from vow selection) or default to today (= day 1)
        update_kwargs["join_date"] = join_date if join_date else date.today().isoformat()
        # All 10 kebajikan still active for the 06:00 check
        update_kwargs["kebajikan_fokus"] = list(range(1, 11))

    await update_user(user_id, **update_kwargs)

    label_map = {
        "pemula": "Pemula 🌱",
        "menengah": "Praktisi Menengah 🌿",
        "mahir": "Praktisi Mahir 🌳",
        "advanced": "Advanced 🪷",
        "super_advanced": "Super Advanced 💎",
    }

    extra = ""
    if target == "advanced":
        extra = (
            "\n\n🪷 *Sumpah Bodhisattva* akan dikirim 6 kali sehari:\n"
            "07:00 · 09:30 · 12:00 · 14:30 · 17:00 · 19:30\n"
            "Rotasi 147 hari — setiap sumpah muncul sekali per siklus."
        )
    elif target == "super_advanced":
        extra = (
            "\n\n💎 *Sumpah Tantra* akan dikirim 6 kali sehari:\n"
            "07:00 · 09:30 · 12:00 · 14:30 · 17:00 · 19:30\n"
            "Rotasi 44 hari — 265 sumpah dalam satu siklus."
        )

    text = f"✅ Level berhasil diubah ke *{label_map[target]}*!{extra}\n\n_Semoga praktik Anda semakin mendalam._ 🙏"

    if hasattr(source, "edit_message_text"):
        await source.edit_message_text(text, parse_mode="Markdown")
    else:
        await source.reply_text(text, parse_mode="Markdown")

    context.user_data.clear()


# ─── CONVERSATION HANDLER ────────────────────────────────────────────────────
def build_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("refleksi", cmd_refleksi),
            CommandHandler("ganti", cmd_ganti),
            CommandHandler("tambahan", cmd_tambahan),
            CommandHandler("level", cmd_level),
        ],
        states={
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
            UPGRADE_PASSWORD: [
                CallbackQueryHandler(upgrade_level_cb, pattern="^upgrade_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_password),
            ],
            PILIH_VOW_AWAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_vow_awal),
                CallbackQueryHandler(konfirmasi_vow_awal_cb, pattern="^konfirmasi_vow_awal$|^ubah_vow_awal$"),
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
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
    )
