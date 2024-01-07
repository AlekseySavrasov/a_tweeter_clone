from typing import List, Optional

from pydantic import BaseModel


class TweetIn(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class TweetOut(BaseModel):
    result: bool
    id: int


class MediaResponse(BaseModel):
    result: bool
    media_id: int


class OperationResult(BaseModel):
    result: bool
