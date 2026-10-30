"""Exhaustive Pytest 8.x Suite for Digital Signature Algorithm (DSA) & Nonce-Reuse Exploit.

Covers:
1. Domain parameter validation and preset catalog.
2. Subgroup generator derivation and dynamic domain parameter generation.
3. Asymmetric key pair generation (CSPRNG and deterministic).
4. FIPS 186-4 message hashing, bit truncation, and traced signing.
5. FIPS 186-4 resampling behavior (r = 0, s = 0) and retry budget exhaustion.
6. Signature verification mathematics, modular inversion, and step traces.
7. Interactive single-bit tampering detection (message, signature r, signature s).
8. Sony PlayStation 3 fail0verflow nonce-reuse private key extraction.
9. Immutability of dataclasses and comprehensive domain exception handling.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from unittest.mock import patch

import pytest

from backend.core.dsa import (
    DSA_MATHEMATICAL_PROOF,
    DSA_NONCE_REUSE_ALGEBRAIC_PROOF,
    DSA_PRESETS,
    DSACryptanalysisError,
    DSADomainParams,
    DSAError,
    DSAKeyPair,
    DSANonceReuseExploitResult,
    DSAPrivateKey,
    DSAPublicKey,
    DSASignResult,
    DSASignTrace,
    DSASignature,
    DSASignatureError,
    DSAVerificationError,
    DSAVerificationResult,
    DSAVerifyTrace,
    InvalidDomainParametersError,
    InvalidKeyError,
    ResamplingFailureError,
    SONY_PS3_HISTORICAL_CONTEXT,
    TamperDetectionResult,
    derive_generator,
    detect_tampering,
    exploit_nonce_reuse,
    exploit_nonce_reuse_from_hashes,
    generate_dsa_domain,
    generate_ephemeral_k,
    generate_key_pair,
    get_dsa_preset,
    list_dsa_presets,
    sign_hash_int,
    sign_message,
    tamper_message_bit,
    tamper_signature_component,
    verify_domain_params,
    verify_hash_int,
    verify_key_pair,
    verify_message,
)
from backend.core.number_theory import sha256_digest_int


# ---------------------------------------------------------------------------
# 1. TestDSADomainParamsAndPresets
# ---------------------------------------------------------------------------


class TestDSADomainParamsAndPresets:
    """Tests DSA domain parameter validation, presets, and generator derivation."""

    def test_valid_domain_params_init(self) -> None:
        """Validates successful initialization with primes p, q and valid generator g."""
        domain = DSADomainParams(p=607, q=101, g=64, name="Test Domain")
        assert domain.p == 607
        assert domain.q == 101
        assert domain.g == 64
        assert domain.p_bits == 10
        assert domain.q_bits == 7
        assert domain.name == "Test Domain"
        assert verify_domain_params(domain) is True

    def test_invalid_modulus_rejection(self) -> None:
        """Modulus p <= 2 or non-prime raises InvalidDomainParametersError."""
        # Non-positive / trivial modulus
        with pytest.raises(InvalidDomainParametersError, match="Modulus p must be an integer > 2"):
            DSADomainParams(p=2, q=101, g=64)

        with pytest.raises(InvalidDomainParametersError, match="Modulus p must be an integer > 2"):
            DSADomainParams(p=-5, q=101, g=64)

        # Composite modulus (e.g., 609 = 3 * 7 * 29, q=101)
        with pytest.raises(InvalidDomainParametersError, match="Modulus p must be a prime number"):
            DSADomainParams(p=609, q=101, g=64)

    def test_subprime_divisibility_rejection(self) -> None:
        """Failure when (p - 1) % q != 0 raises InvalidDomainParametersError."""
        # p=607 is prime, q=103 is prime, but (607 - 1) % 103 = 606 % 103 = 91 != 0
        with pytest.raises(InvalidDomainParametersError, match="Subgroup order q .* must divide p - 1"):
            DSADomainParams(p=607, q=103, g=2)

    def test_subprime_non_prime_rejection(self) -> None:
        """Subgroup order q <= 1 or non-prime raises InvalidDomainParametersError."""
        with pytest.raises(InvalidDomainParametersError, match="Subgroup divisor q must be an integer > 1"):
            DSADomainParams(p=607, q=1, g=64)

        # Composite q (e.g., q=6 divides 606, but 6 is composite)
        with pytest.raises(InvalidDomainParametersError, match="Subgroup divisor q must be a prime number"):
            DSADomainParams(p=607, q=6, g=64)

    def test_generator_out_of_bounds(self) -> None:
        """Generator g <= 1 or g >= p raises InvalidDomainParametersError."""
        with pytest.raises(InvalidDomainParametersError, match="Generator g must be in range"):
            DSADomainParams(p=607, q=101, g=1)

        with pytest.raises(InvalidDomainParametersError, match="Generator g must be in range"):
            DSADomainParams(p=607, q=101, g=607)

    def test_generator_order_verification(self) -> None:
        """Confirms g^q == 1 mod p for all presets, and rejects invalid generator orders."""
        for name, preset in DSA_PRESETS.items():
            assert pow(preset.g, preset.q, preset.p) == 1, f"Generator order failed for {name}"

        # Valid range [2, p - 1] but g^q != 1 mod p
        with pytest.raises(InvalidDomainParametersError, match="Generator g of order q must satisfy g\\^q mod p == 1"):
            DSADomainParams(p=607, q=101, g=2)

    def test_all_standard_presets_load(self) -> None:
        """Verifies that all 4 catalog presets load and pass verification."""
        expected_presets = ["fips_186_4_1024_160", "educational_10", "educational_16", "educational_24"]
        for preset_name in expected_presets:
            preset = get_dsa_preset(preset_name)
            assert isinstance(preset, DSADomainParams)
            assert verify_domain_params(preset) is True
            assert preset.p_bits >= preset.q_bits

        # Check FIPS bit lengths specifically
        fips = get_dsa_preset("fips_186_4_1024_160")
        assert fips.p_bits == 1024
        assert fips.q_bits == 160

    def test_get_preset_unknown_raises_key_error(self) -> None:
        """Unknown preset name raises KeyError."""
        with pytest.raises(KeyError, match="Unknown DSA preset 'non_existent_preset'"):
            get_dsa_preset("non_existent_preset")

    def test_list_dsa_presets(self) -> None:
        """Returns list of registered DSADomainParams."""
        presets = list_dsa_presets()
        assert len(presets) == len(DSA_PRESETS)
        assert all(isinstance(p, DSADomainParams) for p in presets)

    def test_derive_generator(self) -> None:
        """Confirms generator derivation g = h^((p - 1)/q) mod p produces elements of order q."""
        p = 607
        q = 101
        h = 2
        g = derive_generator(p, q, h)
        assert g == 64
        assert pow(g, q, p) == 1

        # Out of bounds h
        with pytest.raises(InvalidDomainParametersError, match="Base h must satisfy 1 < h < p - 1"):
            derive_generator(p, q, 1)

        with pytest.raises(InvalidDomainParametersError, match="Base h must satisfy 1 < h < p - 1"):
            derive_generator(p, q, p - 1)

    def test_generate_dsa_domain_dynamic(self) -> None:
        """Dynamically generates small domain parameters and confirms validity."""
        domain, logs = generate_dsa_domain(p_bits=16, q_bits=8)
        assert isinstance(domain, DSADomainParams)
        assert domain.p_bits == 16
        assert domain.q_bits == 8
        assert verify_domain_params(domain) is True
        assert len(logs) >= 3

        # Invalid bit lengths
        with pytest.raises(InvalidDomainParametersError, match="Modulus bit length p_bits .* must be strictly greater"):
            generate_dsa_domain(p_bits=8, q_bits=8)

        with pytest.raises(InvalidDomainParametersError, match="Minimum supported bit lengths"):
            generate_dsa_domain(p_bits=3, q_bits=2)

    def test_frozen_dataclass_immutability(self) -> None:
        """Ensures DSADomainParams attributes cannot be mutated."""
        domain = get_dsa_preset("educational_10")
        with pytest.raises(FrozenInstanceError):
            domain.p = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 2. TestDSAKeyGeneration
# ---------------------------------------------------------------------------


class TestDSAKeyGeneration:
    """Tests key pair generation, bounds checking, and validation."""

    def test_generate_key_pair_random(self) -> None:
        """Generates key pair with CSPRNG and verifies 1 <= x < q and y = g^x mod p."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain)
        assert isinstance(key_pair, DSAKeyPair)
        assert 1 <= key_pair.private_key.x < domain.q
        assert 1 < key_pair.public_key.y < domain.p
        assert key_pair.public_key.y == pow(domain.g, key_pair.private_key.x, domain.p)
        assert verify_key_pair(key_pair) is True

    def test_generate_key_pair_deterministic_seed(self) -> None:
        """Generates key pair with fixed seed_x and confirms expected public key."""
        domain = get_dsa_preset("educational_10")
        seed_x = 42
        key_pair = generate_key_pair(domain, seed_x=seed_x)
        assert key_pair.private_key.x == seed_x
        expected_y = pow(domain.g, seed_x, domain.p)
        assert key_pair.public_key.y == expected_y

    def test_private_key_bounds_validation(self) -> None:
        """Private key x < 1 or x >= q raises InvalidKeyError."""
        domain = get_dsa_preset("educational_10")
        with pytest.raises(InvalidKeyError, match="Private key x must satisfy 1 <= x < q"):
            DSAPrivateKey(p=domain.p, q=domain.q, g=domain.g, x=0)

        with pytest.raises(InvalidKeyError, match="Private key x must satisfy 1 <= x < q"):
            DSAPrivateKey(p=domain.p, q=domain.q, g=domain.g, x=domain.q)

        with pytest.raises(InvalidKeyError, match="Private key x must satisfy 1 <= x < q"):
            generate_key_pair(domain, seed_x=0)

    def test_public_key_bounds_validation(self) -> None:
        """Public key y < 2 or y >= p raises InvalidKeyError."""
        domain = get_dsa_preset("educational_10")
        with pytest.raises(InvalidKeyError, match="Public key y must satisfy 1 < y < p"):
            DSAPublicKey(p=domain.p, q=domain.q, g=domain.g, y=1)

        with pytest.raises(InvalidKeyError, match="Public key y must satisfy 1 < y < p"):
            DSAPublicKey(p=domain.p, q=domain.q, g=domain.g, y=domain.p)

    def test_verify_key_pair_valid(self) -> None:
        """Returns True for authentic key pair."""
        domain = get_dsa_preset("educational_16")
        kp = generate_key_pair(domain, seed_x=123)
        assert verify_key_pair(kp) is True

    def test_verify_key_pair_mismatch(self) -> None:
        """Detects corrupted key pairs, returning False."""
        domain = get_dsa_preset("educational_10")
        kp = generate_key_pair(domain, seed_x=42)
        # Corrupted public key y
        corrupted_pub = DSAPublicKey(p=domain.p, q=domain.q, g=domain.g, y=(kp.public_key.y + 1) % domain.p)
        corrupted_kp = DSAKeyPair(public_key=corrupted_pub, private_key=kp.private_key, domain_params=domain)
        assert verify_key_pair(corrupted_kp) is False

        # Domain mismatch
        other_dom = get_dsa_preset("educational_16")
        mismatched_kp = DSAKeyPair(public_key=kp.public_key, private_key=kp.private_key, domain_params=other_dom)
        assert verify_key_pair(mismatched_kp) is False


