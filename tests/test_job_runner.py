from unittest.mock import MagicMock, patch

import pytest
from kubernetes.client.exceptions import ApiException

from cli.job_runner import (
    retry_patch,
    rollback_application_pods,
    update_application_pods,
    write_metrics,
)


@pytest.fixture
def mock_k8s_client():
    return MagicMock()


@pytest.fixture
def mock_pod():
    mock = MagicMock()
    mock.metadata.name = "app-1"
    mock.metadata.namespace = "default"
    return mock


@patch("cli.job_runner.client.CoreV1Api")
@patch("cli.job_runner.config.load_kube_config")
def test_update_application_pods_no_pods(
    mock_load_config, mock_core_api, mock_k8s_client,
):
    """Test update_application_pods when no pods are found."""
    mock_core_api.return_value = mock_k8s_client
    mock_k8s_client.list_pod_for_all_namespaces.return_value.items = []

    with patch("cli.job_runner.Path.write_text") as mock_write:
        update_application_pods("2.0.0", "canary")
    mock_load_config.assert_called_once()
    mock_core_api.assert_called_once()
    mock_k8s_client.list_pod_for_all_namespaces.assert_called_once_with(label_selector="status=idle")
    # Verify metrics were written even with no pods
    assert mock_write.call_count > 0


@patch("cli.job_runner.client.CoreV1Api")
@patch("cli.job_runner.config.load_kube_config")
@patch("cli.job_runner.retry_patch")
def test_update_application_pods_with_pods(
    mock_retry_patch, mock_load_config, mock_core_api, mock_k8s_client, mock_pod,
):
    """Test update_application_pods with pods to update."""
    mock_core_api.return_value = mock_k8s_client
    mock_k8s_client.list_pod_for_all_namespaces.return_value.items = [mock_pod]
    mock_retry_patch.return_value = True

    with patch("cli.job_runner.Path.write_text") as mock_write:
        update_application_pods("2.0.0", "canary")
    mock_load_config.assert_called_once()
    mock_core_api.assert_called_once()
    mock_k8s_client.list_pod_for_all_namespaces.assert_called_once_with(label_selector="status=idle")
    mock_retry_patch.assert_called_once()
    # Verify metrics were written
    assert mock_write.call_count > 0


@patch("cli.job_runner.client.CoreV1Api")
@patch("cli.job_runner.config.load_kube_config")
@patch("cli.job_runner.retry_patch")
def test_rollback_application_pods_with_pods(
    mock_retry_patch, mock_load_config, mock_core_api, mock_k8s_client, mock_pod,
):
    """Test rollback_application_pods with pods to rollback."""
    mock_core_api.return_value = mock_k8s_client
    mock_k8s_client.list_pod_for_all_namespaces.return_value.items = [mock_pod]
    mock_retry_patch.return_value = True

    with patch("cli.job_runner.Path.write_text") as mock_write, patch("cli.job_runner.Path.read_text") as mock_read:
        mock_read.return_value = "existing metrics"
        rollback_application_pods("1.0.0", "green")
    mock_load_config.assert_called_once()
    mock_core_api.assert_called_once()
    mock_k8s_client.list_pod_for_all_namespaces.assert_called_once_with(label_selector="status=updated")
    mock_retry_patch.assert_called_once()
    # Verify metrics were written
    assert mock_write.call_count > 0


@patch("cli.job_runner.Path.write_text")
@patch("cli.job_runner.Path.read_text")
def test_write_metrics(mock_read, mock_write):
    """Test write_metrics writes the correct metrics."""
    mock_read.side_effect = FileNotFoundError  # No existing metrics
    write_metrics(1, 2)
    mock_write.assert_called_once()
    # Check that metrics content was written
    args, kwargs = mock_write.call_args
    assert "ota_jobs_pending" in args[0]  # Content contains expected metrics


@patch("cli.job_runner.time.sleep")
def test_retry_patch_success(mock_sleep, mock_k8s_client, mock_pod):
    """Test retry_patch succeeds on first try."""
    mock_k8s_client.patch_namespaced_pod.return_value = True

    result = retry_patch(
        mock_k8s_client,
        mock_pod.metadata.name,
        mock_pod.metadata.namespace,
        {"metadata": {"labels": {"sw_version": "2.0.0", "status": "updated"}}},
    )
    assert result is True
    mock_k8s_client.patch_namespaced_pod.assert_called_once()
    mock_sleep.assert_not_called()


@patch("cli.job_runner.time.sleep")
def test_retry_patch_failure(mock_sleep, mock_k8s_client, mock_pod):
    """Test retry_patch retries on failure."""
    mock_k8s_client.patch_namespaced_pod.side_effect = [ApiException("Error"), True]

    result = retry_patch(
        mock_k8s_client,
        mock_pod.metadata.name,
        mock_pod.metadata.namespace,
        {"metadata": {"labels": {"sw_version": "2.0.0", "status": "updated"}}},
        retries=2,
    )
    assert result is True
    expected_call_count = 2
    assert mock_k8s_client.patch_namespaced_pod.call_count == expected_call_count
    mock_sleep.assert_called_once()
