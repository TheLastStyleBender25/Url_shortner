from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logger import logger
from app.exceptions.exceptions import InvalidTokenException, RateLimitExceededException, UrlExpiredException, UrlNotFoundException, UnauthorizedException


async def invalid_token_handler(request: Request, exception: InvalidTokenException):
    logger.exception(f"inavlid_token_handler: {request.url}")
    return JSONResponse(status_code=401,content={"message":"Invalid token"})

async  def rate_limit_handler(request: Request, exception: RateLimitExceededException):
    logger.exception(f"rate_limit_exception: {request.url}")
    return JSONResponse(status_code=429,content={"message":"Rate limit exceeded"})

async  def url_not_found_handler(request: Request, exception: UrlNotFoundException):
    logger.exception(f"url not found: {request.url}")
    return JSONResponse(status_code=404,content={"message":"Url not found"})

async  def url_expired_handler(request: Request, exception: UrlExpiredException):
    logger.exception(f"url has expired: {request.url}")
    return JSONResponse(status_code=404,content={"message":"Url has expired"})

async  def unauthorized_handler(request: Request, exception: UnauthorizedException):
    logger.exception(f"cannot access: {request.url}")
    return JSONResponse(status_code=401,content={"message":"cannot access"})
