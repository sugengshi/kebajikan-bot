# handlers/admin.py
import os
import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import get_all_users, get_user, get_catatan_hari_ini, get_tambahan_malam, get_activity_last_7_days

logger = logging.getLogger(__name__)
WIB = pytz.timezone("Asia/Jakarta")

LEVEL_EMOJI = {
    "pemula":         "🌱",
    "menengah":       "🌿",
    "mahir":          "🌳",
    "advanced":       "🪷",
    "super_advanced": "💎",
}

LEVEL_DISPLAY = {
    "pemula":         "🌱 Pemula",
    "menengah":       "🌿 Menengah",
    "mahir":          "🌳 Mahir",
    "advanced":       "🪷 Bodhisattva",
    "super_advanced": "💎 Diamond",
}


def _is_admin(user_id: int) -> bool:
    admin_id = os.environ.get("ADMIN_USER_ID", "")
    return str(user_id) == admin_id


def _esc(text: str) -> str:
    """Escape Markdown v1 special characters in user-generated text."""
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


# ─── /adminusers ─────────────────────────────────────────────────────────────

async def cmd_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all registered users grouped by level, with a 📋 button per user."""
    if not _is_admin(update.effective_user.id):
        return

    users = await get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    activity = await get_activity_last_7_days()  # {user_id: {days, entries}}

    # Define display order and headers for each level
    LEVEL_ORDER = ["super_advanced", "advanced", "mahir", "menengah", "pemula"]
    LEVEL_LABEL = {
        "super_advanced": "💎 Diamond",
        "advanced":       "🪷 Bodhisattva",
        "mahir":          "🌳 Mahir",
        "menengah":       "🌿 Menengah",
        "pemula":         "🌱 Pemula",
    }

    # Group users by level
    from collections import defaultdict
    grouped = defaultdict(list)
    for u in users:
        lvl = u.get("level") or "pemula"
        grouped[lvl].append(u)

    active_total   = len(activity)
    inactive_total = len(users) - active_total
    lines = [f"👥 *All Users* ({len(users)} total) — 🟢 {active_total} active · ⚪️ {inactive_total} inactive (7d)\n"]
    buttons = []

    # ── Active users grouped by level ──────────────────────────────────────────
    lines.append("*🟢 Active (last 7 days)*")
    for lvl in LEVEL_ORDER:
        members = [u for u in grouped.get(lvl, []) if u["user_id"] in activity]
        if not members:
            continue
        label = LEVEL_LABEL.get(lvl, lvl)
        lines.append(f"\n*{label}* ({len(members)})")
        for u in members:
            uid       = u["user_id"]
            name      = u.get("username") or "—"
            lang      = u.get("bahasa") or "id"
            tz        = u.get("timezone") or "Asia/Jakarta"
            done      = "✅" if u.get("onboarding_selesai") else "⏳"
            safe_name = name.replace("`", "'")
            act       = activity[uid]
            lines.append(f"{done} `{uid}` — `{safe_name}` [{lang}] `{tz}` _{act['days']}/7d_")
            buttons.append(InlineKeyboardButton(f"📋 {safe_name}", callback_data=f"admin_entries_{uid}"))

    # ── Inactive users grouped by level ────────────────────────────────────────
    lines.append(f"\n\n*⚪️ Inactive (7d)*")
    any_inactive = False
    for lvl in LEVEL_ORDER:
        members = [u for u in grouped.get(lvl, []) if u["user_id"] not in activity]
        if not members:
            continue
        any_inactive = True
        label = LEVEL_LABEL.get(lvl, lvl)
        lines.append(f"\n*{label}* ({len(members)})")
        for u in members:
            uid       = u["user_id"]
            name      = u.get("username") or "—"
            lang      = u.get("bahasa") or "id"
            tz        = u.get("timezone") or "Asia/Jakarta"
            done      = "✅" if u.get("onboarding_selesai") else "⏳"
            safe_name = name.replace("`", "'")
            lines.append(f"{done} `{uid}` — `{safe_name}` [{lang}] `{tz}`")
            buttons.append(InlineKeyboardButton(f"📋 {safe_name}", callback_data=f"admin_entries_{uid}"))
    if not any_inactive:
        lines.append("_Everyone has been active this week!_ 🎉")

    # Pair buttons into rows of 2
    kb_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    kb = InlineKeyboardMarkup(kb_rows)

    text = "\n".join(lines)
    # Split if too long, attach buttons only to the last chunk
    if len(text) > 4000:
        chunks = []
        chunk = lines[0] + "\n"
        for line in lines[1:]:
            if len(chunk) + len(line) + 1 > 4000:
                chunks.append(chunk)
                chunk = ""
            chunk += line + "\n"
        chunks.append(chunk)
        for i, c in enumerate(chunks):
            if i < len(chunks) - 1:
                await update.message.reply_text(c, parse_mode="Markdown")
            else:
                await update.message.reply_text(c, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


# ─── Entries callback (tap 📋 button) ────────────────────────────────────────

async def admin_entries_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for 📋 buttons in /adminusers — show today's entries for that user."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(query.from_user.id):
        return

    uid = int(query.data.replace("admin_entries_", ""))
    await _send_entries(query.message.reply_text, uid)


# ─── /adminuser <user_id> ─────────────────────────────────────────────────────

async def cmd_admin_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show full profile for a single user. Usage: /adminuser 123456789"""
    if not _is_admin(update.effective_user.id):
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: `/adminuser <user_id>`", parse_mode="Markdown")
        return

    try:
        uid = int(args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return

    u = await get_user(uid)
    if not u:
        await update.message.reply_text(f"No user found with ID `{uid}`.", parse_mode="Markdown")
        return

    level      = u.get("level") or "pemula"
    emoji      = LEVEL_EMOJI.get(level, "•")
    fokus      = u.get("kebajikan_fokus") or []
    join_dt    = u.get("join_date")
    if join_dt:
        today = datetime.now(WIB).date()
        jd = join_dt.date() if hasattr(join_dt, "date") else join_dt
        day_num = (today - jd).days + 1
        join_str = f"{jd} (Day {day_num})"
    else:
        join_str = "—"

    vow_times  = u.get("vow_times") or "default"
    safe_name  = (u.get("username") or "—")
    safe_goal  = (u.get("tujuan_smart") or "—")[:120]
    lines = [
        f"👤 User Profile\n",
        f"ID:       {uid}",
        f"Name:     {safe_name}",
        f"Level:    {emoji} {level}",
        f"Language: {u.get('bahasa') or 'id'}",
        f"Timezone: {u.get('timezone') or 'Asia/Jakarta'}",
        f"Onboarding: {'✅ done' if u.get('onboarding_selesai') else '⏳ pending'}",
        f"Join date: {join_str}",
        f"Vow times: {vow_times}",
        f"Kebajikan fokus: {fokus}",
        f"SMART goal: {safe_goal}",
        f"\nNotification times:",
        f"  jam_fokus  → {u.get('jam_fokus',    '06:00')}",
        f"  jam_pagi   → {u.get('jam_pagi',     '07:00')}",
        f"  jam_siang  → {u.get('jam_siang',    '12:00')}",
        f"  jam_sore   → {u.get('jam_sore',     '18:00')}",
        f"  jam_malam  → {u.get('jam_malam',    '20:00')}",
        f"  jam_ring   → {u.get('jam_ringkasan','21:00')}",
        f"  jam_cof    → {u.get('jam_cofmed',   '21:30')}",
    ]
    # Button to view today's entries
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📋 View Today's Entries", callback_data=f"admin_entries_{uid}")
    ]])
    await update.message.reply_text("\n".join(lines), reply_markup=kb)


