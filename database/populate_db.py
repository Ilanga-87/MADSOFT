import asyncio
import logging

from sqlalchemy import insert

from db import Base, engine, async_session_maker
from models.media_models import Meme
from population_data import data


async def populate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        for item in data:
            stmt = insert(Meme).values(item)
            await session.execute(stmt)
            await session.commit()
        logging.info("Database was populated")


async def main():
    await populate()


if __name__ == "__main__":
    asyncio.run(main())