# ---------------------------------------------------------------------------
# 3. TestDSASigning
# ---------------------------------------------------------------------------


class TestDSASigning:
    """Tests signing engine, hash truncation, determinism, and FIPS 186-4 resampling."""

    def test_sign_message_all_presets(self) -> None:
        """Verifies successful signing across all presets."""
        message = "DSA Pedagogy Specification Test"
        for preset_name in DSA_PRESETS:
            domain = get_dsa_preset(preset_name)
            key_pair = generate_key_pair(domain, seed_x=17)
            result = sign_message(message, key_pair.private_key)
            assert isinstance(result, DSASignResult)
            assert isinstance(result.signature, DSASignature)
            assert 0 < result.signature.r < domain.q
            assert 0 < result.signature.s < domain.q
            assert result.trace.z == sha256_digest_int(message, bit_limit=domain.q_bits)

    def test_sign_with_deterministic_k(self) -> None:
        """Generates identical signatures when given deterministic seed_k."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Deterministic Nonce Test"
        seed_k = 29

        sig1 = sign_message(message, key_pair.private_key, seed_k=seed_k)
        sig2 = sign_message(message, key_pair.private_key, seed_k=seed_k)

        assert sig1.signature.r == sig2.signature.r
        assert sig1.signature.s == sig2.signature.s
        assert sig1.trace.k == seed_k
        assert sig2.trace.k == seed_k

    def test_hash_truncation_fips_186_4(self) -> None:
        """Confirms message digest is properly left-truncated to N = min(bit_length(q), 256) bits."""
        # Educational 10-bit group has q=101, which is 7 bits long
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=5)
        message = "Truncation Test Message"

        res = sign_message(message, key_pair.private_key, seed_k=13)
        assert res.trace.z.bit_length() <= domain.q_bits

        # For 160-bit q, z must be <= 160 bits
        fips_dom = get_dsa_preset("fips_186_4_1024_160")
        fips_kp = generate_key_pair(fips_dom, seed_x=12345)
        fips_res = sign_message(message, fips_kp.private_key, seed_k=9999)
        assert fips_res.trace.z.bit_length() <= 160

    def test_sign_trace_attributes(self) -> None:
        """Validates that DSASignTrace populates all step fields, intermediate products, and formulas."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        res = sign_message("Trace Testing", key_pair.private_key, seed_k=29)

        trace = res.trace
        assert isinstance(trace, DSASignTrace)
        assert trace.message == "Trace Testing"
        assert len(trace.message_hash_hex) == 64
        assert trace.k == 29
        assert trace.k_inv == pow(29, -1, domain.q)
        assert trace.gk_mod_p == pow(domain.g, 29, domain.p)
        assert trace.r == trace.gk_mod_p % domain.q
        assert trace.xr_mod_q == (42 * trace.r) % domain.q
        assert trace.z_plus_xr == trace.z + 42 * trace.r
        assert trace.s == (trace.k_inv * trace.z_plus_xr) % domain.q
        assert "r = (g^k mod p) mod q" in trace.r_formula
        assert "s = (k^-1 * (z + x * r)) mod q" in trace.s_formula
        assert trace.attempts >= 1

    def test_resampling_when_r_or_s_is_zero(self) -> None:
        """Tests that the signing loop resamples ephemeral secrets until r > 0 and s > 0."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        # For seed_k = 29, r = pow(64, 29, 607) % 101 = 45.
        # If z = (-x * r) % q = (-42 * 45) % 101 = (-1890) % 101 = 29.
        # Then z + x*r = 29 + 1890 = 1919 % 101 = 0, causing s = 0 on attempt 1!
        r_first = pow(domain.g, 29, domain.p) % domain.q
        z_causing_s_zero = (-key_pair.private_key.x * r_first) % domain.q

        # Signing should notice s == 0, resample a new random k on attempt 2, and succeed!
        res = sign_hash_int(
            z=z_causing_s_zero,
            private_key=key_pair.private_key,
            seed_k=29,
            max_attempts=10,
        )
        assert res.trace.attempts >= 2
        assert res.signature.s > 0
        assert res.signature.r > 0

    def test_max_attempts_exceeded(self) -> None:
        """Raises ResamplingFailureError if maximum retry budget is exhausted."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        r_first = pow(domain.g, 29, domain.p) % domain.q
        z_causing_s_zero = (-key_pair.private_key.x * r_first) % domain.q

        # When max_attempts = 1, attempt 1 produces s = 0 and terminates immediately with ResamplingFailureError
        with pytest.raises(ResamplingFailureError, match="Exceeded maximum resampling attempts"):
            sign_hash_int(
                z=z_causing_s_zero,
                private_key=key_pair.private_key,
                seed_k=29,
                max_attempts=1,
            )

    def test_generate_ephemeral_k_bounds(self) -> None:
        """Confirms generate_ephemeral_k enforces 1 <= k < q."""
        q = 101
        for _ in range(50):
            k = generate_ephemeral_k(q)
            assert 1 <= k < q

        assert generate_ephemeral_k(q, seed_k=50) == 50

        with pytest.raises(DSASignatureError, match="Ephemeral nonce k must satisfy 1 <= k < q"):
            generate_ephemeral_k(q, seed_k=0)

        with pytest.raises(DSASignatureError, match="Ephemeral nonce k must satisfy 1 <= k < q"):
            generate_ephemeral_k(q, seed_k=q)


