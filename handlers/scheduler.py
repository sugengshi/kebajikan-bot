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
    get_tambahan_malam, set_pending, get_pending, get_user_lang
)
from utils.messages import (
    format_pertanyaan_refleksi, format_pertanyaan_tambahan_malam,
    format_pengingat, format_ringkasan_positif, format_arsip_pribadi,
    format_pagi_ganti_tanya
)
from utils.i18n import T
from data.kebajikan import KEBAJIKAN, LEVEL_CONFIG
from data.vows import (
    ADVANCED_VOWS, SUPER_ADVANCED_VOWS,
    ADV_TIMES, SA_TIMES,
    get_adv_vows_for_day, get_sa_vows_for_day,
    format_vow_message, format_vow_pair_message
)

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
        kirim_notifikasi_harian,
        CronTrigger(minute="0,30", timezone=WIB),
        args=[bot],
        id="notifikasi_harian",
        replace_existing=True,
    )
    _scheduler.add_job(
        kirim_pengingat,
        CronTrigger(minute="5,35", timezone=WIB),
        args=[bot],
        id="pengingat",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started.")
    return _scheduler


# ─── MAIN DISPATCHER ─────────────────────────────────────────────────────────

async def kirim_notifikasi_harian(bot: Bot):
    """
    Runs every 30 min. Checks which notification each user should receive,
    using the user's own timezone for time comparison.
    """
    now_utc = datetime.now(pytz.utc)
    users = await get_all_users()
    total = len(users)
    logger.info(f"[scheduler] firing for {total} users at UTC {now_utc.strftime('%H:%M')}")

    tasks = []
    for i, u in enumerate(users):
        user_id = u["user_id"]
        # Get user's local time in their timezone
        tz_str = u.get("timezone") or "Asia/Jakarta"
        try:
            user_tz = pytz.timezone(tz_str)
        except Exception:
            user_tz = WIB
        jam_user = now_utc.astimezone(user_tz).strftime("%H:%M")
        coro = _dispatch(bot, user_id, u, jam_user)
        tasks.append(_kirim_dengan_jitter(coro, i, total))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def _dispatch(bot: Bot, user_id: int, u: dict, jam: str):
    """Route a single user to the right send function for this hour."""
    try:
        level = u.get("level", "pemula")

        # Advanced and Super Advanced: 6 vow prompts per day at fixed times
        if level in ("advanced", "super_advanced"):
            custom_times = u.get("vow_times", "")
            if custom_times:
                vow_times = custom_times.split()
            else:
                vow_times = ADV_TIMES if level == "advanced" else SA_TIMES
            tz_name = u.get("timezone") or "Asia/Jakarta"
            logger.info(f"[dispatch] user={user_id} level={level} tz={tz_name} jam={jam!r} vow_times={vow_times}")
            if jam in vow_times:
                await kirim_sumpah(bot, user_id, level, jam, u, vow_times)
                return
            # Also send daily bookends for advanced users
            if jam == u.get("jam_fokus", "06:00"):
                await _kirim_06(bot, user_id)
            elif jam == u.get("jam_ringkasan", "21:00"):
                await kirim_ringkasan(bot, user_id)
            elif jam == u.get("jam_cofmed", "21:30"):
                await kirim_arsip(bot, user_id)
            return

        # Standard levels: existing schedule
        if jam == u.get("jam_fokus", "06:00"):
            await _kirim_06(bot, user_id)
        elif jam == u.get("jam_pagi", "07:00"):
            await kirim_sesi(bot, user_id, "pagi")
        elif jam == u.get("jam_siang", "12:00"):
            await kirim_sesi(bot, user_id, "siang")
        elif jam == u.get("jam_sore", "18:00"):
            await kirim_sesi(bot, user_id, "sore")
        elif jam == u.get("jam_malam", "20:00"):
            await kirim_malam(bot, user_id)
        elif jam == u.get("jam_ringkasan", "21:00"):
            await kirim_ringkasan(bot, user_id)
        elif jam == u.get("jam_cofmed", "21:30"):
            await kirim_arsip(bot, user_id)
    except Exception as e:
        logger.error(f"Error notifikasi user {user_id} jam {jam}: {e}")


async def kirim_sumpah(bot: Bot, user_id: int, level: str, jam: str, u: dict, vow_times: list = None):
    """Send a single vow prompt at the scheduled time for Advanced/Super Advanced."""
    from datetime import date
    import pytz

    db_user = await get_user(user_id)
    if not db_user:
        return

    # Calculate day number since join
    join_date_raw = db_user.get("join_date")
    if not join_date_raw:
        day_number = 1
    else:
        today = datetime.now(WIB).date()
        if hasattr(join_date_raw, 'date'):
            jd = join_date_raw.date()
        else:
            from datetime import date as dt_date
            jd = join_date_raw if isinstance(join_date_raw, dt_date) else today
        day_number = (today - jd).days + 1

    # Get slot index from time
    if vow_times is None:
        vow_times = ADV_TIMES if level == "advanced" else SA_TIMES
    times = vow_times
    if jam not in times:
        return
    slot_index = times.index(jam)

    # Get vow for this day and slot
    lang = db_user.get("bahasa", "id") or "id"
    if level == "advanced":
        vows_today = get_adv_vows_for_day(day_number)
        vow = vows_today[slot_index]
        label = T("sumpah_label_advanced", lang)
        vow_dict = ADVANCED_VOWS
    else:
        vows_today = get_sa_vows_for_day(day_number)
        vow = vows_today[slot_index]
        label = T("sumpah_label_super", lang)
        vow_dict = SUPER_ADVANCED_VOWS

    # Check which vow slots are already filled today
    from utils.database import get_catatan_hari_ini as _get_cat
    catatan_today = await _get_cat(user_id)
    filled_vows = {c["kebajikan_id"] for c in catatan_today}
    filled_sesi = {c["sesi"] for c in catatan_today}

    def _slot_filled(v, si):
        """Return True if this slot's vow or slot sesi is already filled."""
        sesi_key = f"slot_{times[si]}"
        vow_id = v[0] if isinstance(v, list) else v
        return sesi_key in filled_sesi or vow_id in filled_vows

    # If this slot is already filled, find the next unfilled one
    if _slot_filled(vow, slot_index):
        # Search remaining slots for an unfilled one
        next_vow = None
        next_slot = None
        next_jam = None
        for si in range(slot_index + 1, len(vows_today)):
            if not _slot_filled(vows_today[si], si):
                next_vow = vows_today[si]
                next_slot = si
                next_jam = times[si]
                break

        if next_vow is None:
            # All remaining vows are filled — ask if they want to rewrite
            await _send_all_done(bot, user_id, lang, vows_today, times, vow_dict, label)
            return

        # Send the next unfilled vow instead
        vow = next_vow
        slot_index = next_slot
        jam = next_jam
        if isinstance(vow, list):
            vow_intro = T("sumpah_berikutnya", lang) + "\n\n"
            text = vow_intro + format_vow_pair_message(vow, vow_dict, label)
            vow_num = vow[0]
        else:
            vow_intro = T("sumpah_berikutnya", lang) + "\n\n"
            text = vow_intro + format_vow_message(vow, vow_dict, label)
            vow_num = vow
    else:
        # Normal case — send this slot's vow
        if isinstance(vow, list):
            text = format_vow_pair_message(vow, vow_dict, label)
            vow_num = vow[0]
        else:
            text = format_vow_message(vow, vow_dict, label)
            vow_num = vow

    # Add inline reflect button
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    slot_index_str = str(slot_index)
    reflect_label = T("sumpah_mulai_refleksi_label", lang)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(reflect_label, callback_data=f"reflect_vow_{slot_index_str}_{jam.replace(':','')}")
    ]])

    await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown", reply_markup=kb)


