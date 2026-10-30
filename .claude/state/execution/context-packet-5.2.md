# Context Packet 5.2: Traced Signing Engine with SHA-256 and FIPS 186-4 Resampling

## 1. Goal
Implement the Traced Digital Signature Algorithm (DSA) Signing Engine in `backend/core/dsa.py` in pure Python 3.12+, adhering to FIPS 186-4 standards:
1. Message digest computation and bit truncation:
   - Compute SHA-256 digest of message $M$.
   - Left-truncate the hash to $N = \min(\text{bit\_length}(q), 256)$ bits:
     $$z = \text{leftmost } N \text{ bits of } \text{SHA-256}(M)$$
     utilizing `sha256_digest_int(message, bit_limit=domain.q_bits)` from `backend.core.number_theory`.
2. Ephemeral secret generation ($k \in [1, q - 1]$):
   - Uniformly drawn via CSPRNG `secrets.randbelow(q - 1) + 1`.
   - Optional deterministic `seed_k` parameter for reproducible unit testing, fixed vectors, and predictable visual demonstrations.
3. Ephemeral component calculation & FIPS 186-4 Resampling:
   - Compute $r = (g^k \pmod p) \pmod q$.
   - If $r == 0$, resample a new ephemeral secret $k$ and retry.
4. Signature component calculation & FIPS 186-4 Resampling:
   - Compute modular inverse $k^{-1} = \text{mod\_inverse}(k, q)$.
   - Compute $s = (k^{-1} \cdot (z + x \cdot r)) \pmod q$.
   - If $s == 0$, resample a new ephemeral secret $k$ and retry.
5. Pedagogical execution tracing:
   - Provide structured trace records (`DSASignTrace`) capturing message hex, digest integer $z$, ephemeral nonce $k$, modular inverse $k^{-1}$, intermediate product $x \cdot r$, sum $z + x \cdot r$, final $s$, and formatted arithmetic formulas for educational display.
   - Return structured `DSASignature` and `DSASignResult` objects.

## 2. Allowed Files
* `backend/core/dsa.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Any

from backend.core.dsa import (
    DSADomainParams,
    DSAError,
    DSAPrivateKey,
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

class DSASignatureError(DSAError):
    """Raised when signature generation fails or invalid inputs are provided."""
    pass


class ResamplingFailureError(DSASignatureError):
    """Raised if maximum resampling attempts are exceeded without generating valid (r, s)."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DSASignature:
    """Represents a DSA digital signature pair (r, s)."""
    r: int                          # r = (g^k mod p) mod q
    s: int                          # s = k^-1 * (z + x * r) mod q
    q: int                          # Subgroup modulus q for boundary validation

    def __post_init__(self) -> None:
        if not (0 < self.r < self.q):
            raise DSASignatureError(f"Signature component r must satisfy 0 < r < q, got {self.r}")
        if not (0 < self.s < self.q):
            raise DSASignatureError(f"Signature component s must satisfy 0 < s < q, got {self.s}")


@dataclass
class DSASignTrace:
    """Exhaustive step-by-step arithmetic trace for a DSA signing operation."""
    message: str | bytes
    message_hash_hex: str           # Full SHA-256 hex digest
    z: int                          # Truncated integer hash value
    k: int                          # Ephemeral nonce k in [1, q - 1]
    k_inv: int                      # k^-1 mod q
    gk_mod_p: int                   # g^k mod p
    r: int                          # (g^k mod p) mod q
    xr_mod_q: int                   # (x * r) mod q
    z_plus_xr: int                  # (z + x * r)
    s: int                          # (k_inv * (z + x * r)) mod q
    r_formula: str                  # e.g., "r = (g^k mod p) mod q = (64^29 mod 607) mod 101 = 81"
    s_formula: str                  # e.g., "s = (k^-1 * (z + x * r)) mod q = (7^1 * (12 + 42 * 81)) mod 101 = 65"
    attempts: int                   # Number of resampling attempts required
    domain_name: str                # Domain preset name


@dataclass
class DSASignResult:
    """Encapsulates the signature and its educational arithmetic trace."""
    signature: DSASignature
    trace: DSASignTrace


# ---------------------------------------------------------------------------
# Functions to Implement
# ---------------------------------------------------------------------------

def generate_ephemeral_k(q: int, seed_k: int | None = None) -> int:
    """Generates an ephemeral secret nonce k in [1, q - 1] uniformly via CSPRNG or seed."""
    ...

def sign_hash_int(
    z: int,
    private_key: DSAPrivateKey,
    seed_k: int | None = None,
    max_attempts: int = 100,
    message_repr: str | bytes = "<hash-input>"
) -> DSASignResult:
    """Signs a pre-hashed/truncated integer digest z with FIPS 186-4 resampling."""
    ...

def sign_message(
    message: str | bytes,
    private_key: DSAPrivateKey,
    seed_k: int | None = None,
    max_attempts: int = 100
) -> DSASignResult:
    """Computes SHA-256, truncates to bit_length(q), and generates DSA signature (r, s)."""
    ...
```

## 4. Acceptance Criteria
1. SHA-256 hash truncation adheres strictly to FIPS 186-4 (leftmost $N = \min(\text{bit\_length}(q), 256)$ bits).
2. Ephemeral secret $k \in [1, q - 1]$ generated with cryptographically secure randomness via `secrets.randbelow(q - 1) + 1`.
3. If $r == 0$ or $s == 0$, the algorithm resamples $k$ until $0 < r < q$ and $0 < s < q$.
4. Deterministic `seed_k` parameter allows exact CAVP test vector reproduction and predictable pedagogical traces.
5. All intermediate values and human-readable LaTeX/formula strings are recorded in `DSASignTrace`.