# ---------------------------------------------------------------------------
# 4. TestDSAVerification
# ---------------------------------------------------------------------------


class TestDSAVerification:
    """Tests signature verification pipeline, edge cases, and arithmetic proofs."""

    def test_verify_valid_signature_all_presets(self) -> None:
        """Signs and verifies messages across all domain presets."""
        message = "Verification Across All Presets"
        for preset_name in DSA_PRESETS:
            domain = get_dsa_preset(preset_name)
            key_pair = generate_key_pair(domain, seed_x=19)
            sign_res = sign_message(message, key_pair.private_key)
            verify_res = verify_message(message, sign_res.signature, key_pair.public_key)

            assert isinstance(verify_res, DSAVerificationResult)
            assert verify_res.is_valid is True
            assert "verified successfully" in verify_res.reason.lower()
            assert verify_res.trace is not None
            assert verify_res.trace.is_valid is True
            assert verify_res.trace.v == sign_res.signature.r

    def test_reject_signature_out_of_bounds(self) -> None:
        """Verifies rejection when r <= 0, r >= q, s <= 0, or s >= q."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)

        # DSASignature dataclass enforces 0 < r, s < q
        with pytest.raises(DSASignatureError, match="Signature component r must satisfy 0 < r < q"):
            DSASignature(r=0, s=10, q=domain.q)

        with pytest.raises(DSASignatureError, match="Signature component r must satisfy 0 < r < q"):
            DSASignature(r=domain.q, s=10, q=domain.q)

        with pytest.raises(DSASignatureError, match="Signature component s must satisfy 0 < s < q"):
            DSASignature(r=10, s=0, q=domain.q)

        with pytest.raises(DSASignatureError, match="Signature component s must satisfy 0 < s < q"):
            DSASignature(r=10, s=domain.q, q=domain.q)

        # When signature with larger q is tested against a smaller q public key
        sig_large = DSASignature(r=150, s=50, q=257)
        verify_res = verify_hash_int(z=12, signature=sig_large, public_key=key_pair.public_key)
        assert verify_res.is_valid is False
        assert "out of bounds" in verify_res.reason.lower()

    def test_reject_wrong_message(self) -> None:
        """Verification fails when message text does not match signature."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Original Authentic Message"
        sign_res = sign_message(message, key_pair.private_key)

        wrong_message = "Forged Tampered Message"
        verify_res = verify_message(wrong_message, sign_res.signature, key_pair.public_key)
        assert verify_res.is_valid is False
        assert "verification failed" in verify_res.reason.lower()
        assert verify_res.trace is not None
        assert verify_res.trace.v != sign_res.signature.r

    def test_reject_wrong_public_key(self) -> None:
        """Verification fails when valid signature is checked against a different public key."""
        domain = get_dsa_preset("educational_10")
        kp1 = generate_key_pair(domain, seed_x=42)
        kp2 = generate_key_pair(domain, seed_x=43)

        message = "Key Specific Message"
        sign_res = sign_message(message, kp1.private_key)

        # Verifying against kp2 public key
        verify_res = verify_message(message, sign_res.signature, kp2.public_key)
        assert verify_res.is_valid is False
        assert verify_res.trace is not None
        assert verify_res.trace.v != sign_res.signature.r

    def test_verification_trace_fields_and_proof(self) -> None:
        """Inspects DSAVerifyTrace verifying that w, u1, u2, v, and proof strings are populated."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Trace Field Test"
        sign_res = sign_message(message, key_pair.private_key, seed_k=29)
        verify_res = verify_message(message, sign_res.signature, key_pair.public_key)

        trace = verify_res.trace
        assert trace is not None
        assert trace.r == sign_res.signature.r
        assert trace.s == sign_res.signature.s
        assert trace.w == pow(sign_res.signature.s, -1, domain.q)
        assert trace.u1 == (trace.z * trace.w) % domain.q
        assert trace.u2 == (trace.r * trace.w) % domain.q
        assert trace.gu1_mod_p == pow(domain.g, trace.u1, domain.p)
        assert trace.yu2_mod_p == pow(key_pair.public_key.y, trace.u2, domain.p)
        assert trace.v == ((trace.gu1_mod_p * trace.yu2_mod_p) % domain.p) % domain.q
        assert trace.is_valid is True
        assert "w = s^-1 mod q" in trace.w_formula
        assert "u1 = (z * w) mod q" in trace.u1_formula
        assert "u2 = (r * w) mod q" in trace.u2_formula
        assert "v = ((g^u1 * y^u2) mod p) mod q" in trace.v_formula
        assert "v == r" in trace.verification_formula
        assert trace.mathematical_proof == DSA_MATHEMATICAL_PROOF


# ---------------------------------------------------------------------------
# 5. TestDSATamperingDetection
# ---------------------------------------------------------------------------


class TestDSATamperingDetection:
    """Tests message and signature mutation helpers and side-by-side detection."""

    def test_tamper_message_bit_flips_single_bit(self) -> None:
        """Confirms tamper_message_bit flips exactly 1 bit across multiple bit indices."""
        message = "DSA Pedagogy Single Bit Tamper Testing"
        for bit_idx in range(16):
            tampered = tamper_message_bit(message, bit_index=bit_idx)
            assert tampered != message
            b_orig = message.encode("utf-8")
            b_tamp = tampered.encode("utf-8")
            # Calculate Hamming distance between byte streams
            diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(b_orig, b_tamp))
            assert diff_bits == 1, f"Failed at bit_index {bit_idx}: diff_bits={diff_bits}"

        with pytest.raises(ValueError, match="Cannot tamper with an empty message"):
            tamper_message_bit("")

    def test_tamper_message_causes_verification_failure(self) -> None:
        """Verifies that single-bit altered message is detected and rejected."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Transfer $1,000 to Alice"
        sign_res = sign_message(message, key_pair.private_key)

        tampered_msg = tamper_message_bit(message, bit_index=0)
        verify_res = verify_message(tampered_msg, sign_res.signature, key_pair.public_key)
        assert verify_res.is_valid is False
        assert verify_res.trace is not None
        assert verify_res.trace.v != sign_res.signature.r

    def test_tamper_signature_r_detected(self) -> None:
        """Verifies that altering r causes verification failure."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Tamper r test"
        sign_res = sign_message(message, key_pair.private_key, seed_k=29)

        tampered_r, s_same = tamper_signature_component(sign_res.signature, component="r", delta=1)
        assert tampered_r != sign_res.signature.r
        assert s_same == sign_res.signature.s

        tampered_sig = DSASignature(r=tampered_r, s=s_same, q=domain.q)
        verify_res = verify_message(message, tampered_sig, key_pair.public_key)
        assert verify_res.is_valid is False

    def test_tamper_signature_s_detected(self) -> None:
        """Verifies that altering s causes verification failure."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Tamper s test"
        sign_res = sign_message(message, key_pair.private_key, seed_k=29)

        r_same, tampered_s = tamper_signature_component(sign_res.signature, component="s", delta=1)
        assert r_same == sign_res.signature.r
        assert tampered_s != sign_res.signature.s

        tampered_sig = DSASignature(r=r_same, s=tampered_s, q=domain.q)
        verify_res = verify_message(message, tampered_sig, key_pair.public_key)
        assert verify_res.is_valid is False

        with pytest.raises(ValueError, match="Invalid signature component"):
            tamper_signature_component(sign_res.signature, component="z")

    def test_detect_tampering_helper(self) -> None:
        """Verifies comparative output report from detect_tampering."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        message = "Detect Tampering Diagnostic"
        sign_res = sign_message(message, key_pair.private_key, seed_k=29)

        # Message tampering
        report_msg = detect_tampering(message, sign_res.signature, key_pair.public_key, tamper_type="message_bit_flip")
        assert isinstance(report_msg, TamperDetectionResult)
        assert report_msg.original_valid is True
        assert report_msg.tampered_valid is False
        assert report_msg.detected is True
        assert "Single-bit message corruption" in report_msg.explanation

        # Signature r tampering
        report_r = detect_tampering(message, sign_res.signature, key_pair.public_key, tamper_type="signature_r_alter")
        assert report_r.original_valid is True
        assert report_r.tampered_valid is False
        assert report_r.detected is True
        assert "Signature component r altered" in report_r.explanation

        # Signature s tampering
        report_s = detect_tampering(message, sign_res.signature, key_pair.public_key, tamper_type="signature_s_alter")
        assert report_s.original_valid is True
        assert report_s.tampered_valid is False
        assert report_s.detected is True
        assert "Signature component s altered" in report_s.explanation

        with pytest.raises(ValueError, match="Unknown tamper_type"):
            detect_tampering(message, sign_res.signature, key_pair.public_key, tamper_type="invalid_type")


# ---------------------------------------------------------------------------
# 6. TestDSANonceReuseExploit
# ---------------------------------------------------------------------------


class TestDSANonceReuseExploit:
    """Tests Sony PS3 ephemeral nonce reuse cryptanalysis and private key recovery."""

    def test_exploit_nonce_reuse_full_key_recovery(self) -> None:
        """Signs two distinct messages with fixed k, extracts k and x, and confirms match."""
        domain = get_dsa_preset("educational_10")
        actual_x = 42
        key_pair = generate_key_pair(domain, seed_x=actual_x)

        fixed_k = 29
        m1 = "Sony Firmware Update v3.55"
        m2 = "Homebrew Custom Payload Package"

        sig1 = sign_message(m1, key_pair.private_key, seed_k=fixed_k).signature
        sig2 = sign_message(m2, key_pair.private_key, seed_k=fixed_k).signature

        # Confirms signatures share identical r
        assert sig1.r == sig2.r
        assert sig1.s != sig2.s

        # Execute exploit
        exploit_res = exploit_nonce_reuse(
            sig1=sig1,
            sig2=sig2,
            m1=m1,
            m2=m2,
            public_key=key_pair.public_key,
        )

        assert isinstance(exploit_res, DSANonceReuseExploitResult)
        assert exploit_res.is_key_recovered is True
        assert exploit_res.public_key_verified is True
        assert exploit_res.recovered_k == fixed_k
        assert exploit_res.recovered_x == actual_x
        assert pow(domain.g, exploit_res.recovered_x, domain.p) == key_pair.public_key.y

    def test_exploit_nonce_reuse_across_all_presets(self) -> None:
        """Validates exploit across educational and FIPS 186-4 presets."""
        m1 = "Authorization Certificate Alpha"
        m2 = "Authorization Certificate Beta"

        for preset_name in DSA_PRESETS:
            domain = get_dsa_preset(preset_name)
            key_pair = generate_key_pair(domain, seed_x=31)
            fixed_k = 19

            sig1 = sign_message(m1, key_pair.private_key, seed_k=fixed_k).signature
            sig2 = sign_message(m2, key_pair.private_key, seed_k=fixed_k).signature

            exploit_res = exploit_nonce_reuse(sig1, sig2, m1, m2, key_pair.public_key)
            assert exploit_res.is_key_recovered is True
            assert exploit_res.public_key_verified is True
            assert exploit_res.recovered_x == 31
            assert exploit_res.recovered_k == fixed_k

    def test_exploit_rejects_different_r(self) -> None:
        """Raises DSACryptanalysisError if r1 != r2."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)

        sig1 = sign_message("Message 1", key_pair.private_key, seed_k=29).signature
        sig2 = sign_message("Message 2", key_pair.private_key, seed_k=30).signature

        # Different nonces produce different r
        assert sig1.r != sig2.r

        with pytest.raises(DSACryptanalysisError, match="Signatures do not share the same ephemeral component r"):
            exploit_nonce_reuse(sig1, sig2, "Message 1", "Message 2", key_pair.public_key)

    def test_exploit_rejects_identical_messages(self) -> None:
        """Raises DSACryptanalysisError if z1 == z2 mod q."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        sig1 = sign_message("Identical Message", key_pair.private_key, seed_k=29).signature

        with pytest.raises(DSACryptanalysisError, match="Message digests are identical modulo q"):
            exploit_nonce_reuse(sig1, sig1, "Identical Message", "Identical Message", key_pair.public_key)

    def test_exploit_from_hashes_identical_s_rejection(self) -> None:
        """Raises DSACryptanalysisError if s1 == s2 mod q."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        sig1 = DSASignature(r=45, s=70, q=domain.q)
        sig2 = DSASignature(r=45, s=70, q=domain.q)

        with pytest.raises(DSACryptanalysisError, match="Signature components s1 and s2 are identical modulo q"):
            exploit_nonce_reuse_from_hashes(sig1, sig2, z1=10, z2=20, public_key=key_pair.public_key)

    def test_exploit_trace_and_historical_documentation(self) -> None:
        """Confirms trace steps and historical documentation on 2010 PS3 exploit are generated."""
        domain = get_dsa_preset("educational_10")
        key_pair = generate_key_pair(domain, seed_x=42)
        m1 = "Payload 1"
        m2 = "Payload 2"
        sig1 = sign_message(m1, key_pair.private_key, seed_k=29).signature
        sig2 = sign_message(m2, key_pair.private_key, seed_k=29).signature

        exploit_res = exploit_nonce_reuse(sig1, sig2, m1, m2, key_pair.public_key)
        assert len(exploit_res.step_trace) >= 4
        assert exploit_res.algebraic_proof == DSA_NONCE_REUSE_ALGEBRAIC_PROOF
        assert exploit_res.historical_context == SONY_PS3_HISTORICAL_CONTEXT
        assert "PlayStation 3" in exploit_res.historical_context
        assert "fail0verflow" in exploit_res.historical_context
