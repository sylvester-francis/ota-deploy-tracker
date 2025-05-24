import os
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from kubernetes import client, config

# Load environment variables from .env file if it exists
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
OTA_STATUS_FILE = Path(__file__).parent / "ota_status.json"
METRICS_FILE = Path(__file__).parent / "metrics.txt"


def retry_patch(v1, name, namespace, body, retries=3):
    for i in range(retries):
        try:
            v1.patch_namespaced_pod(name=name, namespace=namespace, body=body)
            return True
        except Exception as e:
            print(f"⚠️ Retry {i + 1}/{retries} failed for {name}: {e}")
            time.sleep(2 ** i)
    return False


def write_metrics(updated_count: int, total_jobs: int):
    # Absolute path to root-level metrics.txt
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    metrics_path = os.path.join(root_dir, "metrics.txt")

    # Read existing metrics if they exist
    existing_metrics = ""
    try:
        with open(metrics_path, "r") as f:
            existing_metrics = f.read()
    except FileNotFoundError:
        pass
    # Append job metrics
    job_metrics = f"""
# HELP ota_jobs_pending Number of pending deployment jobs
# TYPE ota_jobs_pending gauge
 ota_jobs_pending {total_jobs - updated_count}

# HELP ota_jobs_successful Number of successfully updated jobs
# TYPE ota_jobs_successful counter
 ota_jobs_successful {updated_count}

# HELP ota_jobs_total Total number of deployment jobs triggered
# TYPE ota_jobs_total gauge
 ota_jobs_total {total_jobs}
"""

    # Write combined metrics
    with open(metrics_path, "w") as f:
        f.write(existing_metrics + "\n" + job_metrics if existing_metrics else job_metrics)


def update_application_pods(version: str, wave: str = "canary"):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print(f"🛠️ update_application_pods called with version={version}, wave={wave}")

    try:
        pods = v1.list_pod_for_all_namespaces(label_selector="status=idle").items
    except Exception as e:
        print(f"❌ Failed to fetch pods: {e}")
        return

    if not pods:
        print("⚠️ No idle pods found to update.")
        # Still write metrics even when no pods are found
        updated_count = 0
        total_jobs = 1
        # Create pod metrics
        pod_metrics = f"""
# HELP ota_updated_pods_total Total pods updated
# TYPE ota_updated_pods_total counter
 ota_updated_pods_total {updated_count}
# HELP ota_last_run_timestamp_seconds Last deployment timestamp
# TYPE ota_last_run_timestamp_seconds gauge
 ota_last_run_timestamp_seconds {int(datetime.utcnow().timestamp())}
""".strip()

        # Absolute path to root-level metrics.txt
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        metrics_path = os.path.join(root_dir, "metrics.txt")
        # Write pod metrics first
        with open(metrics_path, "w") as f:
            f.write(pod_metrics + "\n")
        # Then append job metrics
        write_metrics(updated_count, total_jobs)
        print(f"📊 Metrics written to {metrics_path}")
        return

    wave_map = {
        "canary": 1,
        "blue": min(2, len(pods)),
        "green": len(pods),
    }

    max_to_update = wave_map.get(wave, 1)
    updated_count = 0

    print(
        f"🔁 Starting deployment rollout: version={version}, wave={wave}, targeting {max_to_update} pods"
    )

    for pod in pods:
        if updated_count >= max_to_update:
            break

        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        body = {"metadata": {"labels": {"sw_version": version, "status": "updated"}}}

        success = retry_patch(v1, pod_name, namespace, body)
        if success:
            updated_count += 1
        else:
            print(f"🚫 Skipping {pod_name} after retries.")

    print(f"✅ Deployment rollout complete: {updated_count} pods updated to version {version}")

    # For direct update calls, we'll consider this as 1 job with the given updated_count
    total_jobs = 1
    # Create pod metrics
    pod_metrics = f"""
# HELP ota_updated_pods_total Total pods updated
# TYPE ota_updated_pods_total counter
 ota_updated_pods_total {updated_count}
# HELP ota_last_run_timestamp_seconds Last deployment timestamp
# TYPE ota_last_run_timestamp_seconds gauge
 ota_last_run_timestamp_seconds {int(datetime.utcnow().timestamp())}
""".strip()
    # Absolute path to root-level metrics.txt
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    metrics_path = os.path.join(root_dir, "metrics.txt")

    # Write pod metrics first
    with open(metrics_path, "w") as f:
        f.write(pod_metrics + "\n")
    # Then append job metrics
    write_metrics(updated_count, total_jobs)
    print(f"📊 Metrics written to {metrics_path}")


