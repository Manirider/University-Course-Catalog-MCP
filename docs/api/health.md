# Health Check Endpoint

## Overview

The health check endpoint provides a lightweight way to verify server and database availability.

## Endpoint

```
GET /health
```

## Response

### Success (200 OK)

```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health: `healthy` or `unhealthy` |
| `database` | string | Database status: `connected` or `disconnected` |

## Behavior

### Checks Performed

1. **Database connectivity** — Executes `SELECT 1` query
2. **Application liveness** — Process is running and responsive

### Response Logic

```python
# Pseudocode
async def health_check():
    db_status = "disconnected"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        database=db_status
    )
```

## Usage Examples

### cURL

```bash
# Basic health check
curl http://localhost:8080/health

# With verbose output
curl -v http://localhost:8080/health

# JSON output with jq
curl -s http://localhost:8080/health | jq .
```

### Docker Health Check

```yaml
# docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

### Kubernetes Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Load Balancer Check

```nginx
# NGINX upstream health check
upstream mcp_backend {
    server localhost:8080;
    health_check interval=10s timeout=5s;
}
```

## Monitoring

### Prometheus Metrics

Add custom metrics (requires `prometheus-client`):

```python
# main.py
from prometheus_client import Counter, Histogram, generate_latest

HEALTH_CHECKS = Counter('health_checks_total', 'Total health checks', ['status'])
HEALTH_LATENCY = Histogram('health_check_latency_seconds', 'Health check latency')

@app.get("/health")
async def health_check():
    with HEALTH_LATENCY.time():
        # ... perform checks
        HEALTH_CHECKS.labels(status=db_status).inc()
        return HealthResponse(...)
```

### Grafana Dashboard

Query examples:
```
# Health check success rate
rate(health_checks_total{status="connected"}[5m]) / rate(health_checks_total[5m])

# Health check latency
histogram_quantile(0.95, health_check_latency_seconds_bucket)
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Returns 500 | Database connection failed | Check database file exists and is writable |
| Returns `disconnected` | SQLite locked or path wrong | Verify `./data/catalog.db` accessible |
| Slow response | Database lock contention | Check for concurrent writes |
| Timeout | Health check takes >5s | Investigate database performance |

## Security

- **No authentication required** — Public endpoint
- **No sensitive data** — Only status information
- **Lightweight** — Single SELECT query
- **Rate limiting recommended** — Prevent abuse

## Testing

```bash
# Manual test
curl http://localhost:8080/health

# Automated test
pytest tests/test_health.py -v

# Expected output:
# test_health_endpoint PASSED
# test_root_endpoint PASSED
```

## Related

- [Docker Deployment](../getting-started/docker.md) — Container health checks
- [Configuration](../getting-started/configuration.md) — Environment variables
- [MCP Transport](../mcp/transport.md) — Protocol health checks