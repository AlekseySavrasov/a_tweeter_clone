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
    user = relationship("User", backref="tweets")

    def __repr__(self):
        return f"Твит: {self.tweet_data}"

    def to_json(self) -> Dict[str, Any]:
        return {c.tweet_data: getattr(self, c.tweet_data) for c in
                self.__table__.columns}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    secret_key = Column(String, nullable=False)

    def __repr__(self):
        return f"Пользователь {self.name}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, Sequence("media_id_seq"), primary_key=True, index=True)
    file = Column(String)  # возможно изменение типа колонки на LargeBinary


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, Sequence("like_id_seq"), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship("User", backref="likes")
    tweet_id = Column(Integer, ForeignKey('tweets.id'), index=True)
    tweet = relationship("Tweet", backref="likes")


class Follower(Base):
    __tablename__ = "followers"
    id = Column(Integer, Sequence("like_id_seq"), primary_key=True, index=True)
    src_id = Column(Integer, ForeignKey('users.id'), index=True)
    dst_id = Column(Integer, ForeignKey('users.id'), index=True)
    src_user = relationship("User", foreign_keys=[src_id])
    dst_user = relationship("User", foreign_keys=[dst_id])
