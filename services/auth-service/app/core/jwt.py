from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from app.core.config import settings
from app.exceptions.auth_exceptions import InvalidTokenException

def create_access_token(user_id:str, id):
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    strid = str(id)
    payload = {'sub': user_id, 'id': strid, 'exp': expire}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def create_refresh_token(user_id:str):
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {'sub': user_id, 'exp': expire}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token:str):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
    except JWTError:
        raise InvalidTokenException()