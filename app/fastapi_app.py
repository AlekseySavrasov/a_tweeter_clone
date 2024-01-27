from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import event

from app.database import async_session, engine, initialize_table, metadata
from app.models import Follower, Like, Tweet, User
from app.routes import router, STATIC_PATH, UPLOAD_DIR

MODELS = {User, Follower, Tweet, Like}

for i_model in MODELS:
    event.listen(i_model.__table__, "after_create", initialize_table)

app = FastAPI(title="A tweeter clone")
app.config = {"UPLOAD_FOLDER": UPLOAD_DIR}
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

app.include_router(router)

origins = [
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
