from typing import Any

import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session, declarative_base

from config import configs

engine = create_async_engine(configs.DATABASE_URI)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@sqlalchemy.orm.as_declarative()
class BaseModel:
    id: Any
    __name__: str

    @declared_attr
    def metadata(cls):
        return Base.metadata


Base = declarative_base(cls=BaseModel)


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=True)

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._engine)

    async def session(self) -> Session:
        async with async_session_maker() as session:
            yield session


async def get_async_session():
    async with async_session_maker() as session:
        yield session
