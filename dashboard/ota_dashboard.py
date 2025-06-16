import os
import subprocess
import time

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(layout="wide", page_title="Kubernetes Deployment Manager")
st.title("🚀 Kubernetes Deployment Manager")

# Add auto-refresh functionality
col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.button("🔄 Refresh", help="Refresh all data"):
        st.rerun()
with col3:
    auto_refresh = st.checkbox("Auto-refresh (30s)", help="Automatically refresh every 30 seconds")

# Auto-refresh logic
if auto_refresh:
    # Create a placeholder for the refresh timer
    placeholder = st.empty()
    with placeholder.container():
        st.info(f"🔄 Auto-refreshing in 30 seconds... (Last refresh: {time.strftime('%H:%M:%S')})")
    time.sleep(30)
    placeholder.empty()
    st.rerun()

# --- View All Jobs ---
st.subheader("📋 Deployment Job Queue")
jobs = requests.get(f"{API_URL}/ota/jobs").json()
if jobs:
    df = pd.DataFrame(jobs)
    st.dataframe(df)
else:
    st.info("No deployment jobs found.")

# --- Add New Job ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Create New Deployment")
    with st.form("deploy_form"):
        version = st.text_input("Version", "3.0.0")
        wave = st.selectbox("Wave", ["canary", "blue", "green"])
        submitted = st.form_submit_button("Trigger Deployment")
        if submitted:
            result = subprocess.run(
                ["python", "-m", "cli.client", "deploy", version, "--wave", wave],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                st.success("Deployment triggered successfully!")
            else:
                st.error(f"Error: {result.stderr}")

with col2:
    st.subheader("🔄 Rollback Deployment")
    with st.form("rollback_form"):
        rollback_version = st.text_input("Rollback to Version", "2.0.0")
        rollback_wave = st.selectbox(
            "Rollback Wave", ["canary", "blue", "green"], index=2
        )
        rollback_submitted = st.form_submit_button("Trigger Rollback")
        if rollback_submitted:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "cli.client",
                    "rollback",
                    rollback_version,
                    "--wave",
                    rollback_wave,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                st.success("Rollback triggered successfully!")
            else:
                st.error(f"Error: {result.stderr}")

# --- Live Pod Viewer ---
st.subheader("📦 Application Pod Status (from Kubernetes)")
pod_data = []

# Check if kubectl is available and cluster is accessible
try:
    # Test basic kubectl connectivity first
    subprocess.check_output(["kubectl", "version", "--client"], stderr=subprocess.DEVNULL)
    kubectl_available = True
except (subprocess.CalledProcessError, FileNotFoundError):
    kubectl_available = False

if kubectl_available:
    try:
        # Try to get pods with a simpler command first
        output = subprocess.check_output(
            ["kubectl", "get", "pods", "--no-headers"],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode()

        # If basic command works, try the detailed one
        if output.strip():
            detailed_output = subprocess.check_output(
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-o",
                    'jsonpath={range .items[*]}{.metadata.name} {.metadata.labels.sw_version} {.metadata.labels.status}{"\\n"}{end}',
                ],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()

            for line in detailed_output.strip().split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        # Handle case where labels might not exist
                        name = parts[0] if len(parts) > 0 else "unknown"
                        version = parts[1] if len(parts) > 1 else "unknown"
                        status = parts[2] if len(parts) > 2 else "unknown"
                        pod_data.append({"Name": name, "Version": version, "Status": status})

        if pod_data:
            pod_df = pd.DataFrame(pod_data)
            st.dataframe(pod_df)
        else:
            st.info("No pods found with the expected labels. Showing basic pod list:")
            # Show basic pod info as fallback
            basic_pods = []
            for line in output.strip().split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        basic_pods.append({"Name": parts[0], "Status": parts[1], "Version": "N/A"})

            if basic_pods:
                basic_df = pd.DataFrame(basic_pods)
                st.dataframe(basic_df)
                pod_data = basic_pods  # Use basic pods for log viewing
            else:
                st.info("No pods found in the cluster.")

    except subprocess.TimeoutExpired:
        st.error("Kubernetes cluster connection timed out.")
        st.info("Make sure your Kubernetes cluster is running and kubectl is properly configured.")
    except Exception as e:
        st.error(f"Error fetching pods: {str(e)}")
        st.info("Make sure kubectl is configured and a Kubernetes cluster is accessible.")
else:
    st.warning("kubectl is not available or not in PATH.")
    st.info("To use Kubernetes features, please install kubectl and configure access to a cluster.")
    # Show demo data for development
    st.info("📝 Demo Mode: Showing sample pod data")
    demo_data = [
        {"Name": "application-1", "Version": "1.0.0", "Status": "running"},
        {"Name": "application-2", "Version": "2.0.0", "Status": "pending"},
        {"Name": "application-1-backup", "Version": "1.0.0", "Status": "running"},
    ]
    demo_df = pd.DataFrame(demo_data)
    st.dataframe(demo_df)
    pod_data = demo_data

st.subheader("🧾 Pod Logs")
if pod_data:
    selected_pod = st.selectbox("Choose an application pod", [p["Name"] for p in pod_data])
else:
    st.info("No pods available. Please check your Kubernetes connection.")
if pod_data and st.button("View Logs"):
    if kubectl_available:
        try:
            logs = subprocess.check_output(["kubectl", "logs", selected_pod, "--tail=100"], timeout=10).decode()
            if logs.strip():
                st.code(logs, language="bash")
            else:
                st.info(f"No logs available for pod {selected_pod}")
                st.text("This is normal for pods running simple commands like 'sleep'")
                # Show pod events as alternative
                try:
                    events = subprocess.check_output(
                        ["kubectl", "get", "events", "--field-selector", f"involvedObject.name={selected_pod}", "--sort-by=.lastTimestamp"],
                        timeout=5
                    ).decode()
                    if events.strip():
                        st.subheader("📅 Recent Pod Events")
                        st.code(events, language="bash")
                except Exception:
                    pass
        except subprocess.TimeoutExpired:
            st.error("Timeout while fetching logs")
        except Exception as e:
            st.error(f"Error fetching logs: {e}")
    else:
        # Demo mode - show sample logs
        st.info("📝 Demo Mode: Sample logs for selected pod")
        sample_logs = f"""2025-06-16 02:10:00 INFO Starting application {selected_pod}
2025-06-16 02:10:01 INFO Loading configuration...
2025-06-16 02:10:02 INFO Database connection established
2025-06-16 02:10:03 INFO Server listening on port 8080
2025-06-16 02:10:04 INFO Application ready to serve requests
2025-06-16 02:10:05 INFO Health check passed"""
        st.code(sample_logs, language="bash")
