import os
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

metadata = MetaData()

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
)

INITIAL_DATA = {
    "users": [
            {"name": "user_1", "secret_key": "test"},
            {"name": "user_2", "secret_key": "test_2"},
            {"name": "user_3", "secret_key": "test_3"},
      ],
    "followers": [
        {"follower_id": 3, "followed_id": 1},
        {"follower_id": 1, "followed_id": 2},
        {"follower_id": 1, "followed_id": 3},
      ],
    "tweets": [
        {"tweet_data": "Good day ^_^", "user_id": 1},
        {"tweet_data": "What's up???", "user_id": 2},
        {"tweet_data": "The message has been deleted by admin", "user_id": 3},
      ],
    "likes": [
        {"user_id": 2, "tweet_id": 1},
        {"user_id": 1, "tweet_id": 2},
        {"user_id": 3, "tweet_id": 1},
        {"user_id": 3, "tweet_id": 2},
    ]
}


def initialize_table(target, connection, **kw):
    """This method receives a table, a connection and inserts data to that table"""
    table_name = str(target)

    if table_name in INITIAL_DATA and len(INITIAL_DATA[table_name]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[table_name])
