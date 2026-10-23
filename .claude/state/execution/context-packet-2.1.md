# Context Packet 2.1: Core One-Time Pad (OTP) Engine & Pedagogical Execution Traces

## 1. Goal
Implement the core One-Time Pad (OTP) symmetric encryption/decryption engine in `backend/core/otp.py` in pure Python 3.12+.
The implementation must provide:
1. Cryptographically secure pseudorandom key generation using Python's `secrets` module.
2. Full bitwise and byte-wise XOR execution tracing for pedagogical inspection (bit-by-bit truth tables, byte hex/binary views).
3. Empirical Shannon entropy analysis ($H(X) = -\sum P(x) \log_2 P(x)$) for plaintext, key, and ciphertext.
4. Mathematical explanation of Shannon's Perfect Secrecy theorem ($P(M=m \mid C=c) = P(M=m)$).
5. Safe serialization helpers (Hexadecimal, Base64, and UTF-8 handling).

## 2. Allowed Files
* `backend/core/otp.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import math
import secrets
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BitXORTrace:
    bit_index: int       # Bit position: 7 (MSB) down to 0 (LSB)
    bit_p: int           # Plaintext bit (0 or 1)
    bit_k: int           # Key bit (0 or 1)
    bit_c: int           # Ciphertext bit: bit_p ^ bit_k
    formula: str         # Pedagogical formula, e.g. "1 ^ 0 = 1"


@dataclass
class ByteOTPTrace:
    byte_index: int
    p_char: str          # Printable ASCII character or hex escape (e.g., "'A'" or "'\\x00'")
    p_val: int           # Plaintext byte integer value [0, 255]
    p_bin: str           # 8-bit binary string with leading zeros, e.g. "01000001"
    p_hex: str           # 2-character lowercase hex string, e.g. "41"
    k_val: int           # Key byte integer value [0, 255]
    k_bin: str           # 8-bit binary string with leading zeros, e.g. "10110010"
    k_hex: str           # 2-character lowercase hex string, e.g. "b2"
    c_val: int           # Ciphertext byte integer: p_val ^ k_val
    c_bin: str           # 8-bit binary string with leading zeros, e.g. "11110011"
    c_hex: str           # 2-character lowercase hex string, e.g. "f3"
    c_char: str          # Printable ASCII character or hex escape
    bit_traces: list[BitXORTrace] = field(default_factory=list)


@dataclass
class EntropyAnalysis:
    data_length: int
    entropy: float                 # Shannon entropy in bits per byte [0.0, 8.0]
    max_entropy: float = 8.0       # Theoretical maximum for 8-bit bytes (log2(256) = 8.0)
    entropy_ratio: float = 0.0     # Normalized entropy ratio: entropy / 8.0 in [0.0, 1.0]
    frequencies: dict[int, int] = field(default_factory=dict)  # Byte value -> occurrence count
    is_near_maximal: bool = False  # True if entropy >= 7.5 or uniform
    explanation: str = ""          # Pedagogical explanation of the observed entropy


@dataclass
class OTPEncryptionResult:
    plaintext_bytes: bytes
    key_bytes: bytes
    ciphertext_bytes: bytes
    plaintext_hex: str
    key_hex: str
    ciphertext_hex: str
    ciphertext_base64: str
    traces: list[ByteOTPTrace] = field(default_factory=list)
    plaintext_entropy: EntropyAnalysis = field(default_factory=lambda: EntropyAnalysis(0, 0.0))
    key_entropy: EntropyAnalysis = field(default_factory=lambda: EntropyAnalysis(0, 0.0))
    ciphertext_entropy: EntropyAnalysis = field(default_factory=lambda: EntropyAnalysis(0, 0.0))
    perfect_secrecy_notes: str = ""


@dataclass
class OTPDecryptionResult:
    ciphertext_bytes: bytes
    key_bytes: bytes
    decrypted_bytes: bytes
    decrypted_text: str | None     # Decoded UTF-8 string, or None if raw non-UTF8 binary
    ciphertext_hex: str
    key_hex: str
    decrypted_hex: str
    traces: list[ByteOTPTrace] = field(default_factory=list)
    is_valid_utf8: bool = True


def generate_otp_key(length: int) -> bytes:
    """Generates a cryptographically secure random key of specified byte length using CSPRNG.
    
    Raises:
        ValueError: If length < 0.
    """


def calculate_shannon_entropy(data: bytes) -> EntropyAnalysis:
    """Calculates empirical Shannon entropy H(X) = -sum(P(x) * log2(P(x))) over byte frequencies.
    
    Returns an EntropyAnalysis object with entropy value in [0.0, 8.0], byte frequencies,
    ratio against 8-bit maximum, and a pedagogical explanation.
    """


def encrypt_otp(
    plaintext: str | bytes,
    key: bytes | None = None
) -> OTPEncryptionResult:
    """Encrypts plaintext using One-Time Pad (byte-wise XOR) with detailed pedagogical traces.
    
    If key is None, generates a fresh CSPRNG key matching plaintext length.
    If key is provided and longer than plaintext, slices key to plaintext length.
    
    Raises:
        ValueError: If key is provided but len(key) < len(plaintext).
    """


def decrypt_otp(
    ciphertext: bytes | str,
    key: bytes
) -> OTPDecryptionResult:
    """Decrypts ciphertext using One-Time Pad key (C ^ K) with detailed pedagogical traces.
    
    Accepts raw bytes or a hex-encoded string for ciphertext.
    If key is longer than ciphertext, slices key to ciphertext length.
    
    Raises:
        ValueError: If len(key) < len(ciphertext), or if ciphertext is an invalid hex string.
    """


def format_byte_truth_table(trace: ByteOTPTrace) -> str:
    """Renders an ASCII text truth table for the 8 bit-by-bit XOR operations of a byte trace."""
```

