from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import os

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL is not set in environment variables!")

# Create SQLAlchemy engine
engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Connection manager
@contextmanager
def get_conn():
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# Initialize database (can create tables)
def init_db():
    with get_conn() as conn:
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
                date DATE,
                time TIME,
                parties TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW()
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
                date DATE,
                time TIME,
                parties TEXT,
                description TEXT,
                result TEXT,
                verdict TEXT,
                document TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

    return True
