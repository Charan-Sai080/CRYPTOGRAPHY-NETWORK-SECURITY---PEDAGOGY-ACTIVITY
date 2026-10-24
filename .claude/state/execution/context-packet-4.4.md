# Context Packet 4.4: Comprehensive Pytest 8.x Test Suite & Mathematical Identities

## 1. Goal
Implement an exhaustive, modern Pytest 8.x unit test suite in `backend/tests/test_elgamal.py` covering 100% of the functions, dataclasses, parameter validation rules, mathematical invariants, homomorphic properties, and cryptanalytic exploit routines introduced in Milestone 4 (`backend/core/elgamal.py`).

## 2. Allowed Files
* `backend/tests/test_elgamal.py`
* `backend/tests/__init__.py`

## 3. Test Architecture & Structure

The test suite must be organized into clean, focused test classes adhering to Python 3.12+ and Pytest 8.x standards:

```python
import pytest
from backend.core.elgamal import (
    DOMAIN_PRESETS,
    CryptanalysisError,
    DecryptionError,
    ElGamalCiphertext,
    ElGamalCiphertextBlock,
    ElGamalDecryptTrace,
    ElGamalDecryptionResult,
    ElGamalDomainParams,
    ElGamalEncryptTrace,
    ElGamalEncryptionResult,
    ElGamalError,
    ElGamalKeyPair,
    ElGamalPrivateKey,
    ElGamalPublicKey,
    EncryptionError,
    HomomorphicMultiplicationResult,
    InvalidDomainParametersError,
    InvalidKeyError,
    NonceReuseExploitResult,
    decrypt_integer,
    decrypt_message,
    demonstrate_multiplicative_homomorphism,
    encrypt_integer,
    encrypt_message,
    exploit_nonce_reuse,
    generate_ephemeral_nonce,
    generate_key_pair,
    generate_safe_prime_domain,
    get_domain_preset,
    list_domain_presets,
    multiply_ciphertexts,
    recover_plaintext_ratio,
    verify_key_pair,
    verify_primitive_root,
)
```

### Required Test Classes:

