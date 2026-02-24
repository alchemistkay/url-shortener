import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

# Reads variables from .env file
# This way we NEVER hardcode passwords!
load_dotenv()

# os.getenv() reads environment variables
# Second argument is default value if not found
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "urlshortener")

# ============================================
# BUILD DATABASE URL
# ============================================

# Format: postgresql://user:password@host:port/database
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

print(f"Connecting to: postgresql://{POSTGRES_USER}:****"
      f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# ============================================
# ENGINE
# ============================================
engine = create_engine(
    DATABASE_URL,
    echo=True  # Log all SQL - great for learning!
)

# ============================================
# SESSION
# ============================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================
# BASE
# ============================================
Base = declarative_base()

# ============================================
# DEPENDENCY
# ============================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()