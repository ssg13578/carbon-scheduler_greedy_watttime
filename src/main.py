from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.db import SessionLocal, init_db, CarbonHistory
from src.celery_app import run_hybrid_scheduler_task

app = FastAPI(title="Carbon-Aware Scheduler v6")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/carbon-history/")
def carbon_history(db: Session = Depends(get_db)):
    rows = db.query(CarbonHistory).order_by(CarbonHistory.id.desc()).limit(50).all()
    return [{
        "timestamp": str(r.timestamp),
        "cluster": r.cluster_name,
        "baseline_carbon": r.baseline_carbon,
        "scheduler_carbon": r.scheduler_carbon,
        "reduction_rate": r.reduction_rate
    } for r in rows]

@app.get("/carbon-graph/")
def carbon_graph(db: Session = Depends(get_db)):
    rows = db.query(CarbonHistory).order_by(CarbonHistory.id.desc()).limit(50).all()
    return [{
        "timestamp": str(r.timestamp),
        "baseline_carbon": r.baseline_carbon,
        "scheduler_carbon": r.scheduler_carbon,
        "reduction_rate": r.reduction_rate
    } for r in reversed(rows)]

@app.post("/run-hybrid/")
def trigger():
    task = run_hybrid_scheduler_task.delay()
    return {"message": "하이브리드 스케줄러 실행", "task_id": task.id}
