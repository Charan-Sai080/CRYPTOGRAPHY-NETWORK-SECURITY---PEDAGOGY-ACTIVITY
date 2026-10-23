# Context Packet 3: Milestone 3 Linear Congruential Generator (LCG) Engine & Statistical/Lattice Analysis

## 1. Task Goal
Implement the Linear Congruential Generator (LCG) Engine, Presets Library, Hull-Dobell Theorem Validator, Floyd's Cycle-Finding Period Analyzer, Multiplicative LCG Analyzer, Statistical Uniformity (Chi-Square) Goodness-of-Fit Test, Marsaglia Hyperplane Lattice Point Generator, and LCG State Reconstruction (Cryptanalytic Cracking) in pure Python 3.12+, with exhaustive pedagogical execution traces and a comprehensive Pytest 8.x test suite.

## 2. Granular Sub-Milestones
* **M3.1**: Core LCG Generator, Presets Library, and Sequence Extraction (LCG recurrence relation $X_{n+1} = (a \cdot X_n + c) \pmod m$, normalized float $U_n = X_n / m \in [0, 1)$, historical standard presets, detailed per-step arithmetic traces). Detailed Context: [context-packet-3.1.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-3.1.md)
* **M3.2**: Hull-Dobell Theorem Validator & Floyd's Cycle-Finding Period Analyzer (exact 3-condition Hull-Dobell theorem checker, prime factor analysis, Floyd's tortoise-and-hare cycle-finding algorithm with period $\lambda$ and cycle start $\mu$, multiplicative LCG $c = 0$ period analysis). Detailed Context: [context-packet-3.2.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-3.2.md)
* **M3.3**: Statistical Uniformity (Chi-Square) & Marsaglia Hyperplane Lattice Analysis & State Reconstruction (Chi-square goodness-of-fit test against uniform distribution, 2D/3D Marsaglia lattice point generation and theoretical hyperplane bound $(d! \cdot m)^{1/d}$, algebraic state reconstruction and forward/backward sequence prediction demonstrating cryptographic insecurity). Detailed Context: [context-packet-3.3.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-3.3.md)
* **M3.4**: Comprehensive Pytest 8.x Test Suite covering all LCG features, edge cases, presets, mathematical identities, and theorems. Detailed Context: [context-packet-3.4.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-3.4.md)

## 3. Allowed Files
* `backend/core/lcg.py`
* `backend/core/__init__.py`
* `backend/tests/test_lcg.py`
* `backend/tests/__init__.py`

## 4. Key Architectural Deliverables
* **LCG Parameters & Presets (`LCGParameters`, `LCGPreset`, `STANDARD_PRESETS`)**: Validates $m > 1$, $0 < a < m$, $0 \le c < m$, and $0 \le X_0 < m$. Includes standard historical presets (ANSI C, POSIX rand48, MINSTD / Park-Miller, Numerical Recipes, Borland C/C++, Small Educational, and Small Broken for pedagogy).
* **Pedagogical Step Tracing (`LCGStepTrace`, `LCGSequenceResult`)**: Records step index, previous state $X_n$, intermediate multiplication $a \cdot X_n$, increment $+ c$, modulus $\pmod m$, output state $X_{n+1}$, normalized float $U_{n+1} \in [0.0, 1.0)$, and human-readable mathematical formula string.
* **Hull-Dobell Theorem Validator (`check_hull_dobell(m, a, c) -> HullDobellResult`)**: Evaluates all three criteria for full period $m$:
  1. $\gcd(c, m) = 1$
  2. Every prime factor of $m$ divides $(a - 1)$
  3. If $4 \mid m$, then $4 \mid (a - 1)$
  Provides detailed pass/fail analysis and pedagogical explanation for each condition.
* **Floyd's Cycle-Finding Engine (`detect_cycle_floyd(...) -> CycleDetectionResult`)**: Implements the tortoise-and-hare algorithm to compute exact period length $\lambda$ and cycle start index $\mu$ with bounded iteration limits and step-by-step position traces.
* **Multiplicative LCG Analysis (`analyze_multiplicative_lcg(...) -> MultiplicativeLCGAnalysis`)**: Analyzes Lehmer RNGs ($c = 0$), verifying maximum period conditions ($m - 1$ for prime modulus with primitive root $a$, or $m/4$ for powers of 2).
* **Chi-Square Uniformity Test (`chi_square_uniformity_test(...) -> ChiSquareResult`)**: Evaluates empirical uniformity by binning observed samples into $k$ intervals, computing $\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$, degrees of freedom $df = k - 1$, critical values ($\alpha = 0.05, 0.01$), and approximate $p$-value.
* **Marsaglia Hyperplane Lattice Generator (`generate_marsaglia_lattice(...) -> MarsagliaLatticeAnalysis`)**: Demonstrates George Marsaglia's 1968 theorem ("Random numbers fall mainly in the planes") by computing 2D pairs $(X_n, X_{n+1})$, 3D triplets $(X_n, X_{n+1}, X_{n+2})$, and the theoretical maximum hyperplane bound $\lfloor (d! \cdot m)^{1/d} \rfloor$.
* **LCG Cryptanalysis & State Reconstruction Engine (`crack_lcg(...) -> LCGCrackingResult`)**: Reconstructs internal state and unknown parameters from consecutive outputs:
  - Unknown $c$ with known $a, m$ from 2 consecutive outputs
  - Unknown $a, c$ with known $m$ from 3 consecutive outputs via modular inverse
  - Unknown $m, a, c$ from 6-8 consecutive outputs via differences and determinant GCD
  - Predicts both future and past sequence values, proving why LCGs are cryptographically insecure.
* **Exhaustive Pytest 8.x Suite (`backend/tests/test_lcg.py`)**: Tests presets, parameter boundaries, trace outputs, mathematical proofs, cycle-finding correctness, statistical tests, lattice properties, and cryptanalytic cracking.

## 5. Acceptance Criteria
1. Strictly typed with dataclasses and modern Python 3.12+ syntax (`int | None`, `tuple[int, ...]`, `list[T]`).
2. Pure Python standard library implementation: zero external dependencies required for the core algorithms (no `scipy` or `numpy` required for Chi-Square or lattice calculations).
3. Integration with `backend/core/number_theory.py` for shared primitives (`extended_gcd`, `mod_inverse`, `distinct_prime_factors`, `is_prime`).
4. Full pedagogical traceability: all operations provide structured trace objects suitable for educational UI visualization.
5. All tests in `backend/tests/test_lcg.py` pass cleanly without regressions in `test_number_theory.py` or `test_otp.py`.
