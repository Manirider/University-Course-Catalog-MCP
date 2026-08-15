# Troubleshooting Guide

## Quick Diagnostics

### Health Check

```bash
# Basic health
curl http://localhost:8080/health
# Expected: {"status":"healthy","database":"connected"}

# Server info
curl http://localhost:8080/
# Expected: {"name":"University Course Catalog MCP Server",...}

# MCP endpoint
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

### Container Status

```bash
docker compose ps
# Check STATUS column shows "healthy"

docker compose logs mcp-server
# Check for errors
```

## Common Issues

### 1. Port Already in Use

**Error**: `Address already in use` or `Error: listen EADDRINUSE`

**Diagnosis**:
```bash
# Linux/macOS
lsof -i :8080
netstat -tlnp | grep 8080

# Windows
netstat -ano | findstr :8080
```

**Solution**:
```bash
# Kill existing process
kill -9 <PID>

# Or change port in .env
PORT=8081

# Or in docker-compose.yml
ports:
  - "8081:8080"
```

### 2. Database Locked

**Error**: `sqlite3.OperationalError: database is locked`

**Causes**:
- Multiple processes accessing database
- Previous process didn't close connection
- WAL mode conflicts

**Solutions**:
```bash
# Check for open connections
lsof data/catalog.db

# Kill processes
fuser -k data/catalog.db

# Enable WAL mode (in database.py)
PRAGMA journal_mode=WAL

# Or use in-memory for testing
DATABASE_URL=sqlite:///:memory:
```

### 3. Health Check Failing

**Symptom**: Container shows `unhealthy`

**Diagnosis**:
```bash
# Test manually inside container
docker compose exec mcp-server curl -f http://localhost:8080/health

# Check logs
docker compose logs mcp-server --tail=50
```

**Common Causes**:
| Cause | Solution |
|-------|----------|
| Database not initialized | Check startup logs, ensure seed runs |
| Permission denied on data/ | `chmod 755 data/` |
| Port binding failed | Check port conflicts |
| Import errors | Rebuild with `docker compose build --no-cache` |

### 4. MCP Connection Refused

**Error**: `Connection refused` or `ECONNREFUSED`

**Diagnosis**:
```bash
# Check if server is listening
netstat -tlnp | grep 8080
# or
ss -tlnp | grep 8080

# Check container port mapping
docker compose port mcp-server 8080
```

**Solutions**:
- Ensure using `http://localhost:8080/mcp` (not `/mcp/`)
- Check firewall rules
- Verify Docker port mapping

### 5. Tool Returns "Course not found"

**Symptom**: `{"error": "Course not found"}` for valid course codes

**Causes**:
- Case sensitivity (should be case-insensitive)
- Whitespace issues
- Database not seeded

**Solutions**:
```bash
# Verify database has data
sqlite3 data/catalog.db "SELECT course_code FROM courses;"

# Test with exact case
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_prerequisites","arguments":{"course_code":"CS301"}}}'

# Check logs for case handling
```

### 6. Empty Search Results

**Symptom**: `search_courses` returns `[]` for known queries

**Diagnosis**:
```bash
# Test directly
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_courses","arguments":{"query":"programming"}}}'
```

**Solutions**:
- Check department code spelling
- Try without department filter
- Verify database seeded correctly

### 7. Import Errors

**Error**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or in Docker
docker compose build --no-cache
docker compose up -d

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### 8. Permission Denied

**Error**: `PermissionError: [Errno 13] Permission denied`

**Common Paths**:
- `data/catalog.db`
- `data/` directory
- Log files

**Solutions**:
```bash
# Fix ownership
sudo chown -R $USER:$USER data/

# Fix permissions
chmod 755 data/
chmod 644 data/catalog.db

# In Docker
# Ensure volume mount has correct permissions
volumes:
  - ./data:/app/data
```

### 9. Slow Performance

**Symptoms**: Requests take > 1 second

**Diagnosis**:
```bash
# Time requests
time curl http://localhost:8080/health

# Check database size
ls -lh data/catalog.db

# Analyze query plans
sqlite3 data/catalog.db "EXPLAIN QUERY PLAN SELECT * FROM courses WHERE course_code = 'CS101';"
```

**Optimizations**:
- Ensure indexes exist
- Enable WAL mode
- Consider connection pooling
- Add caching layer

### 10. Memory Issues

**Symptom**: Container OOM killed

**Diagnosis**:
```bash
# Check memory usage
docker stats mcp-server

# Check for memory leaks
docker compose exec mcp-server python -c "import gc; gc.collect(); print(gc.get_stats())"
```

**Solutions**:
```yaml
# docker-compose.yml - add limits
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

## Debugging Techniques

### Enable Debug Logging

```bash
# Environment variable
LOG_LEVEL=DEBUG docker compose up

# Or in .env
LOG_LEVEL=DEBUG
```

### Interactive Debugging

```bash
# Enter container
docker compose exec -it mcp-server bash

# Python REPL
docker compose exec mcp-server python -c "
from university_catalog.database import get_db_session
from university_catalog.models import Course
with get_db_session() as session:
    courses = session.query(Course).all()
    for c in courses:
        print(c.course_code, c.title)
"
```

### Database Inspection

```bash
# SQLite CLI
sqlite3 data/catalog.db

# Useful commands
.tables
.schema courses
SELECT * FROM courses WHERE course_code = 'CS101';
SELECT * FROM prerequisites;
PRAGMA foreign_key_check;
```

### Network Debugging

```bash
# Test from host
curl -v http://localhost:8080/health

# Test from inside container
docker compose exec mcp-server curl -v http://localhost:8080/health

# Check DNS
docker compose exec mcp-server nslookup localhost
```

## Log Analysis

### Common Log Patterns

```bash
# Search for errors
docker compose logs mcp-server | grep -i error

# Search for specific tool
docker compose logs mcp-server | grep search_courses

# Follow real-time
docker compose logs -f mcp-server | grep -E "(ERROR|WARN|search_courses|get_prerequisites)"
```

### Structured Logs (if enabled)

```bash
# Parse JSON logs
docker compose logs mcp-server | jq '. | select(.level=="ERROR")'
```

## Recovery Procedures

### Complete Reset

```bash
# Nuclear option
docker compose down -v
rm -rf data/
docker compose build --no-cache
docker compose up -d
```

### Database Recovery

```bash
# 1. Backup current (if accessible)
cp data/catalog.db data/catalog.db.corrupted

# 2. Try integrity check
sqlite3 data/catalog.db "PRAGMA integrity_check;"

# 3. If corrupted, restore from backup
gunzip -c backups/catalog_latest.db.gz > data/catalog.db

# 4. Or reseed
rm data/catalog.db
docker compose restart mcp-server
```

### Configuration Reset

```bash
# Restore default .env
cp .env.example .env

# Restart
docker compose restart mcp-server
```

## Getting Help

### Information to Collect

When reporting issues, include:

1. **Environment**:
   ```bash
   docker compose version
   python --version
   sqlite3 --version
   ```

2. **Logs**:
   ```bash
   docker compose logs mcp-server --tail=100 > logs.txt
   ```

3. **Health Check**:
   ```bash
   curl -v http://localhost:8080/health
   ```

4. **Database Status**:
   ```bash
   sqlite3 data/catalog.db "PRAGMA integrity_check; SELECT COUNT(*) FROM courses;"
   ```

5. **Steps to Reproduce**:
   - Exact commands run
   - Expected vs actual behavior
   - Error messages

### Resources

- [GitHub Issues](https://github.com/yourusername/university-course-catalog-mcp/issues)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)