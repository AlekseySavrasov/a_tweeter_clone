"""Модуль, содержащий определения маршрутов для приложения."""

from os import path
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import utils
from app.database import async_session
from app.models import Follower, Like, Media, Tweet, User
from app.schemas import MediaOut, OperationOut, TweetIn, TweetOut, TweetsOut, UserProfileOut

STATIC_PATH: Path = Path(__file__).parent.parent / "static"
UPLOAD_DIR: str = "static/images"

router: APIRouter = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.post("/tweets", status_code=201, response_model=TweetOut)
async def add_tweet(tweet_data: TweetIn, user: User = Depends(utils.check_api_key)):
    """
    Добавление нового твита.

    :param tweet_data: Данные нового твита.
    :param user: Пользователь, добавляющий твит (проверенный с помощью API-ключа).
    :raises CustomException: Если данные твита неверны (400).
    :return: Информация о добавленном твите.
    """
    if not tweet_data:
        raise utils.CustomException(status_code=400, detail="Invalid tweet data")

    tweet: Tweet = Tweet(
        tweet_data=tweet_data.tweet_data,
        tweet_media_ids=tweet_data.tweet_media_ids,
        user_id=user.id,
    )

    async with async_session() as session:
        async with session.begin():
            session.add(tweet)
            await session.flush()
            tweet_id = tweet.id if tweet else None

    return TweetOut(result=True, id=tweet_id)


@router.delete("/tweets/{tweet_id}", status_code=202, response_model=OperationOut)
async def delete_tweet(tweet_id: int, user: User = Depends(utils.check_api_key)):
    """
    Удаление твита по его идентификатору.

    :param tweet_id: id удаляемого твита.
    :param user: Пользователь, удаляющий твит (проверенный с помощью API-ключа).
    :raises CustomException: Если твит не принадлежит текущему пользователю (403).
    :return: Информация об успешном удалении твита.
    """
    async with async_session() as session:
        async with session.begin():
            tweet = await utils.check_tweet_exist(session=session, check_id=tweet_id)

            if tweet.user_id != user.id:
                raise utils.CustomException(status_code=403, detail="You are not allowed to delete this tweet")

            await session.delete(tweet)
            await session.commit()

    return OperationOut(result=True)


@router.post("/tweets/{tweet_id}/likes", status_code=201, response_model=OperationOut)
async def add_like(tweet_id: int, user: User = Depends(utils.check_api_key)):
    """
    Установление лайка на твит по id.

    :param tweet_id: id твита на который устанавливается лайк.
    :param user: Пользователь, добавляющий лайк (проверенный с помощью API-ключа).
    :raises CustomException: Если лайк уже установлен на выбранный твит (400).
    :return: Информация об успешном установлении лайка на твит.
    """
    async with async_session() as session:
        async with session.begin():
            await utils.check_tweet_exist(session=session, check_id=tweet_id)

            if await utils.check_like_exist(session=session, tweet_id=tweet_id, user_id=user.id):
                raise utils.CustomException(status_code=400, detail="Like already exists!")

            like: Like = Like(tweet_id=tweet_id, user_id=user.id)
            session.add(like)
            await session.flush()

    return OperationOut(result=True)


@router.delete("/tweets/{tweet_id}/likes", status_code=202, response_model=OperationOut)
async def delete_like(tweet_id: int, user: User = Depends(utils.check_api_key)):
    """
    Удаление лайка с твита.

    :param tweet_id: id твита с которого удаляется лайк
    :param user: Пользователь, удаляющий лайк (проверенный с помощью API-ключа)
    :raises CustomException: Если лайк не существует на данном твите (404)
    :return: Информация об успешном удалении лайка
    """
    async with async_session() as session:
        async with session.begin():
            await utils.check_tweet_exist(session=session, check_id=tweet_id)

            unlike = await utils.check_like_exist(session=session, tweet_id=tweet_id, user_id=user.id)

            if not unlike:
                raise utils.CustomException(status_code=404, detail="Like not found")

            await session.delete(unlike)
            await session.commit()

    return OperationOut(result=True)


@router.post("/users/{follow_id}/follow", status_code=201, response_model=OperationOut)
async def add_follow(follow_id: int, user: User = Depends(utils.check_api_key)):
    """
    Follow другого пользователя по id.

    :param follow_id: id отслеживаемого пользователя
    :param user: Пользователь, отслеживающий, другого пользователя (проверенный с помощью API-ключа)
    :raises CustomException: Если отслеживание уже существует (400)
    :return: Информация об успешном начале отслеживания
    """
    if follow_id == user.id:
        raise utils.CustomException(status_code=400, detail="The current user can't follow himself")

    async with async_session() as session:
        async with session.begin():
            await utils.check_user_exist(session=session, check_id=follow_id)

            follow = await utils.check_follow_exist(session=session, follow_id=follow_id, user_id=user.id)

            if follow:
                raise utils.CustomException(status_code=400, detail="Follow already exists!")

            follow: Follower = Follower(follower_id=user.id, followed_id=follow_id)
            session.add(follow)
            await session.flush()

    return OperationOut(result=True)


