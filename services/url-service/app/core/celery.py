from celery import Celery
from app.core.config import settings

celery_app = Celery("url_service",broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

celery_app.conf.task_routes = {"url_cleanup_task": {"queue": "url_queue"}}
celery_app.conf.imports = ("app.tasks.cleanup_tasks")