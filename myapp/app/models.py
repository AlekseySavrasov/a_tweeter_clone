from typing import Dict, Any

from sqlalchemy import Column, String, Integer, Sequence, ARRAY, ForeignKey, LargeBinary

from app.database import Base
from sqlalchemy.orm import relationship


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, Sequence("like_id_seq"), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), index=True)
    user = relationship("User", back_populates="likes", lazy="select")
    tweet = relationship("Tweet", back_populates="likes", lazy="select")


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, Sequence("tweet_id_seq"), primary_key=True, index=True)
    tweet_data = Column(String(280), nullable=False)
    tweet_media_ids = Column(ARRAY(Integer))
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship("User", back_populates="tweets", lazy="select")
    likes = relationship("Like", back_populates="tweet", lazy="joined", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    secret_key = Column(String, nullable=False)
    tweets = relationship("Tweet", back_populates="user", lazy="select")
    likes = relationship("Like", back_populates="user", lazy="select")
    followers = relationship(
        "Follower",
        foreign_keys="Follower.followed_id",
        back_populates="followed",
        lazy="selectin",
    )
    following = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        back_populates="follower",
        lazy="selectin",
    )


class Follower(Base):
    __tablename__ = "followers"
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, Sequence("media_id_seq"), primary_key=True, index=True)
    file = Column(String)  # возможно изменение типа колонки на LargeBinary
