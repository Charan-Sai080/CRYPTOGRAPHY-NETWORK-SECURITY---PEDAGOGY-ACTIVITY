# Context Packet 5.1: FIPS 186-4 Domain Parameter & Key Pair Generation Engine

## 1. Goal
Implement the Domain Parameter Management, Subgroup Generator Derivation, Domain Preset Registry, Dynamic DSA Domain Generation, and Cryptographically Secure Key Pair Generation Engine for the Digital Signature Algorithm (DSA) in `backend/core/dsa.py` in pure Python 3.12+.

The implementation must provide:
1. Strict mathematical validation of domain parameters $(p, q, g)$:
   - Prime modulus $p$ and prime divisor $q$ such that $q \mid (p - 1)$.
   - Subgroup generator $g = h^{(p - 1)/q} \pmod p > 1$, where $1 < h < p - 1$, guaranteeing $g^q \equiv 1 \pmod p$.
2. Pre-verified Domain Presets Catalog:
   - `fips_186_4_1024_160`: Authenticated NIST CAVP 1024-bit modulus $p$ and 160-bit subgroup prime $q$.
   - `educational_10`: Small prime group ($p = 607, q = 101, g = 64$) for instant visual calculations.
   - `educational_16`: 16-bit modulus group ($p = 34439, q = 257, g = 31028$).
   - `educational_24`: 24-bit modulus group ($p = 9044107, q = 65537, g = 5759125$).
3. Generator Derivation Utility (`derive_generator(p: int, q: int, h: int) -> int`):
   - Computes $g = h^{(p - 1)/q} \pmod p$.
   - Validates that $1 < h < p - 1$ and $g > 1$.
4. Dynamic DSA Domain Generator (`generate_dsa_domain(p_bits: int, q_bits: int) -> tuple[DSADomainParams, list[str]]`):
   - Generates a random prime $q$ of $q\_bits$ bit length.
   - Iteratively searches for multiplier $k$ such that $p = k \cdot q + 1$ is a prime of $p\_bits$ bit length.
   - Finds an integer $h \in [2, p - 2]$ yielding $g = h^{(p - 1)/q} \pmod p > 1$.
   - Emits step-by-step generation logs for educational insight.
5. Structured Key Models and Generation:
   - Data models: `DSADomainParams`, `DSAPublicKey`, `DSAPrivateKey`, `DSAKeyPair`.
   - Private key generation: $x \in [1, q - 1]$ chosen uniformly at random using CSPRNG (`secrets.randbelow(q - 1) + 1`), with optional deterministic `seed_x` support for unit testing and visual pedagogy.
   - Public key computation: $y = g^x \pmod p$.
   - Key verification routine `verify_key_pair(key_pair: DSAKeyPair) -> bool` validating $y == \text{pow}(g, x, p)$ and boundary constraints $1 \le x < q$, $1 < y < p$.
6. Domain-specific exception hierarchy:
   - `DSAError(Exception)`: Root exception.
   - `InvalidDomainParametersError(DSAError)`: Raised when $(p, q, g)$ are mathematically inconsistent or invalid.
   - `InvalidKeyError(DSAError)`: Raised on out-of-bounds keys or public/private key mismatches.

