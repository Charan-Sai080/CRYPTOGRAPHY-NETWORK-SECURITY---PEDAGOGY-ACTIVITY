# Context Packet 1.3: Miller-Rabin Primality Testing

## 1. Goal
Implement the Miller-Rabin primality test in pure Python supporting both deterministic testing for 64-bit integers and cryptographically randomized rounds for arbitrary-size integers. The implementation must decompose $n - 1 = 2^s \cdot d$ ($d$ odd), maintain an audit log of each witness round and squaring chain, and reliably detect composite Carmichael numbers (Fermat pseudoprimes).

## 2. Allowed Files
* `backend/core/number_theory.py`
* `backend/tests/test_number_theory.py`

## 3. Signatures & Contracts

### Constants & Dataclasses
```python
DETERMINISTIC_BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

@dataclass
class MillerRabinRound:
    round_index: int
    base_a: int
    d: int
    s: int
    x_init: int
    passed: bool
    reason: str
    chain: list[int] = field(default_factory=list)

@dataclass
class PrimalityResult:
    n: int
    is_prime: bool
    method: str
    d: int = 0
    s: int = 0
    rounds_executed: int = 0
    rounds: list[MillerRabinRound] = field(default_factory=list)
    confidence: float = 0.0
    summary: str = ""
```

### Functions
```python
def is_prime(n: int, k: int = 40) -> PrimalityResult:
    """Tests if n is prime using the Miller-Rabin probabilistic or deterministic primality test.
    Decomposes n - 1 = 2^s * d where d is odd.
    Returns complete step trace for every witness round.
    """
```

## 4. Acceptance Criteria
1. **Factorization of $n - 1$**: Correctly extracts powers of 2 such that $n - 1 = 2^s \cdot d$ with $d$ odd.
2. **Deterministic Threshold**:
   - For $n < 3,825,123,056,546,413,051$ ($\approx 2^{61.7}$), test using `DETERMINISTIC_BASES` filtered by $b < n$.
   - For larger $n$, sample $k$ distinct random bases in range $[2, n - 2]$ using `secrets.randbelow`.
3. **Witness Chain Verification**:
   - Computes $x_0 = a^d \bmod n$. If $x_0 \in \{1, n - 1\}$, the round passes.
   - Otherwise, repeatedly squares $x_{j+1} = x_j^2 \bmod n$ for $r \in [1, s - 1]$. If any $x_{j+1} = n - 1$, the round passes.
   - If the chain concludes without reaching $n - 1$, base $a$ is a definitive witness to compositeness; testing halts immediately and returns `is_prime = False`.
4. **Carmichael Number Detection**: Must classify all known Carmichael numbers (e.g. 561, 1105, 1729, 2465, 2821) as composite.
5. **Confidence Calculation**: Returns `confidence = 1.0` if proven composite or evaluated with deterministic bases; otherwise returns $1.0 - (0.25)^{\text{rounds\_executed}}$.
6. **Unit Test Suite**: Covered by `TestMillerRabinPrimality` in `backend/tests/test_number_theory.py`.

## 5. Edge Cases
* **Boundary Integers ($n \le 1$)**: Returns `is_prime = False`, `method = "Trivial boundary check"`.
* **Primes 2 and 3**: Returns `is_prime = True`, `method = "Trivial boundary check"`.
* **Even Integers $> 2$**: Returns `is_prime = False`, `method = "Trivial parity check"` without running witness rounds.
* **Carmichael Pseudoprimes**: Pseudoprimes where $a^{n-1} \equiv 1 \pmod n$ for all $\gcd(a, n) = 1$ fail the intermediate non-trivial square root check.
* **Large Mersenne Primes**: Correctly validates primes such as $M_{31} = 2^{31} - 1 = 2,147,483,647$.
* **Base Filter**: Ensures all tested witness bases satisfy $2 \le a \le n - 2$.
