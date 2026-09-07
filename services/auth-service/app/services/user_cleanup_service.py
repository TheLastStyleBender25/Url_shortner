from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.UserRepository import UserRepository

class UserCleanupService:
    def __init__(self):
        self.us_repo = UserRepository()

    async def delete_unverified_user(self, email: str, db: AsyncSession) -> None:
        user = await self.us_repo.get_by_email(email, db)
        if user is None:
            return
        if user.is_verified:
            return
        await self.us_repo.delete(db, user)
        await db.commit()