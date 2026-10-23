"""Unit Tests for Linear Congruential Generator (LCG) Engine & Statistical/Lattice Analysis.

Covers:
- Parameter boundary validation & preset catalog
- Generator recurrence, float normalization, reset, and step traces
- Hull-Dobell Theorem three-condition verification & edge cases
- Floyd's cycle-finding (tortoise-and-hare) lambda/mu period analysis
- Multiplicative LCG analysis (prime modulus, power-of-two, non-coprime seeds)
- Chi-Square uniformity goodness-of-fit test and Wilson-Hilferty approximation
- Marsaglia 2D/3D lattice point generation and theoretical hyperplane bounds
- Algebraic state reconstruction / cryptanalytic cracking (known-m/a, known-m, unknown-all)
- Backward time reversal via modular inverse
"""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError
import pytest

from backend.core.lcg import (
    BinDistribution,
    ChiSquareBin,
    ChiSquareResult,
    CycleDetectionResult,
    FloydStepTrace,
    HullDobellCondition,
    HullDobellResult,
    LCGCrackingResult,
    LCGGenerator,
    LCGParameters,
    LCGPreset,
    LCGSequenceResult,
    LCGStepTrace,
    LatticePoint2D,
    LatticePoint3D,
    MarsagliaLatticeAnalysis,
    MultiplicativeLCGAnalysis,
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


class TestLCGParametersAndPresets:
    """Tests LCG parameter validation and historical presets library."""

    def test_valid_parameters(self) -> None:
        params = LCGParameters(m=16, a=5, c=1, seed=1)
        assert params.m == 16
        assert params.a == 5
        assert params.c == 1
        assert params.seed == 1

    def test_invalid_modulus(self) -> None:
        with pytest.raises(ValueError, match="Modulus m must be an integer > 1"):
            LCGParameters(m=1, a=1, c=1, seed=0)
        with pytest.raises(ValueError, match="Modulus m must be an integer > 1"):
            LCGParameters(m=0, a=1, c=1, seed=0)
        with pytest.raises(ValueError, match="Modulus m must be an integer > 1"):
            LCGParameters(m=-16, a=1, c=1, seed=0)

    def test_invalid_multiplier(self) -> None:
        with pytest.raises(ValueError, match="Multiplier a must be an integer 0 < a < m"):
            LCGParameters(m=16, a=0, c=1, seed=1)
        with pytest.raises(ValueError, match="Multiplier a must be an integer 0 < a < m"):
            LCGParameters(m=16, a=16, c=1, seed=1)
        with pytest.raises(ValueError, match="Multiplier a must be an integer 0 < a < m"):
            LCGParameters(m=16, a=20, c=1, seed=1)

    def test_invalid_increment(self) -> None:
        with pytest.raises(ValueError, match="Increment c must be an integer 0 <= c < m"):
            LCGParameters(m=16, a=5, c=-1, seed=1)
        with pytest.raises(ValueError, match="Increment c must be an integer 0 <= c < m"):
            LCGParameters(m=16, a=5, c=16, seed=1)

    def test_invalid_seed(self) -> None:
        with pytest.raises(ValueError, match="Seed must be an integer 0 <= seed < m"):
            LCGParameters(m=16, a=5, c=1, seed=-1)
        with pytest.raises(ValueError, match="Seed must be an integer 0 <= seed < m"):
            LCGParameters(m=16, a=5, c=1, seed=16)

    def test_multiplicative_zero_seed_rejection(self) -> None:
        with pytest.raises(ValueError, match="For multiplicative LCG .* seed cannot be 0"):
            LCGParameters(m=16, a=5, c=0, seed=0)

    def test_frozen_dataclass_immutability(self) -> None:
        params = LCGParameters(m=16, a=5, c=1, seed=1)
        with pytest.raises((FrozenInstanceError, AttributeError)):
            params.m = 32  # type: ignore[misc]

    def test_standard_presets_catalog(self) -> None:
        required_keys = [
            "ansi_c",
            "posix_rand48",
            "minstd",
            "minstd_revised",
            "numerical_recipes",
            "borland_c",
            "small_educational",
            "small_broken",
        ]
        for key in required_keys:
            assert key in STANDARD_PRESETS
            preset = STANDARD_PRESETS[key]
            assert preset.m > 1
            assert 0 < preset.a < preset.m
            assert 0 <= preset.c < preset.m
            assert 0 <= preset.default_seed < preset.m

    def test_get_preset_success_and_error(self) -> None:
        preset = get_preset("ansi_c")
        assert preset.key == "ansi_c"
        assert preset.m == 2147483648
        assert preset.a == 1103515245

        with pytest.raises(KeyError, match="Preset 'non_existent_preset' not found"):
            get_preset("non_existent_preset")

    def test_list_presets(self) -> None:
        presets = list_presets()
        assert len(presets) >= 8
        assert all(isinstance(p, LCGPreset) for p in presets)


class TestLCGGenerator:
    """Tests LCG sequence generation, float normalization, reset, and step tracing."""

    def test_generator_initialization(self) -> None:
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        assert gen.params.m == 16
        assert gen.current_state == 1
        assert gen.step_counter == 0

        # Default params
        gen_def = LCGGenerator()
        assert gen_def.params.m == 2147483648
        assert gen_def.current_state == 1

    def test_from_preset(self) -> None:
        gen1 = LCGGenerator.from_preset("small_educational")
        assert gen1.params.m == 16
        assert gen1.current_state == 1

        # Overridden seed
        gen2 = LCGGenerator.from_preset("small_educational", seed=7)
        assert gen2.params.m == 16
        assert gen2.current_state == 7

    def test_next_int_recurrence(self) -> None:
        # m=16, a=5, c=1, seed=1
        # X1 = (5*1 + 1) % 16 = 6
        # X2 = (5*6 + 1) % 16 = 31 % 16 = 15
        # X3 = (5*15 + 1) % 16 = 76 % 16 = 12
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        assert gen.next_int() == 6
        assert gen.next_int() == 15
        assert gen.next_int() == 12
        assert gen.step_counter == 3

    def test_next_float_bounds(self) -> None:
        gen = LCGGenerator.from_preset("numerical_recipes")
        for _ in range(100):
            u = gen.next_float()
            assert 0.0 <= u < 1.0

    def test_step_trace_structure(self) -> None:
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        tr = gen.step()
        assert tr.step_index == 1
        assert tr.x_prev == 1
        assert tr.a_times_x == 5
        assert tr.plus_c == 6
        assert tr.mod_m == 16
        assert tr.x_next == 6
        assert tr.u_next == 6 / 16
        assert "(5 * 1 + 1) mod 16 = 6 mod 16 = 6" in tr.formula

    def test_generator_reset(self) -> None:
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        gen.next_int()
        gen.next_int()
        assert gen.step_counter == 2
        assert gen.current_state != 1

        gen.reset()
        assert gen.step_counter == 0
        assert gen.current_state == 1

        gen.reset(seed=9)
        assert gen.step_counter == 0
        assert gen.current_state == 9

        with pytest.raises(ValueError, match="Seed must be an integer"):
            gen.reset(seed=-1)

    def test_generate_sequence_count_zero(self) -> None:
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        seq = gen.generate(0)
        assert seq.count == 0
        assert seq.values == []
        assert seq.normalized == []
        assert seq.traces == []

    def test_generate_sequence_negative_count(self) -> None:
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        with pytest.raises(ValueError, match="count must be a non-negative integer"):
            gen.generate(-5)

    def test_functional_generate_lcg_sequence(self) -> None:
        res1 = generate_lcg_sequence(m=16, a=5, c=1, seed=1, count=10)
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        res2 = gen.generate(count=10)
        assert res1.values == res2.values
        assert res1.normalized == res2.normalized
        assert len(res1.traces) == 10

    def test_known_test_vectors_minstd(self) -> None:
        # MINSTD: m = 2^31 - 1 = 2147483647, a = 16807, c = 0, seed = 1
        # Known standard test vectors: X1 = 16807, X2 = 282475249, X3 = 1622650073
        gen = LCGGenerator.from_preset("minstd", seed=1)
        assert gen.next_int() == 16807
        assert gen.next_int() == 282475249
        assert gen.next_int() == 1622650073

    def test_known_test_vectors_ansi_c(self) -> None:
        # ANSI C: m = 2^31, a = 1103515245, c = 12345, seed = 12345
        gen = LCGGenerator.from_preset("ansi_c", seed=12345)
        x1 = (1103515245 * 12345 + 12345) % 2147483648
        assert gen.next_int() == x1

    def test_iterable_protocol(self) -> None:
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        it = iter(gen)
        assert next(it) == 6
        assert next(it) == 15


class TestHullDobellValidator:
    """Tests Hull-Dobell Theorem three-condition evaluation."""

    def test_hull_dobell_full_period_presets(self) -> None:
        for key in ["ansi_c", "numerical_recipes", "borland_c", "small_educational"]:
            preset = STANDARD_PRESETS[key]
            res = check_hull_dobell(preset.m, preset.a, preset.c)
            assert res.is_full_period is True
            assert all(cond.passed for cond in res.conditions)

    def test_hull_dobell_condition_1_failure(self) -> None:
        # gcd(c, m) != 1
        # m = 16, a = 5, c = 2 -> gcd(2, 16) = 2 != 1
        res = check_hull_dobell(m=16, a=5, c=2)
        assert res.is_full_period is False
        assert res.conditions[0].passed is False
        assert res.conditions[0].condition_number == 1
        assert "gcd(2, 16) = 2" in res.conditions[0].mathematical_statement

    def test_hull_dobell_condition_2_failure(self) -> None:
        # Prime factor of m does not divide a - 1
        # m = 15 = 3 * 5, a = 4, c = 1 -> a - 1 = 3. 3 | 3, but 5 does not divide 3.
        res = check_hull_dobell(m=15, a=4, c=1)
        assert res.is_full_period is False
        assert res.conditions[0].passed is True  # gcd(1, 15) == 1
        assert res.conditions[1].passed is False  # 5 does not divide 3
        assert 5 in res.prime_factors_m

    def test_hull_dobell_condition_3_failure(self) -> None:
        # 4 | m, but 4 does not divide a - 1
        # m = 8, a = 3, c = 1 -> 4 | 8, a - 1 = 2, 4 does not divide 2.
        res = check_hull_dobell(m=8, a=3, c=1)
        assert res.is_full_period is False
        assert res.conditions[0].passed is True  # gcd(1, 8) == 1
        assert res.conditions[1].passed is True  # prime factor is 2, 2 | 2
        assert res.conditions[2].passed is False  # 4 does not divide 2

    def test_hull_dobell_condition_3_vacuous(self) -> None:
        # m % 4 != 0 -> Condition 3 vacuously satisfied
        # m = 14 = 2 * 7. 4 does not divide 14.
        res = check_hull_dobell(m=14, a=3, c=1)
        assert res.conditions[2].passed is True
        assert "vacuously satisfied" in res.conditions[2].details

    def test_multiplicative_lcg_fails_hull_dobell(self) -> None:
        # Multiplicative LCG (c = 0) has gcd(0, m) = m > 1, so Condition 1 always fails
        res = check_hull_dobell(m=2147483647, a=16807, c=0)
        assert res.is_full_period is False
        assert res.conditions[0].passed is False

    def test_invalid_modulus(self) -> None:
        with pytest.raises(ValueError, match="Modulus m must be an integer > 1"):
            check_hull_dobell(m=1, a=1, c=1)


class TestFloydCycleDetection:
    """Tests Floyd's cycle-finding (tortoise-and-hare) algorithm."""

    def test_floyd_full_period_generator(self) -> None:
        # small_educational: m = 16, a = 5, c = 1, seed = 1
        res = detect_cycle_floyd(m=16, a=5, c=1, seed=1)
        assert res.is_full_period is True
        assert res.period_length == 16
        assert res.cycle_start_index == 0
        assert len(res.sample_cycle_values) == 16
        assert set(res.sample_cycle_values) == set(range(16))

    def test_floyd_short_period_generator(self) -> None:
        # small_broken: m = 16, a = 4, c = 2, seed = 1
        res = detect_cycle_floyd(m=16, a=4, c=2, seed=1)
        assert res.is_full_period is False
        assert res.period_length < 16
        assert res.period_length == 1
        assert res.cycle_start_index == 2

    def test_floyd_pre_period_detection(self) -> None:
        # Sequence: X0 = 1, X1 = 6, X2 = 10, X3 = 10 -> mu = 2, lambda = 1
        res = detect_cycle_floyd(m=16, a=4, c=2, seed=1)
        assert res.cycle_start_index == 2
        assert res.period_length == 1

    def test_floyd_trace_steps(self) -> None:
        res = detect_cycle_floyd(m=16, a=5, c=1, seed=1, trace_steps=5)
        assert len(res.traces) <= 5
        assert isinstance(res.traces[0], FloydStepTrace)
        assert res.traces[0].iteration == 1

    def test_floyd_sample_cycle_values(self) -> None:
        # Period 4 generator: m = 16, a = 5, c = 4, seed = 0
        res = detect_cycle_floyd(m=16, a=5, c=4, seed=0)
        assert res.period_length == 4
        assert len(res.sample_cycle_values) == 4
        assert res.sample_cycle_values == [0, 4, 8, 12]

    def test_floyd_timeout_protection(self) -> None:
        with pytest.raises(TimeoutError, match="exceeded maximum allowed iterations"):
            detect_cycle_floyd(m=2147483648, a=1103515245, c=12345, seed=1, max_iterations=5)


class TestMultiplicativeLCGAnalysis:
    """Tests Multiplicative (Lehmer, c = 0) PRNG cycle analysis."""

    def test_multiplicative_prime_modulus(self) -> None:
        # Prime m = 17, a = 3 is primitive root mod 17 -> max period = 16
        res = analyze_multiplicative_lcg(m=17, a=3, seed=1)
        assert res.is_modulus_prime is True
        assert res.is_power_of_two is False
        assert res.theoretical_max_period == 16
        assert res.actual_period == 16
        assert res.achieves_max_period is True
        assert res.is_primitive_root is True
        assert res.is_seed_coprime is True

    def test_multiplicative_power_of_two_modulus(self) -> None:
        # m = 16 = 2^4, a = 5 (a % 8 == 5), odd seed = 1 -> max period = m / 4 = 4
        res = analyze_multiplicative_lcg(m=16, a=5, seed=1)
        assert res.is_modulus_prime is False
        assert res.is_power_of_two is True
        assert res.power_of_two_exponent == 4
        assert res.theoretical_max_period == 4
        assert res.actual_period == 4
        assert res.achieves_max_period is True

    def test_multiplicative_non_coprime_seed(self) -> None:
        # Seed shares factor with modulus
        res = analyze_multiplicative_lcg(m=16, a=5, seed=2)
        assert res.is_seed_coprime is False

    def test_multiplicative_zero_seed_error(self) -> None:
        with pytest.raises(ValueError, match="seed cannot be 0"):
            analyze_multiplicative_lcg(m=17, a=3, seed=0)


class TestChiSquareUniformity:
    """Tests Chi-Square goodness-of-fit statistical uniformity testing."""

    def test_uniform_distribution_acceptance(self) -> None:
        # 1000 samples from numerical_recipes
        gen = LCGGenerator.from_preset("numerical_recipes", seed=42)
        seq = gen.generate(1000)
        res = chi_square_uniformity_test(seq.normalized, num_bins=10)
        assert res.num_samples == 1000
        assert res.num_bins == 10
        assert res.degrees_of_freedom == 9
        assert res.p_value >= 0.05
        assert res.is_uniform_hypothesis_accepted is True

    def test_non_uniform_distribution_rejection(self) -> None:
        # Degenerate sequence with heavy bias into one bin
        samples = [0.1] * 1000
        res = chi_square_uniformity_test(samples, num_bins=10)
        assert res.p_value < 0.001
        assert res.is_uniform_hypothesis_accepted is False

    def test_bin_counts_and_frequencies(self) -> None:
        samples = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95] * 10
        res = chi_square_uniformity_test(samples, num_bins=10)
        total_obs = sum(b.observed_count for b in res.bins)
        assert total_obs == 100
        for b in res.bins:
            assert b.observed_count == 10
            assert b.expected_count == 10.0
            assert b.chi_square_contribution == 0.0
        assert res.chi_square_statistic == 0.0
        assert res.p_value == 1.0

    def test_integer_samples_with_m(self) -> None:
        # Test providing integer outputs and modulus m
        gen = LCGGenerator(m=16, a=5, c=1, seed=1)
        seq = gen.generate(160)
        res1 = chi_square_uniformity_test(seq.values, m=16, num_bins=4)
        res2 = chi_square_uniformity_test(seq.normalized, num_bins=4)
        assert res1.chi_square_statistic == res2.chi_square_statistic
        assert res1.p_value == res2.p_value

    def test_invalid_bins(self) -> None:
        with pytest.raises(ValueError, match="num_bins must be an integer >= 2"):
            chi_square_uniformity_test([0.5, 0.6], num_bins=1)

    def test_integer_samples_without_m_raises(self) -> None:
        with pytest.raises(ValueError, match="modulus m must be specified"):
            chi_square_uniformity_test([1, 2, 3])

    def test_empty_samples_raises(self) -> None:
        with pytest.raises(ValueError, match="samples list cannot be empty"):
            chi_square_uniformity_test([])


