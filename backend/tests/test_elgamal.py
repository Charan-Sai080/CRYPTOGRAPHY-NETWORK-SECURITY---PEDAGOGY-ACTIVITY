"""Unit test suite for ElGamal Public-Key Cryptosystem & Multiplicative Homomorphism.

Covers:
- Domain parameters & preset catalog validation
- Safe prime generation & primitive root checks
- Key pair generation (CSPRNG and deterministic)
- Integer encryption/decryption roundtrips (16-bit to 1024-bit MODP)
- Step traces and mathematical formula formatting
- Multi-block UTF-8 text chunking and reconstruction
- Multiplicative homomorphism over ciphertexts
- Nonce-reuse known-plaintext cryptanalysis & ratio recovery
- Comprehensive boundary and domain exception handling
- Immutability and zero-regression verification
"""

import math
from dataclasses import FrozenInstanceError

import pytest

from backend.core.elgamal import (
    DOMAIN_PRESETS,
    CryptanalysisError,
    DecryptionError,
    DomainParameterError,
    ElGamalCiphertext,
    ElGamalCiphertextBlock,
    ElGamalDecryptTrace,
    ElGamalDecryptionResult,
    ElGamalDomainParams,
    ElGamalEncryptTrace,
    ElGamalEncryptionResult,
    ElGamalError,
    ElGamalKeyPair,
    ElGamalMultiBlockResult,
    ElGamalPrivateKey,
    ElGamalPublicKey,
    EncryptionError,
    HomomorphicMultiplicationResult,
    HomomorphismError,
    InvalidDomainParametersError,
    InvalidKeyError,
    KeyValidationError,
    NonceReuseAttackResult,
    NonceReuseError,
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
from backend.core.number_theory import is_prime, mod_inverse


# ===========================================================================
# 1. Domain Parameters & Presets
# ===========================================================================


class TestElGamalDomainParamsAndPresets:
    def test_valid_domain_params(self) -> None:
        dom = ElGamalDomainParams(p=65537, g=3, name="Test 16-bit")
        assert dom.p == 65537
        assert dom.g == 3
        assert dom.bits == 17
        assert dom.name == "Test 16-bit"
        assert dom.q is None

    def test_invalid_modulus_rejection(self) -> None:
        # Non-positive or too small
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=2, g=1)
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=1, g=1)
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=-17, g=2)
        # Composite modulus
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=15, g=2)
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=100, g=3)

    def test_invalid_generator_bounds(self) -> None:
        p = 65537
        # g < 2
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=p, g=1)
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=p, g=0)
        # g >= p
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=p, g=p)
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=p, g=p + 1)

    def test_all_standard_presets_load(self) -> None:
        expected_keys = [
            "rfc_2409_1024",
            "educational_16",
            "educational_20",
            "educational_24",
            "educational_32",
        ]
        for key in expected_keys:
            preset = get_domain_preset(key)
            assert isinstance(preset, ElGamalDomainParams)
            assert preset.p > 2
            assert 2 <= preset.g < preset.p
            assert preset.bits == preset.p.bit_length()

    def test_get_preset_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="not found"):
            get_domain_preset("unknown_nonexistent_group")

    def test_list_domain_presets(self) -> None:
        presets = list_domain_presets()
        assert len(presets) == 5
        names = [p.name for p in presets]
        assert any("1024-bit" in name for name in names)
        assert any("16-bit" in name for name in names)

    def test_verify_primitive_root_valid(self) -> None:
        # g = 3 is a generator for Fermat prime 65537
        assert verify_primitive_root(g=3, p=65537) is True
        # g = 5 is a generator for educational 20-bit group 1048583
        assert verify_primitive_root(g=5, p=1048583) is True
        # Safe prime 23 (q = 11), g = 5 is a primitive root
        assert verify_primitive_root(g=5, p=23, q=11) is True

    def test_verify_primitive_root_invalid(self) -> None:
        # g = 1 is never a primitive root
        assert verify_primitive_root(g=1, p=65537) is False
        # g = 2 is a quadratic residue mod 65537 (order 32768 != 65536)
        assert verify_primitive_root(g=2, p=65537) is False
        # Out of bounds g
        assert verify_primitive_root(g=65537, p=65537) is False
        assert verify_primitive_root(g=0, p=65537) is False
        # Safe prime 23 (q = 11): g = 2 is not primitive (2^11 mod 23 = 1)
        assert verify_primitive_root(g=2, p=23, q=11) is False

    def test_verify_primitive_root_rfc_2409(self) -> None:
        rfc = get_domain_preset("rfc_2409_1024")
        assert verify_primitive_root(g=rfc.g, p=rfc.p) is True

    def test_generate_safe_prime_domain(self) -> None:
        # Generate 16-bit safe prime domain
        domain = generate_safe_prime_domain(bits=16)
        assert isinstance(domain, ElGamalDomainParams)
        assert domain.bits == 16
        assert domain.q is not None
        assert domain.p == 2 * domain.q + 1
        assert is_prime(domain.p).is_prime is True
        assert is_prime(domain.q).is_prime is True
        assert verify_primitive_root(domain.g, domain.p, q=domain.q) is True


