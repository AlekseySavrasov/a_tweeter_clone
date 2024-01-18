import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models import User, Follower, Tweet, Like
from app.database import async_session, Base, engine
from app.fastapi_app import create_app


async def check_api_key():
    return User(id=1, name="name_1", secret_key="test")


async def clone_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True, scope="session")
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def db():
    async with clone_async_session() as db:
        yield db


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=create_app(), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def mock_check_api_key():
    with MagicMock() as mock:
        mock.side_effect = check_api_key
        yield mock
