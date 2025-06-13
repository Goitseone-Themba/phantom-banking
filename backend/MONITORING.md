# Phantom Banking Monitoring & Admin Dashboard

Comprehensive monitoring and admin dashboard solution for Phantom Banking using Grafana, Prometheus, and Django Admin with real-time performance metrics.

## 🚀 Features

### Django Admin Dashboard
- **Real-time System Metrics**: CPU, Memory, Disk usage with visual indicators
- **Business Metrics**: Customer counts, transaction volumes, wallet balances
- **KYC Management**: Pending reviews, approval rates, processing times
- **Interactive Charts**: Dynamic performance visualization using Chart.js
- **Quick Actions**: Direct links to monitoring tools and admin functions
- **Auto-refresh**: Updates every 5 minutes automatically

### Prometheus Metrics
- **System Metrics**: CPU, memory, disk, network I/O
- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: Customer growth, transaction volumes, wallet statistics
- **Database Metrics**: Query performance, connection pools
- **Security Metrics**: Failed logins, suspicious activity
- **Cache Metrics**: Redis performance and hit rates

### Grafana Dashboards
- **System Overview**: Resource usage and performance
- **Business Intelligence**: Customer and transaction analytics
- **Alerting**: Automated notifications for critical issues
- **Historical Data**: Long-term trend analysis

### Monitoring Stack
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notifications
- **Node Exporter**: System metrics
- **Redis Exporter**: Cache metrics
- **PostgreSQL Exporter**: Database metrics

## 📁 Project Structure

```
backend/
├── phantom_apps/monitoring/          # Django monitoring app
│   ├── apps.py                       # App configuration
│   ├── views.py                      # Dashboard and API views
│   ├── urls.py                       # URL routing
│   ├── metrics.py                    # Prometheus metrics definitions
│   ├── signals.py                    # Django signal handlers
│   ├── middleware.py                 # Request tracking middleware
│   └── admin.py                      # Custom admin site
├── monitoring/                       # Monitoring configuration
│   ├── prometheus.yml                # Prometheus configuration
│   ├── alerts.yml                    # Alert rules
│   ├── alertmanager.yml              # Alert routing
│   └── grafana/                      # Grafana configuration
│       ├── provisioning/
│       │   ├── datasources/          # Data source config
│       │   └── dashboards/           # Dashboard provisioning
│       └── dashboards/               # Dashboard definitions
├── templates/admin/monitoring/       # Django admin templates
│   └── dashboard.html                # Admin dashboard template
├── docker-compose.monitoring.yml     # Docker compose for monitoring
└── start-monitoring.sh               # Startup script
```

## 🛠 Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Django 5.2+

### Quick Start

1. **Install Python dependencies**:
   ```bash
   pip install prometheus-client django-prometheus psutil
   ```

2. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Start monitoring stack**:
   ```bash
   ./start-monitoring.sh
   ```

### Manual Setup

1. **Start monitoring services**:
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

2. **Start Django development server**:
   ```bash
   python manage.py runserver
   ```

## 🌐 Access Points

### Main Dashboards
- **Django Admin Dashboard**: http://localhost:8000/admin
- **Django Monitoring Dashboard**: http://localhost:8000/monitoring/dashboard/
- **Grafana**: http://localhost:3000 (admin/phantom_admin_2025)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### API Endpoints
- **Prometheus Metrics**: http://localhost:8000/monitoring/metrics/
- **Health Check**: http://localhost:8000/monitoring/health/
- **System Health**: http://localhost:8000/health/

## 📊 Django Admin Dashboard Features

### System Health Panel
- Real-time CPU, Memory, and Disk usage
- Color-coded status indicators (Green/Yellow/Red)
- Auto-refreshing metrics

### Business Metrics Cards
- **Customer Analytics**: Total, verified, new registrations
- **Merchant Status**: Active merchants and growth
- **Wallet Management**: Total balance, frozen accounts, KYC status
- **Transaction Monitoring**: Volume, success rates, average amounts
- **QR Code Usage**: Generation and scanning statistics
- **KYC Processing**: Pending reviews, approval rates

### Interactive Charts
- **System Resource Usage**: Doughnut chart for CPU/Memory/Disk
- **Business Entity Counts**: Bar chart comparison
- **Transaction Volume**: Line chart trends
- **KYC Status Distribution**: Pie chart breakdown

### Quick Actions
- Direct links to Prometheus metrics
- Health check endpoints
- Pending KYC reviews
- Recent transactions

## ⚡ Prometheus Metrics Reference

### System Metrics
```
phantom_banking_cpu_usage_percent
phantom_banking_memory_usage_bytes
phantom_banking_disk_usage_percent
phantom_banking_network_io_bytes_total
```

### Application Metrics
```
phantom_banking_requests_total
phantom_banking_request_duration_seconds
phantom_banking_active_sessions
phantom_banking_errors_total
```

