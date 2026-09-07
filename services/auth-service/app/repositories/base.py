from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model:ModelType):
        self.model = model

    async  def create(self, db:AsyncSession, obj:ModelType):
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db:AsyncSession, obj:ModelType):
        await db.delete(obj)
        await db.flush()

    async def get_by_id(self, db:AsyncSession, id):
        result = await db.execute(Select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
