# Context Packet 3.3: Statistical Uniformity (Chi-Square), Marsaglia Hyperplane Lattice Analysis, and State Reconstruction

## 1. Goal
Implement Statistical Uniformity Testing (Chi-Square Goodness-of-Fit), Marsaglia Hyperplane Lattice Point Generation, and Algebraic State Reconstruction (Cryptanalytic Cracking) in `backend/core/lcg.py` in pure Python 3.12+.

The implementation must provide:
1. **Chi-Square Goodness-of-Fit Test**: Evaluates whether an LCG output sequence behaves uniformly across $[0.0, 1.0)$, computing bin distributions, $\chi^2$ statistic, degrees of freedom $df$, critical threshold comparison ($\alpha = 0.05, 0.01$), and approximate $p$-value in pure standard library Python.
2. **Marsaglia Hyperplane Lattice Analysis**: Demonstrates George Marsaglia's 1968 foundational result ("Random numbers fall mainly in the planes"), generating 2D consecutive pairs $(X_n, X_{n+1})$, 3D consecutive triplets $(X_n, X_{n+1}, X_{n+2})$, and computing the theoretical maximum hyperplane bound $\lfloor (d! \cdot m)^{1/d} \rfloor$.
3. **Cryptanalytic State Reconstruction & Cracker**: Proves mathematically and practically why LCG is broken for cryptography:
   - Recovers $c$ when $m, a$ are known from 2 consecutive outputs.
   - Recovers $a, c$ when $m$ is known from 3 consecutive outputs via modular inverse.
   - Recovers $m, a, c$ when ALL parameters are unknown from 6–8 consecutive outputs via difference sequences and determinant GCD.
   - Predicts future outputs $X_{n+1}, X_{n+2}, \dots$ and past states $X_{n-1}, X_{n-2}, \dots$.

## 2. Allowed Files
* `backend/core/lcg.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any
from backend.core.number_theory import extended_gcd, mod_inverse


@dataclass
class BinDistribution:
    bin_index: int
    lower_bound: float
    upper_bound: float
    observed_count: int
    expected_count: float
    chi_square_contribution: float


@dataclass
class ChiSquareResult:
    num_samples: int
    num_bins: int
    degrees_of_freedom: int
    chi_square_statistic: float
    critical_value_95: float       # Threshold at alpha = 0.05
    critical_value_99: float       # Threshold at alpha = 0.01
    p_value: float                 # Estimated p-value in [0.0, 1.0]
    is_uniform_hypothesis_accepted: bool  # True if p_value >= 0.05 (cannot reject H0)
    bins: list[BinDistribution]
    interpretation: str


@dataclass
class LatticePoint2D:
    x: float      # U_n = X_n / m
    y: float      # U_{n+1} = X_{n+1} / m
    raw_x: int    # X_n
    raw_y: int    # X_{n+1}


@dataclass
class LatticePoint3D:
    x: float      # U_n
    y: float      # U_{n+1}
    z: float      # U_{n+2}
    raw_x: int    # X_n
    raw_y: int    # X_{n+1}
    raw_z: int    # X_{n+2}


@dataclass
class MarsagliaLatticeAnalysis:
    m: int
    a: int
    c: int
    sample_count: int
    max_hyperplanes_2d: int       # floor((2! * m)^(1/2))
    max_hyperplanes_3d: int       # floor((3! * m)^(1/3))
    points_2d: list[LatticePoint2D]
    points_3d: list[LatticePoint3D]
    theoretical_explanation: str
    pedagogical_insight: str


@dataclass
class LCGCrackingResult:
    recovered_m: int | None
    recovered_a: int | None
    recovered_c: int | None
    is_successful: bool
    predicted_next_values: list[int]
    reconstruction_method: str
    steps: list[str]
    explanation: str


def chi_square_uniformity_test(
    samples: list[float] | list[int],
    m: int | None = None,
    num_bins: int = 10,
) -> ChiSquareResult:
    """Performs Chi-Square goodness-of-fit test against a continuous uniform distribution U(0, 1).

    If integer samples are passed, m must be provided to normalize samples to [0, 1).
    """
    ...


def marsaglia_max_hyperplanes(m: int, dimensions: int) -> int:
    """Computes Marsaglia's upper bound on the number of hyperplanes containing all d-tuples:

        floor((d! * m)^(1/d))
    """
    ...


def generate_marsaglia_lattice(
    m: int,
    a: int,
    c: int,
    seed: int,
    count: int = 500,
) -> MarsagliaLatticeAnalysis:
    """Generates 2D pairs (X_n, X_{n+1}) and 3D triplets (X_n, X_{n+1}, X_{n+2})

    for Marsaglia lattice plane inspection and computes theoretical hyperplane limits.
    """
    ...


def crack_lcg(
    outputs: list[int],
    known_m: int | None = None,
    known_a: int | None = None,
    predict_count: int = 5,
) -> LCGCrackingResult:
    """Algebraically reconstructs LCG parameters from observed consecutive outputs.

    - If m and a are known, 2 outputs suffice to recover c.
    - If only m is known, 3 outputs suffice to recover a and c via modular inverse.
    - If m, a, and c are all unknown, 6-8 consecutive outputs recover m via determinant GCD,
      then a and c.
    Predicts the next `predict_count` values to verify reconstruction accuracy.
    """
    ...


def predict_lcg_backward(
    x_current: int,
    m: int,
    a: int,
    c: int,
    steps: int = 1,
) -> list[int]:
    """Reverses LCG generation backward in time:

        X_{n-1} = a^(-1) * (X_n - c) mod m
    Requires gcd(a, m) == 1.
    """
    ...
```

