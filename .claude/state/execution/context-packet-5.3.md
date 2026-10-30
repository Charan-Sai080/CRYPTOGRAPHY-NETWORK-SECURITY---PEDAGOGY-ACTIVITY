# Context Packet 5.3: Traced Verification Engine & Interactive Tampering Detection

## 1. Goal
Implement the Traced DSA Signature Verification Engine and Interactive Tampering Detection in `backend/core/dsa.py` in pure Python 3.12+, adhering to FIPS 186-4:
1. Strict boundary verification:
   - Check that signature components satisfy $0 < r < q$ and $0 < s < q$. Reject immediately with `is_valid = False` if either condition is violated.
2. Verification arithmetic pipeline:
   - Compute modular inverse $w = s^{-1} \pmod q = \text{mod\_inverse}(s, q)$.
   - Compute subgroup exponents:
     $$u_1 = (z \cdot w) \pmod q$$
     $$u_2 = (r \cdot w) \pmod q$$
   - Compute verification point $v$:
     $$v = ((g^{u_1} \cdot y^{u_2}) \pmod p) \pmod q$$
   - Signature is authenticated if and only if:
     $$v == r$$
3. Full pedagogical verification tracing (`DSAVerifyTrace`):
   - Record $z, r, s, w, u_1, u_2, g^{u_1} \pmod p, y^{u_2} \pmod p, v$, formulas, and the formal algebraic correctness proof demonstrating why $g^{u_1} y^{u_2} \equiv g^k \pmod p$.
4. Interactive Tampering Detection:
   - Provide utilities to mutate 1 bit in the message (`tamper_message_bit`) or modify signature components $r, s$ (`tamper_signature_component`).
   - Execute side-by-side verification comparing original vs tampered inputs (`detect_tampering`), demonstrating why even a single-bit alteration catastrophically breaks the verification identity $v == r$.

## 2. Allowed Files
* `backend/core/dsa.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.dsa import (
    DSADomainParams,
    DSAError,
    DSAPublicKey,
    DSASignature,
    InvalidKeyError,
)
from backend.core.number_theory import (
    mod_inverse,
    mod_pow,
    sha256_digest_int,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DSAVerificationError(DSAError):
    """Raised when an unrecoverable error occurs during signature verification."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class DSAVerifyTrace:
    """Detailed step-by-step arithmetic trace for a DSA verification operation."""
    message: str | bytes
    z: int                          # Truncated hash integer
    r: int                          # Signature r
    s: int                          # Signature s
    w: int                          # w = s^-1 mod q
    u1: int                         # u1 = (z * w) mod q
    u2: int                         # u2 = (r * w) mod q
    gu1_mod_p: int                  # g^u1 mod p
    yu2_mod_p: int                  # y^u2 mod p
    v: int                          # v = ((g^u1 * y^u2) mod p) mod q
    is_valid: bool                  # True iff v == r
    w_formula: str                  # e.g., "w = s^-1 mod q = 65^-1 mod 101 = 42"
    u1_formula: str                 # e.g., "u1 = (z * w) mod q = (12 * 42) mod 101 = 100"
    u2_formula: str                 # e.g., "u2 = (r * w) mod q = (81 * 42) mod 101 = 71"
    v_formula: str                  # e.g., "v = ((g^u1 * y^u2) mod p) mod q = ((64^100 * 123^71) mod 607) mod 101 = 81"
    verification_formula: str       # e.g., "v == r: 81 == 81 (Valid)"
    mathematical_proof: str = ""    # LaTeX/algebraic proof that g^u1 * y^u2 == g^k mod p


@dataclass
class DSAVerificationResult:
    """High-level verification result encapsulating boolean status and trace."""
    is_valid: bool
    reason: str
    trace: DSAVerifyTrace | None = None


@dataclass
class TamperDetectionResult:
    """Comparative report demonstrating tampering detection."""
    tamper_type: str                # "message_bit_flip", "signature_r_alter", "signature_s_alter"
    original_valid: bool
    tampered_valid: bool
    detected: bool                  # True if tampered signature was successfully rejected
    original_value: Any
    tampered_value: Any
    original_v: int | None
    tampered_v: int | None
    explanation: str


# ---------------------------------------------------------------------------
# Functions to Implement
# ---------------------------------------------------------------------------

def verify_hash_int(
    z: int,
    signature: DSASignature,
    public_key: DSAPublicKey,
    message_repr: str | bytes = "<hash-input>"
) -> DSAVerificationResult:
    """Verifies a signature against a truncated hash digest integer z."""
    ...

def verify_message(
    message: str | bytes,
    signature: DSASignature,
    public_key: DSAPublicKey
) -> DSAVerificationResult:
    """Computes SHA-256(message), truncates to bit_length(q), and verifies signature."""
    ...

def tamper_message_bit(message: str, bit_index: int = 0) -> str:
    """Flips exactly 1 bit in a UTF-8 message string for educational demonstration."""
    ...

def tamper_signature_component(
    signature: DSASignature,
    component: str = "r",
    delta: int = 1
) -> tuple[int, int]:
    """Mutates signature component r or s by adding delta."""
    ...

def detect_tampering(
    message: str | bytes,
    signature: DSASignature,
    public_key: DSAPublicKey,
    tamper_type: str = "message_bit_flip"
) -> TamperDetectionResult:
    """Runs original and tampered verifications side-by-side to demonstrate failure."""
    ...
```

## 4. Acceptance Criteria
1. Strict FIPS 186-4 parameter checks: reject immediately if $r \le 0$ or $r \ge q$ or $s \le 0$ or $s \ge q$.
2. Exact modular operations: $w = s^{-1} \pmod q$, $u_1 = (z \cdot w) \pmod q$, $u_2 = (r \cdot w) \pmod q$, $v = ((g^{u_1} \cdot y^{u_2}) \pmod p) \pmod q$.
3. Comprehensive educational traces in `DSAVerifyTrace` including step formulas and mathematical equivalence proof.
4. Tampering engine reliably demonstrates rejection of single-bit modified messages and altered signature components.
