from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base Pydantic model enforcing strict validation and alias population."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
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
        description="UTC timestamp of error occurrence",
    )
    errors: list[ErrorDetail] = Field(
        default_factory=list,
        description="Granular field-level errors if applicable",
    )


class HealthResponse(BaseSchema):
    """API health status report."""

    status: str = Field("healthy", description="Overall service status")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current server UTC timestamp",
    )
    modules: dict[str, str] = Field(
        default_factory=lambda: {
            "number_theory": "active",
            "otp": "active",
            "lcg": "active",
            "elgamal": "active",
            "dsa": "active",
        },
        description="Status of core cryptographic engines",
    )


class RootResponse(BaseSchema):
    """Root metadata response."""

    app: str = Field("CNS Cryptography Pedagogy API")
    version: str = Field("1.0.0")
    docs_url: str = Field("/docs")
    redoc_url: str = Field("/redoc")
    endpoints_prefix: str = Field("/api/v1")
