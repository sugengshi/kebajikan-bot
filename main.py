# main.py
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from utils.database import init_db, get_user, update_user
from handlers.conversation import (
    build_conversation_handler, cmd_kebajikan,
    cmd_bantuan, cmd_laporan
)
from handlers.scheduler import init_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application):
    """Initialize DB and scheduler after bot starts."""
    await init_db()
    init_scheduler(application.bot)
    logger.info("Bot initialized successfully.")


async def callback_pagi_ganti(update, context):
    """Handle 06:00 ganti/lanjutkan callback."""
    query = update.callback_query
    await query.answer()

    if query.data == "pagi_ganti_ya":
        await query.edit_message_text(
            "🔄 Gunakan /ganti untuk memilih kebajikan fokus baru hari ini.",
            parse_mode="Markdown"
        )
    else:
        user_id = query.from_user.id
        db_user = await get_user(user_id)
        fokus = db_user.get("kebajikan_fokus", []) if db_user else []
        from data.kebajikan import KEBAJIKAN
        lines = ["✅ *Fokus kebajikan hari ini tetap:*\n"]
        for k_id in fokus:
            k = KEBAJIKAN.get(k_id, {})
            if k:
                lines.append(f"{k['emoji']} {k['nama']}")
        lines.append("\n\nRefleksi pagi akan dimulai sesuai jadwal Anda. 🙏")
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")


async def atur_jam(update, context):
    """Simple jam customization guide."""
    await update.message.reply_text(
        "⏰ *Atur Jam Notifikasi*\n\n"
        "Kirim pesan dalam format berikut untuk mengubah jam notifikasi:\n\n"
        "`/setjam pagi 07:30`\n"
        "`/setjam siang 13:00`\n"
        "`/setjam sore 17:00`\n"
        "`/setjam malam 19:30`\n"
        "`/setjam cofmed 22:00`\n\n"
        "Semua waktu dalam WIB (UTC+7).",
        parse_mode="Markdown"
    )


async def setjam(update, context):
    """Handle /setjam sesi HH:MM."""
    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "Format: `/setjam pagi 07:30`", parse_mode="Markdown"
        )
        return

    sesi_map = {
        "pagi": "jam_pagi",
        "siang": "jam_siang",
        "sore": "jam_sore",
        "malam": "jam_malam",
        "cofmed": "jam_cofmed",
    }
    sesi = args[0].lower()
    jam = args[1]

    if sesi not in sesi_map:
        await update.message.reply_text(
            f"Sesi tidak dikenal: {sesi}\nPilihan: pagi, siang, sore, malam, cofmed"
        )
        return

    # Validasi format jam
    try:
        h, m = jam.split(":")
        assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except Exception:
        await update.message.reply_text("Format jam tidak valid. Gunakan HH:MM, contoh: 07:30")
        return

    user_id = update.effective_user.id
    await update_user(user_id, **{sesi_map[sesi]: jam})
    await update.message.reply_text(
        f"✅ Jam {sesi} berhasil diubah ke *{jam}* WIB.", parse_mode="Markdown"
    )


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable tidak ditemukan!")

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    # Conversation handler (onboarding + refleksi + ganti + tambahan)
    app.add_handler(build_conversation_handler())

    # Standalone commands
    app.add_handler(CommandHandler("kebajikan", cmd_kebajikan))
    app.add_handler(CommandHandler("bantuan", cmd_bantuan))
    app.add_handler(CommandHandler("laporan", cmd_laporan))
    app.add_handler(CommandHandler("atur_jam", atur_jam))
    app.add_handler(CommandHandler("setjam", setjam))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_pagi_ganti, pattern="^pagi_ganti_"))
    app.add_handler(CallbackQueryHandler(konfirmasi_laporan_cb, pattern="^konfirmasi_laporan"))
    app.add_handler(CallbackQueryHandler(koreksi_laporan_cb, pattern="^koreksi_laporan"))

    logger.info("Bot berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
