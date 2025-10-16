import json, hashlib, functools, inspect
from fastapi import Request
from app.core.redis import r_get, r_set

def _cache_key(path: str, params: dict) -> str:
    # stable, order-insensitive key
    raw = json.dumps({"p": path, "q": params}, sort_keys=True)
    return "api:cache:" + hashlib.sha256(raw.encode()).hexdigest()

def cacheable(ttl: int = 10):
    """
    Decorator for read-only endpoints. Caches identical requests for `ttl` seconds.
    Works for async endpoints that return JSON-serializable data.
    """
    def wrap(func):
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def inner(*args, **kwargs):
            # try to locate the Request object (positional or kw)
            req = next((a for a in args if isinstance(a, Request)), kwargs.get("request"))
            path = req.url.path if req else func.__name__
            params = dict(req.query_params) if req else kwargs

            key = _cache_key(path, params)
            hit = await r_get(key)
            if hit:
                return json.loads(hit)

            # call the original function
            result = await func(*args, **kwargs) if is_async else func(*args, **kwargs)

            # store
            await r_set(key, json.dumps(result), ttl)
            return result

        return inner
    return wrap
