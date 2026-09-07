from celery import Celery
from app.core.config import settings


celery_app = Celery("auth_service",broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

celery_app.conf.task_routes = {
    "auth_cleanup_task": {"queue": "auth_queue"},
    "auth_email_task": {"queue": "auth_queue"},
    "auth_otp_task": {"queue": "auth_queue"}
}
celery_app.conf.imports = ("app.tasks.email_tasks", "app.tasks.cleanup_tasks")