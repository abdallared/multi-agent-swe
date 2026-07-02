"""
One-time database setup script:
1. Creates the ai_software_db database if it doesn't exist
2. Creates all auth tables (users)
"""

import sys
import os

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Step 1: Create the database ───────────────────────────────────
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="abdoreda12",
        dbname="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("ai_software_db",))
    exists = cur.fetchone()

    if not exists:
        cur.execute("CREATE DATABASE ai_software_db")
        print("[OK] Database 'ai_software_db' created")
    else:
        print("[INFO] Database 'ai_software_db' already exists")

    cur.close()
    conn.close()
except Exception as e:
    print(f"[ERROR] Failed to connect/create database: {e}")
    sys.exit(1)

# ── Step 2: Create tables via SQLAlchemy ──────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:abdoreda12@localhost:5432/ai_software_db",
)

try:
    from auth.database import engine, Base
    import auth.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("[OK] Tables created successfully")

    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"[INFO] Tables in database: {tables}")

except Exception as e:
    print(f"[ERROR] Failed to create tables: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[DONE] Database setup complete! You can now start the backend.")
