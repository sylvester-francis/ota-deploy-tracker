from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

# HTTP status constants
HTTP_OK = 200


def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == HTTP_OK
    assert response.json() == {"msg": "Kubernetes Deployment Manager Running"}


@patch("backend.main.get_db")
def test_deploy_ota(mock_get_db):
    """Test deployment creation."""
    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    # Mock the job object
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.version = "2.0.0"
    mock_job.status = "pending"

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    mock_db.close.return_value = None

    with patch("backend.models.OTAJob", return_value=mock_job):
        response = client.post("/ota/deploy?version=2.0.0&wave=canary")

    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["job_id"] == 1
    assert data["version"] == "2.0.0"
    assert data["status"] == "pending"


@patch("backend.main.get_db")
def test_list_jobs(mock_get_db):
    """Test job listing."""
    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    # Mock job data
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.version = "2.0.0"
    mock_job.wave = "canary"
    mock_job.status = "complete"
    mock_job.created_at.isoformat.return_value = "2025-05-24T16:29:22"

    mock_db.query.return_value.order_by.return_value.all.return_value = [mock_job]
    mock_db.close.return_value = None

    response = client.get("/ota/jobs")

    assert response.status_code == HTTP_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["version"] == "2.0.0"


def test_metrics():
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == HTTP_OK
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

