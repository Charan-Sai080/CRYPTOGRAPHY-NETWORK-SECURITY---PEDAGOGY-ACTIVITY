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
