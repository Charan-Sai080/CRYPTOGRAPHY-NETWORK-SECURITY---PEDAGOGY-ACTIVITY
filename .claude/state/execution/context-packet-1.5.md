# Context Packet 1.5: String Block Chunking, SHA-256 Truncation (FIPS 186-4), and RFC MODP Groups

## 1. Goal
Implement cryptographic encoding and utility primitives in pure Python:
1. Message block chunking and reconstruction converting arbitrary UTF-8 text strings into bounded integers suitable for ElGamal modular encryption ($m < p$).
2. FIPS 186-4 compliant SHA-256 digest hashing with leftmost bit-truncation for Digital Signature Algorithm (DSA) parameter matching.
3. Standard MODP group definitions: pre-verified RFC 2409 1024-bit Oakley Group 2 and small educational groups (16-bit to 32-bit) with pre-computed cyclic generators for fast UI demonstrations.

## 2. Allowed Files
* `backend/core/number_theory.py`
* `backend/tests/test_number_theory.py`

## 3. Signatures & Contracts

### Functions
```python
def string_to_int_blocks(text: str, max_prime_bits: int) -> list[int]:
    """Encodes a UTF-8 text string into an array of integers, where each integer value
    is guaranteed to be strictly less than 2^(max_prime_bits - 1).
    This ensures that each block can be directly encrypted under ElGamal modulo p.
    """

def int_blocks_to_string(blocks: list[int], max_prime_bits: int) -> str:
    """Decodes an array of block integers back into a UTF-8 string."""

def sha256_digest_int(message: str | bytes, bit_limit: int | None = None) -> int:
    """Computes SHA-256 of message and returns integer value.
    If bit_limit is specified, truncates to the leftmost bit_limit bits (per FIPS 186-4 DSA).
    """
```

### MODP Group Dictionaries
```python
RFC_2409_1024_MODP = {
    "name": "RFC 2409 / RFC 3526 1024-bit MODP Group",
    "bits": 1024,
    "generator": 2,
    "prime_hex": "...",
    "prime": int("...", 16)
}

EDUCATIONAL_MODP_GROUPS = [
    {"name": "Educational 16-bit", "bits": 16, "prime": 65537, "generator": 3},
    {"name": "Educational 20-bit", "bits": 20, "prime": 1048583, "generator": 2},
    {"name": "Educational 24-bit Safe Prime", "bits": 24, "prime": 16777259, "generator": 2},
    {"name": "Educational 32-bit Safe Prime", "bits": 32, "prime": 4294967311, "generator": 3},
]
```

## 4. Acceptance Criteria
1. **Bounded Block Sizing**:
   - `chunk_size = max(1, (max_prime_bits - 1) // 8)`.
   - Each chunk of bytes is converted to big-endian integer: `int.from_bytes(chunk, byteorder="big")`.
   - Guarantees $val < 2^{\text{max\_prime\_bits} - 1} < p$ for any modulus of length $\ge \text{max\_prime\_bits}$.
2. **Lossless Round-Trip**:
   - `int_blocks_to_string(string_to_int_blocks(text, bits), bits) == text` for all UTF-8 strings.
3. **FIPS 186-4 SHA-256 Leftmost Truncation**:
   - Computes 32-byte SHA-256 digest integer.
   - When `bit_limit < 256`, shifts right by `(256 - bit_limit)` bits: `val >>= (256 - bit_limit)`, preserving the most significant `bit_limit` bits per FIPS 186-4 section 6.4.
4. **MODP Group Validation**:
   - RFC 2409 1024-bit group verified for bit length (1024) and generator (2).
   - Educational groups (16, 20, 24, 32 bits) verified for primality and order $g^{p-1} \equiv 1 \pmod p$.
5. **Unit Test Suite**: Covered by `TestEncodingAndHashing` and `TestRFCGroups` in `backend/tests/test_number_theory.py`.

## 5. Edge Cases
* **Empty String**: Chunking empty string returns `[]`.
* **Multi-Byte UTF-8 Characters**: Properly preserves multi-byte UTF-8 sequences across chunk boundaries.
* **Null Byte Integrity**: Blocks containing zero or leading null bytes are safely decoded without data loss.
* **Input Types**: `sha256_digest_int` transparently accepts both `str` and `bytes`.
* **Bit Limit Out-of-Bounds**: If `bit_limit >= 256` or `bit_limit is None`, full 256-bit hash integer is retained.
* **Standard 160-bit Truncation**: Correctly produces $\le 160$-bit integer for standard DSA-1024/SHA-256 interop.
