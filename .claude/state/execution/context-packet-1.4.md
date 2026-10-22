# Context Packet 1.4: Prime Factorization, Primitive Root Discovery, and Safe Prime Generation

## 1. Goal
Implement integer prime factorization, primitive root discovery for cyclic multiplicative groups $\mathbb{Z}_p^*$, and Sophie Germain safe prime generation ($p = 2q + 1$ with $p, q$ both prime) in pure Python. Provide structured verification traces showing subgroup tests for all prime factors of $\phi(p)$.

## 2. Allowed Files
* `backend/core/number_theory.py`
* `backend/tests/test_number_theory.py`

## 3. Signatures & Contracts

### Dataclasses
```python
@dataclass
class CandidateTest:
    candidate: int
    is_primitive: bool
    checks: list[dict[str, Any]]

@dataclass
class PrimitiveRootResult:
    p: int
    phi: int
    prime_factors_phi: list[int]
    primitive_root: int | None
    candidates_tested: list[CandidateTest] = field(default_factory=list)
    explanation: str = ""
```

### Functions
```python
def distinct_prime_factors(n: int) -> list[int]:
    """Returns the sorted list of distinct prime factors of integer n."""

def find_primitive_root(p: int, max_candidates: int = 50) -> PrimitiveRootResult:
    """Finds a primitive root modulo prime p with complete verification step logs.
    For prime p, the order of Z_p* is phi(p) = p - 1.
    An element g is a primitive root iff for every prime factor q of p - 1:
        g^((p - 1)/q) != 1 (mod p)
    """

def generate_safe_prime(bits: int) -> tuple[int, int, list[str]]:
    """Generates a safe prime p = 2q + 1 where both p and q are prime.
    Returns (p, q, trace_logs).
    """
```

## 4. Acceptance Criteria
1. **Factorization**: `distinct_prime_factors(n)` efficiently extracts unique prime factors of $|n|$ via trial division up to $\sqrt{|n|}$, returning a sorted list with no duplicates.
2. **Primitive Root Verification**:
   - For prime $p$, $\phi(p) = p - 1$. Factorize $\phi(p) = \prod q_j^{e_j}$.
   - For each candidate generator $g \in [2, \min(p, 2 + \text{max\_candidates}))$, test whether $g^{\phi(p)/q_j} \equiv 1 \pmod p$ for any prime factor $q_j$.
   - If for all $q_j$, $g^{\phi(p)/q_j} \not\equiv 1 \pmod p$, then $g$ is a primitive root generating the full multiplicative group $\mathbb{Z}_p^*$.
   - Captures each evaluated candidate, exponent, intermediate power, and pass/fail status in `CandidateTest`.
3. **Cyclic Group Order Guarantee**: The identified primitive root $g$ satisfies $\operatorname{ord}(g) = p - 1$, generating all elements $\{g^1, g^2, \dots, g^{p-1}\} \pmod p = \{1, 2, \dots, p - 1\}$.
4. **Safe Prime Generation**:
   - Generates random odd candidate $q$ of bit-length $bits - 1$ using `secrets.randbits`.
   - Sets MSB and LSB to guarantee exact bit-length and odd parity: `q = secrets.randbits(bits - 1) | (1 << (bits - 2)) | 1`.
   - Validates that $q$ is prime using Miller-Rabin ($k = 25$).
   - Constructs $p = 2q + 1$ and validates that $p$ is prime using Miller-Rabin ($k = 25$).
   - Returns $(p, q, \text{logs})$ with search attempt metrics.
5. **Unit Test Suite**: Covered by `TestPrimeFactorizationAndPrimitiveRoot` and `TestSafePrimeGenerator` in `backend/tests/test_number_theory.py`.

## 5. Edge Cases
* **Factorization Inputs**: $n \le 1$ returns `[]`. Handles powers of two, composite numbers with large prime factors, and pure primes.
* **Primitive Root Input Validation**: $p \le 1$ raises `ValueError("p must be a prime > 1")`.
* **Candidate Budget Exhaustion**: If no generator found within `max_candidates`, sets `primitive_root = None` with descriptive explanation without crashing.
* **Safe Prime Minimum Bits**: $bits < 4$ raises `ValueError("Bits must be at least 4.")`.
* **Small Prime Validation**: Correctly finds known primitive roots for small primes (e.g. $p=7 \to 3$, $p=11 \to 2$, $p=13 \to 2$, $p=17 \to 3$, $p=19 \to 2$, $p=23 \to 5$).
