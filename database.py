import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set!")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
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
            );
        """))

        conn.execute(text("""
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
            );
        """))

def get_conn():
    return engine.connect()
