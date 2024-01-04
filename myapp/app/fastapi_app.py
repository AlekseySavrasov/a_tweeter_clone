from fastapi import FastAPI
from sqlalchemy import select

from app.models import Base, engine, async_session, Item

app: FastAPI = FastAPI()


@app.on_event("startup")
async def startup():
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

