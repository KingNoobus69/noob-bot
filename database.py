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
                cr_tag TEXT NOT NULL UNIQUE,
                linked_by_discord_id TEXT,
                linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def insert_link(discord_user_id: int, cr_tag: str, linked_by_discord_id: int):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO player_links (discord_user_id, cr_tag, linked_by_discord_id)
            VALUES (?, ?, ?)
        """, (str(discord_user_id), cr_tag, str(linked_by_discord_id)))
        conn.commit()


def update_link(discord_user_id: int, cr_tag: str, linked_by_discord_id: int):
    with get_connection() as conn:
        conn.execute("""
            UPDATE player_links
            SET cr_tag = ?, linked_by_discord_id = ?, linked_at = CURRENT_TIMESTAMP
            WHERE discord_user_id = ?
        """, (cr_tag, str(linked_by_discord_id), str(discord_user_id)))
        conn.commit()


def get_tag(discord_user_id: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT cr_tag
            FROM player_links
            WHERE discord_user_id = ?
        """, (str(discord_user_id),)).fetchone()
        return row[0] if row else None


def get_discord_user_by_tag(cr_tag: str):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT discord_user_id
            FROM player_links
            WHERE cr_tag = ?
        """, (cr_tag,)).fetchone()
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


def get_all_links_by_tag():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT cr_tag, discord_user_id
            FROM player_links
        """).fetchall()
        return rows