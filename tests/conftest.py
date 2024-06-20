import asyncio
import warnings

import pytest
import pytest_asyncio

from config import configs
from database.db import Database, get_async_session


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_session():
    db = Database(configs.DATABASE_URI)
    db.create_database()
    async with get_async_session() as session:
        yield session
