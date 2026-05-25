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
    cmd_bantuan, cmd_laporan, cmd_level, cmd_language,
    callback_pagi_ganti, cmd_atur_jam, cmd_setjam
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


# atur_jam and setjam are now in handlers/conversation.py


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
    app.add_handler(CommandHandler("atur_jam", cmd_atur_jam))
    app.add_handler(CommandHandler("setjam", cmd_setjam))
    app.add_handler(CommandHandler("level", cmd_level))
    app.add_handler(CommandHandler("language", cmd_language))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_pagi_ganti, pattern="^pagi_ganti_"))

    logger.info("Bot berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
