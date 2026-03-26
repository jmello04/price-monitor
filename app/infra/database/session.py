"""Database engine and session factory configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from typing import Generator

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after use.

    Yields:
        An active SQLAlchemy Session bound to the application engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined in the ORM metadata if they do not yet exist."""
    Base.metadata.create_all(bind=engine)
