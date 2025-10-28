import os
from celery import Celery
from datetime import timedelta
from src.scheduler.carbon_scheduler_hybrid import run_hybrid_scheduler

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis_kuber:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis_kuber:6379/0")
)

@celery_app.task
def run_hybrid_scheduler_task():
    return run_hybrid_scheduler()

celery_app.conf.beat_schedule = {
    "run-hybrid-scheduler-every-5min": {
        "task": "src.celery_app.run_hybrid_scheduler_task",
        "schedule": timedelta(minutes=5),
    }
}
celery_app.conf.timezone = "Asia/Seoul"