class TestMarsagliaLattice:
    """Tests Marsaglia hyperplane lattice point generation and theoretical bounds."""

    def test_lattice_points_count(self) -> None:
        res = generate_marsaglia_lattice(m=16, a=5, c=1, seed=1, count=100)
        assert res.sample_count == 100
        assert len(res.points_2d) == 99
        assert len(res.points_3d) == 98

    def test_lattice_points_coordinates(self) -> None:
        res = generate_marsaglia_lattice(m=16, a=5, c=1, seed=1, count=20)
        for pt2 in res.points_2d:
            assert 0.0 <= pt2.x < 1.0
            assert 0.0 <= pt2.y < 1.0
            assert pt2.raw_x == int(pt2.x * 16)
            assert pt2.raw_y == int(pt2.y * 16)

        for pt3 in res.points_3d:
            assert 0.0 <= pt3.x < 1.0
            assert 0.0 <= pt3.y < 1.0
            assert 0.0 <= pt3.z < 1.0

    def test_marsaglia_max_hyperplanes_formula(self) -> None:
        # m = 256, d = 2 -> floor(sqrt(2 * 256)) = floor(sqrt(512)) = 22
        assert marsaglia_max_hyperplanes(m=256, dimensions=2) == 22

        # m = 256, d = 3 -> floor((6 * 256)^(1/3)) = floor(1536^(1/3)) = 11
        assert marsaglia_max_hyperplanes(m=256, dimensions=3) == 11

        # m = 2^31 = 2147483648, d = 3 -> floor((6 * 2^31)^(1/3)) = 2344
        assert marsaglia_max_hyperplanes(m=2147483648, dimensions=3) == 2344

    def test_invalid_dimensions(self) -> None:
        with pytest.raises(ValueError, match="dimensions must be a positive integer"):
            marsaglia_max_hyperplanes(m=256, dimensions=0)
        with pytest.raises(ValueError, match="dimensions must be a positive integer"):
            marsaglia_max_hyperplanes(m=256, dimensions=-2)

    def test_invalid_count(self) -> None:
        with pytest.raises(ValueError, match="count must be at least 3"):
            generate_marsaglia_lattice(m=16, a=5, c=1, seed=1, count=2)


