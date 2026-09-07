from uuid import UUID

from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.exceptions.exceptions import InvalidTokenException
from app.schemas.url import TokenPayload


security = HTTPBearer()

def get_current_user(credentials:HTTPAuthorizationCredentials = Depends(security)) -> TokenPayload:
    token = credentials.credentials
    if not token:
        raise InvalidTokenException()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        id = payload.get("id")
        token_data = TokenPayload(id=UUID(id))
        return token_data
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")


