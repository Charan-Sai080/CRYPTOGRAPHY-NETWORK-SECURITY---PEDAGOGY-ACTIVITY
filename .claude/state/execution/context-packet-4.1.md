# Context Packet 4.1: Domain Parameter & Key Pair Generation Engine

## 1. Goal
Implement the Domain Parameter Management, Primitive Root Verification, Domain Preset Registry, Safe Prime Domain Generation, and Cryptographically Secure Key Pair Generation Engine for the ElGamal Public-Key Cryptosystem in `backend/core/elgamal.py` in pure Python 3.12+.

The implementation must provide:
1. Strict validation of domain parameters $(p, g)$ ensuring $p$ is an odd prime and $g$ is a mathematically valid primitive root / generator of the multiplicative group $\mathbb{Z}_p^*$.
2. Primitive root verification over $\mathbb{Z}_p^*$:
   - For safe primes $p = 2q + 1$, the only prime factors of $p - 1$ are $2$ and $q$. A generator $g \in [2, p - 1]$ is valid iff $g^2 \not\equiv 1 \pmod p$ and $g^q \not\equiv 1 \pmod p$.
   - For general educational primes, test $g^{(p-1)/q_i} \not\equiv 1 \pmod p$ for all distinct prime factors $q_i$ of $p - 1$.
   - For standard RFC MODP groups (e.g. RFC 2409 1024-bit), recognize pre-verified parameters.
3. Pre-verified Domain Presets Catalog:
   - RFC 2409 1024-bit MODP Oakley Group 2 ($g = 2$).
   - Educational 16-bit group ($p = 65537, g = 3$).
   - Educational 20-bit group ($p = 1048583, g = 2$).
   - Educational 24-bit safe prime group ($p = 16777259, g = 2$).
   - Educational 32-bit safe prime group ($p = 4294967311, g = 3$).
4. Dynamic Custom Safe Prime Domain Generator (`generate_safe_prime_domain(bits: int)`):
   - Derives a Sophie Germain safe prime $p = 2q + 1$ using `generate_safe_prime` from `backend.core.number_theory`.
   - Discovers and confirms a primitive root $g \in [2, p - 1]$ satisfying $g^2 \not\equiv 1 \pmod p$ and $g^q \not\equiv 1 \pmod p$.
5. Structured Key Models and Generation:
   - `ElGamalDomainParams`, `ElGamalPublicKey`, `ElGamalPrivateKey`, `ElGamalKeyPair`.
   - Private key generation: $x \in [2, p - 2]$ chosen uniformly at random using CSPRNG (`secrets.randbelow(p - 3) + 2`), with optional deterministic seed support for testing and visual pedagogy.
   - Public key computation: $y = g^x \pmod p$.
   - Key verification routine `verify_key_pair(key_pair)` checking $y == \text{pow}(g, x, p)$ and boundary constraints.
6. Domain-specific exception hierarchy:
   - `ElGamalError(Exception)`: Root exception.
   - `InvalidDomainParametersError(ElGamalError)`: Raised on non-prime modulus, invalid generator, or out-of-bounds parameters.
   - `InvalidKeyError(ElGamalError)`: Raised on out-of-bounds exponents, key mismatch, or corrupted key pairs.