# ─── /adminentries <user_id> ─────────────────────────────────────────────────

async def cmd_admin_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's reflection entries for a user. Usage: /adminentries 123456789"""
    if not _is_admin(update.effective_user.id):
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: `/adminentries <user_id>`", parse_mode="Markdown")
        return

    try:
        uid = int(args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return

    await _send_entries(update.message.reply_text, uid)


# ─── Shared entries formatter ─────────────────────────────────────────────────

async def _send_entries(reply_fn, uid: int):
    """Fetch and send today's entries for uid using the given reply function."""
    catatan  = await get_catatan_hari_ini(uid)
    tambahan = await get_tambahan_malam(uid)
    today    = datetime.now(WIB).strftime("%d %B %Y")

    if not catatan and not tambahan:
        await reply_fn(f"📭 No entries today for user {uid}.")
        return

    lines = [f"📋 Entries for {uid}\n{today}\n"]
    for c in catatan:
        sesi   = c.get("sesi", "")
        k_id   = c.get("kebajikan_id", 0)
        pos    = c.get("catatan_positif", "").strip()
        neg    = c.get("catatan_negatif", "").strip()
        plan   = c.get("rencana_kedepan", "").strip()
        lines.append(f"[ {sesi} | #{k_id} ]")
        if pos:  lines.append(f"  ✅ {pos}")
        if neg and neg.lower() not in ("-", "tidak ada", "none", ""):
            lines.append(f"  ❌ {neg}")
        if plan: lines.append(f"  🌱 {plan}")
        lines.append("")

    if tambahan:
        lines.append("🌙 Tambahan:")
        for t in tambahan:
            lines.append(f"  ✅ {str(t)}")

    await reply_fn("\n".join(lines))
