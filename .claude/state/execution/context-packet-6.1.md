# Context Packet 6.1: FastAPI App Architecture, CORS Middleware, Global Error Handlers, and Base Schemas

## 1. Goal
Establish the foundational FastAPI application architecture, root & health endpoints, CORS middleware, global error-handling infrastructure, and shared base Pydantic schemas in `backend/main.py`, `backend/api/v1/router.py`, and `backend/api/schemas/common.py`.

The sub-milestone delivers:
1. **FastAPI Application Initialization** (`backend/main.py`):
   - Configured with title `"CNS Cryptography Pedagogy API"`, description, version `"1.0.0"`.
   - OpenAPI documentation accessible at `/docs` and ReDoc at `/redoc`.
   - Root endpoint `GET /` providing API metadata, version, and links to documentation.
   - System health check endpoint `GET /api/v1/health` reporting server status, ISO-8601 timestamp, and status of core modules (`number_theory`, `otp`, `lcg`, `elgamal`, `dsa`).
2. **CORS Middleware Configuration**:
   - `CORSMiddleware` configured with permissive origins for interactive frontend development (`["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"]`), allowing all methods, headers, and credentials.
3. **Global Exception Handlers**:
   - Standardized error response envelope `ErrorResponse` returned on failures.
   - Handler for cryptographic domain exceptions (`DSAError`, `ElGamalError`, `ValueError`, `KeyError`) returning HTTP 400 Bad Request with precise error details.
   - Handler for Pydantic `RequestValidationError` formatting field-level validation errors into clean, readable JSON structures with HTTP 422 Unprocessable Entity.
   - Catch-all handler for unhandled `Exception` logging the traceback and returning HTTP 500 Internal Server Error without leaking sensitive system internals.
4. **Master API Router Architecture** (`backend/api/v1/router.py`):
   - Creates an `APIRouter(prefix="")` that registers the four pedagogical pillar routers:
     - `/otp` -> `otp_router`
     - `/lcg` -> `lcg_router`
     - `/elgamal` -> `elgamal_router`
     - `/dsa` -> `dsa_router`
   - Mounts onto the main app under `/api/v1`.
5. **Base Schemas** (`backend/api/schemas/common.py`):
   - `BaseSchema` with `model_config = ConfigDict(populate_by_name=True, extra="forbid")`.
   - `HealthResponse`, `RootResponse`, `ErrorResponse`, `ErrorDetail`.

## 2. Allowed Files
* `backend/main.py`
* `backend/api/__init__.py`
* `backend/api/v1/__init__.py`
* `backend/api/v1/router.py`
* `backend/api/schemas/__init__.py`
* `backend/api/schemas/common.py`

## 3. Strict Data Contracts & Signatures

### Base Schemas (`backend/api/schemas/common.py`)
```python
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base Pydantic model enforcing strict validation and alias population."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class ErrorDetail(BaseSchema):
    """Structured detail for a specific error or invalid field."""
    loc: list[str | int] = Field(default_factory=list, description="Location of error in payload")
    msg: str = Field(..., description="Human-readable error description")
    type: str = Field(..., description="Error type classifier")


class ErrorResponse(BaseSchema):
    """Consistent error response payload for all API errors."""
    error: str = Field(..., description="Short error classification name")
    detail: str = Field(..., description="Human-readable explanation of error")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of error occurrence"
    )
    errors: list[ErrorDetail] = Field(
        default_factory=list,
        description="Granular field-level errors if applicable"
    )


class HealthResponse(BaseSchema):
    """API health status report."""
    status: str = Field("healthy", description="Overall service status")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current server UTC timestamp"
    )
    modules: dict[str, str] = Field(
        default_factory=lambda: {
            "number_theory": "active",
            "otp": "active",
            "lcg": "active",
            "elgamal": "active",
            "dsa": "active",
        },
        description="Status of core cryptographic engines"
    )


class RootResponse(BaseSchema):
    """Root metadata response."""
    app: str = Field("CNS Cryptography Pedagogy API")
    version: str = Field("1.0.0")
    docs_url: str = Field("/docs")
    redoc_url: str = Field("/redoc")
    endpoints_prefix: str = Field("/api/v1")
```

### Application Entry Point (`backend/main.py`)
```python
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.schemas.common import ErrorDetail, ErrorResponse, HealthResponse, RootResponse
from backend.api.v1.router import api_v1_router
from backend.core.dsa import DSAError
from backend.core.elgamal import ElGamalError

app = FastAPI(
    title="CNS Cryptography Pedagogy API",
    description="Interactive Pedagogical REST API demonstrating One-Time Pad, LCG, ElGamal, and DSA.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(DSAError)
@app.exception_handler(ElGamalError)
@app.exception_handler(ValueError)
async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    ...

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    ...

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    ...

# Core Root & Health Endpoints
@app.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    ...

@app.get("/api/v1/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    ...

# Mount master v1 router
app.include_router(api_v1_router, prefix="/api/v1")
```

### Master Router (`backend/api/v1/router.py`)
```python
from fastapi import APIRouter
# Sub-routers imported from backend.api.v1.otp, lcg, elgamal, dsa

api_v1_router = APIRouter()
# Include sub-routers:
# api_v1_router.include_router(otp_router, prefix="/otp", tags=["One-Time Pad"])
# api_v1_router.include_router(lcg_router, prefix="/lcg", tags=["Linear Congruential Generator"])
# api_v1_router.include_router(elgamal_router, prefix="/elgamal", tags=["ElGamal Cryptosystem"])
# api_v1_router.include_router(dsa_router, prefix="/dsa", tags=["Digital Signature Algorithm"])
```

## 4. Acceptance Criteria
1. Application successfully instantiates with `uvicorn backend.main:app` or FastAPI TestClient.
2. `GET /` returns status 200 with `RootResponse` payload.
3. `GET /api/v1/health` returns status 200 with `HealthResponse` showing `"healthy"` and all 5 modules active.
4. Preflight CORS `OPTIONS /api/v1/health` returns allowed origin and methods headers.
5. Raising a `ValueError` or `DSAError` returns HTTP 400 Bad Request with `ErrorResponse` schema.
6. Passing an invalid request body to a validated endpoint returns HTTP 422 Unprocessable Entity with structured `ErrorDetail` objects.
7. Unhandled exceptions return HTTP 500 Internal Server Error without crashing the process.
