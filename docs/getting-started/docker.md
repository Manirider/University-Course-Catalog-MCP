# Docker Deployment

## Quick Start

```bash
# Build and start (detached)
docker compose up --build -d

# Verify health
curl http://localhost:8080/health
```

## Service Management

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start in background |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop, remove containers AND volumes |
| `docker compose ps` | Show container status |
| `docker compose logs -f mcp-server` | Follow logs |
| `docker compose restart mcp-server` | Restart service |

## Clean Rebuild

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/catalog.db` | Database connection string |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8080` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

Override in `docker-compose.yml`:

```yaml
services:
  mcp-server:
    environment:
      - DATABASE_URL=sqlite:///./data/catalog.db
      - HOST=0.0.0.0
      - PORT=8080
      - LOG_LEVEL=DEBUG
```

Or use `.env` file:

```bash
# .env
DATABASE_URL=sqlite:///./data/catalog.db
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
```

## Volume Persistence

The database persists via volume mount:

```yaml
volumes:
  - ./data:/app/data
```

This ensures data survives container restarts.

To reset database:

```bash
docker compose down -v
rm -rf data/
docker compose up --build
```

## Health Checks

The container includes a health check:

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

## Production Considerations

### Reverse Proxy (Nginx)

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
    }
}
```

### SSL with Certbot

```bash
sudo certbot --nginx -d your-domain.com
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

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs mcp-server

# Common issues:
# - Port 8080 already in use
# - Permission denied on ./data directory
# - Missing .env file
```

### Database Issues

```bash
# Reset database
docker compose down -v
rm -rf data/
docker compose up --build
```

### Health Check Failing

```bash
# Test manually
docker compose exec mcp-server curl -f http://localhost:8080/health

# Check if server is listening
docker compose exec mcp-server netstat -tlnp | grep 8080
```

## Multi-Stage Build

The Dockerfile uses multi-stage build for smaller images:

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
# ... install dependencies

# Runtime stage
FROM python:3.12-slim
# ... copy only necessary files
```

Result: ~150MB image size.