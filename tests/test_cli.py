from unittest.mock import MagicMock, patch

import pytest

import cli.client
from cli.client import deploy, update
from cli.client import list as list_jobs


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"job_id": 1, "status": "pending"}
    return mock


@patch("cli.client.requests.post")
def test_deploy(mock_post, mock_response):
    """Test the deploy command sends the correct request."""
    mock_post.return_value = mock_response

    with patch("cli.client.typer.echo") as mock_echo:
        deploy("2.0.0", "canary")

    mock_post.assert_called_once_with(
        f"{cli.client.API_URL}/ota/deploy", params={"version": "2.0.0", "wave": "canary"}
    )
    mock_echo.assert_called_once()


@patch("cli.client.requests.get")
def test_list_jobs(mock_get, mock_response):
    """Test the list command sends the correct request."""
    mock_response.json.return_value = [
        {"id": 1, "version": "1.0.0", "wave": "canary", "status": "complete"}
    ]
    mock_get.return_value = mock_response

    with patch("cli.client.typer.echo") as mock_echo:
        list_jobs()

    mock_get.assert_called_once_with(f"{cli.client.API_URL}/ota/jobs")
    mock_echo.assert_called_once()


@patch("cli.client.update_robot_pods")
def test_update(mock_update_robot_pods):
    """Test the update command calls update_robot_pods with correct args."""
    with patch("cli.client.typer.echo") as mock_echo:
        update("2.0.0", "canary")

    mock_update_robot_pods.assert_called_once_with(version="2.0.0", wave="canary")
    mock_echo.assert_called_once()
