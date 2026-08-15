from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from university_catalog.config import get_settings

engine = None
SessionLocal = None


def get_engine():
    global engine
    if engine is None:
        settings = get_settings()
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False}
            if "sqlite" in settings.database_url
            else {},
            echo=False,
        )
        if "sqlite" in settings.database_url:

            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    return engine


def get_session_factory():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    from university_catalog.models import Base

    Base.metadata.create_all(bind=get_engine())
