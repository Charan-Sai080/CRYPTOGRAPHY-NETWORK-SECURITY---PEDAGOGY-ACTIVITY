# Context Packet 6.2: One-Time Pad REST Router (`/api/v1/otp/*`) with Typed Pydantic Models

## 1. Goal
Implement the REST API router and Pydantic request/response schemas for the One-Time Pad (OTP) cryptographic pillar in `backend/api/v1/otp.py` and `backend/api/schemas/otp.py`.

The sub-milestone delivers endpoints for:
1. **CSPRNG Key Generation** (`POST /api/v1/otp/generate-key`): Secure cryptographic key generation with length validation, returning Hex, Base64, and Shannon entropy.
2. **Traced Encryption** (`POST /api/v1/otp/encrypt`): Encryption of plaintext with optional custom or auto-generated key, returning ciphertext representations (Hex, Base64), Shannon entropy comparison, and pedagogical step traces (`BitXORTrace`, `ByteOTPTrace`, ASCII truth table).
3. **Traced Decryption** (`POST /api/v1/otp/decrypt`): Decryption of ciphertext using provided key, returning recovered plaintext, ASCII validity flag, and bitwise verification traces.
4. **Two-Time Pad Key-Reuse Vulnerability Analysis** (`POST /api/v1/otp/two-time-pad/analyze`): Analysis of two ciphertexts encrypted with the identical key demonstrating algebraic key cancellation $C_1 \oplus C_2 = P_1 \oplus P_2$, entropy comparison, and optional known-plaintext derivation ($P_2 = C_1 \oplus C_2 \oplus P_1$).
5. **Interactive & Automated Crib-Dragging Attack** (`POST /api/v1/otp/two-time-pad/crib-drag`):
   - Targeted position crib-drag: Slide crib string at specific index $k$ to reveal candidate plaintext in second message.
   - Automated attack: Multi-position crib dragging across candidate dictionaries with English readability heuristics.
6. **Shannon Entropy Analysis** (`POST /api/v1/otp/entropy`): Standalone information-theoretic entropy evaluation computing symbol frequencies, observed entropy $H(X)$, maximum entropy $\log_2(n)$, efficiency ratio, and randomness verdict.

## 2. Allowed Files
* `backend/api/v1/otp.py`
* `backend/api/schemas/otp.py`
* `backend/api/schemas/__init__.py`
* `backend/api/v1/router.py` (to register otp_router)

## 3. Strict Data Contracts & Signatures

