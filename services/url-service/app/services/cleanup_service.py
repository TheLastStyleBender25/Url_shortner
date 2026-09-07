from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.url_repository import UrlRepository

class CleanupService:
    def __init__(self):
        self.url_repository = UrlRepository()

    async def delete_expired_url(self, id: UUID, db: AsyncSession) -> None:
        # url = await self.url_repository.get_by_id(db,id)
        # if url is None:
        #     return
        # if not url.is_active:
        #     return
        # if url.expires_at is not None and url.expires_at > datetime.now(timezone.utc):
        #     return
        # url.is_active = False
        # await db.commit()
        url = await self.url_repository.get_by_id(db, id)

        if url is None:
            return

        if not url.is_active:
            return

        url.is_active = False

        await db.commit()
