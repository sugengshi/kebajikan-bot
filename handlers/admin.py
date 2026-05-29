# handlers/admin.py
import os
import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import get_all_users, get_user, get_catatan_hari_ini, get_tambahan_malam

logger = logging.getLogger(__name__)
WIB = pytz.timezone("Asia/Jakarta")

LEVEL_EMOJI = {
    "pemula":         "🌱",
    "menengah":       "🌿",
    "mahir":          "🌳",
    "advanced":       "🪷",
    "super_advanced": "💎",
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
    """List all registered users with a 📋 button to view each user's entries."""
    if not _is_admin(update.effective_user.id):
        return

    users = await get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    lines = [f"👥 *All Users* ({len(users)} total)\n"]
    buttons = []
    for u in users:
        uid       = u["user_id"]
        name      = u.get("username") or "—"
        level     = u.get("level") or "pemula"
        emoji     = LEVEL_EMOJI.get(level, "•")
        lang      = u.get("bahasa") or "id"
        tz        = u.get("timezone") or "Asia/Jakarta"
        done      = "✅" if u.get("onboarding_selesai") else "⏳"
        safe_name = name.replace("`", "'")
        lines.append(f"{done} `{uid}` — `{safe_name}` {emoji} `{level}` [{lang}] {tz}")
        # One button per user — tap to see today's entries
        btn_label = f"📋 {safe_name} {emoji}"
        buttons.append(InlineKeyboardButton(btn_label, callback_data=f"admin_entries_{uid}"))

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
    safe_name  = (u.get("username") or "—").replace("`", "'")
    safe_goal  = (u.get("tujuan_smart") or "—")[:120].replace("`", "'")
    lines = [
        f"👤 *User Profile*\n",
        f"ID: `{uid}`",
        f"Name: `{safe_name}`",
        f"Level: {emoji} `{level}`",
        f"Language: `{u.get('bahasa') or 'id'}`",
        f"Timezone: `{u.get('timezone') or 'Asia/Jakarta'}`",
        f"Onboarding: {'✅ done' if u.get('onboarding_selesai') else '⏳ pending'}",
        f"Join date: `{join_str}`",
        f"Vow times: `{vow_times}`",
        f"Kebajikan fokus: `{fokus}`",
        f"SMART goal: `{safe_goal}`",
        f"\n*Notification times:*",
        f"06:00 jam_fokus → `{u.get('jam_fokus', '06:00')}`",
        f"07:00 jam_pagi  → `{u.get('jam_pagi',  '07:00')}`",
        f"12:00 jam_siang → `{u.get('jam_siang', '12:00')}`",
        f"18:00 jam_sore  → `{u.get('jam_sore',  '18:00')}`",
        f"20:00 jam_malam → `{u.get('jam_malam', '20:00')}`",
        f"21:00 jam_ring  → `{u.get('jam_ringkasan', '21:00')}`",
        f"21:30 jam_cof   → `{u.get('jam_cofmed', '21:30')}`",
    ]
    # Button to view today's entries
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📋 View Today's Entries", callback_data=f"admin_entries_{uid}")
    ]])
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=kb)


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