### Schemas (`backend/api/schemas/otp.py`)
```python
from __future__ import annotations

from typing import Literal
from pydantic import Field
from backend.api.schemas.common import BaseSchema


class BitXORTraceSchema(BaseSchema):
    bit_index: int
    bit_m: int
    bit_k: int
    bit_c: int
    equation: str


class ByteOTPTraceSchema(BaseSchema):
    byte_index: int
    char_m: str
    byte_m_val: int
    byte_m_bin: str
    byte_k_val: int
    byte_k_bin: str
    byte_c_val: int
    byte_c_bin: str
    byte_c_hex: str
    bit_traces: list[BitXORTraceSchema]


class OTPKeyGenerateRequest(BaseSchema):
    length: int = Field(..., ge=1, le=65536, description="Key length in bytes (1 to 65,536)")
    format: Literal["hex", "base64", "raw"] = Field("hex", description="Output serialization format")


class OTPKeyGenerateResponse(BaseSchema):
    key_hex: str
    key_base64: str
    length: int
    entropy: float


class OTPEncryptRequest(BaseSchema):
    plaintext: str = Field(..., min_length=1, description="Plaintext string to encrypt")
    key: str | None = Field(None, description="Optional hex-encoded key. If omitted, CSPRNG key is generated.")
    key_format: Literal["hex", "ascii"] = Field("hex", description="Encoding format of provided key")


class OTPEncryptResponse(BaseSchema):
    plaintext_ascii: str
    key_hex: str
    key_base64: str
    ciphertext_hex: str
    ciphertext_base64: str
    length: int
    entropy_plaintext: float
    entropy_key: float
    entropy_ciphertext: float
    byte_traces: list[ByteOTPTraceSchema]
    truth_table: str


class OTPDecryptRequest(BaseSchema):
    ciphertext: str = Field(..., min_length=1, description="Ciphertext to decrypt")
    key: str = Field(..., min_length=1, description="Decryption key")
    ciphertext_format: Literal["hex", "base64", "ascii"] = Field("hex", description="Encoding of ciphertext")
    key_format: Literal["hex", "ascii"] = Field("hex", description="Encoding of key")


class OTPDecryptResponse(BaseSchema):
    recovered_ascii: str
    recovered_hex: str
    ciphertext_hex: str
    key_hex: str
    length: int
    is_valid_ascii: bool
    byte_traces: list[ByteOTPTraceSchema]


class TwoTimePadAnalyzeRequest(BaseSchema):
    c1: str = Field(..., description="First ciphertext")
    c2: str = Field(..., description="Second ciphertext (encrypted with identical key)")
    input_format: Literal["hex", "base64", "ascii"] = Field("hex", description="Encoding of input ciphertexts")
    p1_known: str | None = Field(None, description="Optional known plaintext for c1 to demonstrate recovery of p2")


class TwoTimePadAnalyzeResponse(BaseSchema):
    c1_hex: str
    c2_hex: str
    xor_diff_hex: str
    length: int
    proof_steps: list[str]
    p1_known_ascii: str | None
    derived_p2_ascii: str | None
    shannon_entropy_c1: float
    shannon_entropy_c2: float
    shannon_entropy_diff: float


class CribDragRequest(BaseSchema):
    c1: str = Field(..., description="First ciphertext")
    c2: str = Field(..., description="Second ciphertext")
    input_format: Literal["hex", "base64", "ascii"] = Field("hex", description="Encoding of ciphertexts")
    crib: str = Field(..., min_length=1, description="Known or guessed crib word (e.g., 'the ', 'HELLO')")
    position: int | None = Field(None, ge=0, description="Optional target index. If None, automated crib drag is run.")
    min_readability_score: float = Field(0.3, ge=0.0, le=1.0, description="Threshold for automated crib scoring")


class CribDragCandidateSchema(BaseSchema):
    position: int
    crib: str
    revealed_text: str
    readability_score: float
    is_likely_english: bool


class CribDragResponse(BaseSchema):
    c1_hex: str
    c2_hex: str
    crib: str
    position: int | None
    single_result: CribDragCandidateSchema | None
    candidates: list[CribDragCandidateSchema]
    best_candidate: CribDragCandidateSchema | None
    summary: str


class EntropyRequest(BaseSchema):
    data: str = Field(..., min_length=1, description="Data to analyze")
    input_format: Literal["text", "hex"] = Field("text", description="Encoding of input data")


class EntropyResponse(BaseSchema):
    entropy: float
    max_entropy: float
    efficiency: float
    length: int
    unique_symbols: int
    verdict: str
    frequency_table: dict[str, int]
    probability_table: dict[str, float]
```

### Router Endpoints (`backend/api/v1/otp.py`)
```python
from fastapi import APIRouter, HTTPException, status
# Core helpers imported from backend.core.otp

router = APIRouter(prefix="/otp", tags=["One-Time Pad"])

@router.post("/generate-key", response_model=OTPKeyGenerateResponse)
async def generate_key(req: OTPKeyGenerateRequest) -> OTPKeyGenerateResponse:
    ...

@router.post("/encrypt", response_model=OTPEncryptResponse)
async def encrypt(req: OTPEncryptRequest) -> OTPEncryptResponse:
    ...

@router.post("/decrypt", response_model=OTPDecryptResponse)
async def decrypt(req: OTPDecryptRequest) -> OTPDecryptResponse:
    ...

@router.post("/two-time-pad/analyze", response_model=TwoTimePadAnalyzeResponse)
async def analyze_two_time_pad_endpoint(req: TwoTimePadAnalyzeRequest) -> TwoTimePadAnalyzeResponse:
    ...

@router.post("/two-time-pad/crib-drag", response_model=CribDragResponse)
async def crib_drag_endpoint(req: CribDragRequest) -> CribDragResponse:
    ...

@router.post("/entropy", response_model=EntropyResponse)
async def calculate_entropy_endpoint(req: EntropyRequest) -> EntropyResponse:
    ...
```

## 4. Acceptance Criteria
1. Key generation produces exact byte length with CSPRNG entropy $\approx 8.0$ bits/byte for sufficiently large keys.
2. Encrypt/decrypt roundtrip yields identical plaintext with 100% bit trace accuracy.
3. Key length mismatches raise clean HTTP 400 Bad Request errors.
4. Two-Time Pad endpoint mathematically verifies $C_1 \oplus C_2 = P_1 \oplus P_2$ and accurately recovers $P_2$ when $P_1$ is supplied.
5. Crib-dragging correctly ranks candidate English words at matching offsets.
6. Entropy endpoint provides exact Shannon calculations matching theoretical bounds.
