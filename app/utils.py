"""Модуль вспомогательных функций."""

from typing import Any, Dict, List

from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import Follower, Like, Tweet, User
from app.schemas import UserProfileOut

allowed_extensions: set[str] = {'png', 'jpg', 'jpeg', 'gif'}


class CustomException(HTTPException):
    """
    Кастомное исключение для обработки ошибок HTTP.

    :param status_code: Код статуса HTTP.
    :param detail: Детали ошибки.
    """

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


def allowed_file(filename: str) -> bool:
    """
    Проверяет разрешенное расширение файла.

    :param filename: Имя файла для проверки.
    :return: Результат проверки (True, если разрешенное расширение, иначе False).
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


async def check_api_key(api_key: str = Header(...)) -> User:
    """
    Проверяет API-ключ пользователя.

    :param api_key: API-ключ пользователя.
    :return: Объект пользователя, если ключ действителен.
    :raises CustomException: Если ключ недействителен (401).
    """
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(User).filter(User.secret_key == api_key),
            )
            user = user.scalar_one_or_none()

            if not user:
                raise CustomException(status_code=401, detail="Invalid API Key")
            return user


async def check_user_exist(session, check_id: int):
    """
    Проверяет существование пользователя.

    :param session: Сессия базы данных.
    :param check_id: ID пользователя для проверки.
    :raises CustomException: Если пользователь не найден (404).
    """
    follow_user = await session.execute(
        select(User).
        where(User.id == check_id),
    )
    follow_user = follow_user.scalar_one_or_none()

    if not follow_user:
        raise CustomException(status_code=404, detail="User not found")


async def check_tweet_exist(session, check_id: int):
    """
    Проверяет существование твита.

    :param session: Сессия базы данных.
    :param check_id: ID твита для проверки.
    :return: Объект твита, если существует.
    :raises CustomException: Если твит не найден (404).
    """
    tweet = await session.execute(
        select(Tweet).
        options(selectinload(Tweet.likes)).
        where(Tweet.id == check_id),
    )
    tweet = tweet.scalar_one_or_none()

    if not tweet:
        raise CustomException(status_code=404, detail="Tweet not found")

    return tweet


async def check_like_exist(session, tweet_id: int, user_id: int):
    """
    Проверяет существование лайка.

    :param session: Сессия базы данных.
    :param tweet_id: ID твита.
    :param user_id: ID пользователя.
    :return: Объект лайка, если существует.
    """
    like = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id),
    )

    return like.scalar_one_or_none()


async def check_follow_exist(session, follow_id: int, user_id: int):
    """
    Проверяет существование подписки.

    :param session: Сессия базы данных.
    :param follow_id: ID пользователя, на которого подписываются.
    :param user_id: ID пользователя, который подписывается.
    :return: Объект подписки, если существует.
    """
    follow = await session.execute(
        select(Follower).
        where(Follower.followed_id == follow_id, Follower.follower_id == user_id),
    )

    return follow.scalar_one_or_none()


async def get_user_profile_data(user_id: int) -> UserProfileOut:
    """
    Получает данные профиля пользователя.

    :param user_id: ID пользователя.
    :return: Данные профиля пользователя.
    """
    async with async_session() as session:
        async with session.begin():
            await check_user_exist(session, user_id)
            query = select(User).filter(User.id == user_id).options(
                selectinload(User.followers).selectinload(Follower.follower),
                selectinload(User.following).selectinload(Follower.followed),
            )
            user_with_relationships = await session.execute(query)
            user_data = user_with_relationships.scalar()
            return UserProfileOut.from_db_user(user_data)


async def tweet_response(media_dict: Dict[int, Any], tweets: List[Tweet]) -> List[Dict[str, Any]]:
    """
    Формирует ответ на запрос твитов.

    :param media_dict: Словарь медиафайлов.
    :param tweets: Список твитов.
    :return: Список ответов на запрос твитов.
    """
    return [
        {
            "id": tweet.id,
            "content": tweet.tweet_data,
            "attachments": [
                media_dict.get(media_id, None) for media_id in tweet.tweet_media_ids
            ] if tweet.tweet_media_ids else [],
            "author": {"id": tweet.user.id, "name": tweet.user.name},
            "likes": [
                {"user_id": like.user.id, "name": like.user.name}
                for like in tweet.likes
            ] if tweet.likes else [],
        }
        for tweet in tweets
    ]
