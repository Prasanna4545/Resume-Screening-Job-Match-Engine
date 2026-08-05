from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings
import os
import socket

settings = get_settings()

db_url = settings.DATABASE_URL

def is_postgres_reachable(url: str) -> bool:
    try:
        if not url.startswith("postgresql"):
            return False
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

# Fallback to sqlite if postgres is specified but unreachable or psycopg2 driver is missing
if db_url.startswith("postgresql"):
    if not is_postgres_reachable(db_url):
        db_url = "sqlite:///./local_dev.db"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True if db_url.startswith("postgresql") else False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


