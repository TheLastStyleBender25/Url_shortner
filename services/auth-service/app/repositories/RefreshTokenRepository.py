from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, delete
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository

class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def __init__(self):
        super().__init__(RefreshToken)

    async def delet_by_id(self, db:AsyncSession, id) -> bool:
        return await db.execute(delete(RefreshToken).where(RefreshToken.user_id == id))

    async def get_by_token_hash(self, db:AsyncSession, token_hash):
        result = await db.execute(Select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalars().one_or_none()