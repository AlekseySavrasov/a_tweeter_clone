from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.database import Base, engine, async_session
from app.models import Item

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
                    Item(name="item1"),
                    Item(name="item2"),
                    Item(name="item3"),
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


@app.get('/ping')
async def main():
    return {"Success": True}


@app.post('/items', status_code=201)
async def insert_product_handler():
    async with async_session() as session:
        async with session.begin():
            a_item = Item(name="new item")
            session.add(a_item)
            await session.flush()


@app.get('/items')
async def get_items_handler():
    async with async_session() as session:
        async with session.begin():
            q = await session.execute(select(Item))

            items = q.scalars().all()
            items_list = []
            for p in items:
                product_obj = p.to_json()
                items_list.append(product_obj)
            return items_list
