# Architecture Specification: Milestone 1 Number Theory Engine

## Module: `backend/core/number_theory.py`

### 1. Architectural Intent
The number theory engine provides mathematically deterministic, high-precision primitives required by all 4 pedagogical pillars:
* One-Time Pad: Bit/byte transformations and entropy measurements.
* LCG: Greatest Common Divisor ($\gcd$), prime factorization for Hull-Dobell theorem.
* ElGamal: Prime generation, Miller-Rabin test, primitive roots, fast modular exponentiation, modular multiplicative inverse.
* DSA: Domain parameter generation ($(p, q, g)$), subgroup validation, modular inversion, SHA-256 truncation.

### 2. Design Contracts & Signatures

#### A. Extended Euclidean Algorithm
```python
class EEAStep:
    step: int
    q: int
    r: int
    s: int
    t: int
    equation: str

class EEAResult:
    gcd: int
    x: int  # Bezout coefficient for a
    y: int  # Bezout coefficient for b
    steps: list[EEAStep]

def extended_gcd(a: int, b: int) -> EEAResult:
    """Computes gcd(a, b) and Bezout coefficients (x, y) such that a*x + b*y = gcd(a, b),
    with full tabular step-by-step trace."""
```

#### B. Modular Multiplicative Inverse
```python
class ModInverseResult:
    a: int
    m: int
    inverse: int | None
    is_coprime: bool
    gcd: int
    steps: list[str]
    explanation: str

def mod_inverse(a: int, m: int) -> ModInverseResult:
    """Computes a^(-1) mod m using extended Euclidean algorithm with explanation."""
```

#### C. Modular Exponentiation (Square-and-Multiply)
```python
class ModPowStep:
    bit_index: int
    bit_value: int
    operation: str  # 'Square' or 'Square and Multiply'
    intermediate_value: int
    equation: str

class ModPowResult:
    base: int
    exponent: int
    modulus: int
    result: int
    binary_exponent: str
    steps: list[ModPowStep]

def mod_pow(base: int, exp: int, mod: int) -> ModPowResult:
    """Computes (base^exp) % mod using binary exponentiation with full step trace."""
```

#### D. Miller-Rabin Primality Test
```python
class MillerRabinRound:
    round_index: int
    base_a: int
    d: int
    s: int
    x0: int
    is_composite: bool
    notes: str

class PrimalityResult:
    n: int
    is_prime: bool
    method: str
    d: int
    s: int
    rounds: list[MillerRabinRound]
    confidence: float

def is_prime(n: int, k: int = 40) -> PrimalityResult:
    """Tests if n is prime using Miller-Rabin algorithm with step trace."""
```

#### E. Safe Prime & Primitive Root Generation
```python
class PrimitiveRootResult:
    p: int
    is_safe_prime: bool
    q: int  # (p - 1) // 2 if safe prime
    candidate: int
    tested_candidates: list[dict]
    is_primitive_root: bool
    explanation: str

def find_primitive_root(p: int) -> PrimitiveRootResult:
    """Finds a primitive root modulo p with step trace."""

def generate_safe_prime(bits: int) -> tuple[int, int, list[str]]:
    """Generates a safe prime p = 2q + 1 where q is also prime."""
```

#### F. Standard MODP Groups (RFC 3526)
```python
RFC_MODP_1536: dict  # Pre-verified RFC 3526 1536-bit MODP Group (p, g)
RFC_MODP_2048: dict  # Pre-verified RFC 3526 2048-bit MODP Group (p, g)
```

### 3. Error & Edge Case Handling
* Non-integer or negative inputs where non-negative/positive integers are required.
* Modulus $m \le 1$.
* Non-invertible elements ($\gcd(a, m) \ne 1$).
* Primes $p \le 2$ or composite candidates in primitive root search.