## 2. Allowed Files
* `backend/core/dsa.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any

from backend.core.number_theory import is_prime, mod_pow


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DSAError(Exception):
    """Base exception for all DSA cryptographic operations."""
    pass


class InvalidDomainParametersError(DSAError):
    """Raised when DSA domain parameters (p, q, g) are mathematically invalid."""
    pass


class InvalidKeyError(DSAError):
    """Raised when a DSA public or private key is malformed or out of bounds."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DSADomainParams:
    """Represents public DSA cyclic subgroup domain parameters (p, q, g)."""
    p: int                          # Prime modulus p
    q: int                          # Prime subprime divisor q (order of subgroup)
    g: int                          # Generator g of order q in Z_p*
    name: str = "Custom Domain"     # Descriptive identifier
    p_bits: int = field(init=False) # Bit length of p
    q_bits: int = field(init=False) # Bit length of q

    def __post_init__(self) -> None:
        object.__setattr__(self, "p_bits", self.p.bit_length())
        object.__setattr__(self, "q_bits", self.q.bit_length())
        if not isinstance(self.p, int) or self.p <= 2:
            raise InvalidDomainParametersError(f"Modulus p must be an integer > 2, got {self.p}")
        if not isinstance(self.q, int) or self.q <= 1:
            raise InvalidDomainParametersError(f"Subgroup divisor q must be an integer > 1, got {self.q}")
        if (self.p - 1) % self.q != 0:
            raise InvalidDomainParametersError(f"Subgroup order q ({self.q}) must divide p - 1 ({self.p - 1})")
        if not isinstance(self.g, int) or not (1 < self.g < self.p):
            raise InvalidDomainParametersError(
                f"Generator g must be in range [2, p - 1] ([2, {self.p - 1}]), got {self.g}"
            )


@dataclass(frozen=True)
class DSAPublicKey:
    """DSA public key component (p, q, g, y)."""
    p: int
    q: int
    g: int
    y: int                          # y = g^x mod p

    def __post_init__(self) -> None:
        if not (1 < self.y < self.p):
            raise InvalidKeyError(f"Public key y must satisfy 1 < y < p, got {self.y}")


@dataclass(frozen=True)
class DSAPrivateKey:
    """DSA private key component (p, q, g, x)."""
    p: int
    q: int
    g: int
    x: int                          # x in [1, q - 1]

    def __post_init__(self) -> None:
        if not (1 <= self.x < self.q):
            raise InvalidKeyError(f"Private key x must satisfy 1 <= x < q, got {self.x}")


@dataclass(frozen=True)
class DSAKeyPair:
    """Encapsulates a matched DSA keypair with domain metadata."""
    public_key: DSAPublicKey
    private_key: DSAPrivateKey
    domain_params: DSADomainParams


# ---------------------------------------------------------------------------
# Pre-Verified Domain Presets
# ---------------------------------------------------------------------------

FIPS_186_4_1024_160_MODULUS = int(
    "A8F9CD201E5E35D892F85F80E4DB2599A5676A3B1D4F190330ED3256B26D0E80"
    "A0E49A8FFFAAAD2A24F472D2573241D4D6D6C7480C80B4C67BB4479C15ADA7EA"
    "8424D2502FA01472E760241713DAB025AE1B02E1703A1435F62DDF4EE4C1B664"
    "066EB22F2E3BF28BB70A2A76E4FD5EBE2D1229681B5B06439AC9C7E9D8BDE283",
    16
)
FIPS_186_4_1024_160_DIVISOR = int("F85F0F83AC4DF7EA0CDF8F469BFEEAEA14156495", 16)
FIPS_186_4_1024_160_GENERATOR = int(
    "2B3152FF6C62F14622B8F48E59F8AF46883B38E79B8C74DEEAE9DF131F8B856E"
    "3AD6C8455DAB87CC0DA8AC973417CE4F7878557D6CDF40B35B4A0CA3EB310C6A"
    "95D68CE284AD4E25EA28591611EE08B8444BD64B25F3F7C572410DDFB39CC728"
    "B9C936F85F419129869929CDB909A6A3A99BBE089216368171BD0BA81DE4FE33",
    16
)

DSA_PRESETS: dict[str, DSADomainParams] = {
    "fips_186_4_1024_160": DSADomainParams(
        p=FIPS_186_4_1024_160_MODULUS,
        q=FIPS_186_4_1024_160_DIVISOR,
        g=FIPS_186_4_1024_160_GENERATOR,
        name="FIPS 186-4 Standard 1024/160-bit (NIST CAVP)"
    ),
    "educational_10": DSADomainParams(
        p=607,
        q=101,
        g=64,
        name="Educational 10-bit Group (p=607, q=101, g=64)"
    ),
    "educational_16": DSADomainParams(
        p=34439,
        q=257,
        g=31028,
        name="Educational 16-bit Group (p=34439, q=257, g=31028)"
    ),
    "educational_24": DSADomainParams(
        p=9044107,
        q=65537,
        g=5759125,
        name="Educational 24-bit Group (p=9044107, q=65537, g=5759125)"
    ),
}


# ---------------------------------------------------------------------------
# Functions to Implement
# ---------------------------------------------------------------------------

def derive_generator(p: int, q: int, h: int) -> int:
    """Derives a subgroup generator g = h^((p - 1)/q) mod p."""
    ...

def verify_domain_params(domain: DSADomainParams) -> bool:
    """Verifies that p and q are prime, q | (p - 1), 1 < g < p, and g^q mod p == 1."""
    ...

def generate_dsa_domain(p_bits: int = 16, q_bits: int = 8) -> tuple[DSADomainParams, list[str]]:
    """Generates dynamic educational DSA domain parameters (p, q, g)."""
    ...

def generate_key_pair(domain: DSADomainParams, seed_x: int | None = None) -> DSAKeyPair:
    """Generates a DSA key pair (public_key, private_key) using CSPRNG or deterministic seed."""
    ...

def verify_key_pair(key_pair: DSAKeyPair) -> bool:
    """Verifies that private key x in [1, q - 1] and public key y == g^x mod p."""
    ...

def get_dsa_preset(name: str) -> DSADomainParams:
    """Retrieves a pre-verified DSA domain preset by name."""
    ...

def list_dsa_presets() -> list[DSADomainParams]:
    """Lists all available pre-verified DSA domain presets."""
    ...
```

## 4. Acceptance Criteria
1. Full parameter checking in `__post_init__` and `verify_domain_params`.
2. Generator $g$ verification ensuring order is exactly $q$ via $\text{pow}(g, q, p) == 1$ and $g > 1$.
3. Key generation securely draws $x \in [1, q - 1]$ via CSPRNG `secrets.randbelow(q - 1) + 1`.
4. Deterministic `seed_x` option allows exact unit testing and predictable pedagogical visualization.
5. All presets are valid and pre-tested.
