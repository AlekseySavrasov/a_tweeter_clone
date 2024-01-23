import asyncio
import os
from typing import MutableMapping, Any

import pytest_asyncio
from httpx import AsyncClient
from asgi_lifespan import LifespanManager


from app.database import engine, metadata
from app.fastapi_app import create_app, UPLOAD_DIR


@pytest_asyncio.fixture(scope="function")
async def app() -> MutableMapping[str, Any]:
    loop = asyncio.get_running_loop()
    app = create_app()
    yield app


@pytest_asyncio.fixture(autouse=True, scope="function")
async def prepare_db(app):
    loop = asyncio.get_running_loop()
    async with LifespanManager(app):
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(app):
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client


@pytest_asyncio.fixture(scope="function")
def cleanup_uploaded_files():
    yield
    uploaded_files = os.listdir(UPLOAD_DIR)

    for file_name in uploaded_files:
        if file_name.startswith("test_file"):
            os.remove(os.path.join(UPLOAD_DIR, file_name))
