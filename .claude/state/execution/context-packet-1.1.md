# Context Packet 1.1: Extended Euclidean Algorithm (EEA) & Modular Multiplicative Inverse

## 1. Goal
Implement the Extended Euclidean Algorithm (EEA) and Modular Multiplicative Inverse in pure Python. The implementation must produce an exhaustive, step-by-step tabular trace of quotients, remainders, and Bezout coefficients ($x, y$ such that $a \cdot x + b \cdot y = \gcd(a, b)$) for educational display, and provide graceful non-coprime error handling for modular inversion.

## 2. Allowed Files
* `backend/core/number_theory.py`
* `backend/tests/test_number_theory.py`

## 3. Signatures & Contracts

### Dataclasses
```python
@dataclass
class EEAStep:
    step: int
    q: int
    r: int
    s: int
    t: int
    equation: str

@dataclass
class EEAResult:
    a: int
    b: int
    gcd: int
    x: int  # Bezout coefficient for a
    y: int  # Bezout coefficient for b
    steps: list[EEAStep] = field(default_factory=list)
    identity_verified: bool = False
    formula: str = ""

@dataclass
class ModInverseResult:
    a: int
    m: int
    inverse: int | None
    is_coprime: bool
    gcd: int
    eea_result: EEAResult
    explanation: str
    verification: str
```

### Functions
```python
def extended_gcd(a: int, b: int) -> EEAResult:
    """Computes gcd(a, b) and Bezout coefficients (x, y) such that:
        a * x + b * y = gcd(a, b)
    Maintains a full tabular step trace for pedagogy.
    """

def mod_inverse(a: int, m: int) -> ModInverseResult:
    """Calculates the modular multiplicative inverse a^(-1) mod m such that:
        (a * a^(-1)) = 1 (mod m)
    Requires gcd(a, m) == 1. Returns a complete pedagogical trace.
    """
```

## 4. Acceptance Criteria
1. **Full Tabular Trace**: `extended_gcd` must capture step 0, step 1, and all iterative reduction steps recording $q = r_{k-2} // r_{k-1}$, $r = r_{k-2} \bmod r_{k-1}$, and updated Bezout values $s_{k} = s_{k-2} - q \cdot s_{k-1}$, $t_{k} = t_{k-2} - q \cdot t_{k-1}$.
2. **Bezout Identity Verification**: Validates that $a \cdot x + b \cdot y == \gcd(a, b)$ and sets `identity_verified = True`.
3. **Modular Inversion**: When $\gcd(a, m) = 1$, calculates $inv = x \bmod m$ and verifies $(a \cdot inv) \bmod m == 1$.
4. **Non-Coprime Handling**: When $\gcd(a, m) \ne 1$, returns `inverse = None`, `is_coprime = False`, `gcd = eea.gcd`, and provides an explanatory string stating that no inverse exists in $\mathbb{Z}_m$.
5. **Unit Test Suite**: Covered by unit test classes `TestExtendedGCD` and `TestModInverse` in `backend/tests/test_number_theory.py`.

## 5. Edge Cases
* **Zero Inputs**: $\gcd(0, b) = |b|$, $\gcd(a, 0) = |a|$, and $\gcd(0, 0) = 0$.
* **Negative Numbers**: Negative values for $a$ or $b$ must be handled correctly by adjusting signs of Bezout coefficients while preserving $\gcd > 0$ and $a \cdot x + b \cdot y = \gcd(a, b)$.
* **Degenerate Ring ($m = 1$)**: Modulo 1 ring where $x \bmod 1 = 0$; returns `inverse = 0`, `is_coprime = True`.
* **Invalid Modulus ($m \le 0$)**: Raises `ValueError("Modulus m must be a positive integer greater than 0.")`.
* **Negative $a$ in `mod_inverse`**: Normalizes $a \bmod m$ before running inversion.
* **Large Integers**: Handles multi-word integers (arbitrary precision) without overflow.
