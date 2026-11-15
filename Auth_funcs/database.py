import os
from functools import lru_cache
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import Base

load_dotenv()


@lru_cache(maxsize=1)
def get_engine():
    database_url = os.getenv("DATABASE_USER_AUTHENTICATION")
    if not database_url:
        raise RuntimeError("Set the DATABASE_USER_AUTHENTICATION environment variable")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
