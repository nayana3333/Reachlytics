from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "reachlytics",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(task_track_started=True)
