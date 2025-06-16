#!/bin/bash

echo "🚀 Starting Kubernetes Deployment Manager Monitoring Stack..."

# Start the monitoring services
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

echo ""
echo "✅ Monitoring stack started!"
echo ""
echo "📊 Access URLs:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana:    http://localhost:3000 (admin/admin)"
echo "  - Metrics:    http://localhost:8000/metrics"
echo ""
echo "🔍 Prometheus Targets:"
echo "  - Go to http://localhost:9090/targets to verify scraping"
echo ""
echo "📈 Grafana Dashboard:"
echo "  - Login with admin/admin"
echo "  - The 'Kubernetes Deployment Manager' dashboard should be pre-loaded"
echo ""
echo "⏹️  To stop: docker-compose -f monitoring/docker-compose.monitoring.yml down"