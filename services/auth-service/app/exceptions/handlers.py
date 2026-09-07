from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logger import logger
from app.exceptions.auth_exceptions import InvalidRefreshTokenException, InvalidCredentialsException, UserNotFoundException, EmailAlreadyExistsException, RateLimitExceededException, UserNotVerifiedException, IncorrectOTPException, CeleryTaskException, InvalidTokenException


async def email_exist_exception(request: Request, exception: EmailAlreadyExistsException):
    logger.exception(f"email_exist_exception: {request.url}")
    # Conflict
    return JSONResponse(status_code=409,content={"message":"Email already exists"})

async def invalid_credentials_exception(request: Request, exception: InvalidCredentialsException):
    logger.exception(f"invalid_credentials_exception: {request.url}")
    # Unauthorized
    return JSONResponse(status_code=401,content={"message":"Invalid credentials"})

async def user_not_found_exception(request: Request, exception: UserNotFoundException):
    logger.exception(f"user_not_found_exception: {request.url}")
    # Not Found
    return JSONResponse(status_code=404,content={"message":"User not found"})

async def invalid_refresh_token_exception(request: Request, exception: InvalidRefreshTokenException):
    logger.exception(f"invalid_refresh_token_exception: {request.url}")
    # Unauthorized
    return JSONResponse(status_code=401,content={"message":"Invalid refresh token"})

async  def rate_limit_exception(request: Request, exception: RateLimitExceededException):
    logger.exception(f"rate_limit_exception: {request.url}")
    # Too Many Requests
    return JSONResponse(status_code=429,content={"message":"Rate limit exceeded"})

async def user_not_verified_handler(request: Request, exception: UserNotVerifiedException):
    logger.exception(f"user_not_verified_handler: {request.url}")
    # Forbidden
    return JSONResponse(status_code=403,content={"message":"User not verified"})

async def incorrect_otp_handler(request: Request, exception: IncorrectOTPException):
    logger.exception(f"incorrect_oyp_handler: {request.url}")
    # Bad Request
    return JSONResponse(status_code=400,content={"message":"Incorrect OTP"})

async def celery_task_handler(request: Request, exception: CeleryTaskException):
    logger.exception(f"celery_task_handler: {request.url}")
    # Internal Server Error
    return JSONResponse(status_code=500,content={"message":"Celery task failed"})

async def invalid_token_handler(request: Request, exception: InvalidTokenException):
    logger.exception(f"inavlid_token_handler: {request.url}")
    # Unauthorized
    return JSONResponse(status_code=401,content={"message":"Invalid token"})

