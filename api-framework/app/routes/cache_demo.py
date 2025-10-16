import asyncio
from fastapi import APIRouter, Request
from app.utils.cache import cacheable

router = APIRouter(prefix="/demo", tags=["Demo"])

@router.get("/cache")
@cacheable(ttl=10)  # cached for 10 seconds
async def cache_demo(request: Request, name: str = "world"):
    # simulate slow work so you can see the cache effect
    await asyncio.sleep(2)
    return {"hello": name}
