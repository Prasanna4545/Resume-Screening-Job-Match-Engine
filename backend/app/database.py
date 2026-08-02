from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings
import os

settings = get_settings()

db_url = settings.DATABASE_URL

# Fallback to sqlite if postgres is specified but psycopg2 driver is not present locally
try:
    if db_url.startswith("postgresql"):
        import psycopg2
except ImportError:
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

