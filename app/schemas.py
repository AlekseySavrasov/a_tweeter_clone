from typing import List, Optional

from pydantic import BaseModel


class OperationOut(BaseModel):
    result: bool


class MediaOut(OperationOut):
    media_id: int


class TweetIn(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


class TweetOut(OperationOut):
    id: int


class Author(BaseModel):
    id: int
    name: str


class Like(BaseModel):
    user_id: int
    name: str


class Tweet(BaseModel):
    id: int
    content: str
    attachments: List[str] = []
    author: Author
    likes: List[Like] = []


class ErrorResponse(BaseModel):
    error_type: str
    error_message: str


class TweetsOut(OperationOut):
    tweets: List[Tweet]


class UserProfileOut(OperationOut):
    user: Author
    followers: Optional[List[Author]] = []
    following: Optional[List[Author]] = []

    @classmethod
    def from_db_user(cls, user_with_relationships):
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
            following=following
        )
