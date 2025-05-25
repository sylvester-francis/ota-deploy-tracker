import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "OTA Deploy Tracker Running"}


def test_list_jobs_endpoint(client):
    """Test the list jobs endpoint returns a list."""
    response = client.get("/ota/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_deploy_ota_endpoint(client):
    """Test the deploy OTA endpoint creates a job."""
    response = client.post("/ota/deploy", params={"version": "1.0.0", "wave": "canary"})
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert response.json()["status"] == "pending"


def test_update_status_endpoint(client):
    """Test the update status endpoint updates a job status."""
    # First create a job
    deploy_response = client.post("/ota/deploy", params={"version": "1.0.0", "wave": "canary"})
    job_id = deploy_response.json()["job_id"]

    # Then update its status
    update_response = client.post(
        "/ota/update_status",
        params={"job_id": job_id, "status": "complete"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "complete"
