# utils/database.py
# PostgreSQL via asyncpg — drop-in replacement for the SQLite version.
# Railway provides DATABASE_URL automatically when you add a Postgres plugin.

import asyncpg
import json
import os
from datetime import datetime
import pytz

WIB = pytz.timezone("Asia/Jakarta")

# Connection pool — shared across the whole app lifetime
_pool: asyncpg.Pool | None = None


async def init_db():
    """Create connection pool and ensure all tables exist."""
    global _pool
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL environment variable tidak ditemukan!")

    # asyncpg needs postgresql:// not postgres:// (Railway sometimes sends the latter)
    dsn = dsn.replace("postgres://", "postgresql://", 1)

    _pool = await asyncpg.create_pool(dsn, min_size=2, max_size=10)

    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     BIGINT PRIMARY KEY,
                username    TEXT,
                level       TEXT    DEFAULT 'pemula',
                kebajikan_fokus TEXT DEFAULT '[]',
                tujuan_smart    TEXT,
                siapa_dibantu   TEXT,
                rencana_pelaksanaan TEXT,
                jam_pagi    TEXT DEFAULT '07:00',
                jam_siang   TEXT DEFAULT '12:00',
                jam_sore    TEXT DEFAULT '18:00',
                jam_malam   TEXT DEFAULT '20:00',
                jam_cofmed  TEXT DEFAULT '21:30',
                rotasi_index    INTEGER DEFAULT 0,
                onboarding_selesai INTEGER DEFAULT 0,
                bahasa      TEXT DEFAULT 'id',
                timezone    TEXT DEFAULT 'Asia/Jakarta',
                join_date   DATE,
                jam_fokus   TEXT DEFAULT '06:00',
                jam_pagi    TEXT DEFAULT '07:00',
                jam_siang   TEXT DEFAULT '12:00',
                jam_sore    TEXT DEFAULT '18:00',
                jam_malam   TEXT DEFAULT '20:00',
                jam_ringkasan TEXT DEFAULT '21:00',
                jam_cofmed  TEXT DEFAULT '21:30',
                created_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS catatan_harian (
                id          BIGSERIAL PRIMARY KEY,
                user_id     BIGINT,
                tanggal     DATE,
                sesi        TEXT,
                kebajikan_id INTEGER,
                catatan_positif  TEXT,
                catatan_negatif  TEXT,
                rencana_kedepan  TEXT,
                created_at  TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE (user_id, tanggal, sesi)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tambahan_malam (
                id          BIGSERIAL PRIMARY KEY,
                user_id     BIGINT,
                tanggal     DATE,
                catatan     TEXT,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_responses (
                user_id     BIGINT,
                sesi        TEXT,
                tanggal     DATE,
                kebajikan_id INTEGER,
                step        TEXT DEFAULT 'positif',
                temp_positif TEXT DEFAULT '',
                temp_negatif TEXT DEFAULT '',
                PRIMARY KEY (user_id, sesi, tanggal)
            )
        """)
        # Migrations — add new columns to existing tables safely
        for col, default in [
            ("bahasa",        "'id'"),
            ("timezone",      "'Asia/Jakarta'"),
            ("join_date",     "NULL"),
            ("vow_times",     "'07:00 09:30 12:00 14:30 17:00 19:30'"),
            ("jam_fokus",     "'06:00'"),
            ("jam_pagi",      "'07:00'"),
            ("jam_siang",     "'12:00'"),
            ("jam_sore",      "'18:00'"),
            ("jam_malam",     "'20:00'"),
            ("jam_ringkasan", "'21:00'"),
            ("jam_cofmed",    "'21:30'"),
        ]:
            try:
                await conn.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} TEXT DEFAULT {default}")
            except Exception:
                pass  # column already exists with different type

        # Indexes for common query patterns
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_catatan_user_tanggal
            ON catatan_harian (user_id, tanggal)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tambahan_user_tanggal
            ON tambahan_malam (user_id, tanggal)
        """)


def _pool_conn():
    """Return a connection from the pool as async context manager."""
    if _pool is None:
        raise RuntimeError("Database pool belum diinisialisasi. Panggil init_db() dulu.")
    return _pool.acquire()


def _today() -> str:
    return datetime.now(WIB).strftime("%Y-%m-%d")


# ─── USERS ───────────────────────────────────────────────────────────────────

async def get_user(user_id: int) -> dict | None:
    async with _pool_conn() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )
        if row:
            data = dict(row)
            data["kebajikan_fokus"] = json.loads(data["kebajikan_fokus"] or "[]")
            return data
    return None


