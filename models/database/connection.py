from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

SQLALCHEMY_DATABASE_URL = "sqlite:///./jobs.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Specific to SQLite
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize database tables."""
    from .schemas import Base
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Generator:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()