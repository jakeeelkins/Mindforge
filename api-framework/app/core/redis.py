import os
from functools import lru_cache
import redis.asyncio as redis  # official async client

@lru_cache()
def _url():
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")

@lru_cache()
def _client():
    # One shared async client per process
    return redis.from_url(_url(), encoding="utf-8", decode_responses=True)

async def get_client():
    return _client()

async def r_get(key: str):
    r = get_client()
    return await (await r).get(key)

async def r_set(key: str, val: str, ttl: int):
    r = get_client()
    await (await r).setex(key, ttl, val)
