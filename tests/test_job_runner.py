import pytest
from unittest.mock import patch, MagicMock
import os
from cli.job_runner import update_robot_pods, write_metrics, retry_patch


@pytest.fixture
def mock_k8s_client():
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_pod():
    mock = MagicMock()
    mock.metadata.name = "robot-1"
    mock.metadata.namespace = "default"
    return mock


@patch("cli.job_runner.client.CoreV1Api")
@patch("cli.job_runner.config.load_kube_config")
def test_update_robot_pods_no_pods(mock_load_config, mock_core_api, mock_k8s_client):
    """Test update_robot_pods when no pods are found."""
    mock_core_api.return_value = mock_k8s_client
    mock_k8s_client.list_pod_for_all_namespaces.return_value.items = []
    
    with patch("cli.job_runner.open", create=True) as mock_open:
        update_robot_pods("2.0.0", "canary")
    
    mock_load_config.assert_called_once()
    mock_core_api.assert_called_once()
    mock_k8s_client.list_pod_for_all_namespaces.assert_called_once_with(label_selector="status=idle")
    # Verify metrics were written even with no pods
    assert mock_open.call_count > 0


@patch("cli.job_runner.client.CoreV1Api")
@patch("cli.job_runner.config.load_kube_config")
@patch("cli.job_runner.retry_patch")
def test_update_robot_pods_with_pods(mock_retry_patch, mock_load_config, mock_core_api, mock_k8s_client, mock_pod):
    """Test update_robot_pods with pods to update."""
    mock_core_api.return_value = mock_k8s_client
    mock_k8s_client.list_pod_for_all_namespaces.return_value.items = [mock_pod]
    mock_retry_patch.return_value = True
    
    with patch("cli.job_runner.open", create=True) as mock_open:
        update_robot_pods("2.0.0", "canary")
    
    mock_load_config.assert_called_once()
    mock_core_api.assert_called_once()
    mock_k8s_client.list_pod_for_all_namespaces.assert_called_once_with(label_selector="status=idle")
    mock_retry_patch.assert_called_once()
    # Verify metrics were written
    assert mock_open.call_count > 0


@patch("builtins.open", create=True)
def test_write_metrics(mock_open):
    """Test write_metrics writes the correct metrics."""
    write_metrics(1, 2)
    mock_open.assert_called()
    # Check that the file was opened for writing
    args, kwargs = mock_open.call_args
    assert kwargs.get('mode', 'w') == 'w'


@patch("cli.job_runner.time.sleep")
def test_retry_patch_success(mock_sleep, mock_k8s_client, mock_pod):
    """Test retry_patch succeeds on first try."""
    mock_k8s_client.patch_namespaced_pod.return_value = True
    
    result = retry_patch(
        mock_k8s_client, 
        mock_pod.metadata.name, 
        mock_pod.metadata.namespace, 
        {"metadata": {"labels": {"sw_version": "2.0.0", "status": "updated"}}}
    )
    
    assert result is True
    mock_k8s_client.patch_namespaced_pod.assert_called_once()
    mock_sleep.assert_not_called()


@patch("cli.job_runner.time.sleep")
def test_retry_patch_failure(mock_sleep, mock_k8s_client, mock_pod):
    """Test retry_patch retries on failure."""
    mock_k8s_client.patch_namespaced_pod.side_effect = [Exception("Error"), True]
    
    result = retry_patch(
        mock_k8s_client, 
        mock_pod.metadata.name, 
        mock_pod.metadata.namespace, 
        {"metadata": {"labels": {"sw_version": "2.0.0", "status": "updated"}}},
        retries=2
    )
    
    assert result is True
    assert mock_k8s_client.patch_namespaced_pod.call_count == 2
    mock_sleep.assert_called_once()
