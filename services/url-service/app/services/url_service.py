from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.url_repository import UrlRepository
import secrets, string
from app.models.url import Url
from app.schemas.url import CreateUrlRequest, UrlResponse, UrlListResponse, ShortToUrlResponse
from datetime import datetime, timezone, timedelta
from uuid import UUID
from app.exceptions.exceptions import UrlExpiredException, UrlNotFoundException, UnauthorizedException
from app.tasks.cleanup_tasks import cleanup_task



class UrlService:

    def __init__(self):
        self.url_repo = UrlRepository()

    def generate_short_code(self, length:int=6) -> str:
        char = string.ascii_letters + string.digits
        return "".join(secrets.choice(char) for i in range(length))

    async def create_url(self, user_id, url:CreateUrlRequest,db: AsyncSession) -> UrlResponse:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        while True:
            short = self.generate_short_code()
            exist = await self.url_repo.get_by_short_code(short,db)
            if exist is None:
                break
        _url = Url(user_id= user_id, original_url=str(url.url),short_code=short, expires_at=expires_at)
        create = await self.url_repo.create(_url, db)
        response = UrlResponse(id=_url.id, url=url.url, short=short, expires_at=expires_at,is_active=True, created_at=datetime.now(timezone.utc))
        cleanup_task.apply_async(args=[str(response.id)], countdown=360)
        return response

    async def get_url_by_short_code(self, short_code:str, db: AsyncSession) -> ShortToUrlResponse:
        url = await self.url_repo.get_by_short_code(short_code,db)
        if url is None or not url.is_active:
            raise UrlNotFoundException()
        if (url.expires_at is not None and url.expires_at <= datetime.now(timezone.utc)):
            raise UrlExpiredException()
        response = ShortToUrlResponse(or_url=url.original_url)
        return response

    async def get_url_by_id(self,url_id: UUID,user_id: UUID,db: AsyncSession,) -> UrlResponse:
        url = await self.url_repo.get_by_id(db,url_id)
        if url is None or not url.is_active:
            raise UrlNotFoundException()
        if url.user_id != user_id:
            raise UnauthorizedException()
        response = UrlResponse(id=url.id, url=url.original_url, short=url.short_code,expires_at=url.expires_at,is_active=url.is_active,created_at=url.created_at)
        return response

    async def delete_url(self,url_id: UUID,user_id: UUID,db: AsyncSession) -> None:
        url = await self.url_repo.get_by_id(db,url_id)
        if url is None:
            raise UrlNotFoundException()
        if url.user_id != user_id:
            raise UnauthorizedException()
        url.is_active = False
        await db.commit()

    async def get_user_urls(self,user_id: UUID,db: AsyncSession) -> UrlListResponse:
        result = await self.url_repo.get_active_urls(db,user_id)
        return UrlListResponse(urls=result,total=len(result))




