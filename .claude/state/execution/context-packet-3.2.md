# Context Packet 3.2: Hull-Dobell Theorem Validator & Floyd's Cycle-Finding Period Analyzer

## 1. Goal
Implement the Hull-Dobell Theorem Validator, Floyd's Cycle-Finding Algorithm (Tortoise and Hare), and Multiplicative LCG Period Analyzer in `backend/core/lcg.py` in pure Python 3.12+.

The implementation must provide:
1. Exact mathematical validation of the Hull-Dobell Theorem (1962), which provides necessary and sufficient conditions for an LCG to have full period length $m$ for all seeds.
2. Prime factor decomposition of modulus $m$ using `distinct_prime_factors` from `backend.core.number_theory`.
3. Floyd's cycle-finding (tortoise-and-hare) algorithm to determine the exact cycle period length $\lambda$ (lambda) and cycle start index $\mu$ (mu) in $O(\lambda + \mu)$ time and $O(1)$ auxiliary space, bounded by a configurable iteration cap.
4. Period analysis for Multiplicative LCGs ($c = 0$, Lehmer RNGs) where full period $m$ is impossible, analyzing the theoretical maximum period for prime moduli ($m - 1$ when $a$ is a primitive root) and power-of-two moduli ($m/4$ when $a \equiv 3, 5 \pmod 8$ and seed is odd).

## 2. Allowed Files
* `backend/core/lcg.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any
from backend.core.number_theory import distinct_prime_factors, extended_gcd, is_prime


@dataclass
class HullDobellCondition:
    condition_number: int          # 1, 2, or 3
    title: str                     # Short descriptive title
    passed: bool                   # True if criterion is satisfied
    mathematical_statement: str    # e.g., "gcd(c, m) = gcd(1, 16) = 1"
    details: str                   # Detailed analysis of this specific condition


@dataclass
class HullDobellResult:
    m: int
    a: int
    c: int
    is_full_period: bool           # True iff ALL 3 conditions pass
    conditions: list[HullDobellCondition]
    prime_factors_m: list[int]     # Distinct prime factors of m
    summary: str
    pedagogical_notes: str


@dataclass
class FloydStepTrace:
    iteration: int
    tortoise_index: int
    tortoise_val: int
    hare_index: int
    hare_val: int


@dataclass
class CycleDetectionResult:
    m: int
    a: int
    c: int
    seed: int
    period_length: int              # lambda: period length of the repeating loop
    cycle_start_index: int          # mu: 0-indexed position where cycle begins
    is_full_period: bool            # True if period_length == m and cycle_start_index == 0
    meeting_iteration: int          # Iteration when tortoise and hare first collided
    sample_cycle_values: list[int]  # First min(period_length, 25) values of cycle
    traces: list[FloydStepTrace]    # Step traces during initial tortoise-and-hare phase
    iterations_run: int             # Total steps executed during detection
    explanation: str


@dataclass
class MultiplicativeLCGAnalysis:
    m: int
    a: int
    seed: int
    is_modulus_prime: bool
    is_power_of_two: bool
    power_of_two_exponent: int | None
    theoretical_max_period: int
    actual_period: int
    achieves_max_period: bool
    is_primitive_root: bool | None
    is_seed_coprime: bool
    explanation: str


def check_hull_dobell(m: int, a: int, c: int) -> HullDobellResult:
    """Validates the three necessary and sufficient conditions of the Hull-Dobell Theorem (1962).

    An LCG has full period m for all seeds iff:
      1. gcd(c, m) == 1 (c and m are coprime)
      2. Every prime factor of m divides (a - 1), i.e., for all prime q | m, (a - 1) % q == 0
      3. If 4 divides m, then 4 divides (a - 1), i.e., if m % 4 == 0, then (a - 1) % 4 == 0
    """
    ...


def detect_cycle_floyd(
    m: int,
    a: int,
    c: int,
    seed: int,
    max_iterations: int = 1_000_000,
    trace_steps: int = 25,
) -> CycleDetectionResult:
    """Applies Floyd's cycle-finding (tortoise-and-hare) algorithm to determine

    period length (lambda) and cycle start (mu) for an LCG sequence.
    Safe against infinite loops with max_iterations.
    """
    ...


def analyze_multiplicative_lcg(
    m: int,
    a: int,
    seed: int,
    max_iterations: int = 100_000,
) -> MultiplicativeLCGAnalysis:
    """Analyzes cycle structure and maximum period of a Multiplicative LCG (c = 0).

    When c = 0, state 0 is absorbing, so full period m is impossible.
    - If m is prime, max period is m - 1 (achieved iff a is a primitive root mod m).
    - If m = 2^k (k >= 3), max period is m / 4 (achieved iff a % 8 in (3, 5) and seed is odd).
    """
    ...
```

