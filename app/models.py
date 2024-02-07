"""Модуль для работы с моделями."""

from typing import Any, Dict

from sqlalchemy import ARRAY, Column, ForeignKey, Integer, MetaData, Sequence, String
from sqlalchemy.orm import relationship

from app.database import Base, metadata

MAX_TWEET_LENGTH: int = 280
MAX_NAME_LENGTH: int = 50


class Like(Base):
    """
    Модель представляющая сущность "Лайк".

    :param id: Уникальный идентификатор лайка.
    :param user_id: Идентификатор пользователя, поставившего лайк.
    :param tweet_id: Идентификатор твита, которому поставлен лайк.
    :param user: Связь с моделью пользователя, поставившего лайк.
    :param tweet: Связь с моделью твита, которому поставлен лайк.
    """

    __tablename__: str = "likes"
    metadata: MetaData = metadata

    id: int = Column(Integer, Sequence("like_id_seq"), primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), index=True)
    tweet_id: int = Column(Integer, ForeignKey('tweets.id'), index=True)
    user: relationship = relationship("User", back_populates="likes", lazy="select")
    tweet: relationship = relationship("Tweet", back_populates="likes", lazy="select")

    def to_json(self) -> Dict[str, Any]:
        """
        Преобразует объект Like в формат JSON.

        :return: Словарь с данными объекта Like.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Tweet(Base):
    """
    Модель представляющая сущность "Твит".

    :param id: Уникальный идентификатор твита.
    :param tweet_data: Текст твита.
    :param tweet_media_ids: Идентификаторы медиафайлов в твите.
    :param user_id: Идентификатор пользователя, создавшего твит.
    :param user: Связь с моделью пользователя, создавшего твит.
    :param likes: Связь с моделью лайков, поставленных к твиту.
    """

    __tablename__: str = "tweets"
    metadata: MetaData = metadata

    id: int = Column(Integer, Sequence("tweet_id_seq"), primary_key=True, index=True)
    tweet_data: str = Column(String(MAX_TWEET_LENGTH), nullable=False)
    tweet_media_ids = Column(ARRAY(Integer))
    user_id: int = Column(Integer, ForeignKey('users.id'), index=True)
    user: relationship = relationship("User", back_populates="tweets", lazy="select")
    likes: relationship = relationship("Like", back_populates="tweet", lazy="joined", cascade="all, delete-orphan")

    def repr(self):
        """
        Возвращает строковое представление объекта Tweet.

        :return: Строковое представление объекта Tweet.
        """
        return f"Tweet: {self.tweet_data}"

    def to_json(self) -> Dict[str, Any]:
        """
        Преобразует объект Tweet в формат JSON.

        :return: Словарь с данными объекта Tweet.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class User(Base):
    """
    Модель представляющая сущность "Пользователь".

    :param id: Уникальный идентификатор пользователя.
    :param name: Имя пользователя.
    :param secret_key: Секретный ключ пользователя.
    :param tweets: Связь с моделью твитов, созданных пользователем.
    :param likes: Связь с моделью лайков, которые поставил пользователь.
    :param followers: Связь с моделью подписчиков пользователя.
    :param following: Связь с моделью пользователей, на которых подписан пользователь.
    """

    __tablename__: str = "users"
    metadata: MetaData = metadata

    id: int = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    name: str = Column(String(MAX_NAME_LENGTH), nullable=False)
    secret_key: str = Column(String, nullable=False)
    tweets: relationship = relationship("Tweet", back_populates="user", lazy="select")
    likes: relationship = relationship("Like", back_populates="user", lazy="select")
    followers: relationship = relationship(
        "Follower",
        foreign_keys="Follower.followed_id",
        back_populates="followed",
        lazy="selectin",
    )
    following: relationship = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        back_populates="follower",
        lazy="selectin",
    )

    def repr(self):
        """
        Возвращает строковое представление объекта User.

        :return: Строковое представление объекта User.
        """
        return f"User: {self.name}"

    def to_json(self) -> Dict[str, Any]:
        """
        Преобразует объект User в формат JSON.

        :return: Словарь с данными объекта User.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Follower(Base):
    """
    Модель представляющая сущность "Подписчик".

    :param follower_id: Идентификатор пользователя, который подписывается.
    :param followed_id: Идентификатор пользователя, на которого подписываются.
    :param follower: Связь с моделью пользователя, который подписывается.
    :param followed: Связь с моделью пользователя, на которого подписываются.
    """

    __tablename__: str = "followers"
    metadata: MetaData = metadata

    follower_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followed_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True)

    follower: relationship = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed: relationship = relationship("User", foreign_keys=[followed_id], back_populates="followers")


class Media(Base):
    """
    Модель представляющая сущность "Медиа".

    :param id: Уникальный идентификатор медиа.
    :param file_name: Название файла медиа.
    """

    __tablename__: str = "medias"
    metadata: MetaData = metadata

    id: int = Column(Integer, Sequence("media_id_seq"), primary_key=True, index=True)
    file_name: str = Column(String)
