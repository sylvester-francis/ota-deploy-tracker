import os

import requests
import typer
from dotenv import load_dotenv

from .job_runner import rollback_application_pods, update_application_pods

# Load environment variables from .env file if it exists
load_dotenv()

app = typer.Typer()
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


@app.command()
def deploy(version: str, wave: str = "canary"):
    """
    Trigger a new deployment job.
    """
    response = requests.post(
        f"{API_URL}/ota/deploy",
        params={"version": version, "wave": wave},
        timeout=30,
    )
    if response.status_code == requests.codes.ok:
        data = response.json()
        typer.echo(
            f"✅ Deployment Job Created: ID {data['job_id']} | "
            f"Status: {data['status']}",
        )
    else:
        typer.echo("❌ Failed to trigger deployment job.")


@app.command()
def list_jobs():
    """
    List all deployment jobs.
    """
    response = requests.get(f"{API_URL}/ota/jobs", timeout=30)
    if response.status_code == requests.codes.ok:
        for job in response.json():
            job_info = (
                f"[{job['id']}] Version: {job['version']} | "
                f"Wave: {job['wave']} | Status: {job['status']}"
            )
            typer.echo(job_info)
    else:
        typer.echo("❌ Failed to fetch jobs.")


@app.command()
def update(version: str, wave: str = "canary"):
    """
    Run deployment update rollout locally (patch Kubernetes pods).
    """
    typer.echo(
        f"🚀 Running local deployment update for version {version}, wave {wave}",
    )
    update_application_pods(version=version, wave=wave)


@app.command()
def rollback(version: str, wave: str = "green"):
    """
    Rollback application pods to a previous version.
    """
    typer.echo(f"🔄 Rolling back to version {version}, wave {wave}")
    rollback_application_pods(previous_version=version, wave=wave)


if __name__ == "__main__":
    app()
