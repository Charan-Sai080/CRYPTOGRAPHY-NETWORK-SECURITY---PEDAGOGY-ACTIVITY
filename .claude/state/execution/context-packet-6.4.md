# Context Packet 6.4: ElGamal Cryptosystem REST Router (`/api/v1/elgamal/*`) with Typed Pydantic Models

## 1. Goal
Implement the REST API router and Pydantic request/response schemas for the ElGamal Public-Key Cryptosystem, Multiplicative Homomorphism, and Ephemeral Nonce-Reuse Exploit in `backend/api/v1/elgamal.py` and `backend/api/schemas/elgamal.py`.

The sub-milestone delivers endpoints for:
1. **Domain Presets Catalog** (`GET /api/v1/elgamal/presets`): Lists pre-verified educational primes (16-bit to 32-bit safe primes) and standard RFC 2409 MODP groups with modulus $p$ and primitive root $g$.
2. **Dynamic Domain Generation** (`POST /api/v1/elgamal/generate-domain`): Dynamically searches for a safe prime $p = 2q + 1$ and verifies primitive root $g \in \mathbb{Z}_p^*$, returning step generation logs.
3. **Key Pair Generation** (`POST /api/v1/elgamal/generate-keys`): Generates private key $x \in [2, p - 2]$ and computes public key $y = g^x \pmod p$, supporting deterministic seeding for reproducible pedagogy.
4. **Traced Encryption** (`POST /api/v1/elgamal/encrypt`):
   - Integer encryption: Encrypts numerical plaintext $m < p$ using ephemeral key $k \in [2, p - 2]$, calculating $c_1 = g^k \pmod p$, shared secret $s = y^k \pmod p$, and $c_2 = (m \cdot s) \pmod p$, returning full step traces.
   - Text message chunking: Encrypts arbitrary UTF-8 text strings split into mathematical blocks satisfying $m < p$, returning multi-block ciphertexts and traces.
5. **Traced Decryption** (`POST /api/v1/elgamal/decrypt`):
   - Integer decryption: Reconstructs shared secret $s = c_1^x \pmod p$, computes modular inverse $s^{-1} \pmod p$, and recovers $m = (c_2 \cdot s^{-1}) \pmod p$.
   - Multi-block text decryption: Recombines decrypted integer blocks back into the UTF-8 plaintext string.
6. **Multiplicative Homomorphism Demonstration** (`POST /api/v1/elgamal/homomorphic-multiply`): Demonstrates component-wise ciphertext multiplication $E(m_1) \cdot E(m_2) = (c_{1,a} \cdot c_{1,b} \pmod p, c_{2,a} \cdot c_{2,b} \pmod p) = E(m_1 \cdot m_2 \pmod p)$ and verifies equality after decryption.
7. **Ephemeral Nonce-Reuse Known-Plaintext Exploit** (`POST /api/v1/elgamal/exploit-nonce-reuse`): Demonstrates key vulnerability when identical nonce $k$ is reused for distinct messages ($c_{1,a} = c_{1,b}$), recovering unknown plaintext $m_2 = (m_1 \cdot c_{2,b} \cdot c_{2,a}^{-1}) \pmod p$ without the private key.

## 2. Allowed Files
* `backend/api/v1/elgamal.py`
* `backend/api/schemas/elgamal.py`
* `backend/api/schemas/__init__.py`
* `backend/api/v1/router.py` (to register elgamal_router)

## 3. Strict Data Contracts & Signatures

