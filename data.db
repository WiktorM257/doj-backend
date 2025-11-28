import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Tabela aktywnych spraw
    c.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id TEXT PRIMARY KEY,
        name TEXT,
        judge TEXT,
        prosecutor TEXT,
        defendant TEXT,
        lawyer TEXT,
        witnesses TEXT,
        room TEXT,
        date TEXT,
        time TEXT,
        parties TEXT,
        description TEXT
    )
    """)

    # Tabela archiwum
    c.execute("""
    CREATE TABLE IF NOT EXISTS archive (
        id TEXT PRIMARY KEY,
        name TEXT,
        judge TEXT,
        prosecutor TEXT,
        defendant TEXT,
        lawyer TEXT,
        witnesses TEXT,
        room TEXT,
        date TEXT,
        time TEXT,
        parties TEXT,
        description TEXT,
        result TEXT,
        verdict TEXT,
        document TEXT
    )
    """)

    conn.commit()
    conn.close()
