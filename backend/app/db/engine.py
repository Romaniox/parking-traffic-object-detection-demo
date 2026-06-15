from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str):
    # check_same_thread=False: FastAPI may use the connection across threads.
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def init_db(engine) -> None:
    # Import models so they are registered on Base before create_all.
    from app.db import models  # noqa: F401

    Base.metadata.create_all(engine)
