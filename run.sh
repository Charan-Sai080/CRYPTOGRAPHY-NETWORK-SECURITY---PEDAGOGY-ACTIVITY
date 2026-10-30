#!/usr/bin/env bash
# =============================================================================
# Cryptography & Network Security (CNS) Pedagogy Platform
# Universal Orchestration Script
# =============================================================================

set -euo pipefail

# ANSI color codes for formatted terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"

# Determine Python / pytest / uvicorn binaries
if [ -x "/Users/charancherry/miniforge3/envs/cns-pedagogy/bin/python" ]; then
    PYTHON_BIN="/Users/charancherry/miniforge3/envs/cns-pedagogy/bin/python"
    PYTEST_BIN="/Users/charancherry/miniforge3/envs/cns-pedagogy/bin/pytest"
    UVICORN_BIN="/Users/charancherry/miniforge3/envs/cns-pedagogy/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3 || command -v python)"
    PYTEST_BIN="$(command -v pytest || echo "python3 -m pytest")"
    UVICORN_BIN="$(command -v uvicorn)"
else
    PYTHON_BIN="$(command -v python3 || command -v python || echo "python3")"
    PYTEST_BIN="pytest"
    UVICORN_BIN="uvicorn"
fi

NPM_BIN="$(command -v npm || echo "npm")"

# Process IDs for background tasks
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    local exit_code=$?
    echo -e "\n${YELLOW}[!] Shutting down processes...${NC}"
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    exit "$exit_code"
}

check_port() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${YELLOW}[!] Warning: Port $port is already in use by another process.${NC}"
        fi
    fi
}

cmd_dev() {
    echo -e "${BLUE}${BOLD}==> Starting CNS Platform in Development Mode${NC}"
    check_port 8000
    check_port 5173

    trap cleanup SIGINT SIGTERM EXIT

    echo -e "${CYAN}--> Launching FastAPI backend with hot-reload (http://127.0.0.1:8000)...${NC}"
    $UVICORN_BIN backend.main:app --reload --host 127.0.0.1 --port 8000 &
    BACKEND_PID=$!

    echo -e "${CYAN}--> Launching Vite frontend dev server (http://localhost:5173)...${NC}"
    (cd "$FRONTEND_DIR" && $NPM_BIN run dev) &
    FRONTEND_PID=$!

    echo -e "\n${GREEN}${BOLD}[OK] Platform active!${NC}"
    echo -e "     ${BOLD}Frontend UI:${NC}      ${CYAN}http://localhost:5173${NC}"
    echo -e "     ${BOLD}Backend API:${NC}      ${CYAN}http://127.0.0.1:8000${NC}"
    echo -e "     ${BOLD}Interactive Docs:${NC} ${CYAN}http://127.0.0.1:8000/docs${NC}"
    echo -e "     ${YELLOW}Press Ctrl+C to terminate both servers.${NC}\n"

    wait
}

cmd_prod() {
    echo -e "${BLUE}${BOLD}==> Starting CNS Platform in Unified Production Mode${NC}"
    check_port 8000

    echo -e "${CYAN}--> Building production frontend bundle...${NC}"
    (cd "$FRONTEND_DIR" && [ ! -d "node_modules" ] && $NPM_BIN install || true)
    (cd "$FRONTEND_DIR" && $NPM_BIN run build)

    echo -e "\n${GREEN}${BOLD}[OK] Frontend compiled to frontend/dist.${NC}"
    echo -e "${CYAN}--> Launching unified FastAPI server on http://0.0.0.0:8000...${NC}"
    echo -e "     ${BOLD}Unified Platform:${NC} ${CYAN}http://localhost:8000${NC}"
    echo -e "     ${BOLD}Swagger API Docs:${NC} ${CYAN}http://localhost:8000/docs${NC}\n"

    exec $UVICORN_BIN backend.main:app --host 0.0.0.0 --port 8000
}

cmd_test() {
    echo -e "${BLUE}${BOLD}==> Executing Comprehensive Test Suite${NC}\n"
    local backend_status=0
    local typecheck_status=0
    local build_status=0

    echo -e "${CYAN}[1/3] Running backend pytest suite...${NC}"
    if $PYTEST_BIN backend/tests -v; then
        echo -e "${GREEN}[PASS] Backend pytest suite completed successfully.${NC}\n"
    else
        echo -e "${RED}[FAIL] Backend pytest suite encountered errors.${NC}\n"
        backend_status=1
    fi

    echo -e "${CYAN}[2/3] Running frontend TypeScript type check (tsc)...${NC}"
    if (cd "$FRONTEND_DIR" && $NPM_BIN run type-check); then
        echo -e "${GREEN}[PASS] Frontend type checking passed cleanly.${NC}\n"
    else
        echo -e "${RED}[FAIL] Frontend TypeScript type check failed.${NC}\n"
        typecheck_status=1
    fi

    echo -e "${CYAN}[3/3] Running frontend production build verification (vite build)...${NC}"
    if (cd "$FRONTEND_DIR" && $NPM_BIN run build); then
        echo -e "${GREEN}[PASS] Frontend production build succeeded.${NC}\n"
    else
        echo -e "${RED}[FAIL] Frontend build verification failed.${NC}\n"
        build_status=1
    fi

    echo -e "${BLUE}${BOLD}==================== TEST SUMMARY ====================${NC}"
    if [ $backend_status -eq 0 ] && [ $typecheck_status -eq 0 ] && [ $build_status -eq 0 ]; then
        echo -e "${GREEN}${BOLD}[SUCCESS] All tests passed! Platform is production-ready.${NC}"
        return 0
    else
        echo -e "${RED}${BOLD}[FAILURE] Some test phases failed. Check logs above.${NC}"
        return 1
    fi
}

cmd_docker() {
    echo -e "${BLUE}${BOLD}==> Launching CNS Platform with Docker Compose${NC}"

    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not installed or not available in PATH.${NC}"
        exit 1
    fi

    if docker compose version >/dev/null 2>&1; then
        docker compose up --build
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose up --build
    else
        echo -e "${RED}Error: Neither 'docker compose' nor 'docker-compose' was found.${NC}"
        exit 1
    fi
}

cmd_help() {
    cat << EOF
Cryptography & Network Security - Pedagogy Platform Orchestrator

Usage: ./run.sh <command>

Commands:
  dev       Start both FastAPI backend (port 8000) and Vite dev server (port 5173) concurrently
  prod      Compile production frontend bundle and start unified FastAPI server (port 8000)
  test      Execute full test suite: backend pytest (286 tests), frontend type-check & build
  docker    Build and launch the unified container via Docker Compose
  help      Display this usage manual

Environment Requirements:
  - Python 3.10+ (Python 3.12 recommended)
  - Node.js 18+ (Node.js 22 recommended) & npm
  - Docker & Docker Compose (optional, for 'docker' mode)

EOF
}

# Entrypoint argument parsing
COMMAND="${1:-help}"

case "$COMMAND" in
    dev)
        cmd_dev
        ;;
    prod)
        cmd_prod
        ;;
    test)
        cmd_test
        ;;
    docker)
        cmd_docker
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}\n"
        cmd_help
        exit 1
        ;;
esac
