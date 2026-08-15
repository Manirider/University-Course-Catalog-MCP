# Quick Start

## Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/downloads)
- **Docker** (optional) — [Download](https://www.docker.com/products/docker-desktop/)

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/university-course-catalog-mcp.git
cd university-course-catalog-mcp
```

### 2. Create Virtual Environment

=== "Linux/macOS"
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

=== "Windows (PowerShell)"
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

=== "Windows (CMD)"
    ```cmd
    python -m venv .venv
    .venv\Scripts\activate.bat
    ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

### 5. Run Server

```bash
python -m uvicorn university_catalog.main:app --host 0.0.0.0 --port 8080 --reload
```

### 6. Verify

```bash
# Health check
curl http://localhost:8080/health

# Server info
curl http://localhost:8080/
```

## Next Steps

- [MCP Protocol Overview](../mcp/overview.md) — Learn about MCP capabilities
- [API Reference](../api/health.md) — HTTP endpoint documentation
- [Docker Deployment](../getting-started/docker.md) — Production deployment