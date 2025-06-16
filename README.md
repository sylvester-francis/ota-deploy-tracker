# Kubernetes Deployment Manager

> **Professional-grade progressive deployment management for Kubernetes environments**

A comprehensive, enterprise-ready platform for managing safe, controlled software deployments across Kubernetes clusters with real-time monitoring, multiple rollout strategies, and instant rollback capabilities.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Kubernetes](https://img.shields.io/badge/kubernetes-1.20+-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Typer](https://img.shields.io/badge/typer-0.9.0-ff69b4.svg)

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "External Clients"
        CLI[CLI Tool<br/>cli/client.py]
        WebUI[Web Dashboard<br/>dashboard/ota_dashboard.py]
        API_Client[External API Client<br/>CI/CD Systems]
    end
    
    subgraph "Core Platform"
        API[FastAPI Backend<br/>backend/main.py<br/>Port: 8000]
        JobRunner[Job Runner<br/>cli/job_runner.py<br/>Background Processing]
        DB[(SQLite Database<br/>deployment.db)]
    end
    
    subgraph "Kubernetes Cluster"
        K8S_API[Kubernetes API Server]
        Pods[Application Pods<br/>k8s/application.yaml]
        Services[Services & Deployments<br/>k8s/deployment.yaml]
    end
    
    subgraph "Monitoring & Metrics"
        Prometheus[Prometheus Server<br/>Port: 9090]
        Grafana[Grafana Dashboard<br/>Port: 3000]
        Metrics[Metrics Endpoint<br/>/metrics]
        Logs[Application Logs<br/>Structured Logging]
    end
    
    %% Client connections
    CLI -->|HTTP Requests| API
    WebUI -->|Streamlit Server| API
    API_Client -->|REST API| API
    
    %% Core platform flow
    API -->|Job Queue| DB
    DB -->|Pending Jobs| JobRunner
    JobRunner -->|kubectl Operations| K8S_API
    
    %% Kubernetes operations
    K8S_API -->|Manage| Pods
    K8S_API -->|Deploy| Services
    
    %% Monitoring flow
    API -->|Expose| Metrics
    Metrics -->|Scrape| Prometheus
    Prometheus -->|Data Source| Grafana
    JobRunner -->|Generate| Logs
    K8S_API -->|Status Updates| JobRunner
    
    %% Deployment strategies
    JobRunner -.->|Canary<br/>1 Pod| Pods
    JobRunner -.->|Blue<br/>Subset| Pods
    JobRunner -.->|Green<br/>All Pods| Pods
    
    %% Rollback flow
    JobRunner -.->|Rollback<br/>Previous Version| Pods
    
    style CLI fill:#e1f5fe
    style WebUI fill:#e8f5e8
    style API fill:#fff3e0
    style JobRunner fill:#fce4ec
    style K8S_API fill:#f3e5f5
    style Prometheus fill:#e0f2f1
```

---

## 🎯 Why Choose Kubernetes Deployment Manager?

**For DevOps Teams:**
- Reduce deployment risks with progressive rollout strategies
- Gain instant visibility into deployment status across all environments
- Automate complex deployment workflows with simple CLI commands
- Integrate seamlessly with existing CI/CD pipelines

**For Platform Engineers:**
- Enterprise-grade observability with Prometheus metrics
- Kubernetes-native integration with no external dependencies
- Scalable architecture supporting clusters of any size
- Production-tested rollback mechanisms for instant recovery

**For Development Teams:**
- Simple, intuitive interface for deployment management
- Real-time dashboard for monitoring application health
- Consistent deployment processes across all environments
- Reduced time-to-production with automated workflows

---

## ✨ Key Features

### 🚀 Progressive Deployment Strategies
- **Canary**: Test with minimal risk (1 pod)
- **Blue**: Controlled subset rollout (configurable)
- **Green**: Full cluster deployment
- **Custom**: Define your own deployment patterns

### 🔄 Instant Rollback
- One-command rollback to any previous version
- Granular rollback control (canary, blue, green scopes)
- Automated failure detection and recovery
- Zero-downtime rollback operations

### 📊 Enterprise Observability
- Prometheus-compatible metrics out of the box
- Real-time deployment status tracking
- Comprehensive logging and audit trails
- Grafana dashboard templates included

### 🎛️ Multiple Interfaces
- **CLI**: Perfect for CI/CD integration and automation
- **Web Dashboard**: Visual monitoring and management
- **REST API**: Programmatic access for custom integrations
- **Kubernetes Native**: Direct kubectl compatibility

---

## 🚀 Quick Start

### Prerequisites
- **Kubernetes cluster** (v1.20+)
- **Python 3.8+**
- **kubectl** configured and connected
- **Docker** (for containerized deployment)

### 1. Installation

#### Option A: Quick Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/sylvester-francis/ota-deploy-tracker.git
cd ota-deploy-tracker

# Install dependencies
pip install -r requirements.txt

# Deploy sample applications with logging
kubectl apply -f k8s/application.yaml

# Start the system
docker-compose up -d
```

#### Option B: Local Development
```bash
# Clone and setup virtual environment
git clone https://github.com/sylvester-francis/ota-deploy-tracker.git
cd ota-deploy-tracker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start components separately
uvicorn backend.main:app --reload &
streamlit run dashboard/ota_dashboard.py &
python -m cli.job_runner &
```

### 2. Access Your Dashboard

- **Web Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Metrics Endpoint**: http://localhost:8000/metrics

### 3. Start Monitoring (Optional)

```bash
# Launch Prometheus + Grafana monitoring stack
./start-monitoring.sh

# Access monitoring:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

### 4. Your First Deployment

```bash
# Deploy version 2.0.0 using canary strategy
python -m cli.client deploy 2.0.0 --wave canary

# Monitor deployment status
python -m cli.client list

# Scale to blue wave (partial rollout)
python -m cli.client deploy 2.0.0 --wave blue

# Full deployment
python -m cli.client deploy 2.0.0 --wave green

# Rollback if needed
python -m cli.client rollback 1.0.0 --wave green
```

---

## 💻 Usage Examples

### CLI Operations

```bash
# Deployment Management
python -m cli.client deploy 3.1.4 --wave canary    # Canary deployment
python -m cli.client deploy 3.1.4 --wave blue      # Partial rollout
python -m cli.client deploy 3.1.4 --wave green     # Full deployment

# Monitoring
python -m cli.client list                           # List all jobs

# Rollback Operations
python -m cli.client rollback 3.1.3 --wave canary  # Canary rollback
python -m cli.client rollback 3.1.3 --wave green   # Full rollback

# Direct Pod Updates (Advanced)
python -m cli.client update 3.1.4 --wave blue      # Direct update
```

### Docker Operations

```bash
# Production deployment
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f dashboard
docker-compose logs -f job-runner

# Execute CLI commands
docker-compose exec api python -m cli.client deploy 1.5.0 --wave canary
docker-compose exec api python -m cli.client list
docker-compose exec api python -m cli.client rollback 1.4.0

# Scale services
docker-compose up -d --scale job-runner=3
```

---

## 🧪 Development & Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=cli --cov=dashboard --cov-report=html

# Run specific test categories
pytest tests/test_api.py          # API tests
pytest tests/test_cli.py          # CLI tests
pytest tests/test_job_runner.py   # Job runner tests
```

### Code Quality

```bash
# Linting and formatting
ruff check --fix backend/ cli/ dashboard/ tests/
ruff format backend/ cli/ dashboard/ tests/
```

---

## 🧪 Sample Applications

The platform includes sample applications (`app-1` and `app-2`) that demonstrate deployment management capabilities:

### Application Features
- **Realistic Logging**: Continuous application logs with startup sequences and health checks
- **Simulated Metrics**: Random memory usage and connection statistics
- **Version Tracking**: Applications tagged with `sw_version` labels for deployment tracking
- **Health Monitoring**: Periodic health check logs every 30 seconds

### Sample Log Output
```bash
Mon Jun 16 06:23:20 UTC 2025 [INFO] Application app-1 starting up...
Mon Jun 16 06:23:20 UTC 2025 [INFO] Loading configuration for version 1.0.0
Mon Jun 16 06:23:20 UTC 2025 [INFO] Database connection established
Mon Jun 16 06:23:20 UTC 2025 [INFO] Server listening on port 8080
Mon Jun 16 06:23:20 UTC 2025 [INFO] Application ready to serve requests
Mon Jun 16 06:23:20 UTC 2025 [INFO] Health check passed - app-1 running normally
Mon Jun 16 06:23:20 UTC 2025 [DEBUG] Memory usage: 73MB
Mon Jun 16 06:23:20 UTC 2025 [DEBUG] Active connections: 5
```

### Dashboard Features
- **Real-time Pod Status**: View current application versions and status
- **Log Streaming**: Access live application logs through the web interface
- **Auto-refresh**: Optional 30-second auto-refresh for real-time monitoring
- **Manual Refresh**: Instant updates with the refresh button

---

## 📊 Monitoring & Observability

### Quick Start Monitoring Stack

Launch the complete monitoring solution with one command:

```bash
# Start Prometheus + Grafana
./start-monitoring.sh

# Access URLs:
# - Prometheus UI: http://localhost:9090
# - Grafana Dashboard: http://localhost:3000 (admin/admin)
# - Raw Metrics: http://localhost:8000/metrics
```

### Prometheus Metrics

The platform exports comprehensive metrics for monitoring:

```bash
# Deployment Metrics
ota_updated_pods_total                    # Total pods updated
ota_last_run_timestamp_seconds           # Last deployment timestamp
ota_jobs_pending                         # Pending deployment jobs
ota_jobs_successful                      # Successful deployments
ota_jobs_total                          # Total deployment jobs

# Rollback Metrics
ota_rollback_pods_total                  # Total pods rolled back
ota_last_rollback_timestamp_seconds     # Last rollback timestamp
```

### Grafana Dashboard

Pre-configured dashboard includes:

- **📈 Real-time Metrics**: Live deployment statistics and trends
- **📊 Visual Charts**: Deployment timeline and rollback activity
- **🎯 Key Performance Indicators**: Success rates and system health
- **⏰ Historical Data**: Track deployment patterns over time

### Manual Monitoring Setup

```bash
# Start monitoring stack manually
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Stop monitoring stack
docker-compose -f docker-compose.monitoring.yml down

# View raw metrics
curl http://localhost:8000/metrics
```

### Custom Queries

Example Prometheus queries for advanced monitoring:

```promql
# Deployment success rate
(ota_jobs_successful / ota_jobs_total) * 100

# Average deployment frequency (per hour)
rate(ota_jobs_total[1h]) * 3600

# Time since last deployment
time() - ota_last_run_timestamp_seconds

# Rollback frequency
rate(ota_rollback_pods_total[24h])
```

---

## 📄 API Reference

### Deployment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ota/deploy` | Create new deployment |
| `GET` | `/ota/jobs` | List all jobs |
| `POST` | `/ota/update_status` | Update job status |
| `POST` | `/ota/rollback` | Trigger rollback |
| `GET` | `/metrics` | Prometheus metrics |

### CLI Commands

```bash
# Deployment commands
cli.client deploy <version> [--wave <wave>]
cli.client update <version> [--wave <wave>]
cli.client rollback <version> [--wave <wave>]
cli.client list

# Management commands
cli.job_runner                    # Start job runner
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Kubernetes community for the robust container orchestration platform
- FastAPI team for the excellent Python web framework
- Streamlit team for the intuitive dashboard framework
- Contributors and users who make this project better

---

**Ready to transform your deployment process?** [Get started now](#-quick-start) and experience professional-grade Kubernetes deployment management!