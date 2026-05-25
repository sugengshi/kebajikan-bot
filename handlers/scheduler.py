# handlers/scheduler.py
import asyncio
import logging
import random
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from utils.database import (
    get_all_users, get_user, update_user, get_catatan_hari_ini,
    get_tambahan_malam, set_pending, get_pending
)
from utils.messages import (
    format_pertanyaan_refleksi, format_pertanyaan_tambahan_malam,
    format_pengingat, format_ringkasan_positif, format_arsip_pribadi
)
from data.kebajikan import KEBAJIKAN, LEVEL_CONFIG

logger = logging.getLogger(__name__)
WIB = pytz.timezone("Asia/Jakarta")

# Maximum random delay per user in seconds (5-minute window)
JITTER_MAX = 5 * 60  # 300 seconds


async def _kirim_dengan_jitter(coro, user_index: int, total: int):
    """
    Spread messages evenly across JITTER_MAX seconds.
    User 0 sends immediately, last user waits up to JITTER_MAX seconds.
    This guarantees even distribution rather than random clustering.
    """
    if total > 1:
        delay = (user_index / total) * JITTER_MAX
        # Add small random noise (±5s) so messages don't arrive in lockstep
        delay += random.uniform(-5, 5)
        delay = max(0, delay)
        await asyncio.sleep(delay)
    await coro


# ─── SCHEDULER INIT ──────────────────────────────────────────────────────────

_scheduler: AsyncIOScheduler | None = None


def init_scheduler(bot: Bot) -> AsyncIOScheduler:
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone=WIB)

    _scheduler.add_job(
        lambda: kirim_notifikasi_harian(bot),
        CronTrigger(minute=0, timezone=WIB),
        id="notifikasi_harian",
        replace_existing=True,
    )
    _scheduler.add_job(
        lambda: kirim_pengingat(bot),
        CronTrigger(minute=5, timezone=WIB),
        id="pengingat",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started.")
    return _scheduler


# ─── MAIN DISPATCHER ─────────────────────────────────────────────────────────

async def kirim_notifikasi_harian(bot: Bot):
    """
    Runs every hour on the :00. Checks which notification each user
    should receive, then fans out with jitter to stay under Telegram's
    30 msg/sec limit even at large scale.
    """
    jam_sekarang = datetime.now(WIB).strftime("%H:%M")
    users = await get_all_users()
    total = len(users)

    tasks = []
    for i, u in enumerate(users):
        user_id = u["user_id"]
        coro = _dispatch(bot, user_id, u, jam_sekarang)
        tasks.append(_kirim_dengan_jitter(coro, i, total))

    # Fire all tasks concurrently — jitter is applied inside each task
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def _dispatch(bot: Bot, user_id: int, u: dict, jam: str):
    """Route a single user to the right send function for this hour."""
    try:
        if jam == "06:00":
            await _kirim_06(bot, user_id)
        elif jam == u.get("jam_pagi", "07:00"):
            await kirim_sesi(bot, user_id, "pagi")
        elif jam == u.get("jam_siang", "12:00"):
            await kirim_sesi(bot, user_id, "siang")
        elif jam == u.get("jam_sore", "18:00"):
            await kirim_sesi(bot, user_id, "sore")
        elif jam == u.get("jam_malam", "20:00"):
            await kirim_malam(bot, user_id)
        elif jam == "21:00":
            await kirim_ringkasan(bot, user_id)
        elif jam == u.get("jam_cofmed", "21:30"):
            await kirim_arsip(bot, user_id)
    except Exception as e:
        logger.error(f"Error notifikasi user {user_id} jam {jam}: {e}")


# ─── INDIVIDUAL SEND FUNCTIONS ───────────────────────────────────────────────

async def _kirim_06(bot: Bot, user_id: int):
    """06:00 — tanya ganti fokus atau lanjutkan."""
    db_user = await get_user(user_id)
    if not db_user:
        return
    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        return

    lines = ["🌅 *Selamat pagi!*\n\nFokus kebajikan Anda saat ini:\n"]
    for k_id in fokus:
        k = KEBAJIKAN.get(k_id, {})
        if k:
            lines.append(f"{k['emoji']} {k['nama']}")
    lines.append("\n\nApakah ingin *mengganti* fokus kebajikan hari ini?")

    await bot.send_message(
        chat_id=user_id,
        text="\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Ya, ganti", callback_data="pagi_ganti_ya"),
                InlineKeyboardButton("✅ Lanjutkan", callback_data="pagi_ganti_tidak"),
            ]
        ])
    )


async def kirim_sesi(bot: Bot, user_id: int, sesi: str):
    """07:00 / 12:00 / 18:00 — kirim pertanyaan refleksi."""
    db_user = await get_user(user_id)
    if not db_user:
        return
    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        return

    level = db_user.get("level", "pemula")
    if level == "mahir":
        rotasi = db_user.get("rotasi_index", 0)
        k_id = fokus[rotasi % len(fokus)]
        await update_user(user_id, rotasi_index=(rotasi + 1) % len(fokus))
    else:
        idx = {"pagi": 0, "siang": 1, "sore": 2}.get(sesi, 0)
        k_id = fokus[min(idx, len(fokus) - 1)]

    await set_pending(user_id, sesi, k_id)
    await bot.send_message(
        chat_id=user_id,
        text=format_pertanyaan_refleksi(sesi, k_id, "positif"),
        parse_mode="Markdown"
    )


async def kirim_malam(bot: Bot, user_id: int):
    """20:00 — tanya tambahan perbuatan baik."""
    await bot.send_message(
        chat_id=user_id,
        text=format_pertanyaan_tambahan_malam(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Tidak ada tambahan", callback_data="tidak_ada_tambahan")]
        ])
    )


async def kirim_ringkasan(bot: Bot, user_id: int):
    """21:00 — tampilkan semua perbuatan baik hari ini (positif saja)."""
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)

    if not catatan and not tambahan:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "✨ *Perbuatan Baik Hari Ini*\n\n"
                "Belum ada catatan yang masuk hari ini.\n"
                "Tidak apa-apa — besok kita mulai lagi. 🙏"
            ),
            parse_mode="Markdown"
        )
        return

    await bot.send_message(
        chat_id=user_id,
        text=format_ringkasan_positif(catatan, tambahan),
        parse_mode="Markdown"
    )


async def kirim_arsip(bot: Bot, user_id: int):
    """21:30 — arsip pribadi lengkap (semua entri refleksi + tambahan)."""
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)
    db_user = await get_user(user_id)
    nama = db_user.get("username", "") if db_user else ""

    if not catatan and not tambahan:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "📁 *Arsip Pribadi*\n\n"
                "Belum ada entri untuk hari ini.\n"
                "Istirahatlah dengan tenang. 🙏"
            ),
            parse_mode="Markdown"
        )
        return

    await bot.send_message(
        chat_id=user_id,
        text=format_arsip_pribadi(catatan, tambahan, nama),
        parse_mode="Markdown"
    )


async def kirim_pengingat(bot: Bot):
    """
    Runs every hour at :05. Sends a reminder to users who have a
    pending reflection but haven't responded yet.
    Also uses jitter to spread the burst.
    """
    users = await get_all_users()
    total = len(users)

    async def _cek(user_id: int):
        try:
            pending = await get_pending(user_id)
            if pending:
                await bot.send_message(
                    chat_id=user_id,
                    text=format_pengingat(pending["sesi"], pending["kebajikan_id"]),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error pengingat user {user_id}: {e}")

    tasks = [
        _kirim_dengan_jitter(_cek(u["user_id"]), i, total)
        for i, u in enumerate(users)
    ]
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