## 4. Acceptance Criteria
1. **CSPRNG Generation**: `generate_otp_key(n)` must use `secrets.token_bytes(n)`. Keys must be statistically non-repeating across invocations.
2. **Byte-by-Byte & Bit-by-Bit Tracing**:
   - For every byte $i$ from 0 to $N-1$, produces a `ByteOTPTrace`.
   - Each `ByteOTPTrace` must contain exactly 8 `BitXORTrace` items ordered from bit 7 (MSB) down to bit 0 (LSB).
   - Bit formulas must follow `"P_bit ^ K_bit = C_bit"` (e.g., `"1 ^ 0 = 1"`).
   - Binary representations must be zero-padded 8-character strings (`f"{byte:08b}"`).
3. **Shannon Entropy**:
   - Constant repeated bytes (e.g. `b"A" * 100`) must evaluate to exactly $0.0$.
   - Uniform distribution over all 256 byte values must evaluate to $8.0$ bits/byte.
   - Natural language and random keys correctly report their empirical entropy and frequency distribution.
4. **Shannon Perfect Secrecy Invariant**:
   - Provides a comprehensive, rigorous educational explanation detailing why $H(M \mid C) = H(M)$ and $P(M=m \mid C=c) = P(M=m)$ holds when and only when:
     1. Key is truly random and uniformly distributed.
     2. Key length is at least message length ($|K| \ge |M|$).
     3. Key is never reused.
5. **Decryption & Involution**:
   - `decrypt_otp` cleanly recovers original bytes: $(M \oplus K) \oplus K = M$.
   - UTF-8 decoding is attempted; if valid, `decrypted_text` is set and `is_valid_utf8 = True`; otherwise `decrypted_text = None` and `is_valid_utf8 = False`.

## 5. Edge Cases
* **Empty Plaintext / Ciphertext (`b""` or `""`)**: Returns a valid result object with 0 bytes, empty trace list, and 0.0 entropy without errors.
* **Negative Key Length**: `generate_otp_key(-1)` raises `ValueError("Key length must be non-negative.")`.
* **Insufficient Key Length**: `encrypt_otp("hello", key=b"key")` raises `ValueError("Key length (3) must be at least plaintext length (5) for One-Time Pad.")`.
* **Excess Key Length**: If `len(key) > len(plaintext)`, key is safely truncated to `key[:len(plaintext)]`, preserving OTP operation.
* **Unprintable & Null Bytes**: Bytes containing `\x00`, `\xff`, or control characters must be properly escaped in `p_char` and `c_char` (e.g., `repr(chr(val))` or `f"\\x{val:02x}"`).
* **Multi-Byte Unicode**: Text strings containing multi-byte UTF-8 sequences (e.g., emojis, accented letters) are UTF-8 encoded into bytes prior to XOR and preserved across encryption/decryption roundtrips.
* **Ciphertext as Hex String**: `decrypt_otp` accepts both raw `bytes` and hex strings (e.g., `"48656c6c6f"`). Raises `ValueError` on malformed hex strings.
