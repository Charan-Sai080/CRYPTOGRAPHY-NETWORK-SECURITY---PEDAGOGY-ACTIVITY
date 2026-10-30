# Context Packet 8.1: Unified Frontend Production Static File Serving via FastAPI

## 1. Goal
Configure `backend/main.py` to seamlessly serve the built React Single Page Application (`frontend/dist`) in production environments while maintaining full backwards compatibility for API clients, OpenAPI/Swagger documentation, and passing all 282 existing backend tests.

---

## 2. Allowed Files
* `backend/main.py`
* `backend/tests/test_api.py` (add tests for HTML content negotiation & SPA fallback)

---

## 3. Detailed Technical Requirements

### 3.1 Static Asset Mounting
* Resolve `frontend/dist` path relative to `backend/main.py`:
  ```python
  FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
  ```
* If `(FRONTEND_DIST_DIR / "assets").is_dir()`:
  Mount `/assets` to `FRONTEND_DIST_DIR / "assets"` using `starlette.staticfiles.StaticFiles(directory=..., html=False)`.
* Serve `favicon.svg` or `favicon.ico` directly from `FRONTEND_DIST_DIR` if requested, or let the static mount/fallback handle it.

### 3.2 Root Endpoint Content Negotiation (`GET /`)
* Web browsers requesting `/` send `Accept: text/html,application/xhtml+xml,...`.
* API clients, `curl`, and `pytest` (`TestClient`) send `Accept: application/json` or `Accept: */*`.
* Behavior on `GET /`:
  ```python
  @app.get("/", response_model=RootResponse)
  async def root(request: Request):
      accept = request.headers.get("accept", "")
      index_file = FRONTEND_DIST_DIR / "index.html"
      if "text/html" in accept and index_file.is_file():
          return FileResponse(index_file)
      return RootResponse(
          app="CNS Cryptography Pedagogy API",
          version="1.0.0",
          docs_url="/docs",
          redoc_url="/redoc",
          endpoints_prefix="/api/v1",
      )
  ```
* This ensures:
  1. Visiting `http://localhost:8000/` in Chrome/Firefox/Safari immediately loads the interactive web app.
  2. Automated tests (`client.get("/")` in `backend/tests/test_api.py`) continue to receive the typed JSON `RootResponse`.

### 3.3 SPA Client-Side Routing Fallback
* React Router / SPA tabs may be accessed directly by URL (e.g., `/otp`, `/lcg`, `/elgamal`, `/dsa`).
* Register a catch-all route at the bottom of `backend/main.py` (after all routers and Swagger docs are registered):
  ```python
  @app.get("/{full_path:path}")
  async def spa_fallback(full_path: str, request: Request):
      # Do not intercept API routes, docs, or openapi
      if full_path.startswith("api/") or full_path in ("api", "docs", "redoc", "openapi.json"):
          raise HTTPException(status_code=404, detail="Endpoint not found")
      
      # Check if specific static file exists in dist (e.g. favicon.svg)
      requested_file = FRONTEND_DIST_DIR / full_path
      if requested_file.is_file():
          return FileResponse(requested_file)
      
      # Fallback to SPA index.html
      index_file = FRONTEND_DIST_DIR / "index.html"
      if index_file.is_file():
          return FileResponse(index_file)
      
      raise HTTPException(status_code=404, detail="Resource not found")
  ```

### 3.4 Graceful Degradation
* If `frontend/dist` does not exist (e.g., in headless CI, pure backend test runs, or before `npm run build` is executed):
  - Application must start up cleanly without `FileNotFoundError`.
  - API endpoints, Swagger `/docs`, and JSON root `/` must function normally.

---

## 4. Verification and Acceptance Criteria
1. **Pytest Suite Verification**:
   - Run `pytest backend/tests` — all 282 tests must pass with 0 failures and 0 errors.
   - Verify `TestAppArchitectureAndHealth.test_root_endpoint` passes cleanly.
2. **New Test Coverage**:
   - Add test case verifying HTML response when `Accept: text/html` is passed.
   - Add test case verifying 404 behavior for non-existent `/api/v1/*` routes.
3. **SPA Verification**:
   - When `frontend/dist` is present, `client.get("/otp", headers={"Accept": "text/html"})` returns status 200 with HTML content.
