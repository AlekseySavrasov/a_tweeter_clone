from typing import Any, Dict, Optional

import pytest

from httpx import AsyncClient
from sqlalchemy import select

from app.models import User, Follower, Tweet, Like
from app.database import async_session


async def test_hello(client: AsyncClient):
    response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == ["Hello, World!"]


async def test_add_tweet(client: AsyncClient):
    async with async_session() as session:

        tweet_data = {
            "tweet_data": "Test tweet",
            "tweet_media_ids": [1, 2, 3]
        }

        response = await client.post("/api/tweets", headers={"api-key": "test"}, json=tweet_data)

        assert response.status_code == 200
        assert response.json() == {"result": True, "tweet_id": 4}

        result = await session.execute(select(Tweet).where(Tweet.id == 4))
        new_tweet = result.scalar()

        assert new_tweet.to_json() == {
            "id": 4,
            "tweet_data": "Test tweet",
            "tweet_media_ids": [1, 2, 3],
            "user_id": 1
        }


async def test_delete_tweet(client: AsyncClient):
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": [1, 2, 3]}

    async with async_session() as session:

        response = await client.post(f"/api/tweets", headers={"api-key": "test"}, json=tweet_data)
        assert response.status_code == 200
        assert response.json() == {"result": True, "tweet_id": 4}

        response = await client.delete(f"/api/tweets/{4}", headers={"api-key": "test"})
        assert response.status_code == 202
        assert response.json() == {"result": True}

        result = await session.execute(select(Tweet).where(Tweet.id == 4))
        new_tweet = result.scalar()

        assert new_tweet is None
