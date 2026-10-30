# Context Packet 5.5: Comprehensive Pytest 8.x Suite & Pedagogical Edge Cases

## 1. Goal
Implement an exhaustive, modern Pytest 8.x unit test suite in `backend/tests/test_dsa.py` covering 100% of the functions, dataclasses, parameter validation rules, mathematical invariants, signing/verification routines, tampering detection, and nonce-reuse cryptanalysis introduced in Milestone 5 (`backend/core/dsa.py`).

## 2. Allowed Files
* `backend/tests/test_dsa.py`
* `backend/tests/__init__.py`

## 3. Test Architecture & Structure

The test suite must be organized into clean, focused test classes adhering to Python 3.12+ and Pytest 8.x standards:

```python
import pytest
from backend.core.dsa import (
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
```

### Required Test Classes:

#### 1. `TestDSADomainParamsAndPresets`
- `test_valid_domain_params_init`: Validates successful initialization with primes $p, q$ and valid generator $g$.
- `test_invalid_modulus_rejection`: Modulus $p \le 2$ or non-prime raises `InvalidDomainParametersError`.
- `test_subprime_divisibility_rejection`: Failure when $(p - 1) \pmod q \neq 0$ raises `InvalidDomainParametersError`.
- `test_generator_out_of_bounds`: Generator $g \le 1$ or $g \ge p$ raises `InvalidDomainParametersError`.
- `test_generator_order_verification`: Confirms $g^q \equiv 1 \pmod p$ for all presets.
- `test_all_standard_presets_load`: Verifies that `fips_186_4_1024_160`, `educational_10`, `educational_16`, and `educational_24` load and pass verification.
- `test_get_preset_unknown_raises_key_error`: Unknown preset name raises `KeyError`.
- `test_list_dsa_presets`: Returns list of registered `DSADomainParams`.
- `test_derive_generator`: Confirms generator derivation $g = h^{(p-1)/q} \pmod p$ produces elements of order $q$.
- `test_generate_dsa_domain_dynamic`: Dynamically generates small domain parameters and confirms validity.

#### 2. `TestDSAKeyGeneration`
- `test_generate_key_pair_random`: Generates key pair with CSPRNG and verifies $1 \le x < q$ and $y = g^x \pmod p$.
- `test_generate_key_pair_deterministic_seed`: Generates key pair with fixed `seed_x` and confirms public key matches expected modular exponentiation.
- `test_private_key_bounds_validation`: Private key $x < 1$ or $x \ge q$ raises `InvalidKeyError`.
- `test_public_key_bounds_validation`: Public key $y < 2$ or $y \ge p$ raises `InvalidKeyError`.
- `test_verify_key_pair_valid`: Returns `True` for authentic key pair.
- `test_verify_key_pair_mismatch`: Detects corrupted key pairs, returning `False`.

#### 3. `TestDSASigning`
- `test_sign_message_all_presets`: Verifies successful signing across all presets.
- `test_sign_with_deterministic_k`: Generates identical signatures when given deterministic `seed_k`.
- `test_hash_truncation_fips_186_4`: Confirms message digest is properly left-truncated to $N = \min(\text{bit\_length}(q), 256)$ bits.
- `test_sign_trace_attributes`: Validates that `DSASignTrace` populates all step fields, intermediate products, and LaTeX formula strings.
- `test_resampling_when_r_or_s_is_zero`: Tests that the signing loop resamples ephemeral secrets until $r > 0$ and $s > 0$.
- `test_max_attempts_exceeded`: Raises `ResamplingFailureError` if maximum retry budget is exhausted.

#### 4. `TestDSAVerification`
- `test_verify_valid_signature_all_presets`: Signs and verifies messages across all domain presets.
- `test_reject_signature_out_of_bounds`: Verifies rejection when $r \le 0, r \ge q, s \le 0,$ or $s \ge q$.
- `test_reject_wrong_message`: Verification fails when message text does not match signature.
- `test_reject_wrong_public_key`: Verification fails when valid signature is checked against a different public key.
- `test_verification_trace_fields_and_proof`: Inspects `DSAVerifyTrace` verifying that $w, u_1, u_2, v$, and the algebraic proof string are correctly populated.

#### 5. `TestDSATamperingDetection`
- `test_tamper_message_bit_flips_single_bit`: Confirms `tamper_message_bit` flips exactly 1 bit.
- `test_tamper_message_causes_verification_failure`: Verifies that single-bit altered message is detected and rejected.
- `test_tamper_signature_r_detected`: Verifies that altering $r$ causes verification failure.
- `test_tamper_signature_s_detected`: Verifies that altering $s$ causes verification failure.
- `test_detect_tampering_helper`: Verifies comparative output report from `detect_tampering`.

#### 6. `TestDSANonceReuseExploit`
- `test_exploit_nonce_reuse_full_key_recovery`: Signs two distinct messages with fixed $k$, extracts $k$ and $x$, and confirms $x == x_{\text{actual}}$ and $g^x \equiv y \pmod p$.
- `test_exploit_nonce_reuse_across_all_presets`: Validates exploit across educational and FIPS 186-4 presets.
- `test_exploit_rejects_different_r`: Raises `DSACryptanalysisError` if $r_1 \neq r_2$.
- `test_exploit_rejects_identical_messages`: Raises `DSACryptanalysisError` if $z_1 \equiv z_2 \pmod q$.
- `test_exploit_trace_and_historical_documentation`: Confirms trace steps and historical documentation on the 2010 PS3 exploit are generated.

## 4. Acceptance Criteria
1. Test suite runs with modern Pytest 8.x: `python -m pytest backend/tests/test_dsa.py -v`.
2. 100% test pass rate with zero test skips or unexpected failures.
3. Zero regressions across existing test suites (`test_number_theory.py`, `test_otp.py`, `test_lcg.py`, `test_elgamal.py`).
