# backend/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"msg": "OTA Deploy Tracker Running"}


@app.post("/ota/deploy")
def deploy_ota(version: str, wave: str = "canary", db: Session = Depends(get_db)):
    job = models.OTAJob(version=version, wave=wave, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": job.status}


@app.get("/ota/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.OTAJob).order_by(models.OTAJob.created_at.desc()).all()
    return [
        {"id": j.id, "version": j.version, "wave": j.wave, "status": j.status}
        for j in jobs
    ]


@app.post("/ota/update_status")
def update_status(job_id: int, status: str, db: Session = Depends(get_db)):
    job = db.query(models.OTAJob).filter(models.OTAJob.id == job_id).first()
    if job:
        job.status = status
        db.commit()
        return {"job_id": job_id, "status": job.status}
    return {"error": "Job not found"}
