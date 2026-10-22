"""
Unit Tests for Core Number Theory Engine.

Verifies mathematical correctness, edge cases, Carmichael pseudoprimes,
tabular trace generation, and identity properties.
"""

import pytest
import math
from backend.core.number_theory import (
    extended_gcd,
    mod_inverse,
    mod_pow,
    is_prime,
    distinct_prime_factors,
    find_primitive_root,
    generate_safe_prime,
    string_to_int_blocks,
    int_blocks_to_string,
    sha256_digest_int,
    RFC_2409_1024_MODP,
    EDUCATIONAL_MODP_GROUPS
)


class TestExtendedGCD:
    def test_coprime_integers(self):
        res = extended_gcd(17, 13)
        assert res.gcd == 1
        assert res.identity_verified is True
        assert 17 * res.x + 13 * res.y == 1
        assert len(res.steps) > 0

    def test_common_divisor(self):
        res = extended_gcd(35, 15)
        assert res.gcd == 5
        assert res.identity_verified is True
        assert 35 * res.x + 15 * res.y == 5

    def test_zero_inputs(self):
        res1 = extended_gcd(0, 7)
        assert res1.gcd == 7
        assert res1.identity_verified is True

        res2 = extended_gcd(7, 0)
        assert res2.gcd == 7
        assert res2.identity_verified is True

    def test_negative_inputs(self):
        res = extended_gcd(-35, 15)
        assert res.gcd == 5
        assert res.identity_verified is True
        assert -35 * res.x + 15 * res.y == 5

    def test_large_integers(self):
        a = 123456789012345
        b = 987654321
        res = extended_gcd(a, b)
        assert res.gcd == math.gcd(a, b)
        assert res.identity_verified is True
        assert a * res.x + b * res.y == res.gcd


class TestModInverse:
    def test_standard_coprimes(self):
        # 3 * 4 = 12 = 1 mod 11
        res = mod_inverse(3, 11)
        assert res.is_coprime is True
        assert res.inverse == 4
        assert (3 * res.inverse) % 11 == 1

        # 7 * 15 = 105 = 1 mod 26
        res2 = mod_inverse(7, 26)
        assert res2.is_coprime is True
        assert res2.inverse == 15
        assert (7 * res2.inverse) % 26 == 1

    def test_non_coprime_fails_gracefully(self):
        res = mod_inverse(6, 9)
        assert res.is_coprime is False
        assert res.inverse is None
        assert res.gcd == 3
        assert "not coprime" in res.explanation

    def test_negative_input(self):
        # -3 mod 11 = 8 mod 11; 8 * 7 = 56 = 1 mod 11
        res = mod_inverse(-3, 11)
        assert res.is_coprime is True
        assert (-3 * res.inverse) % 11 == 1

    def test_modulus_one_edge_case(self):
        res = mod_inverse(5, 1)
        assert res.inverse == 0
        assert res.is_coprime is True

    def test_invalid_modulus(self):
        with pytest.raises(ValueError):
            mod_inverse(5, 0)
        with pytest.raises(ValueError):
            mod_inverse(5, -10)


class TestModPow:
    @pytest.mark.parametrize("base, exp, mod", [
        (2, 10, 1000),
        (3, 13, 17),
        (7, 256, 101),
        (123456, 65537, 1048583),
        (5, 0, 19),
        (10, 1, 13),
        (42, 100, 1),
    ])
    def test_matches_python_pow(self, base, exp, mod):
        res = mod_pow(base, exp, mod)
        expected = pow(base, exp, mod)
        assert res.result == expected
        if exp > 0 and mod > 1:
            assert len(res.steps) > 0
            assert res.binary_exponent == bin(exp)[2:]

    def test_invalid_parameters(self):
        with pytest.raises(ValueError):
            mod_pow(2, -5, 11)
        with pytest.raises(ValueError):
            mod_pow(2, 5, 0)


class TestMillerRabinPrimality:
    def test_small_known_primes(self):
        known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
        for p in known_primes:
            res = is_prime(p)
            assert res.is_prime is True, f"Failed on prime {p}"

    def test_small_known_composites(self):
        known_composites = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 25, 27, 33, 35]
        for c in known_composites:
            res = is_prime(c)
            assert res.is_prime is False, f"Failed on composite {c}"

    def test_carmichael_pseudoprimes_identified_as_composite(self):
        # Carmichael numbers fool simple Fermat primality tests (a^(n-1) = 1 mod n)
        # Miller-Rabin MUST detect them as composite.
        carmichaels = [561, 1105, 1729, 2465, 2821]
        for c in carmichaels:
            res = is_prime(c)
            assert res.is_prime is False, f"Miller-Rabin failed to detect Carmichael number {c} as composite!"

    def test_large_primes(self):
        # 2^31 - 1 (Mersenne prime M31)
        m31 = 2147483647
        res = is_prime(m31)
        assert res.is_prime is True
        assert res.rounds_executed > 0


class TestPrimeFactorizationAndPrimitiveRoot:
    def test_distinct_prime_factors(self):
        assert distinct_prime_factors(12) == [2, 3]
        assert distinct_prime_factors(100) == [2, 5]
        assert distinct_prime_factors(13) == [13]
        assert distinct_prime_factors(1) == []
        assert distinct_prime_factors(0) == []

    @pytest.mark.parametrize("p, expected_root", [
        (7, 3),
        (11, 2),
        (13, 2),
        (17, 3),
        (19, 2),
        (23, 5),
    ])
    def test_find_primitive_root(self, p, expected_root):
        res = find_primitive_root(p)
        assert res.primitive_root == expected_root
        
        # Verify it generates all elements of Z_p*
        generated = {pow(res.primitive_root, i, p) for i in range(1, p)}
        assert generated == set(range(1, p)), f"g={res.primitive_root} is not a full generator for p={p}"


class TestSafePrimeGenerator:
    def test_generate_small_safe_prime(self):
        p, q, logs = generate_safe_prime(10)
        assert p == 2 * q + 1
        assert is_prime(q).is_prime is True
        assert is_prime(p).is_prime is True
        assert len(logs) > 0


class TestEncodingAndHashing:
    def test_string_to_int_blocks_roundtrip(self):
        msg = "Pedagogy in Cryptography & Network Security 2026!"
        max_prime_bits = 32  # 32-bit prime blocks
        blocks = string_to_int_blocks(msg, max_prime_bits)
        assert len(blocks) > 0
        
        # Ensure all block values are strictly within range
        for b in blocks:
            assert b < (1 << (max_prime_bits - 1))

        # Reconstruct
        decoded = int_blocks_to_string(blocks, max_prime_bits)
        assert decoded == msg

    def test_sha256_digest_truncation(self):
        msg = "Hello Cryptography"
        full_digest = sha256_digest_int(msg)
        assert full_digest.bit_length() <= 256

        # 160-bit truncation for DSA
        truncated_160 = sha256_digest_int(msg, bit_limit=160)
        assert truncated_160.bit_length() <= 160


class TestRFCGroups:
    def test_rfc_2409_loaded(self):
        assert RFC_2409_1024_MODP["generator"] == 2
        assert RFC_2409_1024_MODP["bits"] == 1024
        assert RFC_2409_1024_MODP["prime"].bit_length() == 1024

    def test_educational_groups_verified(self):
        for grp in EDUCATIONAL_MODP_GROUPS:
            p = grp["prime"]
            g = grp["generator"]
            assert is_prime(p).is_prime is True
            # Verify generator order
            assert pow(g, p - 1, p) == 1
