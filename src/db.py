import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://kjune0922:dlrudalswns2@postgres_kuber:5432/kuber_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ClusterStatus(Base):
    __tablename__ = "cluster_status"
    id = Column(Integer, primary_key=True)
    cluster_name = Column(String, index=True, unique=True)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    carbon_emission = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TaskResult(Base):
    __tablename__ = "task_result"
    id = Column(Integer, primary_key=True)
    task_id = Column(String, index=True)
    status = Column(String, default="completed")
    result = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class CarbonHistory(Base):
    __tablename__ = "carbon_history"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    cluster_name = Column(String, index=True)
    baseline_carbon = Column(Float)
    scheduler_carbon = Column(Float)
    reduction_rate = Column(Float)

def init_db():
    Base.metadata.create_all(bind=engine)
