from typing import List

from pydantic import BaseModel


class BaseTweet(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int] = []


class TweetIn(BaseTweet):
    ...


class TweetOut(BaseModel):
    result: bool
    id: int


class MediaResponse(BaseModel):
    result: bool
    media_id: int
