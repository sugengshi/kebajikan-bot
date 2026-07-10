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
    build_conversation_handler, cmd_kebajikan, cmd_help,
    cmd_laporan, cmd_level, cmd_language,
    callback_pagi_ganti, cmd_setjam, cmd_setvowtime, laporan_mode_cb, rewrite_vow_cb
)
from handlers.scheduler import init_scheduler
from handlers.admin import cmd_admin_users, cmd_admin_user, cmd_admin_entries, admin_entries_cb

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """Log all unhandled exceptions so they surface in Railway logs."""
    logger.error("Unhandled exception while processing update", exc_info=context.error)


async def post_init(application):
    """Initialize DB and scheduler after bot starts."""
    await init_db()
    init_scheduler(application.bot)

    # Register commands so they appear when user types "/"
    from telegram import BotCommand
    from telegram import BotCommandScopeDefault
    # Indonesian commands
    id_commands = [
        BotCommand("start",         "Mulai ulang"),
        BotCommand("help",          "Daftar perintah"),
        BotCommand("kebajikan",     "Fokus kebajikan hari ini"),
        BotCommand("refleksi",      "Isi refleksi sekarang"),
        BotCommand("ganti",         "Ganti fokus kebajikan"),
        BotCommand("tambahan",      "Tambah perbuatan baik"),
        BotCommand("laporan",       "Ringkasan hari ini"),
        BotCommand("level",         "Ubah level praktik"),
        BotCommand("language",      "Ganti bahasa"),
        BotCommand("setjam",        "Atur jam notifikasi"),
        BotCommand("setjamsumpah",  "Atur jam notifikasi sumpah (Advanced)"),
    ]
    # English commands
    en_commands = [
        BotCommand("start",       "Restart"),
        BotCommand("help",        "Command list"),
        BotCommand("virtue",      "Today's virtue focus"),
        BotCommand("reflect",     "Fill in reflection now"),
        BotCommand("change",      "Change virtue focus"),
        BotCommand("add",         "Add good deeds"),
        BotCommand("report",      "Today's summary"),
        BotCommand("level",       "Change practice level"),
        BotCommand("language",    "Change language"),
        BotCommand("settime",     "Set notification times"),
        BotCommand("setvowtime",  "Set vow notification times (Advanced)"),
    ]
    from telegram import BotCommandScopeDefault, BotCommandScopeChat
    await application.bot.set_my_commands(id_commands)
    await application.bot.set_my_commands(en_commands, language_code="en")

    # Admin-only commands — visible only in the admin's chat menu
    admin_id_str = os.environ.get("ADMIN_USER_ID", "")
    if admin_id_str:
        try:
            admin_id = int(admin_id_str)
            admin_commands = [
                BotCommand("adminusers",   "👥 All users by level + activity"),
                BotCommand("adminuser",    "👤 Profile for one user"),
                BotCommand("adminentries", "📋 Today's entries for one user"),
            ]
            await application.bot.set_my_commands(
                admin_commands,
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
            logger.info(f"Admin commands registered for user {admin_id}.")
        except Exception as e:
            logger.warning(f"Could not register admin commands: {e}")

    logger.info("Bot commands registered.")
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

    # Conversation handler — handles all multi-step flows
    app.add_handler(build_conversation_handler())

    # Standalone commands (group 0)
    app.add_handler(CommandHandler("kebajikan", cmd_kebajikan))
    app.add_handler(CommandHandler("virtue",    cmd_kebajikan))
    app.add_handler(CommandHandler("laporan",   cmd_laporan))
    app.add_handler(CommandHandler("report",    cmd_laporan))
    app.add_handler(CommandHandler("level",     cmd_level))
    app.add_handler(CommandHandler("language",  cmd_language))
    app.add_handler(CommandHandler("help",         cmd_help))
    app.add_handler(CommandHandler("bantuan",      cmd_help))
    app.add_handler(CommandHandler("setvowtime",   cmd_setvowtime))
    app.add_handler(CommandHandler("setjamsumpah", cmd_setvowtime))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_pagi_ganti, pattern="^pagi_ganti_"))
    app.add_handler(CallbackQueryHandler(laporan_mode_cb, pattern="^laporan_"))
    app.add_handler(CallbackQueryHandler(rewrite_vow_cb, pattern="^rewrite_vow_"))

    # Admin commands (only respond to ADMIN_USER_ID)
    app.add_handler(CommandHandler("adminusers",   cmd_admin_users))
    app.add_handler(CommandHandler("adminuser",    cmd_admin_user))
    app.add_handler(CommandHandler("adminentries", cmd_admin_entries))
    app.add_handler(CallbackQueryHandler(admin_entries_cb, pattern="^admin_entries_"))

    app.add_error_handler(error_handler)

    logger.info("Bot berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
