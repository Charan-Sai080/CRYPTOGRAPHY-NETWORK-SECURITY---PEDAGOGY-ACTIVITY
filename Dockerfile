# =============================================================================
# Stage 1: Frontend Builder
# =============================================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies first for optimal Docker layer caching
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source files and compile static production bundle
COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Production Python Runner
# =============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PYTHONPATH=/app

# Install curl for container health check and clean apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Security hardening: Create unprivileged system user and group
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /sbin/nologin -d /app appuser

# Install pinned Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code and compiled frontend assets from builder stage
COPY backend/ /app/backend/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Secure ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check monitoring API health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production server command with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
