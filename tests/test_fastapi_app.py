"""Модуль, содержащий тесты для маршрутов приложения."""

from typing import Any

from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session
from app.models import Follower, Like, Media, Tweet

test_headers = {
    1: {"api-key": "test"},
    2: {"api-key": "test_2"},
    3: {"api-key": "test_3"},
}


async def test_add_tweet(client: AsyncClient) -> None:
    """
    Тест для добавления твита через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    tweet_data: dict[str, Any] = {
        "tweet_data": "Test tweet",
        "tweet_media_ids": [1, 2, 3],
    }

    response = await client.post("/api/tweets", headers=test_headers[1], json=tweet_data)
    assert response.status_code == 201
    assert response.json() == {"result": True, "id": 4}

    async with async_session() as session:
        result_tweet = await session.execute(select(Tweet).where(Tweet.id == 4))
        new_tweet = result_tweet.scalar()
        assert new_tweet.to_json() == {
            "id": 4,
            "tweet_data": "Test tweet",
            "tweet_media_ids": [1, 2, 3],
            "user_id": 1,
        }


async def test_delete_tweet(client: AsyncClient) -> None:
    """
    Тест для удаления твита через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.delete(f"/api/tweets/{1}", headers=test_headers[1])
    assert response.status_code == 202
    assert response.json() == {"result": True}

    async with async_session() as session:
        result_tweet = await session.execute(select(Tweet).where(Tweet.id == 1))
        old_tweet = result_tweet.scalar()
        assert old_tweet is None


async def test_add_like(client: AsyncClient) -> None:
    """
    Тест для добавления лайка к твиту через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/tweets/{1}/likes", headers=test_headers[1])
    assert response.status_code == 201
    assert response.json() == {"result": True}

    async with async_session() as session:
        result_like = await session.execute(select(Like).where(Like.id == 5))
        new_like = result_like.scalar()
        assert new_like.to_json() == {
            "id": 5,
            "user_id": 1,
            "tweet_id": 1,
        }


async def test_add_like_with_null_tweet(client: AsyncClient) -> None:
    """
    Тест для добавления лайка к несуществующему твиту через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/tweets/{10}/likes", headers=test_headers[1])
    assert response.status_code == 404
    assert response.json() == {"error_message": "Tweet not found", "error_type": "CustomException"}


async def test_add_like_which_exists(client: AsyncClient) -> None:
    """
    Тест для попытки добавления существующего лайка к твиту через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/tweets/{2}/likes", headers=test_headers[1])
    assert response.status_code == 400
    assert response.json() == {"error_message": "Like already exists!", "error_type": "CustomException"}


async def test_delete_like(client: AsyncClient) -> None:
    """
    Тест для удаления лайка к твиту через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.delete(f"/api/tweets/{1}/likes", headers=test_headers[3])
    assert response.status_code == 202
    assert response.json() == {"result": True}

    async with async_session() as session:
        result = await session.execute(select(Like).where(Like.id == 3))
        old_like = result.scalar()
        assert old_like is None


async def test_add_follow(client: AsyncClient) -> None:
    """
    Тест для добавления подписки на пользователя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/users/{3}/follow", headers=test_headers[2])
    assert response.status_code == 201
    assert response.json() == {"result": True}

    async with async_session() as session:
        result_follow = await session.execute(
            select(Follower).
            where(Follower.follower_id == 2, Follower.followed_id == 3),
        )
        new_follow = result_follow.scalar()
        assert new_follow is not None


async def test_add_follow_which_exist(client: AsyncClient) -> None:
    """
    Тест для попытки добавления существующей подписки на пользователя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/users/{2}/follow", headers=test_headers[1])
    assert response.status_code == 400
    assert response.json() == {"error_message": "Follow already exists!", "error_type": "CustomException"}


async def test_add_follow_yourself(client: AsyncClient) -> None:
    """
    Тест для попытки подписки на самого себя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/users/{1}/follow", headers=test_headers[1])
    assert response.status_code == 400
    assert response.json() == {
        "error_message": "The current user can't follow himself",
        "error_type": "CustomException",
    }


async def test_add_follow_null_user(client: AsyncClient) -> None:
    """
    Тест для попытки добавления подписки на несуществующего пользователя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.post(f"/api/users/{10}/follow", headers=test_headers[1])
    assert response.status_code == 404
    assert response.json() == {"error_message": "User not found", "error_type": "CustomException"}


async def test_delete_follow(client: AsyncClient) -> None:
    """
    Тест для удаления подписки на пользователя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.delete(f"/api/users/{3}/follow", headers=test_headers[1])
    assert response.status_code == 202
    assert response.json() == {"result": True}

    async with async_session() as session:
        result_follow = await session.execute(
            select(Follower).
            where(Follower.follower_id == 1, Follower.followed_id == 3),
        )
        old_follow = result_follow.scalar()

        assert old_follow is None


async def test_get_user_tweets(client: AsyncClient) -> None:
    """
    Тест для получения твитов пользователя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.get("/api/tweets", headers=test_headers[1])
    response_data = response.json()
    tweets_data = response_data["tweets"]
    tweet_data = tweets_data[0]

    assert response.status_code == 200
    assert response_data["result"] is True

    for elem in ("id", "content", "attachments", "author", "likes"):
        assert elem in tweet_data


async def test_get_user_profile(client: AsyncClient) -> None:
    """
    Тест для получения профиля пользователя через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.get("/api/users/me", headers=test_headers[1])

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["result"] is True
    assert "user" in response_data
    assert response_data["user"]["id"] == 1
    assert response_data["user"]["name"] == "user_1"


async def test_get_user_by_id(client: AsyncClient) -> None:
    """
    Тест для получения пользователя по ID через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.get(f"/api/users/{2}", headers=test_headers[1])

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["result"] is True
    assert "user" in response_data
    assert response_data["user"]["id"] == 2
    assert response_data["user"]["name"] == "user_2"


async def test_get_null_user_by_id(client: AsyncClient) -> None:
    """
    Тест для получения несуществующего пользователя по ID через API.

    :param client: Клиент для отправки запросов API.
    :return: None
    """
    response = await client.get(f"/api/users/{10}", headers=test_headers[1])
    assert response.status_code == 404
    assert response.json() == {"error_message": "User not found", "error_type": "CustomException"}


async def test_upload_media(client: AsyncClient, cleanup_uploaded_files) -> None:
    """
    Тест для загрузки медиафайла через API.

    :param client: Клиент для отправки запросов API.
    :param cleanup_uploaded_files: Фикстура для очистки загруженных файлов после теста.
    :return: None
    """
    files = {"file": ("test_file.jpg", b"Hello, this is a test file!")}
    response = await client.post("/api/medias", headers=test_headers[1], files=files)
    assert response.status_code == 201
    assert response.json() == {"result": True, "media_id": 1}

    async with async_session() as session:
        media = await session.execute(select(Media).where(Media.id == 1))
        media = media.scalar_one()
        assert media is not None
        assert media.file_name.startswith("/static/images/")


async def test_upload_wrong_media(client: AsyncClient, cleanup_uploaded_files) -> None:
    """
    Тест для загрузки медиафайла неподдерживаемого типа через API.

    :param client: Клиент для отправки запросов API.
    :param cleanup_uploaded_files: Фикстура для очистки загруженных файлов после теста.
    :return: None
    """
    files = {"file": ("test_file.txt", b"Hello, this is a test file!")}
    response = await client.post("/api/medias", headers=test_headers[1], files=files)
    assert response.status_code == 400
    assert response.json() == {"error_message": "Invalid file type", "error_type": "CustomException"}