#### 1. `TestElGamalDomainParamsAndPresets`
- `test_valid_domain_params`: Validates successful initialization with prime $p$ and valid generator $g$.
- `test_invalid_modulus_rejection`: Modulus $p \le 2$ or non-prime raises `InvalidDomainParametersError`.
- `test_invalid_generator_bounds`: Generator $g < 2$ or $g \ge p$ raises `InvalidDomainParametersError`.
- `test_all_standard_presets_load`: Verifies all registered presets (`rfc_2409_1024`, `educational_16`, `educational_20`, `educational_24`, `educational_32`) load correctly.
- `test_get_preset_unknown_raises_key_error`: Unknown preset key raises `KeyError`.
- `test_list_domain_presets`: Returns list of all registered `ElGamalDomainParams`.
- `test_verify_primitive_root_valid`: Confirms $g=3$ is a primitive root for $p=65537$.
- `test_verify_primitive_root_invalid`: Detects non-generator (e.g. $g=1$ or quadratic residue that doesn't generate $\mathbb{Z}_p^*$).
- `test_generate_safe_prime_domain`: Generates small 16-bit safe prime domain dynamically and confirms $p = 2q + 1$ and valid generator $g$.

#### 2. `TestElGamalKeyGeneration`
- `test_generate_key_pair_random`: Generates key pair with CSPRNG and verifies $2 \le x \le p - 2$ and $y = g^x \pmod p$.
- `test_generate_key_pair_deterministic_seed`: Generates key pair with fixed `seed_x` and confirms public key matches known modular exponentiation.
- `test_private_key_bounds_validation`: Private key $x < 2$ or $x > p - 2$ raises `InvalidKeyError`.
- `test_public_key_bounds_validation`: Public key $y < 2$ or $y \ge p$ raises `InvalidKeyError`.
- `test_verify_key_pair_valid`: Verifies `verify_key_pair` returns `True` for authentic key pair.
- `test_verify_key_pair_invalid_mismatch`: Detects tampered public or private key, returning `False`.

#### 3. `TestElGamalIntegerEncryptionDecryption`
- `test_encrypt_decrypt_integer_single_block`: Round-trip test encrypting and decrypting an integer $m$.
- `test_encrypt_decrypt_all_educational_presets`: Verifies round-trip across 16-bit, 20-bit, 24-bit, and 32-bit presets.
- `test_encrypt_decrypt_rfc_2409_1024`: Verifies integer round-trip over 1024-bit RFC 2409 MODP group.
- `test_encryption_trace_fields`: Checks all fields of `ElGamalEncryptTrace` ($k, c_1, s, c_2$, and mathematical formula strings).
- `test_decryption_trace_fields`: Checks all fields of `ElGamalDecryptTrace` ($c_1, c_2, x, s, s^{-1}, m$, and mathematical formula strings).
- `test_ephemeral_nonce_generation_bounds_and_coprimality`: Asserts $2 \le k \le p - 2$ and $\gcd(k, p - 1) = 1$.
- `test_invalid_custom_nonce_rejection`: Out-of-bounds $k$ or $\gcd(k, p - 1) \ne 1$ raises `EncryptionError`.
- `test_plaintext_out_of_bounds_rejection`: $m \le 0$ or $m \ge p$ raises `EncryptionError`.

#### 4. `TestElGamalMessageTextChunking`
- `test_encrypt_decrypt_ascii_string`: Encrypts and decrypts multi-word ASCII sentence ("Hello ElGamal Public Key Cryptosystem!").
- `test_encrypt_decrypt_multiline_text`: Encrypts and decrypts multiline strings with newlines and tabs.
- `test_encrypt_decrypt_unicode_emojis`: Encrypts and decrypts UTF-8 text with special characters and emojis.
- `test_encrypt_empty_string`: Empty string returns valid empty result without exceptions.
- `test_ciphertext_to_tuple_list`: Checks serialization into list of $(c_1, c_2)$ tuples.
- `test_decryption_modulus_mismatch_error`: Decrypting ciphertext with a private key from a different domain raises `DecryptionError`.

#### 5. `TestElGamalMultiplicativeHomomorphism`
- `test_multiply_ciphertexts_basic`: Multiplies two ciphertexts and verifies component-wise modular multiplication.
- `test_demonstrate_homomorphism_small_product`: Encrypts $m_1=7, m_2=6$, multiplies ciphertexts, decrypts product, and confirms decrypted value is $42$.
- `test_demonstrate_homomorphism_modulo_wrapping`: Encrypts $m_1, m_2$ such that $m_1 \cdot m_2 > p$, and verifies decrypted value equals $(m_1 \cdot m_2) \pmod p$.
- `test_homomorphism_step_traces_and_proof`: Asserts mathematical proof text and intermediate calculation step traces are populated.
- `test_homomorphism_with_custom_nonces`: Verifies multiplication with fixed test nonces $k_1, k_2$.

#### 6. `TestElGamalNonceReuseExploit`
- `test_exploit_nonce_reuse_known_plaintext`: Encrypts $m_1, m_2$ with identical $k$; given known $m_1$, successfully recovers $m_2$ without the private key.
- `test_exploit_nonce_reuse_different_nonces_raises_error`: Invoking exploit on ciphertexts with different $c_1$ values raises `CryptanalysisError`.
- `test_recover_plaintext_ratio`: Recovers $m_1 \cdot m_2^{-1} \pmod p$ from $c_a, c_b$ without knowing either message.
- `test_exploit_trace_and_explanation`: Checks diagnostic steps and educational vulnerability explanations in `NonceReuseExploitResult`.

#### 7. `TestElGamalRegressionAndIntegrity`
- `test_zero_regressions`: Runs in harmony with previous test suites (`test_number_theory.py`, `test_otp.py`, `test_lcg.py`).
- Total test count across repository exceeds 200 passing tests.

## 4. Execution Command
```bash
pytest backend/tests/test_elgamal.py -v
```
All tests must execute in under 5 seconds (especially when testing RFC 1024-bit with single-block exponentiations).
