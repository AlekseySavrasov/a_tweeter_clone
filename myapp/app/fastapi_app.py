from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException, Depends, UploadFile, File, Form
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.database import Base, engine, async_session
from app.models import Tweet, User
from app import schemas, models

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
                select(models.User).filter(models.User.secret_key == api_key)
            )
            i_user = user.scalar_one_or_none()

            if not i_user:
                raise HTTPException(status_code=401, detail="Invalid API Key")
            return i_user


@app.post("/api/tweets", status_code=201, response_model=schemas.TweetOut)
async def add_tweet(
        data: schemas.TweetIn,
        user: models.User = Depends(check_api_key)
):
    async with async_session() as session:
        async with session.begin():
            tweet = models.Tweet(
                tweet_data=data.tweet_data,
                tweet_media_ids=data.tweet_media_ids,
                user_id=user.id
            )
            session.add(tweet)
            await session.flush()
            return {"result": True, "id": tweet.id}


@app.post("/api/medias", response_model=schemas.MediaResponse)
async def upload_media(
        file: UploadFile = File(...),
        user: models.User = Depends(check_api_key)
):
    """Эндпоинт для сохранения файла и получения его ID"""
    async with async_session() as session:
        async with session.begin():
            media = models.Media(file=file.filename)
            session.add(media)
            await session.flush()
            media_id = media.id

    return {"result": True, "media_id": media_id}
