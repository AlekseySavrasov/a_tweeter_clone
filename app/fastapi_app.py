from fastapi import FastAPI, Response, Request
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import event

from app.database import async_session, db_engine, initialize_table, metadata
from app.models import Follower, Like, Tweet, User
from app.routes import router, STATIC_PATH, UPLOAD_DIR
from app.utils import CustomException

MODELS: set = {User, Follower, Tweet, Like}

for i_model in MODELS:
    event.listen(i_model.__table__, "after_create", initialize_table)

app: FastAPI = FastAPI(title="A tweeter clone")
app.config = {"UPLOAD_FOLDER": UPLOAD_DIR}
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

app.include_router(router)

origins: list[str] = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.on_event("startup")
async def startup() -> None:
    """
    Handles the startup event of the application.
    Connects to the database and creates all tables if they do not exist.

    :return: None
    """
    logger.info("Connecting to the database")
    async with db_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    """
    Handles the shutdown event of the application.
    Disconnects from the database and disposes of the database engine.

    :return: None
    """
    logger.info("Disconnecting from the database")
    async with async_session() as session:
        await session.close()
        await db_engine.dispose()


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    Middleware function to log incoming requests and outgoing responses.

    :param request: The incoming request object.
    :param call_next: The function to call to continue the request handling.
    :return: The response object.
    """
    logger.info(f"Request received: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response sent: {response.status_code}")
    return response


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    """
    Exception handler for CustomException.

    :param request: The request object.
    :param exc: The instance of CustomException that was raised.
    :return: JSONResponse with error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_type": "CustomException", "error_message": exc.detail}
    )
