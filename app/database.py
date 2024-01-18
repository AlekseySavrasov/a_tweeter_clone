from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from settings import site

DATABASE_URL: str = (f"postgresql+asyncpg://{site.db_user.get_secret_value()}"
                     f":{site.db_pass.get_secret_value()}@{site.db_name.get_secret_value()}")
Base = declarative_base()

metadata = MetaData()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)
