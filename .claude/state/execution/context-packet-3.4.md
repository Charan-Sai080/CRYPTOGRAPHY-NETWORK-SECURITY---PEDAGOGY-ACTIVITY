# Context Packet 3.4: Comprehensive Pytest 8.x Test Suite & Mathematical Identities

## 1. Goal
Implement an exhaustive, modern Pytest 8.x unit test suite in `backend/tests/test_lcg.py` covering 100% of the functions, dataclasses, parameter validation rules, mathematical invariants, theorems, and cryptanalytic cracking routines introduced in Milestone 3 (`backend/core/lcg.py`).

## 2. Allowed Files
* `backend/tests/test_lcg.py`
* `backend/tests/__init__.py`

## 3. Test Architecture & Structure

The test suite must be organized into clean, focused test classes adhering to Python 3.12+ and Pytest 8.x standards:

```python
import math
import pytest
from backend.core.lcg import (
    BinDistribution,
    ChiSquareResult,
    CycleDetectionResult,
    FloydStepTrace,
    HullDobellCondition,
    HullDobellResult,
    LCGGenerator,
    LCGParameters,
    LCGPreset,
    LCGSequenceResult,
    LCGStepTrace,
    LatticePoint2D,
    LatticePoint3D,
    MarsagliaLatticeAnalysis,
    MultiplicativeLCGAnalysis,
    LCGCrackingResult,
    STANDARD_PRESETS,
    analyze_multiplicative_lcg,
    check_hull_dobell,
    chi_square_uniformity_test,
    crack_lcg,
    detect_cycle_floyd,
    generate_lcg_sequence,
    generate_marsaglia_lattice,
    get_preset,
    list_presets,
    marsaglia_max_hyperplanes,
    predict_lcg_backward,
)
```

### Required Test Classes:

#### 1. `TestLCGParametersAndPresets`
- `test_valid_parameters`: Verifies instantiation with valid $m, a, c, seed$.
- `test_invalid_modulus`: Modulus $m \le 1$ raises `ValueError`.
- `test_invalid_multiplier`: Multiplier $a \le 0$ or $a \ge m$ raises `ValueError`.
- `test_invalid_increment`: Increment $c < 0$ or $c \ge m$ raises `ValueError`.
- `test_invalid_seed`: Seed $< 0$ or seed $\ge m$ raises `ValueError`.
- `test_multiplicative_zero_seed_rejection`: $c = 0$ with seed $= 0$ raises `ValueError`.
- `test_standard_presets_catalog`: Verifies all registered presets exist (`ansi_c`, `posix_rand48`, `minstd`, `minstd_revised`, `numerical_recipes`, `borland_c`, `small_educational`, `small_broken`).
- `test_get_preset_success_and_error`: `get_preset("ansi_c")` succeeds; unknown preset key raises `KeyError`.
- `test_list_presets`: Returns non-empty list of `LCGPreset` objects.

#### 2. `TestLCGGenerator`
- `test_generator_initialization`: Default parameters and custom parameters initialize properly.
- `test_from_preset`: Instantiates generator from preset with default and overridden seed.
- `test_next_int_recurrence`: Verifies each consecutive output exactly matches $X_{n+1} = (a \cdot X_n + c) \pmod m$.
- `test_next_float_bounds`: Verifies all generated floats lie strictly in $[0.0, 1.0)$.
- `test_step_trace_structure`: Inspects `LCGStepTrace` properties (`step_index`, `x_prev`, `a_times_x`, `plus_c`, `mod_m`, `x_next`, `u_next`, and formula string).
- `test_generator_reset`: `reset()` restores generator to original seed and resets step counter.
- `test_generate_sequence_count_zero`: `generate(0)` returns empty sequence and traces.
- `test_generate_sequence_negative_count`: `generate(-1)` raises `ValueError`.
- `test_functional_generate_lcg_sequence`: Matches results from `LCGGenerator.generate()`.
- `test_known_test_vectors_minstd`: Verifies MINSTD ($m = 2^{31} - 1, a = 16807, c = 0, \text{seed} = 1$) generates standard Park-Miller vector:
  - $X_1 = 16807$
  - $X_2 = 282475249$
  - $X_3 = 1622650073$
- `test_known_test_vectors_ansi_c`: Verifies ANSI C preset recurrence with known initial seed.

#### 3. `TestHullDobellValidator`
- `test_hull_dobell_full_period_presets`:
  - `ansi_c`, `numerical_recipes`, `borland_c`, and `small_educational` satisfy all 3 conditions and return `is_full_period == True`.
- `test_hull_dobell_condition_1_failure`:
  - $m = 16, a = 5, c = 2 \implies \gcd(2, 16) = 2 \ne 1$. Condition 1 fails, `is_full_period == False`.
- `test_hull_dobell_condition_2_failure`:
  - $m = 15 = 3 \times 5, a = 4, c = 1 \implies a - 1 = 3$. $3 \mid 3$, but $5 \nmid 3$. Condition 2 fails, `is_full_period == False`.
- `test_hull_dobell_condition_3_failure`:
  - $m = 8, a = 3, c = 1 \implies a - 1 = 2$. $4 \mid 8$, but $4 \nmid 2$. Condition 3 fails, `is_full_period == False`.
