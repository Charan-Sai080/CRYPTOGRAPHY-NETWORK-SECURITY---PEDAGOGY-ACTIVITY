from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas.lcg import (
    ChiSquareBinSchema,
    ChiSquareRequest,
    ChiSquareResponse,
    CycleDetectRequest,
    CycleDetectResponse,
    FloydStepTraceSchema,
    HullDobellConditionSchema,
    HullDobellRequest,
    HullDobellResponse,
    LCGCrackRequest,
    LCGCrackResponse,
    LCGGenerateRequest,
    LCGGenerateResponse,
    LCGPresetSchema,
    LCGStepTraceSchema,
    LatticePoint2DSchema,
    LatticePoint3DSchema,
    MarsagliaLatticeRequest,
    MarsagliaLatticeResponse,
)
from backend.core.lcg import (
    check_hull_dobell,
    chi_square_uniformity_test,
    crack_lcg,
    detect_cycle_floyd,
    generate_lcg_sequence,
    generate_marsaglia_lattice,
    get_preset,
    list_presets,
)

router = APIRouter(prefix="/lcg", tags=["Linear Congruential Generator"])


def _resolve_params(
    preset_name: str | None,
    m: int | None,
    a: int | None,
    c: int | None,
    seed: int | None = None,
) -> tuple[int, int, int, int]:
    """Resolves (m, a, c, seed) using preset fallback if provided."""
    if preset_name is not None:
        preset = get_preset(preset_name)
        resolved_m = m if m is not None else preset.m
        resolved_a = a if a is not None else preset.a
        resolved_c = c if c is not None else preset.c
        resolved_seed = seed if seed is not None else preset.default_seed
    else:
        if m is None or a is None or c is None:
            raise ValueError("Modulus 'm', multiplier 'a', and increment 'c' are required when preset_name is omitted.")
        resolved_m = m
        resolved_a = a
        resolved_c = c
        resolved_seed = 1 if seed is None else seed

    return resolved_m, resolved_a, resolved_c, resolved_seed


@router.get("/presets", response_model=list[LCGPresetSchema])
async def get_presets() -> list[LCGPresetSchema]:
    """Lists pre-configured historical and standard LCG presets."""
    presets = list_presets()
    return [
        LCGPresetSchema(
            name=p.key,
            description=p.description,
            m=p.m,
            a=p.a,
            c=p.c,
            default_seed=p.default_seed,
            is_full_period=p.is_full_period_expected,
        )
        for p in presets
    ]


@router.post("/generate", response_model=LCGGenerateResponse)
async def generate_sequence(req: LCGGenerateRequest) -> LCGGenerateResponse:
    """Generates an LCG pseudorandom sequence with arithmetic step traces."""
    m, a, c, seed = _resolve_params(req.preset_name, req.m, req.a, req.c, req.seed)
    seq_res = generate_lcg_sequence(m=m, a=a, c=c, seed=seed, count=req.count, include_traces=True)

    traces = [
        LCGStepTraceSchema(
            step=t.step_index,
            x_prev=t.x_prev,
            formula=t.formula,
            product=t.a_times_x,
            product_plus_c=t.plus_c,
            x_next=t.x_next,
            normalized=t.u_next,
        )
        for t in seq_res.traces
    ]

    return LCGGenerateResponse(
        parameters={"m": m, "a": a, "c": c, "seed": seed},
        values=seq_res.values,
        normalized=seq_res.normalized,
        traces=traces,
    )


@router.post("/hull-dobell", response_model=HullDobellResponse)
async def validate_hull_dobell(req: HullDobellRequest) -> HullDobellResponse:
    """Validates the 3 necessary and sufficient conditions of the Hull-Dobell Theorem."""
    m, a, c, _ = _resolve_params(req.preset_name, req.m, req.a, req.c, seed=0)
    hd_res = check_hull_dobell(m=m, a=a, c=c)

    c1 = hd_res.conditions[0]
    c2 = hd_res.conditions[1]
    c3 = hd_res.conditions[2]

    return HullDobellResponse(
        a=hd_res.a,
        c=hd_res.c,
        m=hd_res.m,
        is_full_period=hd_res.is_full_period,
        condition_1=HullDobellConditionSchema(
            satisfied=c1.passed,
            description=c1.title,
            detail=f"{c1.mathematical_statement}. {c1.details}",
        ),
        condition_2=HullDobellConditionSchema(
            satisfied=c2.passed,
            description=c2.title,
            detail=f"{c2.mathematical_statement}. {c2.details}",
        ),
        condition_3=HullDobellConditionSchema(
            satisfied=c3.passed,
            description=c3.title,
            detail=f"{c3.mathematical_statement}. {c3.details}",
        ),
        prime_factors_m=hd_res.prime_factors_m,
        explanation=hd_res.summary,
    )


