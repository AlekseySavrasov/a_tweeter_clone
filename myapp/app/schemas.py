from typing import List, Optional

from pydantic import BaseModel


class TweetIn(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


class TweetOut(BaseModel):
    result: bool
    id: int


class MediaResponse(BaseModel):
    result: bool
    media_id: int


class OperationResult(BaseModel):
    result: bool


class UserDetail(BaseModel):
    id: int
    name: str


class Like(BaseModel):
    user_id: int
    name: str


class TweetResponse(BaseModel):
    id: Optional[int] = None
    content: Optional[str] = None
    attachments: Optional[List[int]] = []
    author: Optional[UserDetail] = None
    likes: Optional[List[Like]] = []


class UserProfileResponse(BaseModel):
    result: bool
    user: UserDetail
    followers: Optional[List[UserDetail]] = []
    following: Optional[List[UserDetail]] = []
