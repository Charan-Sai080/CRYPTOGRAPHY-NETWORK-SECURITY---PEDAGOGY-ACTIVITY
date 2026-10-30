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
