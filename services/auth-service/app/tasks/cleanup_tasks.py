from app.core.celery import celery_app
from app.db.session import SessionLocal
import asyncio
from app.services.user_cleanup_service import UserCleanupService
from app.tasks.worker import get_worker_session_factory

@celery_app.task(name="auth_cleanup_task")
def cleanup_task(email:str):
    asyncio.run(_delete_unverified_user(email))

async def _delete_unverified_user(email:str):
    SessionLocal = get_worker_session_factory()
    async with SessionLocal() as db:
        clean = UserCleanupService()
        await clean.delete_unverified_user(email, db)


