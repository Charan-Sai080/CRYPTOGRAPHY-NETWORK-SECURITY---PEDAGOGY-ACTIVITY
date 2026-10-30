# Context Packet 5.4: Ephemeral Nonce k Reuse Exploit (Sony PS3 Exploit)

## 1. Goal
Implement the catastrophic Ephemeral Nonce $k$ Reuse Cryptanalytic Exploit for the Digital Signature Algorithm (DSA) in `backend/core/dsa.py` in pure Python 3.12+.

The module must provide:
1. **Mathematical Exploit Engine**:
   - Detect identical ephemeral nonces across distinct messages:
     Given two signatures $(r_1, s_1)$ and $(r_2, s_2)$ where $r_1 == r_2$ and $z_1 \not\equiv z_2 \pmod q$.
   - Recover ephemeral nonce $k$:
     $$s_1 - s_2 \equiv k^{-1}(z_1 - z_2) \pmod q$$
     $$k \equiv (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$$
   - Instant Private Key Extraction:
     $$x \equiv (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$$
   - Verification of recovered private key:
     Confirm $y_{\text{recovered}} = g^{x_{\text{recovered}}} \pmod p == y_{\text{public}}$.
2. **Pedagogical and Historical Documentation**:
   - Provide a complete step-by-step arithmetic trace documenting the recovery of $k$ and $x$.
   - Include a comprehensive LaTeX/markdown explanation of the 2010 PlayStation 3 fail0verflow exploit, detailing how hardcoded/static nonces completely compromised Sony's root code-signing key and allowed arbitrary homebrew execution on the PS3 console.

## 2. Allowed Files
* `backend/core/dsa.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.dsa import (
    DSAError,
    DSAPublicKey,
    DSASignature,
)
from backend.core.number_theory import (
    mod_inverse,
    mod_pow,
    sha256_digest_int,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DSACryptanalysisError(DSAError):
    """Raised when cryptanalytic exploit fails or prerequisites are not met."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class DSANonceReuseExploitResult:
    """Comprehensive diagnostic record of private key recovery via nonce reuse."""
    m1: str | bytes
    m2: str | bytes
    z1: int                          # Truncated hash integer for message 1
    z2: int                          # Truncated hash integer for message 2
    shared_r: int                    # Shared r = r1 == r2
    s1: int                          # Signature component s1
    s2: int                          # Signature component s2
    recovered_k: int                 # Recovered ephemeral nonce k
    recovered_x: int                 # Extracted private key x
    is_key_recovered: bool           # True if algebraic derivation succeeded
    public_key_verified: bool        # True if g^x mod p == public_key.y
    step_trace: list[str] = field(default_factory=list)
    algebraic_proof: str = ""
    historical_context: str = ""


# ---------------------------------------------------------------------------
# Functions to Implement
# ---------------------------------------------------------------------------

def exploit_nonce_reuse_from_hashes(
    sig1: DSASignature,
    sig2: DSASignature,
    z1: int,
    z2: int,
    public_key: DSAPublicKey,
    m1_repr: str | bytes = "<hash-1>",
    m2_repr: str | bytes = "<hash-2>"
) -> DSANonceReuseExploitResult:
    """Recovers private key x from two signatures generated with identical nonce k."""
    ...

def exploit_nonce_reuse(
    sig1: DSASignature,
    sig2: DSASignature,
    m1: str | bytes,
    m2: str | bytes,
    public_key: DSAPublicKey
) -> DSANonceReuseExploitResult:
    """Hashes messages m1 and m2, extracts nonce k, and instantly recovers private key x."""
    ...
```

## 4. Acceptance Criteria
1. Rejects exploit attempts if $r_1 \neq r_2$ or if $z_1 \equiv z_2 \pmod q$ (with informative `DSACryptanalysisError`).
2. Exact algebraic recovery of $k \equiv (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$.
3. Exact algebraic recovery of $x \equiv (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$.
4. Validates recovered $x$ against public key $y = g^x \pmod p$ returning `public_key_verified = True`.
5. Emits detailed pedagogical logs, formulas, and historical notes on the Sony PS3 vulnerability.
