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
# HELP ota_jobs_pending Number of pending OTA jobs
# TYPE ota_jobs_pending gauge
ota_jobs_pending {total_jobs - updated_count}

# HELP ota_jobs_successful Number of successfully updated jobs
# TYPE ota_jobs_successful counter
ota_jobs_successful {updated_count}

# HELP ota_jobs_total Total number of OTA jobs triggered
# TYPE ota_jobs_total gauge
ota_jobs_total {total_jobs}
"""

    # Write combined metrics
    with open(metrics_path, "w") as f:
        f.write(existing_metrics + "\n" + job_metrics if existing_metrics else job_metrics)


def update_robot_pods(version: str, wave: str = "canary"):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print(f"🛠️ update_robot_pods called with version={version}, wave={wave}")

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
# HELP ota_last_run_timestamp_seconds Last OTA timestamp
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
        f"🔁 Starting OTA rollout: version={version}, wave={wave}, targeting {max_to_update} pods"
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

    print(f"✅ OTA rollout complete: {updated_count} pods updated to version {version}")

    # For direct update calls, we'll consider this as 1 job with the given updated_count
    total_jobs = 1
    # Create pod metrics
    pod_metrics = f"""
# HELP ota_updated_pods_total Total pods updated
# TYPE ota_updated_pods_total counter
ota_updated_pods_total {updated_count}
# HELP ota_last_run_timestamp_seconds Last OTA timestamp
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


def run_ota_jobs():
    while True:
        print("🔍 Checking for pending OTA jobs...")
        jobs = requests.get(f"{API_URL}/ota/jobs").json()
        for job in jobs:
            if job["status"] == "pending":
                print(f"➡️  Found job ID {job['id']} — Deploying {job['version']}")  # noqa : E501
                update_robot_pods(job["version"], wave=job.get("wave", "canary"))  # noqa : E501
                requests.post(
                    f"{API_URL}/ota/update_status",
                    params={"job_id": job["id"], "status": "complete"},
                )
        time.sleep(10)


if __name__ == "__main__":
    run_ota_jobs()
