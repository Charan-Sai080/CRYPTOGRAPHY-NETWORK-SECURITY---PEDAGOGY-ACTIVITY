# Context Packet 3.1: Core LCG Generator, Presets Library, and Sequence Extraction

## 1. Goal
Implement the core Linear Congruential Generator (LCG) state machine, standard historical presets library, sequence generation, and detailed per-step arithmetic traces in `backend/core/lcg.py` in pure Python 3.12+.

The implementation must provide:
1. Strict parameter validation for modulus $m$, multiplier $a$, increment $c$, and initial seed $X_0$.
2. Implementation of the canonical recurrence relation:
   $$X_{n+1} = (a \cdot X_n + c) \pmod m$$
   $$U_n = \frac{X_n}{m} \in [0.0, 1.0)$$
3. Catalog of historical and educational LCG presets (ANSI C, POSIX rand48, MINSTD / Park-Miller, MINSTD Revised, Numerical Recipes, Borland C/C++, Small Educational, and Small Broken).
4. Detailed per-step execution tracing (`LCGStepTrace`) recording input state, product, addition, modulo reduction, output state, normalized float, and formatted formula string.
5. Generator class (`LCGGenerator`) with iterable protocol and standalone functional sequence extraction (`generate_lcg_sequence`).

## 2. Allowed Files
* `backend/core/lcg.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class LCGParameters:
    m: int       # Modulus: must be integer > 1
    a: int       # Multiplier: must be integer 0 < a < m
    c: int       # Increment: must be integer 0 <= c < m
    seed: int    # Initial seed X_0: must be integer 0 <= seed < m

    def __post_init__(self) -> None:
        if not isinstance(self.m, int) or self.m <= 1:
            raise ValueError(f"Modulus m must be an integer > 1, got {self.m}")
        if not isinstance(self.a, int) or not (0 < self.a < self.m):
            raise ValueError(f"Multiplier a must be an integer 0 < a < m ({self.m}), got {self.a}")
        if not isinstance(self.c, int) or not (0 <= self.c < self.m):
            raise ValueError(f"Increment c must be an integer 0 <= c < m ({self.m}), got {self.c}")
        if not isinstance(self.seed, int) or not (0 <= self.seed < self.m):
            raise ValueError(f"Seed must be an integer 0 <= seed < m ({self.m}), got {self.seed}")
        if self.c == 0 and self.seed == 0:
            raise ValueError("For multiplicative LCG (c = 0), seed cannot be 0 (0 is an absorbing state).")


@dataclass(frozen=True)
class LCGPreset:
    key: str
    display_name: str
    m: int
    a: int
    c: int
    default_seed: int
    description: str
    is_full_period_expected: bool
    category: str  # "Historical", "Standard", "Educational", or "Vulnerable"


@dataclass
class LCGStepTrace:
    step_index: int       # 1-indexed sequence position
    x_prev: int           # X_n (input state to this step)
    a_times_x: int        # Intermediate multiplication: a * X_n
    plus_c: int           # Intermediate addition: a * X_n + c
    mod_m: int            # Modulus m
    x_next: int           # Output state X_{n+1} = (a * X_n + c) % m
    u_next: float         # Normalized float: X_{n+1} / m in [0.0, 1.0)
    formula: str          # Formatted pedagogical string, e.g. "(5 * 1 + 1) mod 16 = 6 mod 16 = 6"


@dataclass
class LCGSequenceResult:
    params: LCGParameters
    values: list[int]                    # [X_1, X_2, ..., X_count]
    normalized: list[float]              # [U_1, U_2, ..., U_count]
    traces: list[LCGStepTrace] = field(default_factory=list)
    count: int = 0


STANDARD_PRESETS: dict[str, LCGPreset] = {
    "ansi_c": LCGPreset(
        key="ansi_c",
        display_name="ANSI C / GCC rand()",
        m=2147483648,          # 2^31
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
        m=281474976710656,     # 2^48
        a=25214903917,         # 0x5DEECE66D
        c=11,                  # 0xB
        default_seed=1,
        description="POSIX standard 48-bit linear congruential generator with full period 2^48.",
        is_full_period_expected=True,
        category="Standard",
    ),
    "minstd": LCGPreset(
        key="minstd",
        display_name="MINSTD (Park & Miller 1988)",
        m=2147483647,          # 2^31 - 1 (Mersenne prime M31)
        a=16807,               # 7^5 (primitive root modulo 2^31 - 1)
        c=0,                   # Multiplicative LCG (c = 0)
        default_seed=1,
        description="Standard Minimal Lehmer generator over prime modulus 2^31 - 1. Max period m - 1.",
        is_full_period_expected=False,  # Max period is m - 1 because c = 0
        category="Historical",
    ),
    "minstd_revised": LCGPreset(
        key="minstd_revised",
        display_name="MINSTD Revised (Park, Miller, Stockmeyer 1993)",
        m=2147483647,          # 2^31 - 1
        a=48271,               # Revised primitive root with better spectral test score
        c=0,
        default_seed=1,
        description="Updated MINSTD multiplier recommended by Park, Miller, and Stockmeyer (1993).",
        is_full_period_expected=False,
        category="Historical",
    ),
    "numerical_recipes": LCGPreset(
        key="numerical_recipes",
        display_name="Numerical Recipes (Press et al.)",
        m=4294967296,          # 2^32
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
        m=4294967296,          # 2^32
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


class LCGGenerator:
    """Stateful Linear Congruential Generator with step tracing."""

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
        ...

    @property
    def params(self) -> LCGParameters:
        return self._params

    @property
    def current_state(self) -> int:
        return self._current_state

    @property
    def step_counter(self) -> int:
        return self._step_counter

    def reset(self, seed: int | None = None) -> None:
        """Resets the generator state to the initial seed or a new seed."""
        ...

    def step(self) -> LCGStepTrace:
        """Advances the generator state by 1 step, returning the full arithmetic trace."""
        ...

    def next_int(self) -> int:
        """Advances state and returns the next integer X_{n+1}."""
        ...

    def next_float(self) -> float:
        """Advances state and returns normalized float U_{n+1} = X_{n+1} / m in [0.0, 1.0)."""
        ...

    def generate(self, count: int, include_traces: bool = True) -> LCGSequenceResult:
        """Generates `count` successive pseudorandom values and traces."""
        ...


def generate_lcg_sequence(
    m: int,
    a: int,
    c: int,
    seed: int,
    count: int,
    include_traces: bool = True,
) -> LCGSequenceResult:
    """Functional convenience wrapper to generate count values from given LCG parameters."""
    ...


def get_preset(preset_key: str) -> LCGPreset:
    """Retrieves preset by key. Raises KeyError with available keys if not found."""
    ...


def list_presets() -> list[LCGPreset]:
    """Returns a list of all registered presets."""
    ...
```

## 4. Implementation Details & Pedagogical Requirements
1. **Mathematical Invariant**:
   - For every step $n$, $X_{n+1} = (a \cdot X_n + c) \pmod m$.
   - $U_{n+1} = X_{n+1} / m$.
   - The trace formula string should look like:
     `"(a * X_n + c) mod m = (5 * 1 + 1) mod 16 = 6 mod 16 = 6 (U = 0.375000)"`.
2. **Preset Registry**:
   - `get_preset("ansi_c")` must retrieve the preset object.
   - If an invalid key is requested, raise `KeyError(f"Preset '{preset_key}' not found. Available presets: {list(STANDARD_PRESETS.keys())}")`.
3. **Sequence Length**:
   - If `count == 0`, `generate()` returns an empty `LCGSequenceResult` with `values = []`, `normalized = []`, `traces = []`, `count = 0`.
   - If `count < 0`, raise `ValueError("count must be non-negative.")`.
4. **Float Normalization Bounds**:
   - $0.0 \le U_n < 1.0$ is guaranteed since $0 \le X_n \le m - 1 < m$.
