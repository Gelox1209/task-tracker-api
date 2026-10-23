"""Database setup: creates the engine and gives each request its own session."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite for now; later you can point this at PostgreSQL via an env variable.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

engine = create_engine(
    DATABASE_URL,
    # Needed only for SQLite, which by default allows one thread per connection.
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: opens a DB session for a request, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
