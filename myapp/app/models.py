from typing import Dict, Any

from sqlalchemy import Column, String, Integer, Sequence
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


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)

    def __repr__(self):
        return f"Item {self.name}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}