@router.delete("/users/{follow_id}/follow", status_code=202, response_model=OperationOut)
async def delete_follow(follow_id: int, user: User = Depends(utils.check_api_key)):
    """
    Unfollow другого пользователя по id.

    :param follow_id: id пользователя которого перестают отслеживать
    :param user: Пользователь, перестающий отслеживать, другого пользователя (проверенный с помощью API-ключа)
    :raises CustomException: Если отслеживание не найдено (404)
    :return: Информация об успешном удалении отслеживания
    """
    async with async_session() as session:
        async with session.begin():
            unfollow = await utils.check_follow_exist(session=session, follow_id=follow_id, user_id=user.id)

            if not unfollow:
                raise utils.CustomException(status_code=404, detail="Follow not found")

            await session.delete(unfollow)
            await session.commit()

    return OperationOut(result=True)


@router.get("/tweets", response_model=TweetsOut)
async def get_user_tweets(user: User = Depends(utils.check_api_key)):
    """
    Пользователь может получить ленту из твитов отсортированных в порядке убывания.

    По популярности от пользователей, которых он фоловит.

    :param user: Пользователь, добавляющий твит (проверенный с помощью API-ключа)
    :return: Информация о ленте твитов текущего пользователя
    """
    async with async_session() as session:
        async with session.begin():
            try:
                followed_users = (
                    await session.execute(
                        select(User).
                        join(Follower, User.id == Follower.followed_id).
                        filter(Follower.follower_id == user.id).
                        options(selectinload(User.tweets).selectinload(Tweet.likes).selectinload(Like.user))
                    )
                )
            except utils.CustomException as ce:
                return {"result": False, "error_type": "CustomException", "error_message": ce.detail}

            followed_users = followed_users.all()

            tweets: list = [tweet for followed_user in followed_users for tweet in followed_user[0].tweets]
            sorted_tweets: list = sorted(tweets, key=lambda tweet: len(tweet.likes), reverse=True)

            media_data = await session.execute(select(Media))
            media_data = media_data.all()
            media_dict: dict = {media[0].id: media[0].file_name for media in media_data}

            tweets_data = await utils.tweet_response(media_dict=media_dict, tweets=sorted_tweets)

    return TweetsOut(result=True, tweets=tweets_data)


@router.get("/users/me", response_model=UserProfileOut)
async def get_user_profile(user: User = Depends(utils.check_api_key)):
    """
    Пользователь может получить информацию о своём профиле.

    :param user: Пользователь, добавляющий твит (проверенный с помощью API-ключа)
    :return: Информация о профиле текущего пользователя
    """
    return await utils.get_user_profile_data(user.id)


@router.get("/users/{user_id}", response_model=UserProfileOut)
async def get_user_by_id(user_id: int, user: User = Depends(utils.check_api_key)):
    """
    Пользователь может получить информацию о произвольном профиле по его id.

    :param user_id: id искомого пользователя
    :param user: Пользователь, добавляющий твит (проверенный с помощью API-ключа)
    :return: Информация о профиле пользователя по id
    """
    return await utils.get_user_profile_data(user_id)


@router.post("/medias", status_code=201, response_model=MediaOut)
async def upload_media(file: UploadFile = File(...), user: User = Depends(utils.check_api_key)):
    """
    Endpoint для загрузки файлов из твита. Загрузка происходит через отправку формы.

    :param file: Файл для загрузки в твит
    :param user: Пользователь, добавляющий файл в твит (проверенный с помощью API-ключа)
    :raises CustomException: Если формат файла некорректный (400)
    :return: Информация об успешном добавлении файла
    """
    if not utils.allowed_file(file.filename):
        raise utils.CustomException(status_code=400, detail="Invalid file type")

    unique_filename: str = f"{uuid4()}{path.splitext(file.filename)[1]}"
    file_path: str = path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as file_object:
        file_object.write(file.file.read())

    async with async_session() as session:
        async with session.begin():

            media: Media = Media(file_name=f"/static/images/{unique_filename}")

            session.add(media)
            await session.flush()

    return MediaOut(result=True, media_id=media.id)
