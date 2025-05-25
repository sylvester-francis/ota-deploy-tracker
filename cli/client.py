import typer
import requests
import os
from dotenv import load_dotenv
from .job_runner import update_robot_pods  # noqa : E402

# Load environment variables from .env file if it exists
load_dotenv()

app = typer.Typer()
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


@app.command()
def deploy(version: str, wave: str = "canary"):
    """
    Trigger a new OTA job.
    """
    response = requests.post(
        f"{API_URL}/ota/deploy", params={"version": version, "wave": wave}
    )
    if response.status_code == 200:
        data = response.json()
        typer.echo(
            f"✅ OTA Job Created: ID {data['job_id']} | Status: {data['status']}"
        )
    else:
        typer.echo("❌ Failed to trigger OTA job.")


@app.command()
def list():
    """
    List all OTA jobs.
    """
    response = requests.get(f"{API_URL}/ota/jobs")
    if response.status_code == 200:
        for job in response.json():
            job_info = f"[{job['id']}] Version: {job['version']} | Wave: {job['wave']} | Status: {job['status']}"
            typer.echo(job_info)
    else:
        typer.echo("❌ Failed to fetch jobs.")


@app.command()
def update(version: str, wave: str = "canary"):
    """
    Run OTA update rollout locally (patch Kubernetes pods).
    """
    typer.echo(f"🚀 Running local OTA update for version {version}, wave {wave}")  # noqa : E501
    update_robot_pods(version=version, wave=wave)


if __name__ == "__main__":
    app()
