"""Модуль описания схем ответов."""

from typing import List, Optional

from pydantic import BaseModel


class OperationOut(BaseModel):
    """Общая модель для операций, возвращающих результат."""

    result: bool


class MediaOut(OperationOut):
    """Модель данных для медиафайла с дополнительным идентификатором."""

    media_id: int


class TweetIn(BaseModel):
    """Модель данных для создания твита."""

    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


class TweetOut(OperationOut):
    """Модель данных для результата операции создания твита с идентификатором."""

    id: int


class Author(BaseModel):
    """Модель данных для автора твита."""

    id: int
    name: str


class Like(BaseModel):
    """Модель данных для лайка твита."""

    user_id: int
    name: str


class Tweet(BaseModel):
    """Модель данных для твита."""

    id: int
    content: str
    attachments: List[str] = []
    author: Author
    likes: List[Like] = []


class ErrorResponse(BaseModel):
    """Модель данных для ответа с ошибкой."""

    error_type: str
    error_message: str


class TweetsOut(OperationOut):
    """Модель данных для ответа, содержащего список твитов."""

    tweets: List[Tweet]


class UserProfileOut(OperationOut):
    """Модель данных для профиля пользователя."""

    user: Author
    followers: Optional[List[Author]] = []
    following: Optional[List[Author]] = []

    @classmethod
    def from_db_user(cls, user_with_relationships):
        """
        Создает объект класса UserProfileOut из объекта пользователя из базы данных.

        :param user_with_relationships: Объект пользователя с отношениями (подписчики и подписки).
        :return: Объект класса UserProfileOut.
        """
        followers = [
            follower.follower.to_json()
            for follower in user_with_relationships.followers
        ] if user_with_relationships.followers else []

        following = [
            followed.followed.to_json()
            for followed in user_with_relationships.following
        ] if user_with_relationships.following else []

        return cls(
            result=True,
            user=user_with_relationships.to_json(),
            followers=followers,
            following=following,
        )
