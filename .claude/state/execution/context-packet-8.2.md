# Context Packet 8.2: Multi-Stage Production Dockerfile and docker-compose.yml

## 1. Goal
Provide a production-grade, hardened containerization setup enabling single-command build and deployment of the unified application using Docker and Docker Compose.

---

## 2. Allowed Files
* `Dockerfile` (repo root)
* `docker-compose.yml` (repo root)
* `.dockerignore` (repo root)
* `backend/requirements.txt` (pinned dependencies)

---

## 3. Detailed Specifications

### 3.1 Multi-Stage `Dockerfile` Architecture
* **Stage 1: `frontend-builder`**
  - Base Image: `node:22-alpine`
  - Workdir: `/app/frontend`
  - Copy `frontend/package.json` and `frontend/package-lock.json` (if present).
  - Execute `npm install` (or `npm ci` if package-lock is committed).
  - Copy frontend source tree: `frontend/` -> `/app/frontend/`.
  - Execute `npm run build` to produce optimized production bundle in `/app/frontend/dist`.

* **Stage 2: `production-runner`**
  - Base Image: `python:3.12-slim`
  - Workdir: `/app`
  - Environment variables:
    ```dockerfile
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PORT=8000 \
        PYTHONPATH=/app
    ```
  - Install runtime system utility: `curl` (for container healthcheck) with `rm -rf /var/lib/apt/lists/*`.
  - Security hardening: Create non-root system user and group (`appuser:appuser`, UID/GID 10001).
  - Copy and install Python dependencies:
    ```dockerfile
    COPY backend/requirements.txt /app/backend/requirements.txt
    RUN pip install --no-cache-dir -r /app/backend/requirements.txt
    ```
  - Copy application code:
    ```dockerfile
    COPY backend/ /app/backend/
    COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
    ```
  - Set file ownership: `RUN chown -R appuser:appuser /app`
  - Switch to non-root user: `USER appuser`
  - Expose port: `EXPOSE 8000`
  - Health check:
    ```dockerfile
    HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
        CMD curl -f http://localhost:8000/api/v1/health || exit 1
    ```
  - Container Command:
    ```dockerfile
    CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
    ```

### 3.2 `docker-compose.yml` Specification
```yaml
version: "3.9"

services:
  cns-pedagogy:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cns-pedagogy-app
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 5s
```

### 3.3 `.dockerignore` Specification
Must exclude extraneous files to minimize image build context and maximize build caching:
```
.git
.gitignore
.claude
.pytest_cache
__pycache__
*.pyc
*.pyo
*.pyd
*.log
frontend/node_modules
frontend/dist
backend/tests
scratch
.DS_Store
```

### 3.4 Pinned Dependencies (`backend/requirements.txt`)
Ensure deterministic, reproducible builds without unexpected upstream breaking changes:
```
fastapi==0.115.4
uvicorn[standard]==0.32.0
pydantic==2.10.0
pytest==8.3.3
httpx==0.28.1
```

---

## 4. Verification and Acceptance Criteria
1. **Docker Build**:
   - `docker build -t cns-pedagogy:latest .` completes with exit code 0.
   - Build cache efficiently separates node modules, pip packages, and source code.
2. **Container Execution**:
   - `docker run -d -p 8000:8000 cns-pedagogy:latest` boots and serves traffic.
   - `curl http://localhost:8000/api/v1/health` responds with HTTP 200 and `"status": "healthy"`.
   - Browser navigation to `http://localhost:8000/` loads the React app.
3. **Security Audit**:
   - Process runs as non-root user `appuser` (UID 10001).
   - Image size is compact (< 300MB uncompressed).
