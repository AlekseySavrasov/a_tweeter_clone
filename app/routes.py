import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import Follower, Like, Media, Tweet, User
from app.schemas import TweetIn, TweetOut, MediaOut, OperationOut, TweetsOut, UserProfileOut
from app.utils import (check_api_key, check_like_exist, check_tweet_exist, check_user_exist, check_follow_exist,
                       CustomException, get_user_profile_data, allowed_file, tweet_response)

STATIC_PATH = Path(__file__).parent.parent / "static"
UPLOAD_DIR = "static/images"

router = APIRouter(
    prefix="/api",
    tags=["api"]
)


@router.post("/tweets", status_code=201, response_model=TweetOut)
async def add_tweet(data: TweetIn, user: User = Depends(check_api_key)):
    """Добавление нового твита"""
    if not data:
        raise CustomException(status_code=400, detail="Invalid tweet data")

    tweet = Tweet(tweet_data=data.tweet_data, tweet_media_ids=data.tweet_media_ids, user_id=user.id)

    async with async_session() as session:
        async with session.begin():
            session.add(tweet)
            await session.flush()
            tweet_id = tweet.id if tweet else None

    return TweetOut(result=True, id=tweet_id)


@router.delete("/tweets/{tweet_id}", status_code=202, response_model=OperationOut)
async def delete_tweet(tweet_id: int, user: User = Depends(check_api_key)):
    """Удаляем твит по его идентификатору"""
    async with async_session() as session:
        async with session.begin():
            tweet = await check_tweet_exist(session=session, check_id=tweet_id)

            if tweet.user_id != user.id:
                raise CustomException(status_code=403, detail="You are not allowed to delete this tweet")

            await session.delete(tweet)
            await session.commit()

    return OperationOut(result=True)


@router.post("/tweets/{tweet_id}/likes", status_code=201, response_model=OperationOut)
async def add_like(tweet_id: int, user: User = Depends(check_api_key)):
    """Установление лайка на твит по id"""
    async with async_session() as session:
        async with session.begin():
            await check_tweet_exist(session=session, check_id=tweet_id)

            if await check_like_exist(session=session, tweet_id=tweet_id, user_id=user.id):
                raise CustomException(status_code=400, detail="Like already exists!")

            like = Like(tweet_id=tweet_id, user_id=user.id)
            session.add(like)
            await session.flush()

    return OperationOut(result=True)


@router.delete("/tweets/{tweet_id}/likes", status_code=202, response_model=OperationOut)
async def delete_like(tweet_id: int, user: User = Depends(check_api_key)):
    """Удаление лайка с твита"""
    async with async_session() as session:
        async with session.begin():
            await check_tweet_exist(session=session, check_id=tweet_id)

            unlike = await check_like_exist(session=session, tweet_id=tweet_id, user_id=user.id)

            if not unlike:
                raise CustomException(status_code=404, detail="Like not found")

            await session.delete(unlike)
            await session.commit()

    return OperationOut(result=True)


@router.post("/users/{follow_id}/follow", status_code=201, response_model=OperationOut)
async def add_follow(follow_id: int, user: User = Depends(check_api_key)):
    """Follow другого пользователя по id"""
    if follow_id == user.id:
        raise CustomException(status_code=400, detail="The current user can't follow himself")

    async with async_session() as session:
        async with session.begin():
            await check_user_exist(session=session, check_id=follow_id)

            follow = await check_follow_exist(session=session, follow_id=follow_id, user_id=user.id)

            if follow:
                raise CustomException(status_code=400, detail="Follow already exists!")

            follow = Follower(follower_id=user.id, followed_id=follow_id)
            session.add(follow)
            await session.flush()

    return OperationOut(result=True)


@router.delete("/users/{follow_id}/follow", status_code=202, response_model=OperationOut)
async def delete_follow(follow_id: int, user: User = Depends(check_api_key)):
    """Unfollow другого пользователя"""
    async with async_session() as session:
        async with session.begin():
            unfollow = await check_follow_exist(session=session, follow_id=follow_id, user_id=user.id)

            if not unfollow:
                raise CustomException(status_code=404, detail="Follow not found")

            await session.delete(unfollow)
            await session.commit()

    return OperationOut(result=True)


@router.get("/tweets", response_model=TweetsOut)
async def get_user_tweets(user: User = Depends(check_api_key)):
    try:
        async with async_session() as session:
            async with session.begin():
                users_with_tweets = await session.execute(
                    select(User)
                    .filter(Follower.follower_id == user.id)
                    .join(Follower, User.id == Follower.followed_id)
                    .options(
                        selectinload(User.tweets).selectinload(Tweet.likes).selectinload(Like.user),
                    )
                )
                users_with_tweets = users_with_tweets.all()

                media_data = await session.execute(select(Media))
                media_data = media_data.all()
                media_dict = {media[0].id: media[0].file_name for media in media_data}

                tweets_data = await tweet_response(media_dict=media_dict, users_with_tweets=users_with_tweets)

        return TweetsOut(result=True, tweets=tweets_data)

    except CustomException as ce:
        return {"result": False, "error_type": "CustomException", "error_message": ce.detail}


@router.get("/users/me", response_model=UserProfileOut)
async def get_user_profile(user: User = Depends(check_api_key)):
    return await get_user_profile_data(user.id)


@router.get("/users/{user_id}", response_model=UserProfileOut)
async def get_user_by_id(user_id: int, user: User = Depends(check_api_key)):
    return await get_user_profile_data(user_id)


@router.post("/medias", status_code=201, response_model=MediaOut)
async def upload_media(file: UploadFile = File(...), user: User = Depends(check_api_key)):
    if not allowed_file(file.filename):
        raise CustomException(status_code=400, detail="Invalid file type")

    unique_filename = f"{uuid4()}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as file_object:
        file_object.write(file.file.read())

    async with async_session() as session:
        async with session.begin():

            media = Media(file_name=f"/static/images/{unique_filename}")

            session.add(media)
            await session.flush()

    return MediaOut(result=True, media_id=media.id)
