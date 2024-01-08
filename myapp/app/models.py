from typing import Dict, Any

from sqlalchemy import Column, String, Integer, Sequence, ARRAY, ForeignKey, LargeBinary

from app.database import Base
from sqlalchemy.orm import relationship


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, Sequence("tweet_id_seq"), primary_key=True, index=True)
    tweet_data = Column(String(280), nullable=False)
    tweet_media_ids = Column(ARRAY(Integer))
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship("User", back_populates="tweets", lazy="joined")
    likes = relationship("Like", back_populates="tweet", lazy="joined")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    secret_key = Column(String, nullable=False)
    tweets = relationship("Tweet", back_populates="user")
    likes = relationship("Like", back_populates="user")


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, Sequence("media_id_seq"), primary_key=True, index=True)
    file = Column(String)  # возможно изменение типа колонки на LargeBinary


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, Sequence("like_id_seq"), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship("User", back_populates="likes", lazy="joined")
    tweet_id = Column(Integer, ForeignKey('tweets.id'), index=True)
    tweet = relationship("Tweet", back_populates="likes", lazy="joined")


class Follower(Base):
    __tablename__ = "followers"
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
