import os

from sqlalchemy import MetaData, Table, engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL: str = os.getenv("DATABASE_URL")
Base: declarative_base = declarative_base()

metadata: MetaData = MetaData()

db_engine: AsyncEngine = create_async_engine(DATABASE_URL)
async_session: sessionmaker = sessionmaker(
    bind=db_engine, class_=AsyncSession, expire_on_commit=False,
)

INITIAL_DATA: dict[str: list] = {
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


def initialize_table(target: Table, connection: engine.Connection, **kw):
    """
    This method receives a table and a connection, and inserts data into that table.

    :param target: The target table to initialize.
    :type target: sqlalchemy.Table

    :param connection: The database connection to use for inserting data.
    :type connection: sqlalchemy.engine.Connection
    """
    table_name: str = str(target)

    if table_name in INITIAL_DATA and len(INITIAL_DATA[table_name]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[table_name])

