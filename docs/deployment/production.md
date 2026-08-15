# Production Deployment

## Checklist

### Pre-Deployment

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Run full test suite: `pytest -q`
- [ ] Build Docker image: `docker compose build`
- [ ] Test health endpoint: `curl http://localhost:8080/health`
- [ ] Verify MCP endpoint: `npx @modelcontextprotocol/inspector http://localhost:8080/mcp`

### Infrastructure

- [ ] Domain configured with DNS
- [ ] SSL certificate (Let's Encrypt or paid)
- [ ] Reverse proxy (Nginx/Traefik/Caddy)
- [ ] Firewall rules (port 80, 443)
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Logging aggregation (ELK/Loki)
- [ ] Backup strategy for database

### Security

- [ ] Non-root Docker user
- [ ] Rate limiting configured
- [ ] CORS restricted to known origins
- [ ] Secrets in environment variables (not code)
- [ ] Database file permissions restricted
- [ ] Regular security updates

## Environment Variables

```bash
# .env.production
DATABASE_URL=sqlite:///./data/catalog.db
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=WARNING
```

## Reverse Proxy Configuration

### Nginx

```nginx
# /etc/nginx/sites-available/mcp-server
server {
    listen 80;
    server_name mcp.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long timeouts for SSE
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        
        # Buffer settings
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### Caddy (Simpler)

```caddyfile
# Caddyfile
mcp.yourdomain.com {
    reverse_proxy localhost:8080 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

## Process Management

### Systemd Service

```ini
# /etc/systemd/system/mcp-server.service
[Unit]
Description=University Course Catalog MCP Server
After=network.target

[Service]
Type=exec
User=appuser
WorkingDirectory=/opt/mcp-server
Environment=PATH=/opt/mcp-server/.venv/bin
ExecStart=/opt/mcp-server/.venv/bin/python -m uvicorn university_catalog.main:app --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

### Docker Compose (Production)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mcp-server:
    image: yourusername/university-catalog-mcp:latest
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/catalog.db
      - HOST=0.0.0.0
      - PORT=8080
      - LOG_LEVEL=WARNING
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - mcp-server
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done'"
```

## Database Backup

### Automated Backup Script

```bash
#!/bin/bash
# /opt/mcp-server/backup.sh

BACKUP_DIR="/opt/backups/mcp"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/opt/mcp-server/data/catalog.db"

mkdir -p "$BACKUP_DIR"

# Backup
sqlite3 "$DB_PATH" ".backup $BACKUP_DIR/catalog_$DATE.db"

# Compress
gzip "$BACKUP_DIR/catalog_$DATE.db"

# Keep last 30 days
find "$BACKUP_DIR" -name "catalog_*.db.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/catalog_$DATE.db.gz"
```

### Cron Job

```bash
# /etc/cron.d/mcp-backup
0 2 * * * appuser /opt/mcp-server/backup.sh >> /var/log/mcp-backup.log 2>&1
```

### Restore Procedure

```bash
# Stop service
systemctl stop mcp-server

# Restore
gunzip -c /opt/backups/mcp/catalog_20240115_020000.db.gz > /opt/mcp-server/data/catalog.db

# Fix permissions
chown appuser:appuser /opt/mcp-server/data/catalog.db

# Start service
systemctl start mcp-server

# Verify
curl http://localhost:8080/health
```

## Monitoring

### Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `http_requests_total` | Request count | - |
| `http_request_latency_seconds` | Latency | p99 > 1s |
| `health_check_status` | Health status | != 1 |
| `database_connections` | Active connections | > 10 |

### Grafana Alerts

```yaml
# Alert rules
groups:
- name: mcp-server
  rules:
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_latency_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency on MCP server"

  - alert: HealthCheckFailing
    expr: health_check_status != 1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "MCP server health check failing"
```

## Logging

### Structured Logging

```python
# main.py
import json_logging
import logging

json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)

# Or use structlog
import structlog

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
```

### Log Rotation

```bash
# /etc/logrotate.d/mcp-server
/var/log/mcp-server/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 appuser appuser
}
```

## Scaling

### Horizontal Scaling

- SQLite doesn't support concurrent writes
- For scaling: migrate to PostgreSQL
- Use connection pooling (PgBouncer)
- Read replicas for read-heavy workloads

### Vertical Scaling

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

## Disaster Recovery

### RTO/RPO Targets

| Metric | Target |
|--------|--------|
| RTO (Recovery Time Objective) | 15 minutes |
| RPO (Recovery Point Objective) | 24 hours |

### Runbook

1. **Server down**: Check systemd/docker status, restart service
2. **Database corrupted**: Restore from latest backup
3. **High latency**: Check database locks, restart service
4. **SSL expired**: Renew certbot, reload nginx
5. **Disk full**: Clean logs, vacuum database

## Maintenance Windows

### Scheduled Tasks

| Task | Frequency | Window |
|------|-----------|--------|
| Database backup | Daily | 02:00 UTC |
| Log rotation | Daily | 03:00 UTC |
| Security updates | Weekly | Sunday 04:00 UTC |
| Dependency updates | Monthly | 1st Sunday 05:00 UTC |
| SSL renewal | Automatic (certbot) | - |

### Update Procedure

```bash
# 1. Backup
/opt/mcp-server/backup.sh

# 2. Pull latest image
docker compose pull

# 3. Deploy
docker compose up -d

# 4. Verify
curl -f https://mcp.yourdomain.com/health

# 5. Rollback if needed
docker compose down
docker compose up -d  # Previous version
```

## Compliance

### Data Retention

- Course catalog: Permanent
- Access logs: 90 days
- Metrics: 1 year

### Privacy

- No personal data stored
- Instructor emails are public university addresses
- No authentication = no user data

## Contacts

| Role | Contact |
|------|---------|
| Primary On-Call | [Name] - [Phone] - [Email] |
| Secondary On-Call | [Name] - [Phone] - [Email] |
| Database Admin | [Name] - [Phone] - [Email] |
| Security Team | [Name] - [Phone] - [Email] |