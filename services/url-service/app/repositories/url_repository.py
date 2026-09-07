from app.repositories.base import BaseRepository
from app.models.url import Url
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession


class UrlRepository(BaseRepository):
    def __init__(self):
        super().__init__(Url)

    async def get_by_short_code(self, short_code: str, db: AsyncSession):
        result = await db.execute(Select(Url).where(Url.short_code == short_code))
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, db: AsyncSession, id):
        result = await db.execute(Select(Url).where(Url.user_id == id))
        return result.scalars().all()

    async def get_active_urls(self, db: AsyncSession, id):
        result = await db.execute(Select(Url).where(Url.user_id == id and Url.is_active.is_(True)))
        return result.scalars().all()

