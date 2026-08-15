# Docker Deployment

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src ./src
COPY data ./data

# Ensure data directory exists
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Environment
ENV PYTHONUNBUFFERED=1

# Start server
CMD ["python", "-m", "uvicorn", "university_catalog.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/catalog.db
      - HOST=0.0.0.0
      - PORT=8080
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
```

## Quick Start

```bash
# Build and start
docker compose up --build -d

# Check status
docker compose ps

# View logs
docker compose logs -f mcp-server

# Stop
docker compose down
```

## Clean Rebuild

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Volume Persistence

The `./data` directory is mounted to `/app/data`:

```yaml
volumes:
  - ./data:/app/data
```

This preserves the SQLite database across container restarts.

### Reset Database

```bash
docker compose down -v
rm -rf data/
docker compose up --build
```

## Health Checks

Container includes health check:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

Check status:

```bash
docker compose ps
# Should show "healthy" for mcp-server
```

## Environment Variables

Override in `docker-compose.yml` or `.env`:

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/catalog.db
  - HOST=0.0.0.0
  - PORT=8080
  - LOG_LEVEL=INFO
```

Or use `.env` file:

```bash
# .env
DATABASE_URL=sqlite:///./data/catalog.db
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
```

## Production Optimizations

### Multi-Stage Build

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src ./src
COPY data ./data
RUN mkdir -p /app/data
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "university_catalog.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Resource Limits

```yaml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Non-Root User

```dockerfile
# In Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

## Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # MCP SSE support
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

## SSL with Certbot

```bash
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Prometheus Metrics

Add to `main.py`:

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'Request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    REQUEST_LATENCY.observe(time.time() - start)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### Grafana Dashboard

Import dashboard for:
- Request rate
- Latency percentiles
- Error rate
- Health check status

## Logs

### View Logs

```bash
# Follow logs
docker compose logs -f mcp-server

# Last 100 lines
docker compose logs --tail=100 mcp-server

# Since timestamp
docker compose logs --since="2024-01-01T00:00:00" mcp-server
```

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "uvicorn.access",
  "message": "GET /health 200"
}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs mcp-server

# Common issues:
# - Port 8080 already in use on host
# - Permission denied on ./data directory
# - Missing .env file
```

### Health Check Failing

```bash
# Test manually
docker compose exec mcp-server curl -f http://localhost:8080/health

# Check if server is listening
docker compose exec mcp-server netstat -tlnp | grep 8080
```

### Database Issues

```bash
# Reset database
docker compose down -v
rm -rf data/
docker compose up --build
```

### Out of Memory

```bash
# Check memory usage
docker stats mcp-server

# Increase limits in docker-compose.yml
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build Docker image
  run: docker compose build

- name: Test Docker image
  run: |
    docker compose up -d
    sleep 15
    curl -f http://localhost:8080/health
    docker compose down
```

### Docker Hub

```bash
# Tag and push
docker tag university-catalog-mcp:latest yourusername/university-catalog-mcp:latest
docker push yourusername/university-catalog-mcp:latest

# Or use docker-compose
docker compose push
```

## Kubernetes

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: yourusername/university-catalog-mcp:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "sqlite:///./data/catalog.db"
        - name: LOG_LEVEL
          value: "INFO"
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
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: mcp-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### Persistent Volume

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mcp-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```