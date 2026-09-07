from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async  def get_by_email(self, email: str, db:AsyncSession):
        result = await db.execute(Select(User).where(User.email == email))
        return result.scalars().one_or_none()