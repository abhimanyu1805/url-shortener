from __future__ import annotations

import os
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./url_shortener.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session
