import time
import requests
from kubernetes import client, config

API_URL = "http://127.0.0.1:8000"


def update_robot_pods(version: str):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    pods = v1.list_pod_for_all_namespaces(label_selector="status=idle").items
    for pod in pods:
        name = pod.metadata.name
        print(f"🚀 Updating {name} to version {version}")
        v1.patch_namespaced_pod(
            name=name,
            namespace=pod.metadata.namespace,
            body={"metadata": {"labels": {"sw_version": version, "status": "updated"}}},
        )


def run_ota_jobs():
    while True:
        print("🔍 Checking for pending OTA jobs...")
        jobs = requests.get(f"{API_URL}/ota/jobs").json()
        for job in jobs:
            if job["status"] == "pending":
                print(f"➡️  Found job ID {job['id']} — Deploying {job['version']}")
                update_robot_pods(job["version"])
                requests.post(
                    f"{API_URL}/ota/update_status",
                    params={"job_id": job["id"], "status": "complete"},
                )
        time.sleep(10)


if __name__ == "__main__":
    run_ota_jobs()
