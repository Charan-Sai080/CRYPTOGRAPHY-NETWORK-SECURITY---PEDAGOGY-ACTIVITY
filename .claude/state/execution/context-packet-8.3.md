# Context Packet 8.3: Universal Orchestration Startup Script (`run.sh`)

## 1. Goal
Create a unified, robust, and user-friendly orchestration shell script (`run.sh`) in the repository root that automates development, unified production serving, automated testing, and Docker deployment workflows.

---

## 2. Allowed Files
* `run.sh` (repo root)

---

## 3. Detailed Specifications

### 3.1 Script Commands
1. `./run.sh dev`
   - Pre-flight checks: ensures Python 3.10+ and Node.js 18+ are available in PATH.
   - Starts FastAPI backend (`uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`) in the background.
   - Starts Vite frontend dev server (`npm run dev` in `frontend/`) concurrently.
   - Registers signal trap (`SIGINT`, `SIGTERM`, `EXIT`) to cleanly kill both background processes on exit (preventing orphaned processes).
   - Echoes local URLs:
     - Frontend UI: `http://localhost:5173`
     - Backend API & Docs: `http://localhost:8000/docs`

2. `./run.sh prod`
   - Ensures `frontend/` dependencies are installed and builds static bundle: `(cd frontend && npm run build)`.
   - Boots unified FastAPI server: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.
   - Echoes unified production URL: `http://localhost:8000` (serving both UI and API).

3. `./run.sh test`
   - Executes backend pytest suite: `pytest backend/tests -v`.
   - Executes frontend TypeScript compiler check: `(cd frontend && npm run type-check)`.
   - Executes frontend production build test: `(cd frontend && npm run build)`.
   - Emits a unified summary report with green/red status banners and exits with non-zero code on any failure.

4. `./run.sh docker`
   - Detects `docker` and Docker Compose (`docker compose` or legacy `docker-compose`).
   - Executes `docker compose up --build`.

5. `./run.sh help` (or unknown command)
   - Displays clear CLI usage manual with examples and environment requirements.

### 3.2 Shell Scripting Standards
* **Interpreter**: `#!/usr/bin/env bash` with `set -euo pipefail`.
* **Port Conflict Detection**: Optional check with `nc` or `lsof` / `netstat` to warn if port 8000 or 5173 is already occupied.
* **Color Palette**: ANSI escape codes for professional CLI output:
  - `GREEN`: Success messages
  - `RED`: Errors and failure notices
  - `YELLOW`: Warnings and prerequisite notices
  - `BLUE`: Section headers and step banners
  - `CYAN`: URLs and commands
* **Clean Process Lifecycle**:
  ```bash
  BACKEND_PID=""
  FRONTEND_PID=""

  cleanup() {
    echo -e "\n${YELLOW}Shutting down processes...${NC}"
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
      kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
      kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    exit 0
  }
  trap cleanup SIGINT SIGTERM EXIT
  ```

---

## 4. Verification and Acceptance Criteria
1. **Executable Permissions**: `run.sh` has executable bit set (`chmod +x run.sh`).
2. **Help Output**: Executing `./run.sh` or `./run.sh help` prints the help menu with 0 exit code.
3. **Test Mode**: Running `./run.sh test` executes both backend pytest and frontend build without syntax or runtime errors.
4. **Dev Cleanup**: Starting `./run.sh dev` and sending Ctrl+C terminates both uvicorn and vite without leaving background jobs.
