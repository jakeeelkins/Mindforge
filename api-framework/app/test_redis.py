import os, asyncio
from app.core.redis import get_client

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

async def main():
    r = await get_client()
    print("PING ->", await r.ping())

if __name__ == "__main__":
    asyncio.run(main())
