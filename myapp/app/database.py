import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
env_variables = os.environ

database_user = env_variables.get("POSTGRES_USER")
database_psw = env_variables.get("POSTGRES_PASSWORD")
database_db = env_variables.get("POSTGRES_DB")

DATABASE_URL = f"postgresql+asyncpg://{database_user}:{database_psw}@{database_db}"

print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)
Base = declarative_base()
