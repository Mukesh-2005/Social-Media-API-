# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# Try to get DATABASE_URL, but default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, use SQLite (works everywhere!)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./social_media_api.db"
    print(" Using SQLite (DATABASE_URL not found)")
else:
    print(f" Using MySQL/Cloud database")

print(f"Database: {DATABASE_URL}")

# Create engine
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"charset": "utf8mb4"}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
