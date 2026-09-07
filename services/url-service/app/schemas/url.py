from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl, ConfigDict


class CreateUrlRequest(BaseModel):
    url:HttpUrl
    expires_at: datetime | None = None

class UpdateURLRequest(BaseModel):
    original_url: HttpUrl | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None

class ShortToUrlResponse(BaseModel):
    or_url:HttpUrl

class UrlResponse(BaseModel):
    id:UUID
    url:HttpUrl
    short:str
    expires_at:datetime|None
    is_active:bool
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)

class UrlListResponse(BaseModel):
    urls:list[UrlResponse]
    total:int


class TokenPayload(BaseModel):
    id:UUID

