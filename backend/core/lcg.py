"""Linear Congruential Generator (LCG) Engine & Statistical/Lattice Analysis.

Pedagogical and mathematically rigorous implementation of:
- Canonical LCG Recurrence: X_{n+1} = (a * X_n + c) mod m, U_{n+1} = X_{n+1} / m
- Historical & Standard Presets Catalog (ANSI C, POSIX rand48, MINSTD, etc.)
- Hull-Dobell Theorem Validator (exact 3 necessary and sufficient conditions)
- Floyd's Cycle-Finding Algorithm (Tortoise and Hare)
- Multiplicative LCG Period & Primitive Root Analyzer (Lehmer RNG, c = 0)
- Statistical Uniformity Goodness-of-Fit Test (Chi-Square with Wilson-Hilferty)
- Marsaglia Hyperplane Lattice Point Generator (2D/3D & hyperplane bounds)
- Algebraic State Reconstruction & Cryptanalytic Cracker (forward & backward)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterator

from backend.core.number_theory import (
    distinct_prime_factors,
    extended_gcd,
    find_primitive_root,
    is_prime,
    mod_inverse,
)


# -----------------------------------------------------------------------------
# Data Models: LCG Parameters, Presets & Step Traces
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class LCGParameters:
    """Mathematical parameters defining an LCG state machine."""

    m: int  # Modulus: integer > 1
    a: int  # Multiplier: integer 0 < a < m
    c: int  # Increment: integer 0 <= c < m
    seed: int  # Initial seed X_0: integer 0 <= seed < m

    def __post_init__(self) -> None:
        if not isinstance(self.m, int) or isinstance(self.m, bool) or self.m <= 1:
            raise ValueError(f"Modulus m must be an integer > 1, got {self.m}")
        if not isinstance(self.a, int) or isinstance(self.a, bool) or not (0 < self.a < self.m):
            raise ValueError(f"Multiplier a must be an integer 0 < a < m ({self.m}), got {self.a}")
        if not isinstance(self.c, int) or isinstance(self.c, bool) or not (0 <= self.c < self.m):
            raise ValueError(f"Increment c must be an integer 0 <= c < m ({self.m}), got {self.c}")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or not (0 <= self.seed < self.m):
            raise ValueError(f"Seed must be an integer 0 <= seed < m ({self.m}), got {self.seed}")
        if self.c == 0 and self.seed == 0:
            raise ValueError("For multiplicative LCG (c = 0), seed cannot be 0 (0 is an absorbing state).")


@dataclass(frozen=True)
class LCGPreset:
    """Historical or standard preset configuration for an LCG."""

    key: str
    display_name: str
    m: int
    a: int
    c: int
    default_seed: int
    description: str
    is_full_period_expected: bool
    category: str  # "Historical", "Standard", "Educational", or "Vulnerable"


@dataclass(frozen=True)
class LCGStepTrace:
    """Detailed arithmetic trace of a single LCG state transition."""

    step_index: int  # 1-indexed sequence position
    x_prev: int  # X_n (input state)
    a_times_x: int  # Intermediate product: a * X_n
    plus_c: int  # Intermediate sum: a * X_n + c
    mod_m: int  # Modulus m
    x_next: int  # Output state X_{n+1} = (a * X_n + c) % m
    u_next: float  # Normalized float: X_{n+1} / m in [0.0, 1.0)
    formula: str  # Pedagogical formula string


@dataclass(frozen=True)
class LCGSequenceResult:
    """Result of generating a sequence of values from an LCG."""

    params: LCGParameters
    values: list[int]
    normalized: list[float]
    traces: list[LCGStepTrace] = field(default_factory=list)
    count: int = 0


# -----------------------------------------------------------------------------
# Standard Historical & Pedagogical Presets
# -----------------------------------------------------------------------------

STANDARD_PRESETS: dict[str, LCGPreset] = {
    "ansi_c": LCGPreset(
        key="ansi_c",
        display_name="ANSI C / GCC rand()",
        m=2147483648,  # 2^31
        a=1103515245,
        c=12345,
        default_seed=12345,
        description="Classic C library PRNG parameter set (m = 2^31). Meets Hull-Dobell for full period 2^31.",
        is_full_period_expected=True,
        category="Historical",
    ),
    "posix_rand48": LCGPreset(
        key="posix_rand48",
        display_name="POSIX drand48()",
        m=281474976710656,  # 2^48
        a=25214903917,  # 0x5DEECE66D
        c=11,  # 0xB
        default_seed=1,
        description="POSIX standard 48-bit linear congruential generator with full period 2^48.",
        is_full_period_expected=True,
        category="Standard",
    ),
    "minstd": LCGPreset(
        key="minstd",
        display_name="MINSTD (Park & Miller 1988)",
        m=2147483647,  # 2^31 - 1 (Mersenne prime M31)
        a=16807,  # 7^5 (primitive root modulo 2^31 - 1)
        c=0,  # Multiplicative LCG (c = 0)
        default_seed=1,
        description="Standard Minimal Lehmer generator over prime modulus 2^31 - 1. Max period m - 1.",
        is_full_period_expected=False,
        category="Historical",
    ),
    "minstd_revised": LCGPreset(
        key="minstd_revised",
        display_name="MINSTD Revised (Park, Miller, Stockmeyer 1993)",
        m=2147483647,  # 2^31 - 1
        a=48271,  # Revised primitive root with better spectral test score
        c=0,
        default_seed=1,
        description="Updated MINSTD multiplier recommended by Park, Miller, and Stockmeyer (1993).",
        is_full_period_expected=False,
        category="Historical",
    ),
    "numerical_recipes": LCGPreset(
        key="numerical_recipes",
        display_name="Numerical Recipes (Press et al.)",
        m=4294967296,  # 2^32
        a=1664525,
        c=1013904223,
        default_seed=42,
        description="Standard 32-bit generator from Numerical Recipes in C with full period 2^32.",
        is_full_period_expected=True,
        category="Standard",
    ),
    "borland_c": LCGPreset(
        key="borland_c",
        display_name="Borland C/C++",
        m=4294967296,  # 2^32
        a=22695477,
        c=1,
        default_seed=1,
        description="Borland C/C++ compiler runtime generator with increment c = 1 and full period 2^32.",
        is_full_period_expected=True,
        category="Historical",
    ),
    "small_educational": LCGPreset(
        key="small_educational",
        display_name="Small Educational Full-Period (m=16)",
        m=16,
        a=5,
        c=1,
        default_seed=1,
        description="Toy educational LCG satisfying Hull-Dobell theorem: full period 16.",
        is_full_period_expected=True,
        category="Educational",
    ),
    "small_broken": LCGPreset(
        key="small_broken",
        display_name="Small Broken Short-Period (m=16)",
        m=16,
        a=4,
        c=2,
        default_seed=1,
        description="Flawed educational LCG violating Hull-Dobell: period length only 4.",
        is_full_period_expected=False,
        category="Vulnerable",
    ),
}


def get_preset(preset_key: str) -> LCGPreset:
    """Retrieves preset by key. Raises KeyError with available keys if not found."""
    if preset_key not in STANDARD_PRESETS:
        raise KeyError(f"Preset '{preset_key}' not found. Available presets: {list(STANDARD_PRESETS.keys())}")
    return STANDARD_PRESETS[preset_key]


def list_presets() -> list[LCGPreset]:
    """Returns a list of all registered presets."""
    return list(STANDARD_PRESETS.values())


# -----------------------------------------------------------------------------
# Core LCG Generator Class
# -----------------------------------------------------------------------------


class LCGGenerator:
    """Stateful Linear Congruential Generator with arithmetic step tracing."""

    def __init__(
        self,
        params: LCGParameters | None = None,
        *,
        m: int = 2147483648,
        a: int = 1103515245,
        c: int = 12345,
        seed: int = 1,
    ) -> None:
        if params is not None:
            self._params = params
        else:
            self._params = LCGParameters(m=m, a=a, c=c, seed=seed)
        self._current_state: int = self._params.seed
        self._step_counter: int = 0

    @classmethod
    def from_preset(cls, preset_key: str, seed: int | None = None) -> LCGGenerator:
        """Instantiates an LCGGenerator from a registered preset key."""
        preset = get_preset(preset_key)
        actual_seed = preset.default_seed if seed is None else seed
        params = LCGParameters(
            m=preset.m,
            a=preset.a,
            c=preset.c,
            seed=actual_seed,
        )
        return cls(params=params)

    @property
    def params(self) -> LCGParameters:
        """Returns the immutable LCG parameter configuration."""
        return self._params

    @property
    def current_state(self) -> int:
        """Returns the current internal state X_n."""
        return self._current_state

    @property
    def step_counter(self) -> int:
        """Returns the total number of steps executed since initialization/reset."""
        return self._step_counter

    def reset(self, seed: int | None = None) -> None:
        """Resets the generator state to the initial seed or a new seed."""
        if seed is not None:
            if not isinstance(seed, int) or isinstance(seed, bool) or not (0 <= seed < self._params.m):
                raise ValueError(f"Seed must be an integer 0 <= seed < m ({self._params.m}), got {seed}")
            if self._params.c == 0 and seed == 0:
                raise ValueError("For multiplicative LCG (c = 0), seed cannot be 0 (0 is an absorbing state).")
            self._current_state = seed
        else:
            self._current_state = self._params.seed
        self._step_counter = 0

    def step(self) -> LCGStepTrace:
        """Advances the generator state by 1 step, returning the full arithmetic trace."""
        prev = self._current_state
        m = self._params.m
        a = self._params.a
        c = self._params.c

        ax = a * prev
        ax_c = ax + c
        next_val = ax_c % m
        u_val = next_val / m

        self._step_counter += 1
        self._current_state = next_val

        formula = f"({a} * {prev} + {c}) mod {m} = {ax_c} mod {m} = {next_val} (U = {u_val:.6f})"
        return LCGStepTrace(
            step_index=self._step_counter,
            x_prev=prev,
            a_times_x=ax,
            plus_c=ax_c,
            mod_m=m,
            x_next=next_val,
            u_next=u_val,
            formula=formula,
        )

    def next_int(self) -> int:
        """Advances state and returns the next integer X_{n+1}."""
        return self.step().x_next

    def next_float(self) -> float:
        """Advances state and returns normalized float U_{n+1} = X_{n+1} / m in [0.0, 1.0)."""
        return self.step().u_next

    def generate(self, count: int, include_traces: bool = True) -> LCGSequenceResult:
        """Generates `count` successive pseudorandom values and traces."""
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"count must be a non-negative integer, got {count}")
        if count == 0:
            return LCGSequenceResult(
                params=self._params,
                values=[],
                normalized=[],
                traces=[],
                count=0,
            )

        values: list[int] = []
        normalized: list[float] = []
        traces: list[LCGStepTrace] = []

        for _ in range(count):
            tr = self.step()
            values.append(tr.x_next)
            normalized.append(tr.u_next)
            if include_traces:
                traces.append(tr)

        return LCGSequenceResult(
            params=self._params,
            values=values,
            normalized=normalized,
            traces=traces,
            count=count,
        )

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        return self.next_int()


def generate_lcg_sequence(
    m: int,
    a: int,
    c: int,
    seed: int,
    count: int,
    include_traces: bool = True,
) -> LCGSequenceResult:
    """Functional convenience wrapper to generate count values from given LCG parameters."""
    params = LCGParameters(m=m, a=a, c=c, seed=seed)
    gen = LCGGenerator(params=params)
    return gen.generate(count, include_traces=include_traces)


# -----------------------------------------------------------------------------
# Hull-Dobell Theorem Validator & Cycle Detection Models
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class HullDobellCondition:
    """Evaluation result for one of the three Hull-Dobell conditions."""

    condition_number: int  # 1, 2, or 3
    title: str  # Short descriptive title
    passed: bool  # True if criterion is satisfied
    mathematical_statement: str  # e.g., "gcd(c, m) = gcd(1, 16) = 1"
    details: str  # Detailed pedagogical analysis


@dataclass(frozen=True)
class HullDobellResult:
    """Complete Hull-Dobell theorem validation report."""

    m: int
    a: int
    c: int
    is_full_period: bool  # True iff ALL 3 conditions pass
    conditions: list[HullDobellCondition]
    prime_factors_m: list[int]  # Distinct prime factors of m
    summary: str
    pedagogical_notes: str


@dataclass(frozen=True)
class FloydStepTrace:
    """Single step in Floyd's cycle-finding tortoise-and-hare algorithm."""

    iteration: int
    tortoise_index: int
    tortoise_val: int
    hare_index: int
    hare_val: int


