import sqlite3
from config import DB_PATH

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            username      TEXT,
            bot_name      TEXT NOT NULL,
            folder        TEXT NOT NULL,
            files_json    TEXT NOT NULL,
            github_links  TEXT NOT NULL,
            status        TEXT DEFAULT 'pending',   -- pending | running | stopped
            ping_url      TEXT,
            ping_user     TEXT,
            ping_pass     TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

def add_bot(user_id, username, bot_name, folder, files_json, github_links):
    con = sqlite3.connect(DB_PATH)
    cur = con.execute(
        "INSERT INTO bots (user_id, username, bot_name, folder, files_json, github_links) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, username, bot_name, folder, files_json, github_links)
    )
    con.commit()
    bot_id = cur.lastrowid
    con.close()
    return bot_id

def set_running(bot_id, ping_url, ping_user, ping_pass):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "UPDATE bots SET status='running', ping_url=?, ping_user=?, ping_pass=? WHERE id=?",
        (ping_url, ping_user, ping_pass, bot_id)
    )
    con.commit(); con.close()

def set_status(bot_id, status):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE bots SET status=? WHERE id=?", (status, bot_id))
    con.commit(); con.close()

def get_bot(bot_id):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM bots WHERE id=?", (bot_id,)).fetchone()
    con.close()
    return dict(row) if row else None

def get_user_bots(user_id):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM bots WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    con.close()
    return [dict(r) for r in rows]
