from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import User, Tweet, Like, Follower
from app.schemas import UserProfileOut

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


async def check_api_key(api_key: str = Header(...)):
    """Проверка API-ключа"""
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(User).filter(User.secret_key == api_key)
            )
            user = user.scalar_one_or_none()

            if not user:
                raise CustomException(status_code=401, detail="Invalid API Key")
            return user


async def check_user_exist(session, check_id):
    follow_user = await session.execute(
        select(User)
        .where(User.id == check_id)
    )
    follow_user = follow_user.scalar_one_or_none()

    if not follow_user:
        raise CustomException(status_code=404, detail="User not found")


async def check_tweet_exist(session, check_id):
    tweet = await session.execute(
        select(Tweet)
        .options(selectinload(Tweet.likes))
        .where(Tweet.id == check_id)
    )
    tweet = tweet.scalar_one_or_none()

    if not tweet:
        raise CustomException(status_code=404, detail="Tweet not found")

    return tweet


async def check_like_exist(session, tweet_id, user_id):
    like = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )
    like = like.scalar_one_or_none()

    return like


async def check_follow_exist(session, follow_id, user_id):
    follow = await session.execute(
        select(Follower).where(Follower.followed_id == follow_id, Follower.follower_id == user_id)
    )
    follow = follow.scalar_one_or_none()

    return follow


async def get_user_profile_data(user_id):
    async with async_session() as session:
        async with session.begin():
            await check_user_exist(session, user_id)
            query = select(User).filter(User.id == user_id).options(
                selectinload(User.followers).selectinload(Follower.follower),
                selectinload(User.following).selectinload(Follower.followed),
            )
            user_with_relationships = await session.execute(query)
            user_data = user_with_relationships.scalar()
            return UserProfileOut.from_db_user(user_data)


async def tweet_response(media_dict, users_with_tweets):
    return [
        {
            "id": tweet.id,
            "content": tweet.tweet_data,
            "attachments": [media_dict.get(media_id, None) for media_id in
                            tweet.tweet_media_ids] if tweet.tweet_media_ids else [],
            "author": {"id": tweet.user.id, "name": tweet.user.name},
            "likes": [
                {
                    "user_id": like.user.id,
                    "name": like.user.name,
                }
                for like in tweet.likes
            ] if tweet.likes else [],
        }
        for user in users_with_tweets
        for tweet in user[0].tweets
    ]