## 4. Algorithmic Specifications

### Hull-Dobell Theorem
Given recurrence $X_{n+1} = (a \cdot X_n + c) \pmod m$:
1. **Condition 1: Coprimality of $c$ and $m$**
   - Compute $g = \gcd(c, m)$ (via `math.gcd` or `extended_gcd`).
   - Condition passes iff $g == 1$.
   - If $c == 0$, $g = m > 1$, which immediately fails.
2. **Condition 2: Prime factors of $m$ divide $a - 1$**
   - Find distinct prime factors of $m$: $Q = \text{distinct\_prime\_factors}(m)$.
   - For every prime $q \in Q$, verify $(a - 1) \pmod q == 0$.
   - Condition passes iff all $q$ divide $a - 1$.
3. **Condition 3: If $4 \mid m$, then $4 \mid (a - 1)$**
   - If $m \pmod 4 == 0$, verify $(a - 1) \pmod 4 == 0$.
   - If $m \pmod 4 \neq 0$, the condition is vacuously satisfied (passed = True).

### Floyd's Cycle-Finding Algorithm
Let $f(x) = (a \cdot x + c) \pmod m$.
1. **Phase 1: Finding meeting point**
   - Initialize $\text{tortoise} = f(\text{seed})$, $\text{hare} = f(f(\text{seed}))$, $\text{steps} = 1$.
   - Loop while $\text{tortoise} \neq \text{hare}$:
     - $\text{tortoise} = f(\text{tortoise})$
     - $\text{hare} = f(f(\text{hare}))$
     - $\text{steps} += 1$
     - If $\text{steps} \ge \text{max\_iterations}$, raise `TimeoutError` or return truncated analysis.
   - Record first `min(steps, trace_steps)` iterations in `traces`.
2. **Phase 2: Finding cycle start index $\mu$**
   - Reset $\text{tortoise} = \text{seed}$.
   - While $\text{tortoise} \neq \text{hare}$:
     - $\text{tortoise} = f(\text{tortoise})$
     - $\text{hare} = f(\text{hare})$
     - $\mu += 1$
3. **Phase 3: Finding period length $\lambda$**
   - $\text{hare} = f(\text{tortoise})$
   - $\lambda = 1$
   - While $\text{tortoise} \neq \text{hare}$:
     - $\text{hare} = f(\text{hare})$
     - $\lambda += 1$
4. **Extraction**:
   - Starting from state at $\mu$, record up to 25 cycle values.

### Multiplicative LCG Period Analysis ($c = 0$)
1. Check if $m$ is prime using `is_prime(m)`.
2. Check if $m$ is a power of 2: $(m > 0)$ and $(m \& (m - 1)) == 0$. Compute $k = m.\text{bit\_length}() - 1$.
3. Check coprimality of seed: $\gcd(\text{seed}, m) == 1$.
4. Determine theoretical maximum period:
   - If prime $m$: theoretical max is $m - 1$. If $m$ is small enough (or known prime like Mersenne 31), check if $a$ is primitive root via `find_primitive_root(m)` or by checking $a^{(m-1)/q} \not\equiv 1 \pmod m$ for prime factors $q$ of $m - 1$.
   - If $m = 2^k$ ($k \ge 3$): theoretical max is $m // 4$. It is achieved iff $a \pmod 8 \in \{3, 5\}$ and seed is odd.
5. Compute actual period using Floyd's cycle detection.