### Schemas (`backend/api/schemas/elgamal.py`)
```python
from __future__ import annotations

from typing import Literal
from pydantic import Field
from backend.api.schemas.common import BaseSchema


class ElGamalPresetSchema(BaseSchema):
    name: str
    description: str
    p: int
    g: int
    p_bits: int
    is_safe_prime: bool


class ElGamalDomainGenerateRequest(BaseSchema):
    bits: int = Field(16, ge=8, le=64, description="Bit length for educational prime p (8-64 bits)")


class ElGamalDomainGenerateResponse(BaseSchema):
    p: int
    g: int
    p_str: str
    g_str: str
    p_bits: int
    steps: list[str]


class ElGamalKeyGenerateRequest(BaseSchema):
    p: int | None = Field(None, description="Modulus prime p")
    g: int | None = Field(None, description="Primitive root generator g")
    preset_name: str | None = Field(None, description="Preset name to use instead of p and g")
    seed_x: int | None = Field(None, description="Optional deterministic seed for private key x")


class ElGamalPublicKeySchema(BaseSchema):
    p: int
    g: int
    y: int
    p_str: str
    g_str: str
    y_str: str


class ElGamalPrivateKeySchema(BaseSchema):
    p: int
    g: int
    x: int
    p_str: str
    g_str: str
    x_str: str


class ElGamalKeyGenerateResponse(BaseSchema):
    public_key: ElGamalPublicKeySchema
    private_key: ElGamalPrivateKeySchema


class ElGamalEncryptTraceSchema(BaseSchema):
    m: int
    k: int
    y: int
    p: int
    g: int
    c1: int
    c2: int
    shared_secret_s: int
    formula_c1: str
    formula_s: str
    formula_c2: str


class ElGamalCiphertextBlockSchema(BaseSchema):
    index: int
    c1: int
    c2: int
    c1_str: str
    c2_str: str
    original_length: int


class ElGamalEncryptRequest(BaseSchema):
    p: int = Field(..., description="Prime modulus p")
    g: int = Field(..., description="Generator g")
    y: int = Field(..., description="Public key component y")
    message_int: int | None = Field(None, description="Single integer to encrypt (must satisfy 0 < m < p)")
    message_text: str | None = Field(None, description="Arbitrary UTF-8 text string to chunk and encrypt")
    seed_k: int | None = Field(None, description="Optional fixed ephemeral nonce k for deterministic demonstration")


class ElGamalEncryptResponse(BaseSchema):
    is_multi_block: bool
    c1: int | None
    c2: int | None
    c1_str: str | None
    c2_str: str | None
    blocks: list[ElGamalCiphertextBlockSchema]
    single_trace: ElGamalEncryptTraceSchema | None
    block_traces: list[ElGamalEncryptTraceSchema]
    block_size_bytes: int


class ElGamalDecryptTraceSchema(BaseSchema):
    c1: int
    c2: int
    x: int
    p: int
    shared_secret_s: int
    s_inv: int
    recovered_m: int
    formula_s: str
    formula_s_inv: str
    formula_m: str


class ElGamalDecryptRequest(BaseSchema):
    p: int = Field(..., description="Prime modulus p")
    x: int = Field(..., description="Private key exponent x")
    c1: int | None = Field(None, description="c1 for single integer decryption")
    c2: int | None = Field(None, description="c2 for single integer decryption")
    blocks: list[ElGamalCiphertextBlockSchema] | None = Field(None, description="Ciphertext blocks for text decryption")


class ElGamalDecryptResponse(BaseSchema):
    is_multi_block: bool
    recovered_int: int | None
    recovered_text: str | None
    single_trace: ElGamalDecryptTraceSchema | None
    block_traces: list[ElGamalDecryptTraceSchema]


class HomomorphicMultiplyRequest(BaseSchema):
    m1: int = Field(..., description="First plaintext integer (m1 < p)")
    m2: int = Field(..., description="Second plaintext integer (m2 < p)")
    p: int = Field(...)
    g: int = Field(...)
    y: int = Field(...)
    x: int | None = Field(None, description="Optional private key x to verify by decryption")
    seed_k1: int | None = Field(None)
    seed_k2: int | None = Field(None)


class HomomorphicMultiplyResponse(BaseSchema):
    m1: int
    m2: int
    p: int
    c1_a: int
    c2_a: int
    c1_b: int
    c2_b: int
    c1_mult: int
    c2_mult: int
    expected_product: int
    decrypted_product: int | None
    is_verified: bool
    explanation: str


class NonceReuseExploitRequest(BaseSchema):
    p: int = Field(..., description="Prime modulus p")
    c1_a: int = Field(...)
    c2_a: int = Field(...)
    c1_b: int = Field(...)
    c2_b: int = Field(...)
    m1_known: int = Field(..., description="Known plaintext m1 corresponding to (c1_a, c2_a)")


class NonceReuseExploitResponse(BaseSchema):
    is_attack_applicable: bool
    p: int
    c1_identical: bool
    m1_known: int
    recovered_m2: int | None
    ratio: int | None
    proof_steps: list[str]
    explanation: str
```

### Router Endpoints (`backend/api/v1/elgamal.py`)
```python
from fastapi import APIRouter, HTTPException, status
# Core helpers imported from backend.core.elgamal

router = APIRouter(prefix="/elgamal", tags=["ElGamal Cryptosystem"])

@router.get("/presets", response_model=list[ElGamalPresetSchema])
async def get_presets() -> list[ElGamalPresetSchema]:
    ...

@router.post("/generate-domain", response_model=ElGamalDomainGenerateResponse)
async def generate_domain(req: ElGamalDomainGenerateRequest) -> ElGamalDomainGenerateResponse:
    ...

@router.post("/generate-keys", response_model=ElGamalKeyGenerateResponse)
async def generate_keys(req: ElGamalKeyGenerateRequest) -> ElGamalKeyGenerateResponse:
    ...

@router.post("/encrypt", response_model=ElGamalEncryptResponse)
async def encrypt(req: ElGamalEncryptRequest) -> ElGamalEncryptResponse:
    ...

@router.post("/decrypt", response_model=ElGamalDecryptResponse)
async def decrypt(req: ElGamalDecryptRequest) -> ElGamalDecryptResponse:
    ...

@router.post("/homomorphic-multiply", response_model=HomomorphicMultiplyResponse)
async def homomorphic_multiply(req: HomomorphicMultiplyRequest) -> HomomorphicMultiplyResponse:
    ...

@router.post("/exploit-nonce-reuse", response_model=NonceReuseExploitResponse)
async def exploit_nonce_reuse_endpoint(req: NonceReuseExploitRequest) -> NonceReuseExploitResponse:
    ...
```

## 4. Acceptance Criteria
1. String serialization (`p_str`, `g_str`, `y_str`, `c1_str`, `c2_str`) accompanies integer fields for large bit lengths.
2. Single integer and chunked multi-block text encryption/decryption roundtrips preserve 100% data integrity.
3. Homomorphic multiplication verifies $E(m_1) \cdot E(m_2) = E(m_1 \cdot m_2 \pmod p)$.
4. Ephemeral nonce-reuse exploit successfully recovers $m_2$ when $c_{1,a} == c_{1,b}$ and rejects when $c_1$ values differ.
5. Invalid parameters ($m \ge p$, $x \ge p$, composite $p$) return HTTP 400 Bad Request with informative error messages.
