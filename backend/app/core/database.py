from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# In production, check config.py for assembling DATABASE_URL properly.
# Echo is enabled only in debug/development environment for query inspection.
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG and settings.ENVIRONMENT == "development",
    pool_pre_ping=True,  # Automatically verify connection viability before checking it out
)

# SQLAlchemy 2.0 Sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 base class.
    Uses PEP 593 Annotated types or type hints for modern model definitions.
    """
    pass


def get_db() -> Generator:
    """
    FastAPI dependency injection helper to yield a database session context per request.
    Ensures the session is automatically closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