class TestLCGCrackingAndPredictability:
    """Tests cryptanalytic parameter reconstruction and state prediction."""

    def test_crack_c_known_m_and_a(self) -> None:
        m = 2147483648
        a = 1103515245
        c_true = 12345
        x0 = 42
        x1 = (a * x0 + c_true) % m

        res = crack_lcg(outputs=[x0, x1], known_m=m, known_a=a, predict_count=5)
        assert res.is_successful is True
        assert res.recovered_c == c_true
        assert res.recovered_m == m
        assert res.recovered_a == a
        assert len(res.predicted_next_values) == 5

        # Verify predictions match actual future states
        x_curr = x1
        for pred in res.predicted_next_values:
            x_curr = (a * x_curr + c_true) % m
            assert pred == x_curr

    def test_crack_a_and_c_known_m(self) -> None:
        m = 10007  # Prime
        a_true = 7654
        c_true = 321
        x = 99
        outputs = [x]
        for _ in range(4):
            x = (a_true * x + c_true) % m
            outputs.append(x)

        res = crack_lcg(outputs=outputs, known_m=m, predict_count=3)
        assert res.is_successful is True
        assert res.recovered_a == a_true
        assert res.recovered_c == c_true
        assert len(res.predicted_next_values) == 3

    def test_crack_all_unknown_m_a_c(self) -> None:
        m_true = 65537
        a_true = 1234
        c_true = 5678
        x = 42
        outputs = [x]
        for _ in range(8):
            x = (a_true * x + c_true) % m_true
            outputs.append(x)

        res = crack_lcg(outputs=outputs, predict_count=5)
        assert res.is_successful is True
        assert res.recovered_m == m_true
        assert res.recovered_a == a_true
        assert res.recovered_c == c_true

        # Verify predicted values match future ground truth
        x_curr = outputs[-1]
        for pred in res.predicted_next_values:
            x_curr = (a_true * x_curr + c_true) % m_true
            assert pred == x_curr

    def test_predict_lcg_backward(self) -> None:
        m = 65537
        a = 1234
        c = 5678
        # Sequence of 4 values
        x0 = 42
        x1 = (a * x0 + c) % m
        x2 = (a * x1 + c) % m
        x3 = (a * x2 + c) % m

        # Reverse from x3 backward 3 steps
        reversed_states = predict_lcg_backward(x_current=x3, m=m, a=a, c=c, steps=3)
        assert reversed_states == [x2, x1, x0]

    def test_predict_lcg_backward_non_coprime_raises(self) -> None:
        # gcd(a, m) != 1 -> non-invertible
        with pytest.raises(ValueError, match="Multiplier a .* is not invertible modulo m"):
            predict_lcg_backward(x_current=10, m=16, a=4, c=2, steps=1)

    def test_crack_insufficient_outputs(self) -> None:
        res = crack_lcg(outputs=[42])
        assert res.is_successful is False
        assert "Insufficient" in res.explanation