# ===========================================================================
# 2. Key Generation
# ===========================================================================


class TestElGamalKeyGeneration:
    def test_generate_key_pair_random(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        assert isinstance(pair, ElGamalKeyPair)
        assert 2 <= pair.private_key.x <= domain.p - 2
        assert 2 <= pair.public_key.y < domain.p
        assert pair.public_key.y == pow(domain.g, pair.private_key.x, domain.p)
        assert pair.public_key.p == domain.p
        assert pair.private_key.p == domain.p

    def test_generate_key_pair_deterministic_seed(self) -> None:
        domain = get_domain_preset("educational_16")
        seed_x = 12345
        pair = generate_key_pair(domain, seed_x=seed_x)
        assert pair.private_key.x == seed_x
        expected_y = pow(domain.g, seed_x, domain.p)
        assert pair.public_key.y == expected_y

    def test_private_key_bounds_validation(self) -> None:
        domain = get_domain_preset("educational_16")
        # x < 2
        with pytest.raises(InvalidKeyError):
            generate_key_pair(domain, seed_x=1)
        with pytest.raises(InvalidKeyError):
            generate_key_pair(domain, seed_x=0)
        with pytest.raises(InvalidKeyError):
            generate_key_pair(domain, seed_x=-5)
        # x > p - 2
        with pytest.raises(InvalidKeyError):
            generate_key_pair(domain, seed_x=domain.p - 1)
        with pytest.raises(InvalidKeyError):
            generate_key_pair(domain, seed_x=domain.p)

    def test_public_key_bounds_validation(self) -> None:
        p = 65537
        g = 3
        with pytest.raises(InvalidKeyError):
            ElGamalPublicKey(p=p, g=g, y=1)
        with pytest.raises(InvalidKeyError):
            ElGamalPublicKey(p=p, g=g, y=0)
        with pytest.raises(InvalidKeyError):
            ElGamalPublicKey(p=p, g=g, y=p)
        with pytest.raises(InvalidKeyError):
            ElGamalPublicKey(p=p, g=g, y=p + 10)

    def test_verify_key_pair_valid(self) -> None:
        domain = get_domain_preset("educational_20")
        pair = generate_key_pair(domain)
        assert verify_key_pair(pair) is True

    def test_verify_key_pair_invalid_mismatch(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=42)

        # Tampered public key
        tampered_pk = ElGamalPublicKey(
            p=domain.p,
            g=domain.g,
            y=(pair.public_key.y + 1) if (pair.public_key.y + 1 < domain.p) else 2,
            domain_name=domain.name,
        )
        tampered_pair = ElGamalKeyPair(
            public_key=tampered_pk,
            private_key=pair.private_key,
            domain=domain,
        )
        assert verify_key_pair(tampered_pair) is False

        # Modulus mismatch
        other_dom = get_domain_preset("educational_20")
        mismatched_pair = ElGamalKeyPair(
            public_key=pair.public_key,
            private_key=ElGamalPrivateKey(p=other_dom.p, g=other_dom.g, x=42),
            domain=domain,
        )
        assert verify_key_pair(mismatched_pair) is False


# ===========================================================================
# 3. Integer Encryption & Decryption
# ===========================================================================


class TestElGamalIntegerEncryptionDecryption:
    def test_encrypt_decrypt_integer_single_block(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=9876)
        m = 42
        k = 4519

        c1, c2, trace_enc = encrypt_integer(m, pair.public_key, k=k)
        assert c1 == pow(domain.g, k, domain.p)
        s = pow(pair.public_key.y, k, domain.p)
        assert c2 == (m * s) % domain.p

        recovered_m, trace_dec = decrypt_integer(c1, c2, pair.private_key)
        assert recovered_m == m
        assert trace_dec.shared_secret_s == s
        assert trace_dec.recovered_m == m

    def test_encrypt_decrypt_all_educational_presets(self) -> None:
        presets = ["educational_16", "educational_20", "educational_24", "educational_32"]
        test_plaintexts = [1337, 424242, 999999, 12345678]

        for preset_name, m in zip(presets, test_plaintexts, strict=True):
            domain = get_domain_preset(preset_name)
            pair = generate_key_pair(domain)
            c1, c2, _ = encrypt_integer(m, pair.public_key)
            recovered_m, _ = decrypt_integer(c1, c2, pair.private_key)
            assert recovered_m == m

    def test_encrypt_decrypt_rfc_2409_1024(self) -> None:
        domain = get_domain_preset("rfc_2409_1024")
        # Fixed small exponent for high-speed execution
        pair = generate_key_pair(domain, seed_x=123456789)
        m = 0xDEADBEEFCAFE
        k = 987654321
        c1, c2, enc_trace = encrypt_integer(m, pair.public_key, k=k)
        decrypted_m, dec_trace = decrypt_integer(c1, c2, pair.private_key)

        assert decrypted_m == m
        assert enc_trace.shared_secret_s == dec_trace.shared_secret_s

    def test_encryption_trace_fields(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=12345)
        m = 100
        k = 2003

        c1, c2, trace = encrypt_integer(m, pair.public_key, k=k, block_index=5)
        assert trace.block_index == 5
        assert trace.m == m
        assert trace.k == k
        assert trace.c1 == c1
        assert trace.c2 == c2
        assert "c1 = g^k mod p" in trace.c1_formula
        assert "s = y^k mod p" in trace.s_formula
        assert "c2 = (m * s) mod p" in trace.c2_formula

    def test_decryption_trace_fields(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=12345)
        m = 77
        k = 5431

        c1, c2, _ = encrypt_integer(m, pair.public_key, k=k, block_index=2)
        recovered_m, trace = decrypt_integer(c1, c2, pair.private_key, block_index=2)

        assert trace.block_index == 2
        assert trace.c1 == c1
        assert trace.c2 == c2
        assert trace.x == pair.private_key.x
        assert trace.recovered_m == recovered_m
        assert trace.s_inverse == mod_inverse(trace.shared_secret_s, domain.p).inverse
        assert "s = c1^x mod p" in trace.s_formula
        assert "s^-1 = mod_inverse" in trace.s_inv_formula
        assert "m = (c2 * s^-1) mod p" in trace.m_formula

    def test_ephemeral_nonce_generation_bounds_and_coprimality(self) -> None:
        p = 65537
        for _ in range(100):
            k = generate_ephemeral_nonce(p)
            assert 2 <= k <= p - 2
            assert math.gcd(k, p - 1) == 1

    def test_invalid_custom_nonce_rejection(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p

        # Nonce out of bounds
        with pytest.raises(EncryptionError, match="Ephemeral nonce k must be in range"):
            encrypt_integer(42, pair.public_key, k=1)
        with pytest.raises(EncryptionError, match="Ephemeral nonce k must be in range"):
            encrypt_integer(42, pair.public_key, k=p - 1)
        with pytest.raises(EncryptionError, match="Ephemeral nonce k must be in range"):
            encrypt_integer(42, pair.public_key, k=p)

        # Nonce not coprime to p - 1 (for 65537, p - 1 = 65536 = 2^16, so any even k is not coprime)
        with pytest.raises(EncryptionError, match="must be coprime"):
            encrypt_integer(42, pair.public_key, k=4)

    def test_plaintext_out_of_bounds_rejection(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p

        # m <= 0
        with pytest.raises(EncryptionError, match="Plaintext integer m"):
            encrypt_integer(0, pair.public_key)
        with pytest.raises(EncryptionError, match="Plaintext integer m"):
            encrypt_integer(-10, pair.public_key)

        # m >= p
        with pytest.raises(EncryptionError, match="Plaintext integer m"):
            encrypt_integer(p, pair.public_key)
        with pytest.raises(EncryptionError, match="Plaintext integer m"):
            encrypt_integer(p + 1, pair.public_key)


# ===========================================================================
# 4. Multi-Block Text Chunking
# ===========================================================================


class TestElGamalMessageTextChunking:
    def test_encrypt_decrypt_ascii_string(self) -> None:
        domain = get_domain_preset("educational_32")
        pair = generate_key_pair(domain, seed_x=654321)
        message = "Hello ElGamal Public Key Cryptosystem!"

        enc_res = encrypt_message(message, pair.public_key)
        assert enc_res.is_string_message is True
        assert enc_res.original_text == message
        assert len(enc_res.ciphertext.blocks) > 0
        assert len(enc_res.traces) == len(enc_res.ciphertext.blocks)

        dec_res = decrypt_message(enc_res.ciphertext, pair.private_key)
        assert dec_res.plaintext_str == message
        assert dec_res.is_verified is True
        assert dec_res.recovered_blocks == enc_res.message_blocks

    def test_encrypt_decrypt_multiline_text(self) -> None:
        domain = get_domain_preset("educational_24")
        pair = generate_key_pair(domain)
        message = "Line 1: Cryptography\nLine 2: Pedagogy\nLine 3: Homomorphism\t(verified)!"

        enc_res = encrypt_message(message, pair.public_key)
        dec_res = decrypt_message(enc_res.ciphertext, pair.private_key)
        assert dec_res.plaintext_str == message

    def test_encrypt_decrypt_unicode_emojis(self) -> None:
        domain = get_domain_preset("educational_32")
        pair = generate_key_pair(domain)
        message = "CNS 2026 🔐✨ Multiplicative Homomorphism: E(m₁)·E(m₂) 🚀 🌟"

        enc_res = encrypt_message(message, pair.public_key)
        dec_res = decrypt_message(enc_res.ciphertext, pair.private_key)
        assert dec_res.plaintext_str == message

    def test_encrypt_empty_string(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)

        enc_res = encrypt_message("", pair.public_key)
        assert enc_res.ciphertext.total_blocks == 0
        assert len(enc_res.traces) == 0
        assert len(enc_res.message_blocks) == 0

        dec_res = decrypt_message(enc_res.ciphertext, pair.private_key)
        assert dec_res.plaintext_str == ""
        assert len(dec_res.recovered_blocks) == 0
        assert len(dec_res.traces) == 0

    def test_ciphertext_to_tuple_list(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        message = "Test"

        enc_res = encrypt_message(message, pair.public_key)
        tuples = enc_res.ciphertext.to_tuple_list()
        assert isinstance(tuples, list)
        assert len(tuples) == enc_res.ciphertext.total_blocks
        for item in tuples:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], int)
            assert isinstance(item[1], int)

    def test_decryption_modulus_mismatch_error(self) -> None:
        dom16 = get_domain_preset("educational_16")
        dom20 = get_domain_preset("educational_20")

        pair16 = generate_key_pair(dom16)
        pair20 = generate_key_pair(dom20)

        enc_res = encrypt_message("Secret Message", pair16.public_key)

        with pytest.raises(DecryptionError, match="modulus p .* does not match"):
            decrypt_message(enc_res.ciphertext, pair20.private_key)


# ===========================================================================
# 5. Multiplicative Homomorphism
# ===========================================================================


class TestElGamalMultiplicativeHomomorphism:
    def test_multiply_ciphertexts_basic(self) -> None:
        p = 65537
        c_a = (100, 200)
        c_b = (300, 400)
        c1_prod, c2_prod = multiply_ciphertexts(c_a, c_b, p)
        assert c1_prod == (100 * 300) % p
        assert c2_prod == (200 * 400) % p

    def test_demonstrate_homomorphism_small_product(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=13579)
        m1 = 7
        m2 = 6

        res = demonstrate_multiplicative_homomorphism(m1, m2, pair)
        assert isinstance(res, HomomorphicMultiplicationResult)
        assert res.m1 == 7
        assert res.m2 == 6
        assert res.expected_product == 42
        assert res.decrypted_product == 42
        assert res.is_homomorphism_verified is True

    def test_demonstrate_homomorphism_modulo_wrapping(self) -> None:
        domain = get_domain_preset("educational_16")  # p = 65537
        pair = generate_key_pair(domain, seed_x=24680)
        m1 = 500
        m2 = 300
        # 500 * 300 = 150000 > 65537
        expected_wrapped = (m1 * m2) % domain.p

        res = demonstrate_multiplicative_homomorphism(m1, m2, pair)
        assert res.expected_product == expected_wrapped
        assert res.decrypted_product == expected_wrapped
        assert res.is_homomorphism_verified is True

    def test_homomorphism_step_traces_and_proof(self) -> None:
        domain = get_domain_preset("educational_20")
        pair = generate_key_pair(domain)
        res = demonstrate_multiplicative_homomorphism(15, 20, pair)

        assert len(res.step_trace) >= 8
        assert "Multiplicative Homomorphism in ElGamal" in res.mathematical_proof
        assert "D(E(m1) * E(m2)) == (m1 * m2) mod p" in res.mathematical_proof

    def test_homomorphism_with_custom_nonces(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=1234)
        m1 = 11
        m2 = 13
        k1 = 1009
        k2 = 2003

        res = demonstrate_multiplicative_homomorphism(m1, m2, pair, k1=k1, k2=k2)
        assert res.decrypted_product == (11 * 13) % domain.p
        assert res.is_homomorphism_verified is True


# ===========================================================================
# 6. Nonce-Reuse Cryptanalytic Exploit
# ===========================================================================


class TestElGamalNonceReuseExploit:
    def test_exploit_nonce_reuse_known_plaintext(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=43210)
        p = domain.p

        m1 = 1337
        m2 = 4242
        # Fixed shared nonce k
        shared_k = 5555

        c1_a, c2_a, _ = encrypt_integer(m1, pair.public_key, k=shared_k)
        c1_b, c2_b, _ = encrypt_integer(m2, pair.public_key, k=shared_k)

        # Observer confirms identical c1
        assert c1_a == c1_b

        # Attacker executes exploit with known m1
        exploit_res = exploit_nonce_reuse(
            (c1_a, c2_a),
            (c1_b, c2_b),
            known_m1=m1,
            p=p,
            actual_m2=m2,
        )

        assert isinstance(exploit_res, NonceReuseExploitResult)
        assert exploit_res.recovered_m2 == m2
        assert exploit_res.attack_successful is True
        assert exploit_res.c1 == c1_a
        assert exploit_res.c2_a == c2_a
        assert exploit_res.c2_b == c2_b

    def test_exploit_nonce_reuse_different_nonces_raises_error(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p

        c1_a, c2_a, _ = encrypt_integer(100, pair.public_key, k=1009)
        c1_b, c2_b, _ = encrypt_integer(200, pair.public_key, k=2003)

        assert c1_a != c1_b

        with pytest.raises(CryptanalysisError, match="do not match"):
            exploit_nonce_reuse((c1_a, c2_a), (c1_b, c2_b), known_m1=100, p=p)

    def test_recover_plaintext_ratio(self) -> None:
        domain = get_domain_preset("educational_20")
        pair = generate_key_pair(domain)
        p = domain.p

        m1 = 777
        m2 = 888
        shared_k = 12345

        c1_a, c2_a, _ = encrypt_integer(m1, pair.public_key, k=shared_k)
        c1_b, c2_b, _ = encrypt_integer(m2, pair.public_key, k=shared_k)

        ratio = recover_plaintext_ratio((c1_a, c2_a), (c1_b, c2_b), p)
        expected_ratio = (m1 * mod_inverse(m2, p).inverse) % p
        assert ratio == expected_ratio

    def test_exploit_trace_and_explanation(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p

        m1 = 12
        m2 = 34
        k = 999
        c_a = encrypt_integer(m1, pair.public_key, k=k)[:2]
        c_b = encrypt_integer(m2, pair.public_key, k=k)[:2]

        result = exploit_nonce_reuse(c_a, c_b, known_m1=m1, p=p, actual_m2=m2)
        assert len(result.steps) >= 5
        assert "Cryptanalytic Vulnerability of Ephemeral Nonce Reuse" in result.explanation
        assert "Known-Plaintext Attack" in result.explanation


# ===========================================================================
# 7. Edge Cases & Exception Hierarchy
# ===========================================================================


class TestElGamalEdgeCasesAndTypes:
    def test_frozen_dataclass_immutability(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=100)

        with pytest.raises(FrozenInstanceError):
            pair.public_key.y = 999  # type: ignore[misc]

        with pytest.raises(FrozenInstanceError):
            pair.private_key.x = 999  # type: ignore[misc]

        with pytest.raises(FrozenInstanceError):
            domain.p = 123  # type: ignore[misc]

    def test_exception_hierarchy(self) -> None:
        assert issubclass(InvalidDomainParametersError, ElGamalError)
        assert issubclass(DomainParameterError, ElGamalError)
        assert issubclass(InvalidKeyError, ElGamalError)
        assert issubclass(KeyValidationError, ElGamalError)
        assert issubclass(EncryptionError, ElGamalError)
        assert issubclass(DecryptionError, ElGamalError)
        assert issubclass(CryptanalysisError, ElGamalError)
        assert issubclass(NonceReuseError, CryptanalysisError)
        assert issubclass(HomomorphismError, ElGamalError)

    def test_type_aliases_interchangeability(self) -> None:
        assert NonceReuseAttackResult is NonceReuseExploitResult
        assert ElGamalMultiBlockResult is ElGamalEncryptionResult

    def test_encrypt_message_type_validation(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)

        with pytest.raises(EncryptionError, match="must be a string"):
            encrypt_message(12345, pair.public_key)  # type: ignore[arg-type]

    def test_encrypt_message_nonces_count_mismatch(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)

        with pytest.raises(EncryptionError, match="Expected"):
            encrypt_message("Hello World", pair.public_key, nonces=[1009])

    def test_decrypt_integer_invalid_components(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p

        with pytest.raises(DecryptionError, match="Ciphertext component c1"):
            decrypt_integer(0, 100, pair.private_key)
        with pytest.raises(DecryptionError, match="Ciphertext component c1"):
            decrypt_integer(p, 100, pair.private_key)
        with pytest.raises(DecryptionError, match="Ciphertext component c2"):
            decrypt_integer(100, -1, pair.private_key)
        with pytest.raises(DecryptionError, match="Ciphertext component c2"):
            decrypt_integer(100, p, pair.private_key)

    def test_multiply_ciphertexts_with_ciphertext_blocks(self) -> None:
        p = 65537
        b1 = ElGamalCiphertextBlock(c1=5, c2=10)
        b2 = ElGamalCiphertextBlock(c1=7, c2=20)
        c1, c2 = multiply_ciphertexts(b1, b2, p)
        assert c1 == 35
        assert c2 == 200

    def test_multiply_ciphertexts_invalid_p(self) -> None:
        with pytest.raises(HomomorphismError, match="Modulus p must be > 2"):
            multiply_ciphertexts((1, 2), (3, 4), p=2)

    def test_exploit_nonce_reuse_invalid_known_m1(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p
        c = (1234, 5678)

        with pytest.raises(CryptanalysisError, match="Known plaintext m1"):
            exploit_nonce_reuse(c, c, known_m1=0, p=p)
        with pytest.raises(CryptanalysisError, match="Known plaintext m1"):
            exploit_nonce_reuse(c, c, known_m1=p, p=p)

    def test_encrypt_decrypt_single_character(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        enc = encrypt_message("A", pair.public_key)
        dec = decrypt_message(enc.ciphertext, pair.private_key)
        assert dec.plaintext_str == "A"

    def test_encrypt_decrypt_large_text(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        long_text = "The ElGamal encryption system is an asymmetric key encryption algorithm based on Diffie-Hellman key exchange." * 3
        enc = encrypt_message(long_text, pair.public_key)
        assert enc.ciphertext.total_blocks > 50
        dec = decrypt_message(enc.ciphertext, pair.private_key)
        assert dec.plaintext_str == long_text

    def test_demonstrate_homomorphism_with_identity(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        # m1 = 1 (multiplicative identity)
        res = demonstrate_multiplicative_homomorphism(1, 999, pair)
        assert res.decrypted_product == 999
        assert res.is_homomorphism_verified is True

    def test_demonstrate_homomorphism_with_equal_factors(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        res = demonstrate_multiplicative_homomorphism(25, 25, pair)
        assert res.decrypted_product == 625
        assert res.is_homomorphism_verified is True

    def test_exploit_nonce_reuse_with_block_objects(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        p = domain.p
        k = 12345
        c1_a, c2_a, _ = encrypt_integer(50, pair.public_key, k=k)
        c1_b, c2_b, _ = encrypt_integer(80, pair.public_key, k=k)

        b1 = ElGamalCiphertextBlock(c1=c1_a, c2=c2_a)
        b2 = ElGamalCiphertextBlock(c1=c1_b, c2=c2_b)

        res = exploit_nonce_reuse(b1, b2, known_m1=50, p=p, actual_m2=80)
        assert res.recovered_m2 == 80
        assert res.attack_successful is True

    def test_recover_plaintext_ratio_different_nonces_raises_error(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        c1_a, c2_a, _ = encrypt_integer(10, pair.public_key, k=1009)
        c1_b, c2_b, _ = encrypt_integer(20, pair.public_key, k=2003)

        with pytest.raises(CryptanalysisError, match="do not match"):
            recover_plaintext_ratio((c1_a, c2_a), (c1_b, c2_b), domain.p)

    def test_recover_plaintext_ratio_with_block_objects(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain)
        k = 9875
        c1_a, c2_a, _ = encrypt_integer(15, pair.public_key, k=k)
        c1_b, c2_b, _ = encrypt_integer(30, pair.public_key, k=k)

        b1 = ElGamalCiphertextBlock(c1=c1_a, c2=c2_a)
        b2 = ElGamalCiphertextBlock(c1=c1_b, c2=c2_b)

        ratio = recover_plaintext_ratio(b1, b2, domain.p)
        expected = (15 * mod_inverse(30, domain.p).inverse) % domain.p
        assert ratio == expected

    def test_generate_key_pair_custom_domain(self) -> None:
        custom_dom = generate_safe_prime_domain(bits=16)
        pair = generate_key_pair(custom_dom)
        assert verify_key_pair(pair) is True

    def test_generate_ephemeral_nonce_small_modulus_rejection(self) -> None:
        with pytest.raises(EncryptionError, match="too small"):
            generate_ephemeral_nonce(3)

    def test_verify_primitive_root_non_prime(self) -> None:
        # 15 is not prime
        assert verify_primitive_root(g=2, p=15) is False

    def test_domain_params_invalid_type(self) -> None:
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p="not an int", g=3)  # type: ignore[arg-type]
        with pytest.raises(InvalidDomainParametersError):
            ElGamalDomainParams(p=65537, g="not an int")  # type: ignore[arg-type]

    def test_key_pair_dataclass_fields(self) -> None:
        domain = get_domain_preset("educational_16")
        pair = generate_key_pair(domain, seed_x=123)
        assert pair.public_key.p == domain.p
        assert pair.private_key.x == 123
        assert pair.domain == domain


# ===========================================================================
# 8. Regression & Integrity
# ===========================================================================


class TestElGamalRegressionAndIntegrity:
    def test_zero_regressions(self) -> None:
        # Verifies that importing and running ElGamal leaves all previous modules unharmed
        from backend.core.lcg import generate_lcg_sequence
        from backend.core.number_theory import extended_gcd
        from backend.core.otp import encrypt_otp

        assert extended_gcd(240, 46).gcd == 2
        otp_res = encrypt_otp("Test", b"Key1")
        assert otp_res.ciphertext_bytes is not None
        seq = generate_lcg_sequence(m=16, a=5, c=1, seed=7, count=5)
        assert len(seq.values) == 5
