# backend/main.py
import os

from fastapi import FastAPI, Response

from . import database, models

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
def deploy_ota(version: str, wave: str = "canary"):
    """Deploy a new OTA version.

    Args:
        version: The version to deploy
        wave: The deployment wave (default: "canary")
    """
    db = next(get_db())  # Get a new DB session
    try:
        job = models.OTAJob(version=version, wave=wave, status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"job_id": job.id, "version": job.version, "status": job.status}
    finally:
        db.close()


@app.get("/ota/jobs")
def list_jobs():
    """List all OTA jobs.

    Returns:
        List of all OTA jobs with their details
    """
    db = next(get_db())  # Get a new DB session
    try:
        jobs = db.query(models.OTAJob).order_by(models.OTAJob.created_at.desc()).all()
        return [
            {
                "id": job.id,
                "version": job.version,
                "wave": job.wave,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
            }
            for job in jobs
        ]
    finally:
        db.close()


@app.post("/ota/update_status")
def update_status(job_id: int, status: str):
    """Update the status of an OTA job.

    Args:
        job_id: The ID of the job to update
        status: The new status

    Returns:
        Status of the update operation
    """
    db = next(get_db())  # Get a new DB session
    try:
        job = db.query(models.OTAJob).filter(models.OTAJob.id == job_id).first()
        if job:
            job.status = status
            db.commit()
            db.refresh(job)
            return {"status": "success", "job_id": job.id, "new_status": job.status}
        return {"status": "error", "message": "Job not found"}
    finally:
        db.close()


@app.get("/metrics")
def metrics():
    metrics_path = os.path.join(os.path.dirname(__file__), "..", "metrics.txt")
    try:
        with open(metrics_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    except Exception as e:
        return Response(f"# error: {e}", media_type="text/plain")
