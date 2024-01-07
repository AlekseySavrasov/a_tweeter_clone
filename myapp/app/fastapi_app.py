from fastapi import FastAPI, Header, HTTPException, Depends, UploadFile, File
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.database import Base, engine, async_session
from app.models import Follower, Like, Media, Tweet, User
from app.schemas import TweetIn, TweetOut, MediaResponse, OperationResult

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info("Connecting to the database")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    User(name="user_1", secret_key="$BSSh6@lfkj"),
                    User(name="user_2", secret_key="kBSkfjSh6@f"),
                    User(name="user_3", secret_key="dBS[pw;olSh"),
                ]
            )
            await session.commit()


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


async def check_api_key(api_key: str = Header(...)):
    """Проверка API-ключа"""
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(User).filter(User.secret_key == api_key)
            )
            user = user.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=401, detail="Invalid API Key")
            return user


@app.post(
    "/api/tweets",
    status_code=201,
    response_model=TweetOut
)
async def add_tweet(
        data: TweetIn,
        user: User = Depends(check_api_key)
):
    """Добавление нового твита"""
    async with async_session() as session:
        async with session.begin():
            tweet = Tweet(
                tweet_data=data.tweet_data,
                tweet_media_ids=data.tweet_media_ids,
                user_id=user.id
            )
            session.add(tweet)
            await session.flush()

    return {"result": True, "id": tweet.id}


@app.post(
    "/api/medias",
    status_code=201,
    response_model=MediaResponse
)
async def upload_media(
        file: UploadFile = File(...),
        user: User = Depends(check_api_key)
):
    """Сохранения файла и получения его ID"""
    async with async_session() as session:
        async with session.begin():
            media = Media(file=file.filename)
            session.add(media)
            await session.flush()
            media_id = media.id

    return {"result": True, "media_id": media_id}


@app.delete(
    "/api/tweets/{tweet_id}",
    status_code=202,
    response_model=OperationResult
)
async def delete_tweet(
        tweet_id: int,
        user: User = Depends(check_api_key),
):
    """Удаляем твит по его идентификатору"""
    async with async_session() as session:
        async with session.begin():
            tweet = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
            tweet = tweet.scalar_one_or_none()

            if not tweet:
                raise HTTPException(status_code=404, detail="Tweet not found")

            if tweet.user_id != user.id:
                raise HTTPException(status_code=403, detail="You are not allowed to delete this tweet")

            await session.delete(tweet)
            await session.commit()

    return {"result": True}


@app.post(
    "/api/tweets/{tweet_id}/likes",
    status_code=201,
    response_model=OperationResult
)
async def add_like(
        tweet_id: int,
        user: User = Depends(check_api_key)
):
    """Установление лайка на твит по id"""
    async with async_session() as session:
        async with session.begin():
            like = Like(tweet_id=tweet_id, user_id=user.id)
            session.add(like)
            await session.flush()

    return {"result": True}


@app.delete(
    "/api/tweets/{tweet_id}/likes",
    status_code=202,
    response_model=OperationResult
)
async def delete_like(
        tweet_id: int,
        user: User = Depends(check_api_key)
):
    """Удаление лайка с твита"""
    async with async_session() as session:
        async with session.begin():
            unlike = await session.execute(
                select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
            )
            unlike = unlike.scalar_one_or_none()

            if not unlike:
                raise HTTPException(status_code=404, detail="Like not found")

            await session.delete(unlike)
            await session.commit()

    return {"result": True}


@app.post(
    "/api/users/{follow_id}/follow",
    status_code=201,
    response_model=OperationResult
)
async def add_follow(
        follow_id: int,
        user: User = Depends(check_api_key)
):
    """Follow другого пользователя по id"""
    async with async_session() as session:
        async with session.begin():

            if follow_id == user.id:
                raise HTTPException(status_code=404, detail="User can't follow himself")

            follow = Follower(src_id=user.id, dst_id=follow_id)
            session.add(follow)
            await session.flush()

    return {"result": True}


@app.delete(
    "/api/users/{follow_id}/follow",
    status_code=202,
    response_model=OperationResult
)
async def delete_follow(
        follow_id: int,
        user: User = Depends(check_api_key)
):
    """Удаление лайка с твита"""
    async with async_session() as session:
        async with session.begin():
            unfollow = await session.execute(
                select(Follower).where(Follower.dst_id == follow_id, Follower.src_id == user.id)
            )
            unfollow = unfollow.scalar_one_or_none()

            if not unfollow:
                raise HTTPException(status_code=404, detail="Follow not found")

            await session.delete(unfollow)
            await session.commit()

    return {"result": True}
