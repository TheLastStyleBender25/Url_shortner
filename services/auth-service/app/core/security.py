from passlib.context import CryptContext
import hashlib

from app.exceptions.auth_exceptions import InvalidTokenException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_refresh_token(refresh_token:str) -> str:
    if not refresh_token or refresh_token == "":
        raise InvalidTokenException()
    try:
        return hashlib.sha256(refresh_token.encode()).hexdigest()
    except Exception:
        raise InvalidTokenException()



