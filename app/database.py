import os
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:admin@postgres:5432/postgres")
Base = declarative_base()

metadata = MetaData()

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)
