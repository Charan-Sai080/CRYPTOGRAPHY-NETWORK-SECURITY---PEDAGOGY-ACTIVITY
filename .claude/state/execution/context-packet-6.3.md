# Context Packet 6.3: Linear Congruential Generator REST Router (`/api/v1/lcg/*`) with Typed Pydantic Models

## 1. Goal
Implement the REST API router and Pydantic schemas for the Linear Congruential Generator (LCG) and statistical/lattice cryptanalysis engine in `backend/api/v1/lcg.py` and `backend/api/schemas/lcg.py`.

The sub-milestone delivers endpoints for:
1. **LCG Presets Catalog** (`GET /api/v1/lcg/presets`): Lists pre-configured standard and historical generators (ANSI C, POSIX, MINSTD, Borland, Numerical Recipes, RANDU, ZX81) with modulus, multiplier, increment, and period properties.
2. **Traced Sequence Generation** (`POST /api/v1/lcg/generate`): Generates pseudorandom values with detailed arithmetic traces ($X_{n+1} = (a \cdot X_n + c) \pmod m$) and normalized floats $U_n = X_n / m \in [0, 1)$.
3. **Hull-Dobell Theorem Validator** (`POST /api/v1/lcg/hull-dobell`): Mathematical full-period verification checking:
   - Condition 1: $\gcd(c, m) = 1$.
   - Condition 2: Every prime factor of $m$ divides $a - 1$.
   - Condition 3: If $4 \mid m$, then $4 \mid (a - 1)$.
   Emits step-by-step diagnostic breakdown and prime factorization trees.
4. **Floyd's Cycle-Finding Algorithm** (`POST /api/v1/lcg/cycle-detect`): Tortoise-and-hare cycle detection returning exact empirical period $\lambda$, cycle start index $\mu$, sample cycle sequence, and execution traces.
5. **Chi-Square Uniformity Test** (`POST /api/v1/lcg/uniformity-test`): Statistical goodness-of-fit test dividing generated numbers into $k$ equal bins, calculating $\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$, critical value at $\alpha = 0.05$, and uniformity verdict.
6. **Marsaglia Hyperplane Lattice Visualizer** (`POST /api/v1/lcg/marsaglia-lattice`): Generates 2D $(X_n, X_{n+1})$ or 3D $(X_n, X_{n+1}, X_{n+2})$ coordinate points and theoretical Marsaglia hyperplane upper bound $\lfloor(d! \cdot m)^{1/d}\rfloor$.
7. **Algebraic State Reconstruction & Cracking** (`POST /api/v1/lcg/crack`): Reconstructs internal multipliers and increments $(a, c)$ from 3 consecutive outputs using modular linear equations, predicting the next number.

## 2. Allowed Files
* `backend/api/v1/lcg.py`
* `backend/api/schemas/lcg.py`
* `backend/api/schemas/__init__.py`
* `backend/api/v1/router.py` (to register lcg_router)

## 3. Strict Data Contracts & Signatures

