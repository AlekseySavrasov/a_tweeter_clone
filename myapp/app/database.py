from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL: str = "postgresql+asyncpg://admin:admin@postgres"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)

Base = declarative_base()
