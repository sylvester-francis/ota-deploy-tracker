import typer
import requests

app = typer.Typer()
API_URL = "http://127.0.0.1:8000"


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
            typer.echo(
                f"[{job['id']}] Version: {job['version']} | Wave: {job['wave']} | Status: {job['status']}"
            )
    else:
        typer.echo("❌ Failed to fetch jobs.")


if __name__ == "__main__":
    app()