@dataclass(frozen=True)
class CycleDetectionResult:
    """Result of Floyd's cycle detection on an LCG sequence."""

    m: int
    a: int
    c: int
    seed: int
    period_length: int  # lambda: cycle length
    cycle_start_index: int  # mu: 0-indexed position where cycle begins
    is_full_period: bool  # True if period_length == m and cycle_start_index == 0
    meeting_iteration: int  # Step where tortoise and hare collided
    sample_cycle_values: list[int]  # First min(period_length, 25) values of cycle
    traces: list[FloydStepTrace]  # Step traces during initial phase
    iterations_run: int  # Total iterations run
    explanation: str


@dataclass(frozen=True)
class MultiplicativeLCGAnalysis:
    """Analysis of Lehmer PRNG (c = 0) cycle characteristics."""

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
      2. Every prime factor of m divides (a - 1)
      3. If 4 divides m, then 4 divides (a - 1)
    """
    if not isinstance(m, int) or isinstance(m, bool) or m <= 1:
        raise ValueError(f"Modulus m must be an integer > 1, got {m}")

    # Condition 1: gcd(c, m) == 1
    gcd_c_m = math.gcd(c, m)
    cond1_passed = (gcd_c_m == 1)
    cond1 = HullDobellCondition(
        condition_number=1,
        title="Increment and Modulus Coprimality",
        passed=cond1_passed,
        mathematical_statement=f"gcd(c, m) = gcd({c}, {m}) = {gcd_c_m}",
        details=(
            f"gcd({c}, {m}) == 1: Increment c is coprime to modulus m."
            if cond1_passed
            else f"gcd({c}, {m}) == {gcd_c_m} != 1: Increment c and modulus m share common factor {gcd_c_m}. Violates Condition 1."
        ),
    )

    # Condition 2: Every prime factor of m divides (a - 1)
    q_factors = distinct_prime_factors(m)
    a_minus_1 = a - 1
    failing_factors = [q for q in q_factors if a_minus_1 % q != 0]
    cond2_passed = (len(failing_factors) == 0)
    cond2_stmt = f"Prime factors of m={m}: {q_factors}; a - 1 = {a_minus_1}"
    cond2 = HullDobellCondition(
        condition_number=2,
        title="Prime Factor Divisibility of Multiplier Offset",
        passed=cond2_passed,
        mathematical_statement=cond2_stmt,
        details=(
            f"All prime factors {q_factors} of {m} divide a - 1 = {a_minus_1}."
            if cond2_passed
            else f"Prime factors {failing_factors} do not divide a - 1 = {a_minus_1}. Violates Condition 2."
        ),
    )

    # Condition 3: If 4 divides m, then 4 divides (a - 1)
    if m % 4 == 0:
        cond3_passed = (a_minus_1 % 4 == 0)
        cond3_stmt = f"4 divides m ({m} % 4 == 0); (a - 1) % 4 = {a_minus_1} % 4 = {a_minus_1 % 4}"
        cond3_details = (
            f"4 divides m and 4 divides a - 1 = {a_minus_1} ({a_minus_1} % 4 == 0)."
            if cond3_passed
            else f"4 divides m ({m}), but 4 does not divide a - 1 = {a_minus_1} ({a_minus_1} % 4 == {a_minus_1 % 4} != 0). Violates Condition 3."
        )
    else:
        cond3_passed = True
        cond3_stmt = f"4 does not divide m ({m} % 4 = {m % 4} != 0); condition vacuously satisfied"
        cond3_details = f"Since 4 does not divide m={m}, Condition 3 is vacuously satisfied."

    cond3 = HullDobellCondition(
        condition_number=3,
        title="Modulus Divisibility by 4 Constraint",
        passed=cond3_passed,
        mathematical_statement=cond3_stmt,
        details=cond3_details,
    )

    is_full = cond1_passed and cond2_passed and cond3_passed
    summary = (
        f"LCG(m={m}, a={a}, c={c}) satisfies all 3 Hull-Dobell conditions. Full period length m = {m} guaranteed for all seeds."
        if is_full
        else f"LCG(m={m}, a={a}, c={c}) does NOT satisfy the Hull-Dobell theorem. Period length is strictly less than m."
    )
    pedagogical = (
        "The Hull-Dobell Theorem (1962) establishes necessary and sufficient conditions for a Linear "
        "Congruential Generator to possess a full period of length m for every seed: (1) gcd(c, m) = 1, "
        "(2) for all primes q dividing m, q divides (a - 1), and (3) if 4 divides m, 4 divides (a - 1)."
    )

    return HullDobellResult(
        m=m,
        a=a,
        c=c,
        is_full_period=is_full,
        conditions=[cond1, cond2, cond3],
        prime_factors_m=q_factors,
        summary=summary,
        pedagogical_notes=pedagogical,
    )


def detect_cycle_floyd(
    m: int,
    a: int,
    c: int,
    seed: int,
    max_iterations: int = 1_000_000,
    trace_steps: int = 25,
) -> CycleDetectionResult:
    """Applies Floyd's cycle-finding (tortoise-and-hare) algorithm to determine

    period length (lambda) and cycle start index (mu) for an LCG sequence.
    Bounded by max_iterations to safeguard against astronomical moduli.
    """
    if not isinstance(m, int) or isinstance(m, bool) or m <= 1:
        raise ValueError(f"Modulus m must be an integer > 1, got {m}")
    if not isinstance(a, int) or isinstance(a, bool) or not (0 < a < m):
        raise ValueError(f"Multiplier a must satisfy 0 < a < m, got {a}")
    if not isinstance(c, int) or isinstance(c, bool) or not (0 <= c < m):
        raise ValueError(f"Increment c must satisfy 0 <= c < m, got {c}")
    if not isinstance(seed, int) or isinstance(seed, bool) or not (0 <= seed < m):
        raise ValueError(f"Seed must satisfy 0 <= seed < m, got {seed}")

    f = lambda x: (a * x + c) % m

    # Phase 1: Finding meeting point
    tortoise = f(seed)
    hare = f(f(seed))
    meeting_iter = 1
    traces: list[FloydStepTrace] = [
        FloydStepTrace(
            iteration=1,
            tortoise_index=1,
            tortoise_val=tortoise,
            hare_index=2,
            hare_val=hare,
        )
    ]

    while tortoise != hare:
        meeting_iter += 1
        if meeting_iter > max_iterations:
            raise TimeoutError(f"Floyd cycle detection exceeded maximum allowed iterations ({max_iterations}).")
        tortoise = f(tortoise)
        hare = f(f(hare))
        if meeting_iter <= trace_steps:
            traces.append(
                FloydStepTrace(
                    iteration=meeting_iter,
                    tortoise_index=meeting_iter,
                    tortoise_val=tortoise,
                    hare_index=2 * meeting_iter,
                    hare_val=hare,
                )
            )

    # Phase 2: Finding cycle start index mu
    tortoise = seed
    mu = 0
    while tortoise != hare:
        tortoise = f(tortoise)
        hare = f(hare)
        mu += 1
        if mu > max_iterations:
            raise TimeoutError(f"Cycle start search exceeded maximum iterations ({max_iterations}).")

    # Phase 3: Finding cycle period length lambda
    hare = f(tortoise)
    lam = 1
    while tortoise != hare:
        hare = f(hare)
        lam += 1
        if lam > max_iterations:
            raise TimeoutError(f"Period length search exceeded maximum iterations ({max_iterations}).")

    # Sample cycle values (starting from state at mu)
    sample_values: list[int] = [tortoise]
    curr = tortoise
    for _ in range(min(lam - 1, 24)):
        curr = f(curr)
        sample_values.append(curr)

    is_full = (lam == m and mu == 0)
    iterations_run = meeting_iter + mu + lam

    explanation = (
        f"Floyd cycle detection found period lambda = {lam} and pre-period mu = {mu} "
        f"(collision at step {meeting_iter}). {'Full period length m reached.' if is_full else 'Sub-maximal period.'}"
    )

    return CycleDetectionResult(
        m=m,
        a=a,
        c=c,
        seed=seed,
        period_length=lam,
        cycle_start_index=mu,
        is_full_period=is_full,
        meeting_iteration=meeting_iter,
        sample_cycle_values=sample_values,
        traces=traces,
        iterations_run=iterations_run,
        explanation=explanation,
    )


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
    if not isinstance(m, int) or isinstance(m, bool) or m <= 1:
        raise ValueError(f"Modulus m must be an integer > 1, got {m}")
    if not isinstance(a, int) or isinstance(a, bool) or not (0 < a < m):
        raise ValueError(f"Multiplier a must satisfy 0 < a < m, got {a}")
    if seed == 0:
        raise ValueError("For multiplicative LCG (c = 0), seed cannot be 0 (0 is an absorbing state).")
    if not isinstance(seed, int) or isinstance(seed, bool) or not (0 < seed < m):
        raise ValueError(f"Seed must satisfy 0 < seed < m, got {seed}")

    mod_is_prime = is_prime(m).is_prime
    is_pow2 = (m > 0 and (m & (m - 1)) == 0)
    pow2_exp = (m.bit_length() - 1) if is_pow2 else None
    seed_coprime = (math.gcd(seed, m) == 1)

    is_prim_root: bool | None = None
    if mod_is_prime:
        theo_max = m - 1
        factors = distinct_prime_factors(m - 1)
        is_prim_root = all(pow(a, (m - 1) // q, m) != 1 for q in factors)
    elif is_pow2 and pow2_exp is not None and pow2_exp >= 3:
        theo_max = m // 4
    elif is_pow2 and pow2_exp is not None and pow2_exp == 2:
        theo_max = 2
    elif is_pow2 and pow2_exp is not None and pow2_exp == 1:
        theo_max = 1
    else:
        theo_max = m - 1

    cycle_res = detect_cycle_floyd(m=m, a=a, c=0, seed=seed, max_iterations=max_iterations)
    actual_period = cycle_res.period_length
    achieves_max = (actual_period == theo_max)

    if mod_is_prime:
        explanation = (
            f"Modulus m={m} is prime. Theoretical max period is m - 1 = {theo_max}. "
            f"Multiplier a={a} {'is' if is_prim_root else 'is NOT'} a primitive root modulo {m}. "
            f"Observed period is {actual_period}."
        )
    elif is_pow2:
        explanation = (
            f"Modulus m={m}=2^{pow2_exp} is a power of 2. Theoretical max period is m / 4 = {theo_max} "
            f"(achieved when a % 8 in (3, 5) and seed is odd). "
            f"Observed period is {actual_period} (a % 8 = {a % 8}, seed is {'odd' if seed % 2 == 1 else 'even'})."
        )
    else:
        explanation = f"Modulus m={m} is composite. Observed period is {actual_period}."

    return MultiplicativeLCGAnalysis(
        m=m,
        a=a,
        seed=seed,
        is_modulus_prime=mod_is_prime,
        is_power_of_two=is_pow2,
        power_of_two_exponent=pow2_exp,
        theoretical_max_period=theo_max,
        actual_period=actual_period,
        achieves_max_period=achieves_max,
        is_primitive_root=is_prim_root,
        is_seed_coprime=seed_coprime,
        explanation=explanation,
    )


# -----------------------------------------------------------------------------
# Statistical Uniformity: Chi-Square Goodness-of-Fit Test
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class BinDistribution:
    """Observed vs expected frequency distribution for a single interval."""

    bin_index: int
    lower_bound: float
    upper_bound: float
    observed_count: int
    expected_count: float
    chi_square_contribution: float


ChiSquareBin = BinDistribution  # Canonical alias


@dataclass(frozen=True)
class ChiSquareResult:
    """Complete Chi-Square goodness-of-fit test analysis."""

    num_samples: int
    num_bins: int
    degrees_of_freedom: int
    chi_square_statistic: float
    critical_value_95: float  # alpha = 0.05
    critical_value_99: float  # alpha = 0.01
    p_value: float  # Estimated p-value in [0.0, 1.0]
    is_uniform_hypothesis_accepted: bool  # True if p_value >= 0.05
    bins: list[BinDistribution]
    interpretation: str


CHI2_CRITICAL_05: dict[int, float] = {
    1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070,
    6: 12.592, 7: 14.067, 8: 15.507, 9: 16.919, 10: 18.307,
    11: 19.675, 12: 21.026, 13: 22.362, 14: 23.685, 15: 24.996,
    16: 26.296, 17: 27.587, 18: 28.869, 19: 30.144, 20: 31.410,
    21: 32.671, 22: 33.924, 23: 35.172, 24: 36.415, 25: 37.652,
    26: 38.885, 27: 40.113, 28: 41.337, 29: 42.557, 30: 43.773,
}

CHI2_CRITICAL_01: dict[int, float] = {
    1: 6.635, 2: 9.210, 3: 11.345, 4: 13.277, 5: 15.086,
    6: 16.812, 7: 18.475, 8: 20.090, 9: 21.666, 10: 23.209,
    11: 24.725, 12: 26.217, 13: 27.688, 14: 29.141, 15: 30.578,
    16: 32.000, 17: 33.409, 18: 34.805, 19: 36.191, 20: 37.566,
    21: 38.932, 22: 40.289, 23: 41.638, 24: 42.980, 25: 44.314,
    26: 45.642, 27: 46.963, 28: 48.278, 29: 49.588, 30: 50.892,
}


def chi_square_uniformity_test(
    samples: list[float] | list[int],
    m: int | None = None,
    num_bins: int = 10,
) -> ChiSquareResult:
    """Performs Chi-Square goodness-of-fit test against a continuous uniform distribution U(0, 1).

    If integer samples are passed, m must be provided to normalize samples to [0, 1).
    """
    if not isinstance(num_bins, int) or isinstance(num_bins, bool) or num_bins < 2:
        raise ValueError(f"num_bins must be an integer >= 2, got {num_bins}")
    if not samples:
        raise ValueError("samples list cannot be empty.")

    n = len(samples)
    first = samples[0]
    if isinstance(first, int) and not isinstance(first, bool) and m is None:
        raise ValueError("When integer samples are provided, modulus m must be specified.")
    if m is not None and (not isinstance(m, int) or isinstance(m, bool) or m <= 1):
        raise ValueError(f"Modulus m must be an integer > 1, got {m}")

    norm_samples: list[float] = []
    for s in samples:
        if m is not None:
            norm_samples.append(float(s) / m)
        else:
            norm_samples.append(float(s))

    obs = [0] * num_bins
    for u in norm_samples:
        clamped = max(0.0, min(u, 0.9999999999999999))
        idx = min(int(clamped * num_bins), num_bins - 1)
        obs[idx] += 1

    expected_per_bin = n / num_bins
    df = num_bins - 1

    chi2_stat = 0.0
    bins: list[BinDistribution] = []
    for i in range(num_bins):
        low = i / num_bins
        high = (i + 1) / num_bins
        oi = obs[i]
        contrib = ((oi - expected_per_bin) ** 2) / expected_per_bin
        chi2_stat += contrib
        bins.append(
            BinDistribution(
                bin_index=i,
                lower_bound=low,
                upper_bound=high,
                observed_count=oi,
                expected_count=expected_per_bin,
                chi_square_contribution=contrib,
            )
        )

    # Critical thresholds
    if df in CHI2_CRITICAL_05:
        crit_95 = CHI2_CRITICAL_05[df]
        crit_99 = CHI2_CRITICAL_01[df]
    else:
        term = 2.0 / (9.0 * df)
        z95 = 1.6448536269514722
        z99 = 2.3263478740408408
        crit_95 = df * ((1.0 - term + z95 * math.sqrt(term)) ** 3)
        crit_99 = df * ((1.0 - term + z99 * math.sqrt(term)) ** 3)

    # Wilson-Hilferty normal approximation for Chi-Square p-value
    if chi2_stat <= 0.0:
        p_val = 1.0
    else:
        term = 2.0 / (9.0 * df)
        z = ((chi2_stat / df) ** (1.0 / 3.0) - (1.0 - term)) / math.sqrt(term)
        p_val = 0.5 * math.erfc(z / math.sqrt(2.0))
        p_val = max(0.0, min(1.0, p_val))

    accepted = (p_val >= 0.05)
    interpretation = (
        f"Chi-Square test (statistic={chi2_stat:.4f}, df={df}, p={p_val:.4f}): "
        f"{'Uniform distribution hypothesis ACCEPTED at alpha=0.05.' if accepted else 'Uniform distribution hypothesis REJECTED at alpha=0.05.'}"
    )

    return ChiSquareResult(
        num_samples=n,
        num_bins=num_bins,
        degrees_of_freedom=df,
        chi_square_statistic=chi2_stat,
        critical_value_95=crit_95,
        critical_value_99=crit_99,
        p_value=p_val,
        is_uniform_hypothesis_accepted=accepted,
        bins=bins,
        interpretation=interpretation,
    )


# -----------------------------------------------------------------------------
# Marsaglia Hyperplane Lattice Analysis
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class LatticePoint2D:
    """2D consecutive output pair (X_n, X_{n+1})."""

    x: float  # U_n = X_n / m
    y: float  # U_{n+1} = X_{n+1} / m
    raw_x: int  # X_n
    raw_y: int  # X_{n+1}


@dataclass(frozen=True)
class LatticePoint3D:
    """3D consecutive output triplet (X_n, X_{n+1}, X_{n+2})."""

    x: float  # U_n
    y: float  # U_{n+1}
    z: float  # U_{n+2}
    raw_x: int  # X_n
    raw_y: int  # X_{n+1}
    raw_z: int  # X_{n+2}


@dataclass(frozen=True)
class MarsagliaLatticeAnalysis:
    """Analysis of Marsaglia hyperplane lattice structures."""

    m: int
    a: int
    c: int
    sample_count: int
    max_hyperplanes_2d: int  # floor((2! * m)^(1/2))
    max_hyperplanes_3d: int  # floor((3! * m)^(1/3))
    points_2d: list[LatticePoint2D]
    points_3d: list[LatticePoint3D]
    theoretical_explanation: str
    pedagogical_insight: str


def marsaglia_max_hyperplanes(m: int, dimensions: int) -> int:
    """Computes Marsaglia's upper bound on the number of hyperplanes containing all d-tuples:

        floor((d! * m)^(1/d))
    """
    if not isinstance(dimensions, int) or isinstance(dimensions, bool) or dimensions <= 0:
        raise ValueError(f"dimensions must be a positive integer, got {dimensions}")
    if not isinstance(m, int) or isinstance(m, bool) or m <= 1:
        raise ValueError(f"m must be > 1, got {m}")

    fact = math.factorial(dimensions)
    bound = int(math.floor(pow(fact * m, 1.0 / dimensions) + 1e-12))
    return bound


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
    if count < 3:
        raise ValueError(f"count must be at least 3 to generate 2D and 3D points, got {count}")

    gen = LCGGenerator(m=m, a=a, c=c, seed=seed)
    seq = gen.generate(count, include_traces=False)
    vals = seq.values

    pts2d: list[LatticePoint2D] = []
    for i in range(len(vals) - 1):
        pts2d.append(
            LatticePoint2D(
                x=vals[i] / m,
                y=vals[i + 1] / m,
                raw_x=vals[i],
                raw_y=vals[i + 1],
            )
        )

    pts3d: list[LatticePoint3D] = []
    for i in range(len(vals) - 2):
        pts3d.append(
            LatticePoint3D(
                x=vals[i] / m,
                y=vals[i + 1] / m,
                z=vals[i + 2] / m,
                raw_x=vals[i],
                raw_y=vals[i + 1],
                raw_z=vals[i + 2],
            )
        )

    bound_2d = marsaglia_max_hyperplanes(m, 2)
    bound_3d = marsaglia_max_hyperplanes(m, 3)

    theo_expl = (
        f"Marsaglia (1968) proved that d-tuples produced by an LCG modulo m lie on at most "
        f"(d! * m)^(1/d) parallel hyperplanes. In 2D: <= {bound_2d} lines. In 3D: <= {bound_3d} planes."
    )
    pedagogical = (
        "This geometric structure ('planes in the hypercube') demonstrates the non-random linear correlation "
        "between consecutive pseudo-random numbers, rendering LCGs unsuitable for Monte Carlo simulations "
        "requiring high-dimensional independence, and critically flawed for cryptographic keys."
    )

    return MarsagliaLatticeAnalysis(
        m=m,
        a=a,
        c=c,
        sample_count=count,
        max_hyperplanes_2d=bound_2d,
        max_hyperplanes_3d=bound_3d,
        points_2d=pts2d,
        points_3d=pts3d,
        theoretical_explanation=theo_expl,
        pedagogical_insight=pedagogical,
    )


# -----------------------------------------------------------------------------
# Cryptanalysis: Algebraic State Reconstruction & Cracking
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class LCGCrackingResult:
    """Outcome of attempting to algebraically reconstruct LCG parameters."""

    recovered_m: int | None
    recovered_a: int | None
    recovered_c: int | None
    is_successful: bool
    predicted_next_values: list[int]
    reconstruction_method: str
    steps: list[str]
    explanation: str


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
    if not isinstance(outputs, list) or len(outputs) < 2:
        return LCGCrackingResult(
            recovered_m=known_m,
            recovered_a=known_a,
            recovered_c=None,
            is_successful=False,
            predicted_next_values=[],
            reconstruction_method="None",
            steps=["Failed: At least 2 consecutive outputs are required to attempt parameter reconstruction."],
            explanation="Insufficient outputs provided for cryptanalysis.",
        )

    # -------------------------------------------------------------------------
    # Scenario 1: Known m, Known a -> Recover c
    # -------------------------------------------------------------------------
    if known_m is not None and known_a is not None:
        m = known_m
        a = known_a
        c = (outputs[1] - a * outputs[0]) % m
        steps = [
            f"Known parameters: m = {m}, a = {a}",
            f"Using relation X_1 = (a * X_0 + c) mod m:",
            f"c = (X_1 - a * X_0) mod m = ({outputs[1]} - {a} * {outputs[0]}) mod {m} = {c}",
        ]

        # Verify against remaining outputs
        valid = all((a * outputs[i] + c) % m == outputs[i + 1] for i in range(len(outputs) - 1))
        if not valid:
            steps.append("Verification failed: Sequence outputs do not match recovered parameters.")
            return LCGCrackingResult(
                recovered_m=m,
                recovered_a=a,
                recovered_c=None,
                is_successful=False,
                predicted_next_values=[],
                reconstruction_method="Known-m, Known-a",
                steps=steps,
                explanation="Observed outputs inconsistent with given m and a.",
            )

        steps.append("Verification succeeded across all observed outputs.")
        predictions = _predict_forward(outputs[-1], m, a, c, predict_count)
        steps.append(f"Predicted next {predict_count} values: {predictions}")

        return LCGCrackingResult(
            recovered_m=m,
            recovered_a=a,
            recovered_c=c,
            is_successful=True,
            predicted_next_values=predictions,
            reconstruction_method="Known-m, Known-a",
            steps=steps,
            explanation=f"Successfully recovered increment c = {c} from 2 consecutive outputs.",
        )

    # -------------------------------------------------------------------------
    # Scenario 2: Known m, Unknown a, Unknown c -> Recover a and c
    # -------------------------------------------------------------------------
    if known_m is not None and known_a is None:
        m = known_m
        if len(outputs) < 3:
            return LCGCrackingResult(
                recovered_m=m,
                recovered_a=None,
                recovered_c=None,
                is_successful=False,
                predicted_next_values=[],
                reconstruction_method="Known-m",
                steps=["Failed: At least 3 consecutive outputs are required to recover multiplier a and increment c."],
                explanation="Need at least 3 outputs when multiplier a is unknown.",
            )

        steps = [f"Known parameter: m = {m}"]
        recovered_a: int | None = None
        recovered_c: int | None = None

        # Search for a coprime difference pair (d_i, d_{i+1})
        for i in range(len(outputs) - 2):
            d0 = (outputs[i + 1] - outputs[i]) % m
            d1 = (outputs[i + 2] - outputs[i + 1]) % m
            g = math.gcd(d0, m)
            if g == 1:
                inv_res = mod_inverse(d0, m)
                if inv_res.is_coprime and inv_res.inverse is not None:
                    cand_a = (d1 * inv_res.inverse) % m
                    cand_c = (outputs[i + 1] - cand_a * outputs[i]) % m
                    if all((cand_a * outputs[k] + cand_c) % m == outputs[k + 1] for k in range(len(outputs) - 1)):
                        recovered_a = cand_a
                        recovered_c = cand_c
                        steps.append(f"Found coprime difference at index {i}: d0 = {d0}, d1 = {d1}, gcd(d0, m) = 1")
                        steps.append(f"Computed a = (d1 * d0^(-1)) mod m = ({d1} * {inv_res.inverse}) mod {m} = {recovered_a}")
                        steps.append(f"Computed c = (X_{i+1} - a * X_{i}) mod m = {recovered_c}")
                        break

        # Fallback if no d0 was coprime, but d0 has small gcd
        if recovered_a is None:
            for i in range(len(outputs) - 2):
                d0 = (outputs[i + 1] - outputs[i]) % m
                d1 = (outputs[i + 2] - outputs[i + 1]) % m
                g = math.gcd(d0, m)
                if g > 1 and d1 % g == 0:
                    m_reduced = m // g
                    d0_red = d0 // g
                    d1_red = d1 // g
                    inv_red = mod_inverse(d0_red, m_reduced)
                    if inv_red.is_coprime and inv_red.inverse is not None:
                        a_base = (d1_red * inv_red.inverse) % m_reduced
                        for k in range(g):
                            cand_a = a_base + k * m_reduced
                            cand_c = (outputs[i + 1] - cand_a * outputs[i]) % m
                            if all((cand_a * outputs[j] + cand_c) % m == outputs[j + 1] for j in range(len(outputs) - 1)):
                                recovered_a = cand_a
                                recovered_c = cand_c
                                steps.append(f"Solved modular congruence with gcd(d0, m) = {g}: a = {recovered_a}, c = {recovered_c}")
                                break
                    if recovered_a is not None:
                        break

        if recovered_a is None or recovered_c is None:
            steps.append("Failed to recover valid parameters from differences.")
            return LCGCrackingResult(
                recovered_m=m,
                recovered_a=None,
                recovered_c=None,
                is_successful=False,
                predicted_next_values=[],
                reconstruction_method="Known-m",
                steps=steps,
                explanation="Could not invert differences modulo m to recover multiplier a.",
            )

        steps.append("Verification succeeded across all observed outputs.")
        predictions = _predict_forward(outputs[-1], m, recovered_a, recovered_c, predict_count)
        steps.append(f"Predicted next {predict_count} values: {predictions}")

        return LCGCrackingResult(
            recovered_m=m,
            recovered_a=recovered_a,
            recovered_c=recovered_c,
            is_successful=True,
            predicted_next_values=predictions,
            reconstruction_method="Known-m",
            steps=steps,
            explanation=f"Successfully recovered a = {recovered_a} and c = {recovered_c} using modular difference inversion.",
        )

    # -------------------------------------------------------------------------
    # Scenario 3: Unknown m, Unknown a, Unknown c -> Complete Recovery
    # -------------------------------------------------------------------------
    if len(outputs) < 6:
        return LCGCrackingResult(
            recovered_m=None,
            recovered_a=None,
            recovered_c=None,
            is_successful=False,
            predicted_next_values=[],
            reconstruction_method="Unknown-all",
            steps=["Failed: At least 6 consecutive outputs are required to recover unknown modulus m."],
            explanation="Need at least 6 consecutive outputs for determinant GCD analysis.",
        )

    steps = ["All parameters (m, a, c) unknown. Initiating difference determinant GCD analysis."]
    t = [outputs[i + 1] - outputs[i] for i in range(len(outputs) - 1)]
    u = [abs(t[i + 2] * t[i] - t[i + 1] ** 2) for i in range(len(t) - 2)]
    steps.append(f"Computed {len(t)} first differences: t_n = X_{{n+1}} - X_n")
    steps.append(f"Computed cross-determinants: u_n = |t_{{n+2}} * t_n - t_{{n+1}}^2|")

    g = u[0]
    for val in u[1:]:
        g = math.gcd(g, val)
    steps.append(f"Greatest common divisor of cross-determinants: gcd(u_0, ...) = {g}")

    if g <= 1:
        steps.append("Failed: Determinant GCD is <= 1. Cannot determine modulus.")
        return LCGCrackingResult(
            recovered_m=None,
            recovered_a=None,
            recovered_c=None,
            is_successful=False,
            predicted_next_values=[],
            reconstruction_method="Unknown-all",
            steps=steps,
            explanation="Determinant GCD is trivial (<= 1). Modulus reconstruction impossible.",
        )

    max_out = max(outputs)
    candidates: list[int] = []
    # Test divisors of g that exceed max observed output
    for k in range(1, 100):
        if g % k == 0:
            cand = g // k
            if cand > max_out:
                candidates.append(cand)

    recovered_m: int | None = None
    recovered_a: int | None = None
    recovered_c: int | None = None

    for cand_m in candidates:
        sub_crack = crack_lcg(outputs, known_m=cand_m, known_a=None, predict_count=predict_count)
        if sub_crack.is_successful and sub_crack.recovered_a is not None and sub_crack.recovered_c is not None:
            recovered_m = cand_m
            recovered_a = sub_crack.recovered_a
            recovered_c = sub_crack.recovered_c
            steps.append(f"Candidate modulus m = {cand_m} successfully verified!")
            steps.extend([f"  > {s}" for s in sub_crack.steps])
            break

    if recovered_m is None or recovered_a is None or recovered_c is None:
        steps.append("Failed: None of the candidate moduli produced a valid, consistent (a, c) parameter set.")
        return LCGCrackingResult(
            recovered_m=None,
            recovered_a=None,
            recovered_c=None,
            is_successful=False,
            predicted_next_values=[],
            reconstruction_method="Unknown-all",
            steps=steps,
            explanation="Could not find a valid parameter set matching all observed outputs.",
        )

    predictions = _predict_forward(outputs[-1], recovered_m, recovered_a, recovered_c, predict_count)
    steps.append(f"Predicted next {predict_count} values: {predictions}")

    return LCGCrackingResult(
        recovered_m=recovered_m,
        recovered_a=recovered_a,
        recovered_c=recovered_c,
        is_successful=True,
        predicted_next_values=predictions,
        reconstruction_method="Unknown-all",
        steps=steps,
        explanation=f"Full algebraic reconstruction succeeded! Recovered m = {recovered_m}, a = {recovered_a}, c = {recovered_c}.",
    )


def _predict_forward(x_last: int, m: int, a: int, c: int, count: int) -> list[int]:
    """Helper to predict future values from current state."""
    res: list[int] = []
    curr = x_last
    for _ in range(count):
        curr = (a * curr + c) % m
        res.append(curr)
    return res


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
    if not isinstance(m, int) or isinstance(m, bool) or m <= 1:
        raise ValueError(f"Modulus m must be an integer > 1, got {m}")
    if not isinstance(a, int) or isinstance(a, bool) or not (0 < a < m):
        raise ValueError(f"Multiplier a must satisfy 0 < a < m, got {a}")
    if not isinstance(c, int) or isinstance(c, bool) or not (0 <= c < m):
        raise ValueError(f"Increment c must satisfy 0 <= c < m, got {c}")
    if not isinstance(x_current, int) or isinstance(x_current, bool) or not (0 <= x_current < m):
        raise ValueError(f"x_current must satisfy 0 <= x_current < m, got {x_current}")
    if steps < 0:
        raise ValueError(f"steps must be non-negative, got {steps}")
    if steps == 0:
        return []

    inv_res = mod_inverse(a, m)
    if not inv_res.is_coprime or inv_res.inverse is None:
        raise ValueError(f"Multiplier a ({a}) is not invertible modulo m ({m}); gcd(a, m) != 1. Backward prediction is not unique.")

    a_inv = inv_res.inverse
    past_values: list[int] = []
    curr = x_current

    for _ in range(steps):
        prev = (a_inv * (curr - c)) % m
        past_values.append(prev)
        curr = prev

    return past_values
