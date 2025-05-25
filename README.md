# OTA Deploy Tracker

A comprehensive system for managing Over-The-Air (OTA) software updates for robot fleets with Kubernetes integration.

## Overview

The OTA Deploy Tracker provides a complete workflow for managing software updates to robot fleets with monitoring capabilities and different deployment strategies. It includes:

- Backend API for tracking deployment jobs
- CLI tools for triggering and managing deployments
- Dashboard for monitoring deployments
- Kubernetes integration for updating robot pods
- Prometheus-compatible metrics

## Features

- **Multiple Deployment Strategies**:
  - **Canary**: Updates just 1 pod (minimal risk)
  - **Blue**: Updates a subset of pods
  - **Green**: Updates all available pods
- **Real-time Monitoring**: Dashboard to view deployment status
- **Metrics Collection**: Prometheus-compatible metrics for monitoring
- **Kubernetes Integration**: Direct updates to robot pods
- **RESTful API**: Manage deployments programmatically

## System Architecture

The system consists of several components:

1. **Backend API (FastAPI)**: Manages OTA jobs and their statuses
2. **CLI Interface**: Provides command-line tools for triggering deployments
3. **Dashboard (Streamlit)**: Offers a visual interface for monitoring deployments
4. **Kubernetes Integration**: Handles the actual deployment to robot pods

## Installation

### Prerequisites

- Python 3.8+ (for local development)
- Kubernetes cluster (or minikube for local development)
- kubectl configured to access your cluster
- Docker and Docker Compose (for containerized deployment)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sylvester-francis/ota-deploy-tracker.git
   cd ota-deploy-tracker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create sample robot pods:
   ```bash
   kubectl apply -f k8s/robots.yaml
   ```

### Docker Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sylvester-francis/ota-deploy-tracker.git
   cd ota-deploy-tracker
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Create sample robot pods:
   ```bash
   kubectl apply -f k8s/robots.yaml
   ```

## Usage

### Local Development

#### Starting the Backend API

```bash
uvicorn backend.main:app --reload
```

The API will be available at http://127.0.0.1:8000

#### Starting the Dashboard

```bash
streamlit run dashboard/ota_dashboard.py
```

The dashboard will be available at http://localhost:8501

#### Using the CLI

##### Trigger a new OTA deployment:

```bash
python -m cli.client deploy 2.0.0 --wave canary
```

##### List all OTA jobs:

```bash
python -m cli.client list
```

##### Run an OTA update directly:

```bash
python -m cli.client update 2.0.0 --wave blue
```

### Docker Deployment

#### Starting All Services

```bash
docker-compose up -d
```

This will start the API, dashboard, and job-runner services in the background.

#### Viewing Logs

```bash
# View logs from all services
docker-compose logs -f

# View logs from a specific service
docker-compose logs -f api
docker-compose logs -f dashboard
docker-compose logs -f job-runner
```

#### Using the CLI with Docker

```bash
# Trigger a new OTA deployment
docker-compose exec api python -m cli.client deploy 2.0.0 --wave canary

# List all OTA jobs
docker-compose exec api python -m cli.client list

# Run an OTA update directly
docker-compose exec api python -m cli.client update 2.0.0 --wave blue
```

#### Accessing Services

- API: http://localhost:8000
- Dashboard: http://localhost:8501

### Deployment Waves

- **canary**: Updates 1 pod
- **blue**: Updates a subset of pods (default: 2)
- **green**: Updates all available pods

## API Endpoints

- `GET /`: Health check
- `POST /ota/deploy`: Create a new OTA job
- `GET /ota/jobs`: List all OTA jobs
- `POST /ota/update_status`: Update job status
- `GET /metrics`: Prometheus-compatible metrics

## Metrics

The system collects the following metrics:

- **ota_updated_pods_total**: Total number of pods updated
- **ota_last_run_timestamp_seconds**: Timestamp of the last OTA run
- **ota_jobs_pending**: Number of pending OTA jobs
- **ota_jobs_successful**: Number of successfully completed OTA jobs
- **ota_jobs_total**: Total number of OTA jobs triggered

## Development

### Project Structure

```
.
├── backend/                # FastAPI backend
│   ├── database.py         # Database configuration
│   ├── main.py             # API endpoints
│   └── models.py           # Database models
├── cli/                    # Command-line interface
│   ├── job_runner.py       # OTA update logic
│   └── client.py           # CLI commands
├── dashboard/              # Streamlit dashboard
│   └── ota_dashboard.py    # Dashboard UI
├── k8s/                    # Kubernetes configurations
│   └── robots.yaml         # Sample robot pod definitions
├── .dockerignore           # Files to exclude from Docker builds
├── .env.example            # Environment variables template
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Main Dockerfile
├── Dockerfile.api          # API-specific Dockerfile
├── Dockerfile.dashboard    # Dashboard-specific Dockerfile
├── Dockerfile.job-runner   # Job runner-specific Dockerfile
├── metrics.txt             # Generated metrics file
└── requirements.txt        # Python dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.