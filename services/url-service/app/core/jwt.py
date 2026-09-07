from jose import jwt, JWTError
from app.core.config import settings
from app.exceptions.exceptions import InvalidTokenException

def decode_token(token:str):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
    except JWTError:
        raise InvalidTokenException()

