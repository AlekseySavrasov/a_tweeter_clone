import os

import pytest_asyncio
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from app.database import db_engine, metadata
from app.fastapi_app import app, UPLOAD_DIR


@pytest_asyncio.fixture(autouse=True, scope="function")
async def prepare_db() -> None:
    """
    Подготавливает базу данных перед выполнением тестов.

    Создает все таблицы базы данных перед тестированием и удаляет их после тестирования.

    :return: None
    """
    async with LifespanManager(app):
        async with db_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        yield
        async with db_engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
    """
    Создает клиент для отправки запросов API.

    :return: Клиент для отправки запросов API.
    """
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client


@pytest_asyncio.fixture(scope="function")
def cleanup_uploaded_files() -> None:
    """
    Очищает загруженные файлы после выполнения тестов.

    :return: None
    """
    yield
    uploaded_files: list[str] = os.listdir(UPLOAD_DIR)

    for file_name in uploaded_files:
        if file_name.startswith("test_file"):
            os.remove(os.path.join(UPLOAD_DIR, file_name))
