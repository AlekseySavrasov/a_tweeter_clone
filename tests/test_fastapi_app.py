from typing import Any, Dict, Optional

import pytest
from httpx import AsyncClient

from app.models import User, Follower, Tweet, Like


async def check_api_key():
    return User(id=1, name="name_1", secret_key="test")


async def test_hello(client: AsyncClient):
    response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == ["Hello, World!"]
