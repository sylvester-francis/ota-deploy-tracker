# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base


class OTAJob(Base):
    __tablename__ = "ota_jobs"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, index=True)
    wave = Column(String, default="canary")
    status = Column(String, default="pending")  # pending, in_progress, complete, failed
    created_at = Column(DateTime, default=datetime.utcnow)
