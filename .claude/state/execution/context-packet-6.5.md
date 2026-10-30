# Context Packet 6.5: Digital Signature Algorithm REST Router (`/api/v1/dsa/*`) with Typed Pydantic Models

## 1. Goal
Implement the REST API router and Pydantic request/response schemas for the Digital Signature Algorithm (DSA) adhering to FIPS 186-4, Interactive Single-Bit Tampering Detection, and Sony PS3 Nonce-Reuse Private Key Recovery Exploit in `backend/api/v1/dsa.py` and `backend/api/schemas/dsa.py`.

The sub-milestone delivers endpoints for:
1. **DSA Presets Catalog** (`GET /api/v1/dsa/presets`): Lists pre-verified FIPS 186-4 standard 1024/160-bit group (NIST CAVP) and educational small groups (10-bit, 16-bit, 24-bit).
2. **Dynamic Domain Generation** (`POST /api/v1/dsa/generate-domain`): Dynamically searches for prime modulus $p$ and prime divisor $q$ such that $q \mid (p - 1)$ with subgroup generator $g = h^{(p - 1)/q} \pmod p > 1$, outputting Miller-Rabin search logs.
3. **Key Pair Generation** (`POST /api/v1/dsa/generate-keys`): Generates private key $x \in [1, q - 1]$ and public key $y = g^x \pmod p$ with optional deterministic seed support.
4. **Traced Message Signing** (`POST /api/v1/dsa/sign`): Computes SHA-256 message digest left-truncated to bit length of $q$, draws ephemeral secret $k \in [1, q - 1]$, evaluates $r = (g^k \pmod p) \pmod q$, applies FIPS 186-4 $r=0$ resampling, calculates $s = (k^{-1}(z + xr)) \pmod q$ with $s=0$ resampling, returning signature $(r, s)$ and complete trace.
5. **Traced Signature Verification** (`POST /api/v1/dsa/verify`): Verifies boundary constraints $0 < r < q$ and $0 < s < q$, calculates $w = s^{-1} \pmod q$, $u_1 = (z \cdot w) \pmod q$, $u_2 = (r \cdot w) \pmod q$, and $v = ((g^{u_1} y^{u_2}) \pmod p) \pmod q$, validating that $v == r$.
6. **Interactive Single-Bit Tampering Detector** (`POST /api/v1/dsa/detect-tampering`): Simulates single-bit alterations on the message text or signature components $(r, s)$, demonstrating cryptographic fragility and non-repudiation.
7. **Sony PS3 Ephemeral Nonce-Reuse Exploit** (`POST /api/v1/dsa/exploit-nonce-reuse`): Demonstrates the catastrophic vulnerability of reusing ephemeral nonce $k$ across two distinct messages ($M_1 \ne M_2, r_1 == r_2$), algebraically extracting $k = (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$ and private key $x = (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$, validated against public key $y$.

## 2. Allowed Files
* `backend/api/v1/dsa.py`
* `backend/api/schemas/dsa.py`
* `backend/api/schemas/__init__.py`
* `backend/api/v1/router.py` (to register dsa_router)

## 3. Strict Data Contracts & Signatures

### Schemas (`backend/api/schemas/dsa.py`)
```python
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
```

### Router Endpoints (`backend/api/v1/dsa.py`)
```python
from fastapi import APIRouter, HTTPException, status
# Core helpers imported from backend.core.dsa

router = APIRouter(prefix="/dsa", tags=["Digital Signature Algorithm"])

@router.get("/presets", response_model=list[DSAPresetSchema])
async def get_presets() -> list[DSAPresetSchema]:
    ...

@router.post("/generate-domain", response_model=DSADomainGenerateResponse)
async def generate_domain(req: DSADomainGenerateRequest) -> DSADomainGenerateResponse:
    ...

@router.post("/generate-keys", response_model=DSAKeyGenerateResponse)
async def generate_keys(req: DSAKeyGenerateRequest) -> DSAKeyGenerateResponse:
    ...

@router.post("/sign", response_model=DSASignResponse)
async def sign(req: DSASignRequest) -> DSASignResponse:
    ...

@router.post("/verify", response_model=DSAVerifyResponse)
async def verify(req: DSAVerifyRequest) -> DSAVerifyResponse:
    ...

@router.post("/detect-tampering", response_model=DSATamperResponse)
async def detect_tampering_endpoint(req: DSATamperRequest) -> DSATamperResponse:
    ...

@router.post("/exploit-nonce-reuse", response_model=DSANonceReuseExploitResponse)
async def exploit_nonce_reuse_endpoint(req: DSANonceReuseExploitRequest) -> DSANonceReuseExploitResponse:
    ...
```

## 4. Acceptance Criteria
1. String versions (`p_str`, `q_str`, `g_str`, `y_str`, `x_str`, `r_str`, `s_str`) are provided alongside integer representations.
2. Sign/verify cycle succeeds on both FIPS 186-4 1024-bit group and small educational groups.
3. Tampering detector verifies that flipping a single bit in message, $r$, or $s$ causes verification to return `is_valid: False` and `tamper_detected: True`.
4. Ephemeral nonce-reuse exploit successfully recovers $k$ and private key $x$ with $y == g^x \pmod p$ when $r_1 == r_2$ and $M_1 \ne M_2$.
5. Reused nonce on identical messages or mismatched $r$ raises appropriate domain error (400 Bad Request).
