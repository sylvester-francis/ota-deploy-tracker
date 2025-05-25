import os
import subprocess

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(layout="wide")
st.title("🤖 OTA Deployment Tracker")

# --- View All Jobs ---
st.subheader("📋 OTA Job Queue")
jobs = requests.get(f"{API_URL}/ota/jobs").json()
if jobs:
    df = pd.DataFrame(jobs)
    st.dataframe(df)
else:
    st.info("No OTA jobs found.")

# --- Add New Job ---
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
        )
        if result.returncode == 0:
            st.success("Deployment triggered successfully!")
        else:
            st.error(f"Error: {result.stderr}")

# --- Live Pod Viewer ---
st.subheader("📦 Robot Pod Status (from Kubernetes)")
try:
    output = subprocess.check_output(
        [
            "kubectl",
            "get",
            "pods",
            "-o",
            'jsonpath={range .items[*]}{.metadata.name} {.metadata.labels.sw_version} {.metadata.labels.status}{"\\n"}{end}',  # noqa: E501
        ]
    ).decode()
    pod_data = []
    for line in output.strip().split("\n"):
        parts = line.split()
        if len(parts) == 3:
            pod_data.append({"Name": parts[0], "Version": parts[1], "Status": parts[2]})  # noqa : E501
    pod_df = pd.DataFrame(pod_data)
    st.dataframe(pod_df)
except Exception as e:
    st.error(f"Error fetching pods: {e}")

st.subheader("🧾 Pod Logs")
selected_pod = st.selectbox("Choose a robot pod", [p["Name"] for p in pod_data])  # noqa : E501
if st.button("View Logs"):
    try:
        logs = subprocess.check_output(["kubectl", "logs", selected_pod]).decode()  # noqa : E501
        st.code(logs, language="bash")
    except Exception as e:
        st.error(f"Error: {e}")