### Schemas (`backend/api/schemas/lcg.py`)
```python
from __future__ import annotations

from typing import Literal
from pydantic import Field
from backend.api.schemas.common import BaseSchema


class LCGPresetSchema(BaseSchema):
    name: str
    description: str
    m: int
    a: int
    c: int
    default_seed: int
    is_full_period: bool


class LCGStepTraceSchema(BaseSchema):
    step: int
    x_prev: int
    formula: str
    product: int
    product_plus_c: int
    x_next: int
    normalized: float


class LCGGenerateRequest(BaseSchema):
    a: int | None = Field(None, description="Multiplier a")
    c: int | None = Field(None, description="Increment c")
    m: int | None = Field(None, ge=2, description="Modulus m > 1")
    seed: int = Field(1, ge=0, description="Initial seed X_0")
    count: int = Field(10, ge=1, le=10000, description="Number of values to generate")
    preset_name: str | None = Field(None, description="Optional preset name to load parameters from")


class LCGGenerateResponse(BaseSchema):
    parameters: dict[str, int]
    values: list[int]
    normalized: list[float]
    traces: list[LCGStepTraceSchema]


class HullDobellConditionSchema(BaseSchema):
    satisfied: bool
    description: str
    detail: str


class HullDobellRequest(BaseSchema):
    a: int | None = Field(None)
    c: int | None = Field(None)
    m: int | None = Field(None, ge=2)
    preset_name: str | None = Field(None)


class HullDobellResponse(BaseSchema):
    a: int
    c: int
    m: int
    is_full_period: bool
    condition_1: HullDobellConditionSchema
    condition_2: HullDobellConditionSchema
    condition_3: HullDobellConditionSchema
    prime_factors_m: list[int]
    explanation: str


class FloydStepTraceSchema(BaseSchema):
    step: int
    tortoise: int
    hare: int


class CycleDetectRequest(BaseSchema):
    a: int | None = Field(None)
    c: int | None = Field(None)
    m: int | None = Field(None, ge=2)
    seed: int = Field(1, ge=0)
    max_steps: int = Field(100000, ge=1, le=1000000)
    preset_name: str | None = Field(None)


class CycleDetectResponse(BaseSchema):
    period: int
    cycle_start: int
    total_steps: int
    is_full_period: bool
    sample_cycle: list[int]
    traces: list[FloydStepTraceSchema]


class ChiSquareBinSchema(BaseSchema):
    bin_index: int
    range_start: float
    range_end: float
    observed_count: int
    expected_count: float
    deviation: float


class ChiSquareRequest(BaseSchema):
    a: int | None = Field(None)
    c: int | None = Field(None)
    m: int | None = Field(None, ge=2)
    seed: int = Field(1, ge=0)
    count: int = Field(1000, ge=20, le=100000)
    num_bins: int = Field(10, ge=2, le=100)
    preset_name: str | None = Field(None)
    sequence: list[int] | None = Field(None, description="Optional custom sequence to test")


class ChiSquareResponse(BaseSchema):
    chi_square_stat: float
    degrees_of_freedom: int
    critical_value: float
    p_value_approx: float
    is_uniform: bool
    bins: list[ChiSquareBinSchema]
    explanation: str


class LatticePoint2DSchema(BaseSchema):
    x: float
    y: float


class LatticePoint3DSchema(BaseSchema):
    x: float
    y: float
    z: float


class MarsagliaLatticeRequest(BaseSchema):
    a: int | None = Field(None)
    c: int | None = Field(None)
    m: int | None = Field(None, ge=2)
    seed: int = Field(1, ge=0)
    count: int = Field(200, ge=10, le=5000)
    dimension: Literal[2, 3] = Field(2, description="Lattice dimension (2 or 3)")
    preset_name: str | None = Field(None)


class MarsagliaLatticeResponse(BaseSchema):
    dimension: int
    count: int
    theoretical_max_hyperplanes: int
    points_2d: list[LatticePoint2DSchema]
    points_3d: list[LatticePoint3DSchema]
    explanation: str


class LCGCrackRequest(BaseSchema):
    outputs: list[int] = Field(..., min_length=3, description="At least 3 consecutive outputs from the LCG")
    m: int = Field(..., ge=2, description="Modulus m of the generator")


class LCGCrackResponse(BaseSchema):
    is_successful: bool
    m: int
    recovered_a: int | None
    recovered_c: int | None
    predicted_next: int | None
    steps: list[str]
    notes: str
```

### Router Endpoints (`backend/api/v1/lcg.py`)
```python
from fastapi import APIRouter, HTTPException, status
# Core helpers imported from backend.core.lcg

router = APIRouter(prefix="/lcg", tags=["Linear Congruential Generator"])

@router.get("/presets", response_model=list[LCGPresetSchema])
async def get_presets() -> list[LCGPresetSchema]:
    ...

@router.post("/generate", response_model=LCGGenerateResponse)
async def generate_sequence(req: LCGGenerateRequest) -> LCGGenerateResponse:
    ...

@router.post("/hull-dobell", response_model=HullDobellResponse)
async def validate_hull_dobell(req: HullDobellRequest) -> HullDobellResponse:
    ...

@router.post("/cycle-detect", response_model=CycleDetectResponse)
async def detect_cycle(req: CycleDetectRequest) -> CycleDetectResponse:
    ...

@router.post("/uniformity-test", response_model=ChiSquareResponse)
async def uniformity_test(req: ChiSquareRequest) -> ChiSquareResponse:
    ...

@router.post("/marsaglia-lattice", response_model=MarsagliaLatticeResponse)
async def marsaglia_lattice(req: MarsagliaLatticeRequest) -> MarsagliaLatticeResponse:
    ...

@router.post("/crack", response_model=LCGCrackResponse)
async def crack(req: LCGCrackRequest) -> LCGCrackResponse:
    ...
```

## 4. Acceptance Criteria
1. `GET /api/v1/lcg/presets` returns all standard presets with verified parameters.
2. `POST /api/v1/lcg/generate` produces exact sequences with complete trace arithmetic matching $X_{n+1} = (a \cdot X_n + c) \pmod m$.
3. `POST /api/v1/lcg/hull-dobell` accurately validates full period on ANSI C and POSIX, and correctly detects non-full period on RANDU or custom faulty parameters.
4. `POST /api/v1/lcg/cycle-detect` correctly terminates and identifies cycle periods using Floyd's algorithm.
5. `POST /api/v1/lcg/uniformity-test` returns exact bin distributions and $\chi^2$ statistics.
6. `POST /api/v1/lcg/marsaglia-lattice` outputs coordinates bounded in $[0, 1)$ alongside accurate hyperplane upper bounds.
7. `POST /api/v1/lcg/crack` accurately recovers $a$ and $c$ from consecutive sequence numbers.
