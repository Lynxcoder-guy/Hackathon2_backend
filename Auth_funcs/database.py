import os
from functools import lru_cache
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from Auth_funcs.crud_auth import Base

load_dotenv()


def createTableInCase(engine: Optional[Engine] = None) -> None:
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        columns = {
            column["name"] for column in inspect(connection).get_columns("users_auths")
        }
        if "assignedGroup" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE users_auths "
                    "ADD COLUMN assignedGroup VARCHAR(100) NULL"
                )
            )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_USER_AUTHENTICATION")
    if not database_url:
        raise RuntimeError("Set the DATABASE_USER_AUTHENTICATION environment variable")
    engine = create_engine(database_url)
    createTableInCase(engine)
    return engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
