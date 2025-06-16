# backend/main.py
from pathlib import Path

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
    return {"msg": "Kubernetes Deployment Manager Running"}


@app.post("/ota/deploy")
def deploy_ota(version: str, wave: str = "canary"):
    """Deploy a new version.

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
    """List all deployment jobs.

    Returns:
        List of all deployment jobs with their details
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
    """Update the status of a deployment job.

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


@app.post("/ota/rollback")
def rollback_deployment(version: str, wave: str = "green"):
    """Rollback to a previous version.

    Args:
        version: The version to rollback to
        wave: The rollback scope (default: "green")
    """
    db = next(get_db())  # Get a new DB session
    try:
        job = models.OTAJob(version=version, wave=wave, status="rollback_pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {
            "job_id": job.id,
            "version": job.version,
            "status": job.status,
            "type": "rollback",
        }
    finally:
        db.close()


@app.get("/metrics")
def metrics():
    metrics_path = Path(__file__).parent.parent / "metrics.txt"
    try:
        content = metrics_path.read_text(encoding="utf-8")
        return Response(content=content, media_type="text/plain")
    except (FileNotFoundError, OSError) as e:
        return Response(f"# error: {e}", media_type="text/plain")
