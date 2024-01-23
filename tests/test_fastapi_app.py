import os
from typing import Any, Dict, Optional

from httpx import AsyncClient
from sqlalchemy import select

from app.models import Follower, Tweet, Like, Media
from app.database import async_session


async def test_hello(client: AsyncClient):
    response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == ["Hello, World!"]


async def test_add_tweet(client: AsyncClient):
    tweet_data = {
        "tweet_data": "Test tweet",
        "tweet_media_ids": [1, 2, 3]
    }

    response = await client.post("/api/tweets", headers={"api-key": "test"}, json=tweet_data)
    assert response.status_code == 200
    assert response.json() == {"result": True, "tweet_id": 4}

    async with async_session() as session:
        result = await session.execute(select(Tweet).where(Tweet.id == 4))
        new_tweet = result.scalar()
        assert new_tweet.to_json() == {
            "id": 4,
            "tweet_data": "Test tweet",
            "tweet_media_ids": [1, 2, 3],
            "user_id": 1
        }


async def test_delete_tweet(client: AsyncClient):
    response = await client.delete(f"/api/tweets/{1}", headers={"api-key": "test"})
    assert response.status_code == 202
    assert response.json() == {"result": True}

    async with async_session() as session:
        result = await session.execute(select(Tweet).where(Tweet.id == 1))
        old_tweet = result.scalar()
        assert old_tweet is None


async def test_add_like(client: AsyncClient):
    response = await client.post(f"/api/tweets/{1}/likes", headers={"api-key": "test"})
    assert response.status_code == 201
    assert response.json() == {"result": True}

    async with async_session() as session:
        result = await session.execute(select(Like).where(Like.id == 4))
        new_like = result.scalar()
        assert new_like.to_json() == {
            "id": 4,
            "user_id": 1,
            "tweet_id": 1,
        }


async def test_delete_like(client: AsyncClient):
    response = await client.delete(f"/api/tweets/{2}/likes", headers={"api-key": "test_3"})
    assert response.status_code == 202
    assert response.json() == {"result": True}

    async with async_session() as session:
        result = await session.execute(select(Like).where(Like.id == 3))
        old_like = result.scalar()
        assert old_like is None


async def test_add_follow(client: AsyncClient):
    response = await client.post(f"/api/users/{3}/follow", headers={"api-key": "test_2"})
    assert response.status_code == 201
    assert response.json() == {"result": True}

    async with async_session() as session:
        result = await session.execute(
            select(Follower).where(Follower.follower_id == 2, Follower.followed_id == 3)
        )
        new_follow = result.scalar()
        assert new_follow is not None


async def test_delete_follow(client: AsyncClient):
    response = await client.delete(f"/api/users/{3}/follow", headers={"api-key": "test"})
    assert response.status_code == 202
    assert response.json() == {"result": True}

    async with async_session() as session:
        result = await session.execute(
            select(Follower).where(Follower.follower_id == 1, Follower.followed_id == 3)
        )
        old_follow = result.scalar()
        assert old_follow is None


async def test_get_user_tweets(client: AsyncClient):
    response = await client.get("/api/tweets", headers={"api-key": "test"})
    response_data = response.json()
    tweets_data = response_data["tweets"]
    tweet_data = tweets_data[0]

    assert response.status_code == 200
    assert response_data["result"] is True
    assert len(tweets_data) > 0

    for elem in ("id", "content", "attachments", "author", "likes"):
        assert elem in tweet_data


async def test_get_user_profile(client: AsyncClient):
    response = await client.get("/api/users/me", headers={"api-key": "test"})

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["result"] is True
    assert "user" in response_data
    assert response_data["user"]["id"] == 1
    assert response_data["user"]["name"] == "user_1"


async def test_get_user_by_id(client: AsyncClient):
    response = await client.get(f"/api/users/{2}", headers={"api-key": "test"})

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["result"] is True
    assert "user" in response_data
    assert response_data["user"]["id"] == 2
    assert response_data["user"]["name"] == "user_2"


async def test_upload_media(client: AsyncClient, cleanup_uploaded_files):
    files = {"file": ("test_file.jpg", b"Hello, this is a test file!")}
    response = await client.post("/api/medias", headers={"api-key": "test"}, files=files)
    assert response.status_code == 200
    assert response.json() == {"result": True, "media_id": 1}

    async with async_session() as session:
        media = await session.execute(select(Media).where(Media.id == 1))
        media = media.scalar_one()
        assert media is not None
        assert media.file_name.startswith("/static/images/")
