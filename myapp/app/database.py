from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import site

DATABASE_URL: str = (f"postgresql+asyncpg://{site.database_user.get_secret_value()}:"
                     f"{site.database_psw.get_secret_value()}@{site.database_db}")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)

Base = declarative_base()
