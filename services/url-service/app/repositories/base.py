from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from typing import TypeVar, Generic

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):

    def __init__(self, model: ModelType):
        self.model = model

    async def create(self, obj: ModelType, db: AsyncSession):
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType, db: AsyncSession):
        await db.delete(obj)
        await db.commit()
        await db.refresh(obj)

    async def get_by_id(self, db: AsyncSession, id):
        result = await db.execute(Select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()




