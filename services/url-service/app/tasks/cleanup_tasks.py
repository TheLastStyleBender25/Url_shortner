from uuid import UUID
from app.services.cleanup_service import CleanupService
from app.core.celery import celery_app
from app.db.session import DATABASE_URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
import asyncio

_engine = None
_session_factory = None


def get_worker_session_factory():
    global _engine
    global _session_factory
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine,class_=AsyncSession,expire_on_commit=False)
    return _session_factory

@celery_app.task(name="url_cleanup_task")
def cleanup_task(id:str):
    asyncio.run(delete_task(id))


async def delete_task(id:str):
    SessionLocal = get_worker_session_factory()
    async with SessionLocal() as db:
        clean = CleanupService()
        await clean.delete_expired_url(UUID(id), db)


