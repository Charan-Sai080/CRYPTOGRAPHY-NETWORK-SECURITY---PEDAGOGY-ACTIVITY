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
