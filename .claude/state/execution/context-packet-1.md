# Context Packet 1: Milestone 1 Mathematical Core Engine

## 1. Task Goal
Implement the core mathematical number theory engine in pure Python with mandatory pedagogical step tracing for all primitives, and build a comprehensive unit test suite covering normal inputs, edge cases, and known test vectors.

## 2. Allowed Files
* `backend/core/__init__.py`
* `backend/core/number_theory.py`
* `backend/tests/__init__.py`
* `backend/tests/test_number_theory.py`
* `backend/requirements.txt`

## 3. Architecture Excerpts & Requirements
* **Extended Euclidean Algorithm (`extended_gcd(a, b) -> EEAResult`)**:
  Computes $\gcd(a, b)$ and Bezout coefficients $x, y$ such that $a \cdot x + b \cdot y = \gcd(a, b)$.
  Must return full tabular step-by-step trace: step number, quotient $q$, remainder $r$, and updated coefficients.
* **Modular Multiplicative Inverse (`mod_inverse(a, m) -> ModInverseResult`)**:
  Calculates $a^{-1} \pmod m$. Validates $\gcd(a, m) = 1$. Returns detailed trace and explanation.
* **Modular Exponentiation (`mod_pow(base, exp, mod) -> ModPowResult`)**:
  Square-and-Multiply binary exponentiation. Returns binary representation of exponent and per-bit step trace (Square / Square-and-Multiply).
* **Miller-Rabin Primality Test (`is_prime(n, k=40) -> PrimalityResult`)**:
  Decomposition $n - 1 = 2^s \cdot d$. Traces witness rounds with detailed notes.
* **Primitive Root Generator (`find_primitive_root(p) -> PrimitiveRootResult`)**:
  Finds primitive root modulo prime $p$ with testing logs.
* **Safe Prime Generator (`generate_safe_prime(bits) -> (p, q, logs)`)**:
  Generates $p = 2q + 1$ with $p, q$ both prime.
* **Standard MODP Groups**:
  RFC 3526 1536-bit and 2048-bit pre-verified parameters.

## 4. Acceptance Criteria
1. All functions are strictly typed with dataclasses / Pydantic models for results and traces.
2. 100% of the mathematical edge cases pass unit tests:
   - Negative numbers, zero inputs, $m = 1$, non-coprime modular inverse requests.
   - Carmichael numbers and pseudoprimes tested against Miller-Rabin.
   - Identity properties: $(a \cdot a^{-1}) \bmod m == 1$.
   - Square-and-multiply matches Python's native `pow(base, exp, mod)`.
   - Primitive roots verified: $\text{ord}(g) = p - 1$.
3. All unit tests pass using `pytest` executed in Conda env `cns-pedagogy`.