## 4. Algorithmic Specifications

### 1. Chi-Square Uniformity Test
1. Normalization: If samples are `int`, compute `val / m`. Clamp each float strictly into `[0.0, 1.0)`.
2. Bins: Define $k$ equal intervals $[0, 1/k), [1/k, 2/k), \dots, [(k-1)/k, 1.0)$.
3. Counts: $O_i = \text{number of samples in bin } i$. Expected $E_i = N / k$.
4. Statistic: $\chi^2 = \sum_{i=0}^{k-1} \frac{(O_i - E_i)^2}{E_i}$.
5. Degrees of freedom: $df = k - 1$.
6. Standard Critical Values Lookup Table (for $df \in [1, 30]$):
   - At $\alpha = 0.05$ and $\alpha = 0.01$. E.g., for $df = 9$: $\chi^2_{0.05} \approx 16.919$, $\chi^2_{0.01} \approx 21.666$.
   - Approximate $p$-value computation in pure Python: Use the upper incomplete gamma function approximation $Q(df/2, \chi^2/2)$ or Wilson-Hilferty transformation:
     $$Z = \frac{(\chi^2 / df)^{1/3} - (1 - 2/(9 \cdot df))}{\sqrt{2/(9 \cdot df)}}$$
     $$p = \frac{1}{2} \text{erfc}(Z / \sqrt{2})$$
     where `math.erfc` is standard library in Python!
7. Decision: If $\chi^2 \le \chi^2_{0.05}$ ($p \ge 0.05$), accept null hypothesis $H_0$ (distribution is consistent with uniform). Otherwise reject $H_0$.

### 2. Marsaglia Hyperplane Lattice Analysis
1. Marsaglia Theorem (1968): All points $(U_n, U_{n+1}, \dots, U_{n+d-1}) \in [0, 1)^d$ generated by an LCG lie on at most $(d! \cdot m)^{1/d}$ parallel hyperplanes.
2. In 2D: $\lfloor (2 \cdot m)^{1/2} \rfloor$.
3. In 3D: $\lfloor (6 \cdot m)^{1/3} \rfloor$.
4. Pairs and Triplets:
   - Given sequence $X_0, X_1, \dots, X_N$:
   - 2D Points: $(X_i, X_{i+1})$ for $i = 0, \dots, N-2$.
   - 3D Points: $(X_i, X_{i+1}, X_{i+2})$ for $i = 0, \dots, N-3$.

### 3. LCG State Reconstruction (Cryptanalysis)
1. **Scenario 1: Known $m, a$, Recover $c$**:
   - Given consecutive outputs $X_0, X_1$:
   - $c = (X_1 - a \cdot X_0) \pmod m$.
2. **Scenario 2: Known $m$, Recover $a$ and $c$**:
   - Given 3 consecutive outputs $X_0, X_1, X_2$:
   - Differences: $d_0 = (X_1 - X_0) \pmod m$, $d_1 = (X_2 - X_1) \pmod m$.
   - Relation: $d_1 \equiv a \cdot d_0 \pmod m$.
   - If $\gcd(d_0, m) == 1$, compute $a = (d_1 \cdot d_0^{-1}) \pmod m$ using `mod_inverse(d_0, m)`.
   - Then $c = (X_1 - a \cdot X_0) \pmod m$.
3. **Scenario 3: Unknown $m, a, c$, Complete Parameter Recovery**:
   - Given sequence $X_0, X_1, \dots, X_N$ ($N \ge 6$):
   - First differences: $t_n = X_{n+1} - X_n$.
   - Since $t_{n+1} \equiv a \cdot t_n \pmod m$, the cross terms satisfy:
     $$u_n = |t_{n+2} \cdot t_n - t_{n+1}^2| \equiv 0 \pmod m$$
   - Each $u_n$ is an integer multiple of $m$.
   - Compute candidate modulus: $m_{\text{cand}} = \gcd(u_0, u_1, \dots, u_{N-3})$.
   - If $m_{\text{cand}} > 1$, test whether it yields consistent $a$ and $c$. If so, parameters are successfully cracked!
4. **Backward Time Reversal**:
   - $X_n = (a \cdot X_{n-1} + c) \pmod m \iff a \cdot X_{n-1} \equiv (X_n - c) \pmod m$.
   - If $\gcd(a, m) == 1$, let $a_{\text{inv}} = a^{-1} \pmod m$.
   - Then $X_{n-1} = (a_{\text{inv}} \cdot (X_n - c)) \pmod m$.
