from __future__ import annotations

from typing import Literal
from pydantic import Field
from backend.api.schemas.common import BaseSchema


class DSAPresetSchema(BaseSchema):
    name: str
    p: int
    q: int
    g: int
    p_str: str
    q_str: str
    g_str: str
    p_bits: int
    q_bits: int


class DSADomainGenerateRequest(BaseSchema):
    p_bits: int = Field(16, ge=10, le=64, description="Bit length for modulus prime p")
    q_bits: int = Field(8, ge=6, le=32, description="Bit length for subgroup prime divisor q")


class DSADomainGenerateResponse(BaseSchema):
    p: int
    q: int
    g: int
    p_str: str
    q_str: str
    g_str: str
    p_bits: int
    q_bits: int
    logs: list[str]


class DSAKeyGenerateRequest(BaseSchema):
    p: int | None = Field(None, description="Modulus prime p")
    q: int | None = Field(None, description="Subgroup prime divisor q")
    g: int | None = Field(None, description="Subgroup generator g")
    preset_name: str | None = Field(None, description="Preset name to use instead of p, q, g")
    seed_x: int | None = Field(None, description="Optional deterministic seed for private key x")


class DSAPublicKeySchema(BaseSchema):
    p: int
    q: int
    g: int
    y: int
    p_str: str
    q_str: str
    g_str: str
    y_str: str


class DSAPrivateKeySchema(BaseSchema):
    p: int
    q: int
    g: int
    x: int
    p_str: str
    q_str: str
    g_str: str
    x_str: str


class DSAKeyGenerateResponse(BaseSchema):
    public_key: DSAPublicKeySchema
    private_key: DSAPrivateKeySchema


class DSASignTraceSchema(BaseSchema):
    message: str
    hash_hex: str
    hash_int: int
    k: int
    r: int
    s: int
    k_inv: int
    p: int
    q: int
    g: int
    x: int
    formula_r: str
    formula_s: str
    resample_count: int


class DSASignRequest(BaseSchema):
    message: str = Field(..., description="Message string to sign")
    p: int = Field(...)
    q: int = Field(...)
    g: int = Field(...)
    x: int = Field(..., description="Private key exponent x")
    seed_k: int | None = Field(None, description="Optional deterministic nonce k for testing/demonstration")


class DSASignResponse(BaseSchema):
    r: int
    s: int
    r_str: str
    s_str: str
    hash_hex: str
    hash_int: int
    trace: DSASignTraceSchema


class DSAVerifyTraceSchema(BaseSchema):
    message: str
    hash_int: int
    r: int
    s: int
    w: int
    u1: int
    u2: int
    v: int
    is_valid: bool
    p: int
    q: int
    g: int
    y: int
    formula_w: str
    formula_u1: str
    formula_u2: str
    formula_v: str


class DSAVerifyRequest(BaseSchema):
    message: str = Field(..., description="Original message string")
    r: int = Field(..., description="Signature component r")
    s: int = Field(..., description="Signature component s")
    p: int = Field(...)
    q: int = Field(...)
    g: int = Field(...)
    y: int = Field(..., description="Public key y")


class DSAVerifyResponse(BaseSchema):
    is_valid: bool
    reason: str
    v: int | None
    r: int
    trace: DSAVerifyTraceSchema | None


class DSATamperRequest(BaseSchema):
    message: str = Field(..., description="Message string to tamper with")
    p: int = Field(...)
    q: int = Field(...)
    g: int = Field(...)
    x: int = Field(...)
    y: int = Field(...)
    tamper_target: Literal["message", "r", "s"] = Field("message", description="Component to flip bit in")
    bit_index: int = Field(0, ge=0, description="Bit index to invert")
    seed_k: int | None = Field(None)


class DSATamperResponse(BaseSchema):
    tamper_detected: bool
    tamper_type: str
    bit_flipped: int
    original_message: str
    tampered_message: str
    original_signature: dict[str, int]
    tampered_signature: dict[str, int]
    original_verification: bool
    tampered_verification: bool


class DSANonceReuseExploitRequest(BaseSchema):
    m1: str = Field(..., description="First message string")
    r1: int = Field(..., description="Signature r1")
    s1: int = Field(..., description="Signature s1")
    m2: str = Field(..., description="Second message string")
    r2: int = Field(..., description="Signature r2 (must equal r1)")
    s2: int = Field(..., description="Signature s2")
    p: int = Field(...)
    q: int = Field(...)
    g: int = Field(...)
    y: int = Field(...)


class DSANonceReuseExploitResponse(BaseSchema):
    is_exploit_applicable: bool
    recovered_k: int | None
    recovered_x: int | None
    recovered_k_str: str | None
    recovered_x_str: str | None
    is_valid_private_key: bool
    public_key_matched: bool
    steps: list[str]
    proof_summary: str
    historical_context: str
