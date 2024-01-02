import uvicorn
from fastapi import FastAPI
from sqlalchemy import select
# from sqlalchemy.orm import selectinload

from database import Base, engine, async_session
from models import Item

app = FastAPI()


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
            a_item = Item(title="new item")
            session.add(a_item)
            await session.flush()


@app.get('/items')
async def get_items_handler():
    async with async_session() as session:
        async with session.begin():
            # without user
            q = await session.execute(select(Item))
            # withuser
            # q = await session.execute(
            #     select(Item).options(selectinload(Item.name)))

            items = q.scalars().all()
            items_list = []
            for p in items:
                product_obj = p.to_json()
                # product_obj["item"] = p.name.to_json()
                items_list.append(product_obj)
            return items_list


if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", port=5000, host="0.0.0.0")
