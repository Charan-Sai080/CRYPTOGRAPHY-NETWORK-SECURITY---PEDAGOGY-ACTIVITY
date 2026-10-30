from __future__ import annotations

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from backend.api.schemas.common import ErrorDetail, ErrorResponse, HealthResponse, RootResponse
from backend.api.v1.router import api_v1_router
from backend.core.dsa import DSAError
from backend.core.elgamal import ElGamalError

logger = logging.getLogger("cns.backend")

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

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

# Mount frontend compiled static assets if available
if (FRONTEND_DIST_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="assets")


# Exception handlers
@app.exception_handler(DSAError)
@app.exception_handler(ElGamalError)
@app.exception_handler(ValueError)
@app.exception_handler(KeyError)
async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translates domain cryptographic and mathematical exceptions into structured HTTP 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            detail=str(exc),
        ).model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Translates Pydantic request validation errors into structured HTTP 422."""
    errors = [
        ErrorDetail(
            loc=list(err.get("loc", [])),
            msg=str(err.get("msg", "")),
            type=str(err.get("type", "")),
        )
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            detail="Request validation failed. Please check payload parameters.",
            errors=errors,
        ).model_dump(mode="json"),
    )


@app.exception_handler(HTTPException)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Intercepts unexpected server errors without leaking internal stack traces."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="HTTPException",
                detail=str(exc.detail),
            ).model_dump(mode="json"),
        )

    logger.error("Unhandled server exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            detail="An unexpected internal server error occurred.",
        ).model_dump(mode="json"),
    )


# Root & Health Endpoints
@app.get("/", response_model=RootResponse)
async def root(request: Request) -> RootResponse | FileResponse:
    """Returns root metadata and documentation links, or serves SPA index.html if requested by a browser."""
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


@app.get("/api/v1/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Returns operational status for all core platform modules."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        modules={
            "number_theory": "active",
            "otp": "active",
            "lcg": "active",
            "elgamal": "active",
            "dsa": "active",
        },
    )


# Mount master v1 router
app.include_router(api_v1_router, prefix="/api/v1")


# SPA catch-all fallback route (must be defined last)
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str, request: Request):
    """Fallback route for single-page application (SPA) client-side routing."""
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