- `test_hull_dobell_condition_3_vacuous`:
  - When $m$ is not divisible by 4 (e.g. $m = 14$ or $m = 15$), Condition 3 is vacuously satisfied.
- `test_multiplicative_lcg_fails_hull_dobell`:
  - Any LCG with $c = 0$ has $\gcd(0, m) = m > 1$, failing Condition 1.

#### 4. `TestFloydCycleDetection`
- `test_floyd_full_period_generator`:
  - `small_educational` ($m = 16, a = 5, c = 1, \text{seed} = 1$): finds period $\lambda = 16$, cycle start $\mu = 0$, `is_full_period == True`.
- `test_floyd_short_period_generator`:
  - `small_broken` ($m = 16, a = 4, c = 2, \text{seed} = 1$): finds period $\lambda = 4$, `is_full_period == False`.
- `test_floyd_pre_period_detection`:
  - Generator with non-zero start index $\mu > 0$: detects $\mu$ accurately.
- `test_floyd_trace_steps`:
  - Verifies `traces` contains recorded `FloydStepTrace` entries up to `trace_steps`.
- `test_floyd_sample_cycle_values`:
  - Verifies `sample_cycle_values` has length $\min(\lambda, 25)$ and matches the cycle.

#### 5. `TestMultiplicativeLCGAnalysis`
- `test_multiplicative_prime_modulus`:
  - Small prime modulus $m = 17, a = 3, c = 0, \text{seed} = 1$: verifies prime detection and maximum period $m - 1 = 16$.
- `test_multiplicative_power_of_two_modulus`:
  - $m = 16, a = 5, c = 0, \text{seed} = 1$: verifies power-of-two detection and period $\lambda = m / 4 = 4$.
- `test_multiplicative_non_coprime_seed`:
  - Seed sharing factor with modulus is flagged (`is_seed_coprime == False`).

#### 6. `TestChiSquareUniformity`
- `test_uniform_distribution_acceptance`:
  - Generating 1000 samples from a full-period generator (e.g. `numerical_recipes` or `ansi_c`) yields $p \ge 0.05$ and `is_uniform_hypothesis_accepted == True`.
- `test_non_uniform_distribution_rejection`:
  - Degenerate sequence (e.g. constant sequence $[0.5] \times 1000$ or highly biased sequence) yields $p < 0.001$ and `is_uniform_hypothesis_accepted == False`.
- `test_bin_counts_and_frequencies`:
  - Verifies sum of `observed_count` across all bins equals $N$.
  - Verifies each bin's expected count equals $N / k$.
- `test_integer_samples_with_m`:
  - Passing integer samples with modulus $m$ normalizes cleanly and produces identical results.
- `test_invalid_bins`:
  - `num_bins < 2` raises `ValueError`.

#### 7. `TestMarsagliaLattice`
- `test_lattice_points_count`:
  - `count = 100` produces 99 2D points and 98 3D points.
- `test_lattice_points_coordinates`:
  - All 2D and 3D normalized coordinates lie in $[0.0, 1.0)$.
- `test_marsaglia_max_hyperplanes_formula`:
  - $m = 256, d = 2 \implies \lfloor \sqrt{2 \times 256} \rfloor = \lfloor \sqrt{512} \rfloor = 22$.
  - $m = 256, d = 3 \implies \lfloor (6 \times 256)^{1/3} \rfloor = \lfloor 1536^{1/3} \rfloor = 11$.
  - $m = 2^{31}, d = 3 \implies \lfloor (6 \times 2^{31})^{1/3} \rfloor = 2344$.
- `test_invalid_dimensions`:
  - Dimension $d \le 0$ raises `ValueError`.

#### 8. `TestLCGCrackingAndPredictability`
- `test_crack_c_known_m_and_a`:
  - Known $m = 2^{31}, a = 1103515245$, unknown $c = 12345$.
  - Given 2 consecutive outputs $X_0, X_1$: correctly recovers $c = 12345$.
- `test_crack_a_and_c_known_m`:
  - Known $m = 10007$ (prime) or standard modulus.
  - Given 3 consecutive outputs $X_0, X_1, X_2$: correctly recovers both $a$ and $c$.
- `test_crack_all_unknown_m_a_c`:
  - Modulus $m = 65537, a = 1234, c = 5678$.
  - Given 8 consecutive outputs: correctly recovers $m, a, c$, and predicts the next 5 outputs with 100% accuracy.
- `test_predict_lcg_backward`:
  - Given current state $X_n$ and parameters $(m, a, c)$ with $\gcd(a, m) = 1$:
  - `predict_lcg_backward` exactly recovers previous states $X_{n-1}, X_{n-2}, \dots$.

## 4. Acceptance Criteria
1. **Pytest 8.x Execution**: All tests pass cleanly via `pytest backend/tests/test_lcg.py`.
2. **Zero Failures & Zero Regressions**: No regressions in existing Milestone 1 (`test_number_theory.py`) and Milestone 2 (`test_otp.py`) suites.
3. **Comprehensive Coverage**: At least 30 dedicated unit test methods covering all branches, edge cases, presets, mathematical theorems, and cryptanalytic cracking.
4. **Deterministic Behavior**: Tests are fully deterministic without flaky random failures.
