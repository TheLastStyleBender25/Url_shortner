from app.core.redis_component import redis_client
from app.exceptions.exceptions import RateLimitExceededException
from fastapi import Request

def rate_limit(max:int, size:int):
    async def decorator(request: Request):
        ip = request.client.host if request.client else 'unknown'
        key = f"rate_limit:{request.url.path}:{ip}"
        cur = await redis_client.incr(key)
        if key == 1:
            await redis_client.expire(key, size)
        if cur > max:
            raise RateLimitExceededException()

    return decorator