def rollback_application_pods(previous_version: str, wave: str = "green"):
    """
    Rollback application pods to a previous version.
    
    Args:
        previous_version: The version to rollback to
        wave: The rollback scope (default: "green" for all pods)
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print(f"🔄 rollback_application_pods called with version={previous_version}, wave={wave}")

    try:
        # Get all pods that have been updated (status="updated")
        pods = v1.list_pod_for_all_namespaces(label_selector="status=updated").items
    except Exception as e:
        print(f"❌ Failed to fetch pods for rollback: {e}")
        return

    if not pods:
        print("⚠️ No updated pods found to rollback.")
        return

    wave_map = {
        "canary": 1,
        "blue": min(2, len(pods)),
        "green": len(pods),
    }

    max_to_rollback = wave_map.get(wave, len(pods))
    rollback_count = 0

    print(
        f"🔁 Starting rollback: version={previous_version}, wave={wave}, targeting {max_to_rollback} pods"
    )

    for pod in pods:
        if rollback_count >= max_to_rollback:
            break

        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        body = {"metadata": {"labels": {"sw_version": previous_version, "status": "idle"}}}

        success = retry_patch(v1, pod_name, namespace, body)
        if success:
            rollback_count += 1
            print(f"✅ Rolled back {pod_name} to version {previous_version}")
        else:
            print(f"🚫 Failed to rollback {pod_name} after retries.")

    print(f"✅ Rollback complete: {rollback_count} pods rolled back to version {previous_version}")

    # Write rollback metrics
    rollback_metrics = f"""
# HELP ota_rollback_pods_total Total pods rolled back
# TYPE ota_rollback_pods_total counter
 ota_rollback_pods_total {rollback_count}
# HELP ota_last_rollback_timestamp_seconds Last rollback timestamp
# TYPE ota_last_rollback_timestamp_seconds gauge
 ota_last_rollback_timestamp_seconds {int(datetime.utcnow().timestamp())}
""".strip()

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    metrics_path = os.path.join(root_dir, "metrics.txt")

    # Append rollback metrics
    try:
        with open(metrics_path, "a") as f:
            f.write("\n" + rollback_metrics + "\n")
        print(f"📊 Rollback metrics written to {metrics_path}")
    except Exception as e:
        print(f"⚠️ Failed to write rollback metrics: {e}")


def run_ota_jobs():
    while True:
        print("🔍 Checking for pending deployment jobs...")
        jobs = requests.get(f"{API_URL}/ota/jobs").json()
        for job in jobs:
            if job["status"] == "pending":
                print(f"➡️  Found job ID {job['id']} — Deploying {job['version']}")  # noqa : E501
                update_application_pods(job["version"], wave=job.get("wave", "canary"))  # noqa : E501
                requests.post(
                    f"{API_URL}/ota/update_status",
                    params={"job_id": job["id"], "status": "complete"},
                )
            elif job["status"] == "rollback_pending":
                print(f"🔄 Found rollback job ID {job['id']} — Rolling back to {job['version']}")  # noqa : E501
                rollback_application_pods(job["version"], wave=job.get("wave", "green"))  # noqa : E501
                requests.post(
                    f"{API_URL}/ota/update_status",
                    params={"job_id": job["id"], "status": "rollback_complete"},
                )
        time.sleep(10)


if __name__ == "__main__":
    run_ota_jobs()