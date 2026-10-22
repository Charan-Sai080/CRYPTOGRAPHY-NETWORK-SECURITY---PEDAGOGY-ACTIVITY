# Context Packet 1.2: Traced Modular Exponentiation using Binary Square-and-Multiply

## 1. Goal
Implement binary Square-and-Multiply modular exponentiation $(base^{exp} \bmod mod)$ in pure Python, providing an exhaustive pedagogical step-by-step trace of every bit operation traversing from Most Significant Bit (MSB) to Least Significant Bit (LSB). The trace must capture the accumulator state before and after each squaring and multiplication operation.

## 2. Allowed Files
* `backend/core/number_theory.py`
* `backend/tests/test_number_theory.py`

## 3. Signatures & Contracts

### Dataclasses
```python
@dataclass
class ModPowStep:
    step_index: int
    bit_index: int
    bit_value: int
    action: str  # "Square" or "Multiply (bit=1)"
    current_acc_before: int
    current_acc_after: int
    formula: str

@dataclass
class ModPowResult:
    base: int
    exponent: int
    modulus: int
    result: int
    binary_exponent: str
    bit_length: int
    steps: list[ModPowStep] = field(default_factory=list)
```

### Functions
```python
def mod_pow(base: int, exp: int, mod: int) -> ModPowResult:
    """Computes (base^exp) % mod using the binary Square-and-Multiply algorithm,
    recording an exhaustive pedagogical trace of each bit operation.
    """
```

## 4. Acceptance Criteria
1. **MSB-to-LSB Traversal**: Formats the exponent as an unpadded binary string `bin(exp)[2:]` and processes bits sequentially from index 0 (MSB) to length - 1 (LSB).
2. **Deterministic Step Sequence**:
   - For every bit $i$, record a **Square** step: $acc_{next} = (acc^2) \bmod mod$.
   - If bit value is 1, immediately follow with a **Multiply (bit=1)** step: $acc_{next} = (acc \cdot (base \bmod mod)) \bmod mod$.
3. **Trace Completeness**: Each step records `step_index`, `bit_index`, `bit_value`, `action`, `current_acc_before`, `current_acc_after`, and descriptive `formula` (e.g. `"(4^2) mod 17 = 16"`).
4. **Correctness**: The final `result` must strictly equal Python's built-in `pow(base, exp, mod)`.
5. **Unit Test Suite**: Covered by unit test class `TestModPow` in `backend/tests/test_number_theory.py` with parametrized base, exponent, and modulus combinations.

## 5. Edge Cases
* **Zero Exponent ($exp = 0$)**: Any non-zero base raised to power 0 is 1; returns `result = 1 % mod`, `binary_exponent = "0"`, `bit_length = 1`, and `steps = []`.
* **Modulus One ($mod = 1$)**: Any integer modulo 1 is 0; returns `result = 0`, `steps = []`.
* **Zero Base ($base = 0$)**: Returns `result = 0` when $exp > 0$.
* **Negative Exponents ($exp < 0$)**: Raises `ValueError("Negative exponents require modular inverse computation; pass non-negative exp.")`.
* **Invalid Modulus ($mod \le 0$)**: Raises `ValueError("Modulus must be positive.")`.
* **Base Exceeding Modulus ($base \ge mod$)**: Base is automatically reduced modulo $mod$ during multiplication steps to prevent unnecessary memory allocations.
* **Large Exponents**: Cryptographic exponent bit lengths (1024, 2048 bits) compute efficiently without intermediate floating-point overflow.