@router.post("/cycle-detect", response_model=CycleDetectResponse)
async def detect_cycle(req: CycleDetectRequest) -> CycleDetectResponse:
    """Runs Floyd's cycle-finding (tortoise-and-hare) algorithm to identify period and start."""
    m, a, c, seed = _resolve_params(req.preset_name, req.m, req.a, req.c, req.seed)
    res = detect_cycle_floyd(m=m, a=a, c=c, seed=seed, max_iterations=req.max_steps)

    traces = [
        FloydStepTraceSchema(
            step=t.iteration,
            tortoise=t.tortoise_val,
            hare=t.hare_val,
        )
        for t in res.traces
    ]

    return CycleDetectResponse(
        period=res.period_length,
        cycle_start=res.cycle_start_index,
        total_steps=res.iterations_run,
        is_full_period=res.is_full_period,
        sample_cycle=res.sample_cycle_values,
        traces=traces,
    )


@router.post("/uniformity-test", response_model=ChiSquareResponse)
async def uniformity_test(req: ChiSquareRequest) -> ChiSquareResponse:
    """Executes Chi-Square goodness-of-fit uniformity test on an LCG sequence."""
    if req.sequence is not None:
        values = req.sequence
        m = req.m
        chi_res = chi_square_uniformity_test(values, num_bins=req.num_bins, m=m)
    else:
        m, a, c, seed = _resolve_params(req.preset_name, req.m, req.a, req.c, req.seed)
        seq_res = generate_lcg_sequence(m=m, a=a, c=c, seed=seed, count=req.count, include_traces=False)
        chi_res = chi_square_uniformity_test(seq_res.values, num_bins=req.num_bins, m=m)

    bins = [
        ChiSquareBinSchema(
            bin_index=b.bin_index,
            range_start=b.lower_bound,
            range_end=b.upper_bound,
            observed_count=b.observed_count,
            expected_count=b.expected_count,
            deviation=b.chi_square_contribution,
        )
        for b in chi_res.bins
    ]

    return ChiSquareResponse(
        chi_square_stat=chi_res.chi_square_statistic,
        degrees_of_freedom=chi_res.degrees_of_freedom,
        critical_value=chi_res.critical_value_95,
        p_value_approx=chi_res.p_value,
        is_uniform=chi_res.is_uniform_hypothesis_accepted,
        bins=bins,
        explanation=chi_res.interpretation,
    )


@router.post("/marsaglia-lattice", response_model=MarsagliaLatticeResponse)
async def marsaglia_lattice(req: MarsagliaLatticeRequest) -> MarsagliaLatticeResponse:
    """Generates 2D or 3D coordinate points and theoretical Marsaglia hyperplane bounds."""
    m, a, c, seed = _resolve_params(req.preset_name, req.m, req.a, req.c, req.seed)
    analysis = generate_marsaglia_lattice(m=m, a=a, c=c, seed=seed, count=req.count)

    if req.dimension == 2:
        points_2d = [LatticePoint2DSchema(x=p.x, y=p.y) for p in analysis.points_2d]
        points_3d: list[LatticePoint3DSchema] = []
        bound = analysis.max_hyperplanes_2d
    else:
        points_2d = []
        points_3d = [LatticePoint3DSchema(x=p.x, y=p.y, z=p.z) for p in analysis.points_3d]
        bound = analysis.max_hyperplanes_3d

    return MarsagliaLatticeResponse(
        dimension=req.dimension,
        count=req.count,
        theoretical_max_hyperplanes=bound,
        points_2d=points_2d,
        points_3d=points_3d,
        explanation=analysis.theoretical_explanation,
    )


@router.post("/crack", response_model=LCGCrackResponse)
async def crack(req: LCGCrackRequest) -> LCGCrackResponse:
    """Cracks internal multipliers (a, c) and predicts future outputs from observed sequence."""
    crack_res = crack_lcg(req.outputs, known_m=req.m, predict_count=1)
    predicted_next = crack_res.predicted_next_values[0] if crack_res.predicted_next_values else None

    return LCGCrackResponse(
        is_successful=crack_res.is_successful,
        m=req.m,
        recovered_a=crack_res.recovered_a,
        recovered_c=crack_res.recovered_c,
        predicted_next=predicted_next,
        steps=crack_res.steps,
        notes=crack_res.explanation,
    )
