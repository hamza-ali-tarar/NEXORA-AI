from collections.abc import Generator

from sqlalchemy import create_engine  # type: ignore[reportMissingImports]
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker  # type: ignore[reportMissingImports]

from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()