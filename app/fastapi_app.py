import os

from fastapi import FastAPI, Header, HTTPException, Depends, UploadFile, File
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from pathlib import Path
from sqlalchemy import select, event
from sqlalchemy.orm import selectinload

from app.database import async_session, engine, initialize_table, metadata
from app.models import Follower, Like, Media, Tweet, User
from app.schemas import TweetIn, TweetOut, MediaResponse, OperationResult, TweetResponse, UserProfileResponse


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MODELS = {User, Follower, Tweet, Like}
STATIC_PATH = Path(__file__).parent.parent / "static"
UPLOAD_DIR = "static/images"

for i_model in MODELS:
    event.listen(i_model.__table__, "after_create", initialize_table)

app = FastAPI()
app.config = {"UPLOAD_FOLDER": UPLOAD_DIR}
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_user_response(user_with_relationships: User):
    return {
        "result": True,
        "user": {
            "id": user_with_relationships.id,
            "name": user_with_relationships.name,
            "followers": [
                {"id": followers.follower.id, "name": followers.follower.name}
                for followers in user_with_relationships.followers
            ] if user_with_relationships.followers else [],
            "following": [
                {"id": following.followed.id, "name": following.followed.name}
                for following in user_with_relationships.following
            ] if user_with_relationships.following else [],
        },
    }


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


async def get_user_with_relationships(user_id: int = None, user: User = Depends(check_api_key)):
    try:
        async with async_session() as session:
            async with session.begin():
                query = select(User).filter(User.id == (user_id or user.id)).options(
                    selectinload(User.followers).selectinload(Follower.follower),
                    selectinload(User.following).selectinload(Follower.followed),
                )
                user_with_relationships = await session.execute(query)
                return user_with_relationships.scalar()

    except HTTPException as e:
        return {"result": False, "error_type": "HTTPException", "error_message": str(e)}


@app.on_event("startup")
async def startup():
    logger.info("Connecting to the database")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Disconnecting from the database")
    async with async_session() as session:
        await session.close()
        await engine.dispose()


@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request received: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response sent: {response.status_code}")
    return response


@app.get("/hello")
async def main():
    return {"Hello, World!"}


@app.post("/api/tweets", status_code=201, response_model=TweetOut)
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

    return JSONResponse(content={"result": True, "tweet_id": tweet_id}, status_code=201)


@app.delete("/api/tweets/{tweet_id}", status_code=202, response_model=OperationResult)
async def delete_tweet(tweet_id: int, user: User = Depends(check_api_key)):
    """Удаляем твит по его идентификатору"""
    async with async_session() as session:
        async with session.begin():
            tweet = await session.execute(
                select(Tweet)
                .options(selectinload(Tweet.likes))
                .where(Tweet.id == tweet_id)
            )
            tweet = tweet.scalar_one_or_none()

            if not tweet:
                raise CustomException(status_code=404, detail="Tweet not found")
            elif tweet.user_id != user.id:
                raise CustomException(status_code=403, detail="You are not allowed to delete this tweet")

            await session.delete(tweet)
            await session.commit()

    return {"result": True}


@app.post("/api/tweets/{tweet_id}/likes", status_code=201, response_model=OperationResult)
async def add_like(tweet_id: int, user: User = Depends(check_api_key)):
    """Установление лайка на твит по id"""
    async with async_session() as session:
        async with session.begin():
            tweet = await session.execute(
                select(Tweet)
                .options(selectinload(Tweet.likes))
                .where(Tweet.id == tweet_id)
            )
            tweet = tweet.scalar_one_or_none()

            if not tweet:
                raise CustomException(status_code=404, detail="Tweet not found")

            like = await session.execute(
                select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
            )
            like = like.scalar_one_or_none()

            if like:
                raise CustomException(status_code=400, detail="Like already exists!")

            like = Like(tweet_id=tweet_id, user_id=user.id)
            session.add(like)
            await session.flush()

    return {"result": True}


@app.delete("/api/tweets/{tweet_id}/likes", status_code=202, response_model=OperationResult)
async def delete_like(tweet_id: int, user: User = Depends(check_api_key)):
    """Удаление лайка с твита"""
    async with async_session() as session:
        async with session.begin():
            unlike = await session.execute(
                select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
            )
            unlike = unlike.scalar_one_or_none()

            if not unlike:
                raise CustomException(status_code=404, detail="Like not found")

            await session.delete(unlike)
            await session.commit()

    return {"result": True}


@app.post("/api/users/{follow_id}/follow", status_code=201, response_model=OperationResult)
async def add_follow(follow_id: int, user: User = Depends(check_api_key)):
    """Follow другого пользователя по id"""
    if follow_id == user.id:
        raise CustomException(status_code=400, detail="The current user can't follow himself")

    async with async_session() as session:
        async with session.begin():
            follow_user = await session.execute(select(User).where(User.id == follow_id))
            follow_user = follow_user.scalar_one_or_none()

            if not follow_user:
                raise CustomException(status_code=404, detail="User not found")

            follow = await session.execute(
                select(Follower).where(Follower.followed_id == follow_id, Follower.follower_id == user.id)
            )
            follow = follow.scalar_one_or_none()

            if follow:
                raise CustomException(status_code=400, detail="Follow already exists!")

            follow = Follower(follower_id=user.id, followed_id=follow_id)
            session.add(follow)
            await session.flush()

    return {"result": True}


@app.delete("/api/users/{follow_id}/follow", status_code=202, response_model=OperationResult)
async def delete_follow(follow_id: int, user: User = Depends(check_api_key)):
    """Unfollow другого пользователя"""
    async with async_session() as session:
        async with session.begin():
            unfollow = await session.execute(
                select(Follower).where(Follower.followed_id == follow_id, Follower.follower_id == user.id)
            )
            unfollow = unfollow.scalar_one_or_none()

            if not unfollow:
                raise CustomException(status_code=404, detail="Follow not found")

            await session.delete(unfollow)
            await session.commit()

    return {"result": True}


@app.get("/api/tweets", response_model=TweetResponse)
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

                tweets_data = [
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

                return JSONResponse(content={"result": True, "tweets": tweets_data})

    except HTTPException as e:
        return JSONResponse(content={"result": False, "error_type": "HTTPException", "error_message": str(e)})


@app.get("/api/users/me", response_model=UserProfileResponse)
async def get_user_profile(user_with_relationships: User = Depends(get_user_with_relationships)):
    return JSONResponse(content=create_user_response(user_with_relationships))


@app.get("/api/users/{user_id}", response_model=UserProfileResponse)
async def get_user_by_id(user_with_relationships: User = Depends(get_user_with_relationships)):
    return JSONResponse(content=create_user_response(user_with_relationships))


@app.post("/api/medias", status_code=201, response_model=MediaResponse)
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

    return JSONResponse(content={"result": True, "media_id": media.id}, status_code=201)