async def _send_all_done(bot, user_id: int, lang: str, vows_today: list, times: list,
                         vow_dict: dict, label: str):
    """Send 'all done' message with option to rewrite a vow."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    # Build rewrite selection buttons
    rows = []
    for i, (t, v) in enumerate(zip(times, vows_today)):
        vow_id = v[0] if isinstance(v, list) else v
        en_t, id_t = vow_dict.get(vow_id, ("?", "?"))
        short = (id_t if lang == "id" else en_t)[:40] + "..."
        rows.append([InlineKeyboardButton(
            f"{t} — #{vow_id} {short}",
            callback_data=f"reflect_vow_{i}_{t.replace(':','')}"
        )])

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(T("sumpah_tulis_ulang_ya",    lang), callback_data="rewrite_vow_yes"),
            InlineKeyboardButton(T("sumpah_tulis_ulang_tidak", lang), callback_data="rewrite_vow_no"),
        ]
    ])
    await bot.send_message(
        chat_id=user_id,
        text=T("sumpah_semua_selesai", lang),
        parse_mode="Markdown",
        reply_markup=kb
    )


# ─── INDIVIDUAL SEND FUNCTIONS ───────────────────────────────────────────────

async def _kirim_06(bot: Bot, user_id: int):
    """06:00 — tanya ganti fokus atau lanjutkan."""
    db_user = await get_user(user_id)
    if not db_user:
        return
    fokus = db_user.get("kebajikan_fokus", [])
    if not fokus:
        return
    lang = db_user.get("bahasa", "id") or "id"

    await bot.send_message(
        chat_id=user_id,
        text=format_pagi_ganti_tanya(fokus, lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(T("pagi_ganti_ya_label", lang),    callback_data="pagi_ganti_ya"),
                InlineKeyboardButton(T("pagi_ganti_tidak_label", lang), callback_data="pagi_ganti_tidak"),
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
    lang = db_user.get("bahasa", "id") or "id"
    await bot.send_message(
        chat_id=user_id,
        text=format_pertanyaan_refleksi(sesi, k_id, "positif", lang),
        parse_mode="Markdown"
    )


async def kirim_malam(bot: Bot, user_id: int):
    """20:00 — tanya tambahan perbuatan baik."""
    lang = await get_user_lang(user_id)
    await bot.send_message(
        chat_id=user_id,
        text=format_pertanyaan_tambahan_malam(lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(T("tambahan_tidak_ada_label", lang), callback_data="tidak_ada_tambahan")]
        ])
    )


async def kirim_ringkasan(bot: Bot, user_id: int):
    """21:00 — tampilkan semua perbuatan baik hari ini (positif saja)."""
    from utils.messages import build_vow_time_map
    from datetime import date as dt_date
    db_user = await get_user(user_id)
    lang = (db_user.get("bahasa", "id") or "id") if db_user else "id"
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)

    vow_time_map = {}
    if db_user:
        level = db_user.get("level", "pemula")
        if level in ("advanced", "super_advanced"):
            join_date_raw = db_user.get("join_date")
            today = datetime.now(WIB).date()
            jd = join_date_raw if (join_date_raw and isinstance(join_date_raw, dt_date)) else today
            day_number = (today - jd).days + 1
            vow_time_map = build_vow_time_map(level, day_number)

    await bot.send_message(
        chat_id=user_id,
        text=format_ringkasan_positif(catatan, tambahan, lang, vow_time_map=vow_time_map),
        parse_mode="Markdown"
    )


async def kirim_arsip(bot: Bot, user_id: int):
    """21:30 — arsip pribadi lengkap (semua entri refleksi + tambahan)."""
    from utils.messages import build_vow_time_map
    from datetime import date as dt_date
    catatan = await get_catatan_hari_ini(user_id)
    tambahan = await get_tambahan_malam(user_id)
    db_user = await get_user(user_id)
    nama = db_user.get("username", "") if db_user else ""
    lang = (db_user.get("bahasa", "id") or "id") if db_user else "id"

    vow_time_map = {}
    if db_user:
        level = db_user.get("level", "pemula")
        if level in ("advanced", "super_advanced"):
            join_date_raw = db_user.get("join_date")
            today = datetime.now(WIB).date()
            jd = join_date_raw if (join_date_raw and isinstance(join_date_raw, dt_date)) else today
            day_number = (today - jd).days + 1
            vow_time_map = build_vow_time_map(level, day_number)

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
        text=format_arsip_pribadi(catatan, tambahan, lang, nama, vow_time_map=vow_time_map),
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
                lang = await get_user_lang(user_id)
                await bot.send_message(
                    chat_id=user_id,
                    text=format_pengingat(pending["sesi"], pending["kebajikan_id"], lang),
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