### Business Metrics
```
phantom_banking_customers_total
phantom_banking_customers_verified
phantom_banking_customers_created_today
phantom_banking_merchants_total
phantom_banking_merchants_active
phantom_banking_wallets_total
phantom_banking_wallets_balance_total
phantom_banking_wallets_frozen
phantom_banking_transactions_total
phantom_banking_kyc_pending
```

### Database Metrics
```
phantom_banking_db_connections_active
phantom_banking_db_query_duration_seconds
phantom_banking_db_queries_total
```

## 🚨 Alerting Rules

### Critical Alerts
- **Service Down**: Application not responding
- **High CPU Usage**: >85% for 5 minutes
- **High Memory Usage**: >8GB for 5 minutes
- **High Disk Usage**: >90% for 10 minutes
- **High Failed Logins**: >0.5/second for 2 minutes
- **Database Down**: PostgreSQL not responding

### Warning Alerts
- **High Error Rate**: >0.1 errors/second
- **Slow Response Time**: >2 seconds (95th percentile)
- **Pending KYC Reviews**: >50 for 30 minutes
- **Frozen Wallets**: >10 for 15 minutes
- **Slow Database Queries**: >1 second (95th percentile)

## 🔧 Configuration

### Environment Variables
```bash
# Database connection for metrics
DB_PASSWORD=your_db_password

# Monitoring settings
MONITORING_ENABLED=true
METRICS_COLLECTION_INTERVAL=15s

# Alert configuration
ALERT_EMAIL=admin@phantombanking.com
WEBHOOK_URL=http://your-webhook-url.com
```

### Custom Metrics
Add new metrics in `phantom_apps/monitoring/metrics.py`:

```python
from prometheus_client import Counter, Gauge, Histogram

# Custom business metric
custom_metric = Counter(
    'phantom_banking_custom_events_total',
    'Custom business events',
    ['event_type', 'status']
)

# Use in your code
custom_metric.labels(event_type='payment', status='success').inc()
```

### Custom Alerts
Add alert rules in `monitoring/alerts.yml`:

```yaml
- alert: CustomAlert
  expr: phantom_banking_custom_metric > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom alert triggered"
    description: "Custom metric exceeded threshold"
```

## 🐛 Troubleshooting

### Common Issues

1. **Metrics not appearing**:
   - Check Django app is running: `python manage.py runserver`
   - Verify metrics endpoint: http://localhost:8000/monitoring/metrics/
   - Check Prometheus targets: http://localhost:9090/targets

2. **Grafana dashboard empty**:
   - Verify Prometheus datasource configuration
   - Check dashboard provisioning in `monitoring/grafana/`
   - Restart Grafana: `docker restart phantom_grafana`

3. **Alerts not firing**:
   - Check alert rules: http://localhost:9090/alerts
   - Verify Alertmanager config: http://localhost:9093
   - Check email/webhook configuration

4. **High resource usage**:
   - Adjust Prometheus retention: `--storage.tsdb.retention.time=200h`
   - Reduce scrape intervals in `prometheus.yml`
   - Enable metric sampling for high-volume endpoints

### Log Analysis
```bash
# View all monitoring logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Specific service logs
docker logs phantom_prometheus
docker logs phantom_grafana
docker logs phantom_alertmanager

# Django application logs
tail -f logs/phantom_banking.log
```

## 🔐 Security Considerations

### Production Setup
1. **Change default passwords**:
   - Grafana admin password
   - Database credentials
   - API keys and secrets

2. **Enable authentication**:
   - Configure OAuth for Grafana
   - Secure Prometheus with basic auth
   - Use HTTPS for all endpoints

3. **Network security**:
   - Use Docker networks for isolation
   - Configure firewall rules
   - Enable VPN for remote access

### Monitoring Security
- Failed login tracking
- Suspicious activity detection
- Rate limiting on metrics endpoints
- Audit logs for admin actions

## 📈 Performance Optimization

### Metrics Collection
- Use sampling for high-volume metrics
- Configure appropriate retention periods
- Optimize database query performance
- Implement caching for dashboard data

### Resource Management
- Monitor memory usage of exporters
- Configure appropriate scrape intervals
- Use recording rules for complex queries
- Implement metric filtering

## 🤝 Contributing

### Adding New Metrics
1. Define metric in `metrics.py`
2. Add collection logic in appropriate module
3. Update Grafana dashboard
4. Add alert rules if needed
5. Update documentation

### Dashboard Development
1. Use Grafana UI for prototyping
2. Export dashboard JSON
3. Add to `monitoring/grafana/dashboards/`
4. Test provisioning

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Django Prometheus Integration](https://github.com/korfuri/django-prometheus)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/configuration/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

## 🆘 Support

For issues and questions:
1. Check this documentation
2. Review troubleshooting section
3. Check application logs
4. Create GitHub issue with:
   - Error messages
   - Configuration details
   - Steps to reproduce

---

**Built with ❤️ for Phantom Banking - Empowering the Unbanked** 🏦✨