async def create_user(user_id: int, username: str):
    async with _pool_conn() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id, username)


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    if "kebajikan_fokus" in kwargs and isinstance(kwargs["kebajikan_fokus"], list):
        kwargs["kebajikan_fokus"] = json.dumps(kwargs["kebajikan_fokus"])

    # Build SET clause with positional params: $1, $2, ...
    keys = list(kwargs.keys())
    values = list(kwargs.values())
    set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(keys))
    values.append(user_id)  # last param for WHERE

    async with _pool_conn() as conn:
        await conn.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ${len(values)}",
            *values
        )


async def get_all_users() -> list:
    async with _pool_conn() as conn:
        rows = await conn.fetch("""
            SELECT user_id, kebajikan_fokus, jam_pagi, jam_siang, jam_sore,
                   jam_malam, jam_cofmed, onboarding_selesai, level, rotasi_index
            FROM users
            WHERE onboarding_selesai = 1
        """)
        result = []
        for r in rows:
            d = dict(r)
            d["kebajikan_fokus"] = json.loads(d["kebajikan_fokus"] or "[]")
            result.append(d)
        return result


# ─── CATATAN HARIAN ──────────────────────────────────────────────────────────

async def save_catatan(user_id: int, sesi: str, kebajikan_id: int,
                       positif: str, negatif: str, rencana: str):
    tanggal = _today()
    async with _pool_conn() as conn:
        await conn.execute("""
            INSERT INTO catatan_harian
                (user_id, tanggal, sesi, kebajikan_id,
                 catatan_positif, catatan_negatif, rencana_kedepan)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (user_id, tanggal, sesi)
            DO UPDATE SET
                kebajikan_id    = EXCLUDED.kebajikan_id,
                catatan_positif = EXCLUDED.catatan_positif,
                catatan_negatif = EXCLUDED.catatan_negatif,
                rencana_kedepan = EXCLUDED.rencana_kedepan
        """, user_id, tanggal, sesi, kebajikan_id, positif, negatif, rencana)


async def get_catatan_hari_ini(user_id: int) -> list:
    tanggal = _today()
    async with _pool_conn() as conn:
        rows = await conn.fetch("""
            SELECT * FROM catatan_harian
            WHERE user_id = $1 AND tanggal = $2
            ORDER BY sesi
        """, user_id, tanggal)
        return [dict(r) for r in rows]


# ─── TAMBAHAN MALAM ──────────────────────────────────────────────────────────

async def save_tambahan_malam(user_id: int, catatan: str):
    tanggal = _today()
    async with _pool_conn() as conn:
        await conn.execute("""
            INSERT INTO tambahan_malam (user_id, tanggal, catatan)
            VALUES ($1, $2, $3)
        """, user_id, tanggal, catatan)


async def get_tambahan_malam(user_id: int) -> list:
    tanggal = _today()
    async with _pool_conn() as conn:
        rows = await conn.fetch("""
            SELECT catatan FROM tambahan_malam
            WHERE user_id = $1 AND tanggal = $2
            ORDER BY created_at
        """, user_id, tanggal)
        return [r["catatan"] for r in rows]


# ─── PENDING RESPONSES ───────────────────────────────────────────────────────

async def set_pending(user_id: int, sesi: str, kebajikan_id: int,
                      step: str = "positif",
                      temp_positif: str = "", temp_negatif: str = ""):
    tanggal = _today()
    async with _pool_conn() as conn:
        await conn.execute("""
            INSERT INTO pending_responses
                (user_id, sesi, tanggal, kebajikan_id, step, temp_positif, temp_negatif)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (user_id, sesi, tanggal)
            DO UPDATE SET
                kebajikan_id = EXCLUDED.kebajikan_id,
                step         = EXCLUDED.step,
                temp_positif = EXCLUDED.temp_positif,
                temp_negatif = EXCLUDED.temp_negatif
        """, user_id, sesi, tanggal, kebajikan_id, step, temp_positif, temp_negatif)


async def get_pending(user_id: int) -> dict | None:
    tanggal = _today()
    async with _pool_conn() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM pending_responses
            WHERE user_id = $1 AND tanggal = $2
            ORDER BY ctid DESC LIMIT 1
        """, user_id, tanggal)
        return dict(row) if row else None


async def clear_pending(user_id: int):
    tanggal = _today()
    async with _pool_conn() as conn:
        await conn.execute("""
            DELETE FROM pending_responses
            WHERE user_id = $1 AND tanggal = $2
        """, user_id, tanggal)


# ─── COMPAT ALIAS ────────────────────────────────────────────────────────────
async def get_today_str() -> str:
    return _today()


async def get_user_lang(user_id: int) -> str:
    """Return user's language preference: 'id' or 'en'. Defaults to 'id'."""
    user = await get_user(user_id)
    if not user:
        return "id"
    return user.get("bahasa", "id") or "id"
