import sqlite3
from pathlib import Path


DB_PATH = Path("data/bot.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_links (
                discord_user_id TEXT PRIMARY KEY,
                cr_tag TEXT NOT NULL,
                linked_by_discord_id TEXT,
                linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def upsert_link(discord_user_id: int, cr_tag: str, linked_by_discord_id: int):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO player_links (discord_user_id, cr_tag, linked_by_discord_id)
            VALUES (?, ?, ?)
            ON CONFLICT(discord_user_id) DO UPDATE SET
                cr_tag = excluded.cr_tag,
                linked_by_discord_id = excluded.linked_by_discord_id,
                linked_at = CURRENT_TIMESTAMP
        """, (str(discord_user_id), cr_tag, str(linked_by_discord_id)))
        conn.commit()


def get_tag(discord_user_id: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT cr_tag
            FROM player_links
            WHERE discord_user_id = ?
        """, (str(discord_user_id),)).fetchone()

        return row[0] if row else None


def delete_link(discord_user_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM player_links
            WHERE discord_user_id = ?
        """, (str(discord_user_id),))
        conn.commit()

def get_all_links():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT discord_user_id, cr_tag, linked_by_discord_id, linked_at
            FROM player_links
            ORDER BY linked_at DESC
        """).fetchall()

        return rows