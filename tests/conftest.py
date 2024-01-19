import asyncio
import os
from typing import Generator, AsyncGenerator

import pytest
from httpx import AsyncClient
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models import User, Follower, Tweet, Like
from app.database import async_session, Base, engine
from app.fastapi_app import create_app


@pytest.fixture(autouse=True, scope="session")
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all(bind=engine))
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=create_app(), base_url="http://test") as ac:
        yield ac