## 2. Allowed Files
* `backend/core/elgamal.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any

from backend.core.number_theory import (
    EDUCATIONAL_MODP_GROUPS,
    RFC_2409_1024_MODP,
    distinct_prime_factors,
    find_primitive_root,
    generate_safe_prime,
    is_prime,
    mod_pow,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ElGamalError(Exception):
    """Base exception for all ElGamal cryptographic operations."""
    pass


class InvalidDomainParametersError(ElGamalError):
    """Raised when domain parameters (p, g) are mathematically invalid."""
    pass


class InvalidKeyError(ElGamalError):
    """Raised when a public or private key is malformed or out of bounds."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ElGamalDomainParams:
    """Represents public ElGamal cyclic group domain parameters (p, g)."""
    p: int                          # Prime modulus p
    g: int                          # Generator g of Z_p*
    name: str = "Custom Domain"     # Descriptive identifier
    bits: int = field(init=False)   # Bit length of p
    q: int | None = None            # Sophie Germain factor if safe prime (p = 2q + 1)

    def __post_init__(self) -> None:
        object.__setattr__(self, "bits", self.p.bit_length())
        if not isinstance(self.p, int) or self.p <= 2:
            raise InvalidDomainParametersError(f"Modulus p must be an integer > 2, got {self.p}")
        if not isinstance(self.g, int) or not (2 <= self.g < self.p):
            raise InvalidDomainParametersError(
                f"Generator g must be in range [2, p - 1] ([2, {self.p - 1}]), got {self.g}"
            )


@dataclass(frozen=True)
class ElGamalPublicKey:
    """Public key component for ElGamal encryption."""
    p: int
    g: int
    y: int                          # y = g^x mod p
    domain_name: str = "Custom Domain"

    def __post_init__(self) -> None:
        if not (2 <= self.y < self.p):
            raise InvalidKeyError(f"Public key y must be in range [2, p - 1] ([2, {self.p - 1}]), got {self.y}")


@dataclass(frozen=True)
class ElGamalPrivateKey:
    """Private key component for ElGamal decryption."""
    p: int
    g: int
    x: int                          # Private exponent x in [2, p - 2]
    domain_name: str = "Custom Domain"

    def __post_init__(self) -> None:
        if not (2 <= self.x <= self.p - 2):
            raise InvalidKeyError(f"Private key x must be in range [2, p - 2] ([2, {self.p - 2}]), got {self.x}")


@dataclass(frozen=True)
class ElGamalKeyPair:
    """Asymmetric key pair container."""
    public_key: ElGamalPublicKey
    private_key: ElGamalPrivateKey
    domain: ElGamalDomainParams


# ---------------------------------------------------------------------------
# Domain Presets Catalog
# ---------------------------------------------------------------------------

DOMAIN_PRESETS: dict[str, ElGamalDomainParams] = {
    "rfc_2409_1024": ElGamalDomainParams(
        p=RFC_2409_1024_MODP["prime"],
        g=RFC_2409_1024_MODP["generator"],
        name="RFC 2409 / 3526 1024-bit MODP Oakley Group 2",
    ),
    "educational_16": ElGamalDomainParams(
        p=65537,
        g=3,
        name="Educational 16-bit Group (Fermat F4 prime)",
    ),
    "educational_20": ElGamalDomainParams(
        p=1048583,
        g=2,
        name="Educational 20-bit Group",
    ),
    "educational_24": ElGamalDomainParams(
        p=16777259,
        g=2,
        name="Educational 24-bit Safe Prime Group",
        q=8388629,
    ),
    "educational_32": ElGamalDomainParams(
        p=4294967311,
        g=3,
        name="Educational 32-bit Safe Prime Group",
        q=2147483655,
    ),
}


# ---------------------------------------------------------------------------
# Functional Interfaces
# ---------------------------------------------------------------------------

def get_domain_preset(preset_key: str) -> ElGamalDomainParams:
    """Retrieves an ElGamal domain preset by its unique key."""
    if preset_key not in DOMAIN_PRESETS:
        raise KeyError(f"Domain preset '{preset_key}' not found. Available presets: {list(DOMAIN_PRESETS.keys())}")
    return DOMAIN_PRESETS[preset_key]


def list_domain_presets() -> list[ElGamalDomainParams]:
    """Returns a list of all registered ElGamal domain presets."""
    return list(DOMAIN_PRESETS.values())


def verify_primitive_root(g: int, p: int, q: int | None = None) -> bool:
    """Verifies whether g is a generator of Z_p*.

    If q is provided such that p = 2q + 1 is a safe prime, verifies:
      1. g^2 mod p != 1
      2. g^q mod p != 1
    Otherwise, computes prime factors of p - 1 and verifies g^((p-1)/f) mod p != 1.
    """
    ...


def generate_safe_prime_domain(bits: int = 16) -> ElGamalDomainParams:
    """Generates a dynamic safe prime domain p = 2q + 1 with confirmed primitive root g."""
    ...


def generate_key_pair(
    domain: ElGamalDomainParams,
    seed_x: int | None = None,
) -> ElGamalKeyPair:
    """Generates an asymmetric ElGamal key pair over the specified domain.

    If seed_x is provided, validates that 2 <= seed_x <= p - 2 and uses it as private key x.
    Otherwise, generates a cryptographically secure random integer x in [2, p - 2] via secrets.randbelow.
    Computes public key y = g^x mod p.
    """
    ...


def verify_key_pair(key_pair: ElGamalKeyPair) -> bool:
    """Validates consistency between public and private keys (y == g^x mod p)."""
    ...
```

## 4. Implementation Details & Pedagogical Requirements
1. **Domain Boundary Constraints**:
   - $p$ must be an odd prime. For $p \le 2^{32}$, verify primality deterministically using `is_prime(p)`.
   - $g$ must be in the range $2 \le g \le p - 1$.
   - Private key $x$ must satisfy $2 \le x \le p - 2$. The extremes $x = 0$ (which yields $y = 1$) and $x = 1$ (which yields $y = g$) are disallowed in robust implementations to prevent trivial discrete logarithm leakage.
2. **Safe Prime Generator Discovery**:
   - When generating custom domains via `generate_safe_prime_domain(bits)`:
     - Use `generate_safe_prime(bits)` to obtain $(p, q, \text{logs})$.
     - Iterate candidate generators starting from $g = 2, 3, 5, 7, \dots$ until $g^2 \not\equiv 1 \pmod p$ and $g^q \not\equiv 1 \pmod p$.
     - Return `ElGamalDomainParams(p=p, g=g, name=f"Custom Safe Prime ({bits}-bit)", q=q)`.
3. **Deterministic Seed Testing**:
   - For educational demonstrations and automated testing, allowing `seed_x: int | None = None` lets users explore fixed scenarios (e.g. textbook examples with small primes like $p=65537, x=12345$).
   - When `seed_x is None`, use `secrets.randbelow(p - 3) + 2` to ensure uniform selection in $[2, p - 2]$.
