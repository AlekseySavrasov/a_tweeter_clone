from typing import Dict, Any

from sqlalchemy import Column, String, Integer, Sequence

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

# print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)

    def __repr__(self):
        return f"Item {self.name}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}
