#!/bin/bash

# Phantom Banking Monitoring Stack Startup Script

echo "🚀 Starting Phantom Banking Monitoring Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please update it with your configuration."
    else
        echo "❌ .env.example not found. Please create a .env file."
        exit 1
    fi
fi

# Create monitoring directories if they don't exist
mkdir -p logs
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards

# Stop any existing containers
echo "🛑 Stopping existing monitoring containers..."
docker-compose -f docker-compose.monitoring.yml down

# Pull latest images
echo "📥 Pulling latest monitoring images..."
docker-compose -f docker-compose.monitoring.yml pull

# Start monitoring stack
echo "🎯 Starting monitoring services..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

services=("prometheus:9090" "grafana:3000" "node-exporter:9100" "alertmanager:9093")
for service in "${services[@]}"; do
    container_name="phantom_${service%%:*}"
    port="${service##*:}"
    
    if docker ps --format 'table {{.Names}}' | grep -q "$container_name"; then
        echo "✅ $container_name is running"
    else
        echo "❌ $container_name failed to start"
    fi
done

# Display access information
echo ""
echo "🎉 Monitoring stack is ready!"
echo ""
echo "📊 Access your monitoring tools:"
echo "   • Grafana Dashboard: http://localhost:3000 (admin/phantom_admin_2025)"
echo "   • Prometheus: http://localhost:9090"
echo "   • Alertmanager: http://localhost:9093"
echo "   • Node Exporter: http://localhost:9100/metrics"
echo ""
echo "🔧 Django Admin Dashboard: http://localhost:8000/admin"
echo "📈 Django Monitoring: http://localhost:8000/monitoring/dashboard/"
echo "📊 Prometheus Metrics: http://localhost:8000/monitoring/metrics/"
echo "🏥 Health Check: http://localhost:8000/monitoring/health/"
echo ""
echo "📚 To view logs: docker-compose -f docker-compose.monitoring.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.monitoring.yml down"
echo ""

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "🐍 Python virtual environment not found. Please run:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "   pip install -r requirements.txt"
    echo "   python manage.py migrate"
    echo "   python manage.py collectstatic --noinput"
fi

echo "✨ Setup complete! Happy monitoring! 🎯"

