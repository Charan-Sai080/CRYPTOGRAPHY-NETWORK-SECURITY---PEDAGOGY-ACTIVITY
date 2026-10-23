"""
Unit Tests for One-Time Pad Engine & Two-Time Pad Cryptanalysis.

Covers:
- CSPRNG key generation and length validation
- Shannon entropy calculations and theoretical limits
- Byte-wise and bit-wise pedagogical XOR execution traces
- ASCII, Unicode/emoji, and raw binary roundtrips
- Truth table formatting
- Cryptographic identities (involution, identity element, self-inverse, commutativity)
- Two-Time Pad key cancellation (C1 ^ C2 == M1 ^ M2)
- English readability scoring heuristics
- Interactive crib dragging and bounds checks
- Automated dictionary crib dragging attack
"""

import base64
import math
import secrets
import pytest

from backend.core.otp import (
    DEFAULT_CRIB_DICTIONARY,
    AutoCribDragResult,
    BitXORTrace,
    ByteOTPTrace,
    CribDragCandidate,
    CribDragResult,
    EntropyAnalysis,
    OTPDecryptionResult,
    OTPEncryptionResult,
    TwoTimePadAnalysis,
    analyze_two_time_pad,
    auto_crib_drag_attack,
    calculate_shannon_entropy,
    decrypt_otp,
    drag_crib,
    english_readability_score,
    format_byte_truth_table,
    generate_otp_key,
    encrypt_otp,
    xor_bytes,
)


# ===========================================================================
# 1. TestOTPKeyGeneration
# ===========================================================================

class TestOTPKeyGeneration:
    @pytest.mark.parametrize("length", [0, 1, 16, 32, 256])
    def test_generate_otp_key_length(self, length: int):
        key = generate_otp_key(length)
        assert isinstance(key, bytes)
        assert len(key) == length

    def test_generate_otp_key_randomness(self):
        # Two independently generated 32-byte keys must not be equal
        key1 = generate_otp_key(32)
        key2 = generate_otp_key(32)
        assert key1 != key2

        # 128-byte key must have high Shannon entropy
        key_long = generate_otp_key(128)
        entropy_res = calculate_shannon_entropy(key_long)
        assert entropy_res.entropy > 5.5

    def test_generate_otp_key_negative_length(self):
        with pytest.raises(ValueError, match="Key length must be non-negative"):
            generate_otp_key(-1)
        with pytest.raises(ValueError, match="Key length must be non-negative"):
            generate_otp_key(-100)


# ===========================================================================
# 2. TestShannonEntropy
# ===========================================================================

class TestShannonEntropy:
    def test_zero_entropy_constant_bytes(self):
        res1 = calculate_shannon_entropy(b"A" * 128)
        assert res1.entropy == 0.0
        assert res1.entropy_ratio == 0.0
        assert res1.is_near_maximal is False
        assert 65 in res1.frequencies
        assert res1.frequencies[65] == 128

        res2 = calculate_shannon_entropy(bytes([42] * 50))
        assert res2.entropy == 0.0
        assert res2.frequencies[42] == 50

    def test_maximal_entropy_uniform_distribution(self):
        # Exactly one occurrence of each byte in [0, 255]
        uniform_data = bytes(range(256))
        res = calculate_shannon_entropy(uniform_data)
        assert res.entropy == 8.0
        assert res.entropy_ratio == 1.0
        assert res.is_near_maximal is True
        assert len(res.frequencies) == 256

    def test_two_symbol_entropy(self):
        data = b"AB" * 64  # Equal counts of 'A' and 'B' -> log2(2) = 1.0 bit
        res = calculate_shannon_entropy(data)
        assert res.entropy == 1.0
        assert res.entropy_ratio == 0.125
        assert res.is_near_maximal is False

    def test_four_symbol_entropy(self):
        data = b"ABCD" * 32  # Equal counts of 4 symbols -> log2(4) = 2.0 bits
        res = calculate_shannon_entropy(data)
        assert res.entropy == 2.0
        assert res.entropy_ratio == 0.25

    def test_empty_data_entropy(self):
        res = calculate_shannon_entropy(b"")
        assert res.data_length == 0
        assert res.entropy == 0.0
        assert res.entropy_ratio == 0.0
        assert res.frequencies == {}
        assert res.is_near_maximal is False
        assert "zero shannon entropy" in res.explanation.lower()

    def test_entropy_explanation(self):
        res_zero = calculate_shannon_entropy(b"\x00" * 20)
        assert "zero entropy" in res_zero.explanation.lower()

        res_max = calculate_shannon_entropy(bytes(range(256)))
        assert "near-maximal" in res_max.explanation.lower()

        res_mid = calculate_shannon_entropy(b"The quick brown fox jumps over the lazy dog.")
        assert "moderate entropy" in res_mid.explanation.lower()


# ===========================================================================
# 3. TestOTPEncryptionDecryption
# ===========================================================================

class TestOTPEncryptionDecryption:
    def test_otp_roundtrip_ascii(self):
        message = "Pedagogical Cryptography with One-Time Pad!"
        enc = encrypt_otp(message)
        assert isinstance(enc, OTPEncryptionResult)
        assert enc.ciphertext_bytes != enc.plaintext_bytes
        assert len(enc.ciphertext_bytes) == len(enc.plaintext_bytes)

        dec = decrypt_otp(enc.ciphertext_bytes, enc.key_bytes)
        assert isinstance(dec, OTPDecryptionResult)
        assert dec.is_valid_utf8 is True
        assert dec.decrypted_text == message
        assert dec.decrypted_bytes == message.encode("utf-8")

    def test_otp_roundtrip_unicode_and_emojis(self):
        message = "Hello 🌍! Cryptographie sécurisée 🔑 & 日本語 🌸"
        enc = encrypt_otp(message)
        dec = decrypt_otp(enc.ciphertext_bytes, enc.key_bytes)
        assert dec.is_valid_utf8 is True
        assert dec.decrypted_text == message

    def test_otp_roundtrip_raw_bytes(self):
        raw = bytes([0x00, 0xFF, 0x42, 0x7E, 0x1B, 0x80, 0xFE, 0x00])
        enc = encrypt_otp(raw)
        dec = decrypt_otp(enc.ciphertext_bytes, enc.key_bytes)
        assert dec.decrypted_bytes == raw

    def test_otp_traces_structure(self):
        msg = "Hi"
        key = b"\xaa\x55"
        enc = encrypt_otp(msg, key=key)

        assert len(enc.traces) == 2

        for i, trace in enumerate(enc.traces):
            assert isinstance(trace, ByteOTPTrace)
            assert trace.byte_index == i
            assert len(trace.bit_traces) == 8
            assert len(trace.p_bin) == 8
            assert len(trace.k_bin) == 8
            assert len(trace.c_bin) == 8

            # Verify bits are 7 down to 0
            for bit_idx, btrace in enumerate(trace.bit_traces):
                expected_bit_pos = 7 - bit_idx
                assert btrace.bit_index == expected_bit_pos
                assert btrace.bit_c == (btrace.bit_p ^ btrace.bit_k)
                assert btrace.formula == f"{btrace.bit_p} ^ {btrace.bit_k} = {btrace.bit_c}"

    def test_truth_table_formatter(self):
        enc = encrypt_otp("A", key=b"\x0f")
        trace = enc.traces[0]
        table_str = format_byte_truth_table(trace)
        assert "Byte Trace [Index 0]" in table_str
        assert "Bit" in table_str
        assert "Formula" in table_str
        assert "0 ^" in table_str or "1 ^" in table_str

    def test_hex_and_base64_outputs(self):
        msg = "Test Hex & Base64"
        enc = encrypt_otp(msg)

        assert enc.plaintext_hex == msg.encode("utf-8").hex()
        assert enc.key_hex == enc.key_bytes.hex()
        assert enc.ciphertext_hex == enc.ciphertext_bytes.hex()
        assert base64.b64decode(enc.ciphertext_base64) == enc.ciphertext_bytes

    def test_key_longer_than_plaintext(self):
        msg = "Short"
        oversized_key = secrets.token_bytes(64)
        enc = encrypt_otp(msg, key=oversized_key)
        assert len(enc.key_bytes) == len(msg.encode("utf-8"))
        dec = decrypt_otp(enc.ciphertext_bytes, oversized_key)
        assert dec.decrypted_text == msg

    def test_key_shorter_than_plaintext(self):
        msg = "A long message that requires more key bytes"
        short_key = b"short"
        with pytest.raises(ValueError, match="Key length .* must be at least plaintext length"):
            encrypt_otp(msg, key=short_key)

        with pytest.raises(ValueError, match="Key length .* must be at least ciphertext length"):
            decrypt_otp(b"six_bytes", key=b"four")

    def test_empty_plaintext(self):
        enc_str = encrypt_otp("")
        assert enc_str.plaintext_bytes == b""
        assert enc_str.ciphertext_bytes == b""
        assert enc_str.key_bytes == b""
        assert enc_str.traces == []

        enc_bytes = encrypt_otp(b"")
        assert enc_bytes.plaintext_bytes == b""

        dec = decrypt_otp(b"", key=b"")
        assert dec.decrypted_bytes == b""
        assert dec.decrypted_text == ""
        assert dec.traces == []

    def test_ciphertext_as_hex_string(self):
        msg = "Hex Input Decryption"
        enc = encrypt_otp(msg)
        dec = decrypt_otp(enc.ciphertext_hex, enc.key_bytes)
        assert dec.decrypted_text == msg

    def test_invalid_hex_string(self):
        with pytest.raises(ValueError, match="Invalid hexadecimal string"):
            decrypt_otp("not_a_valid_hex_zz!", key=b"123456")
        with pytest.raises(ValueError, match="Invalid hexadecimal string"):
            decrypt_otp("abc", key=b"12")  # Odd number of hex digits

    def test_wrong_key_decryption(self):
        msg = "Top Secret Information"
        enc = encrypt_otp(msg)
        wrong_key = generate_otp_key(len(enc.key_bytes))

        dec = decrypt_otp(enc.ciphertext_bytes, wrong_key)
        # With high probability, wrong key produces invalid UTF-8 or garbled string
        assert dec.decrypted_bytes != msg.encode("utf-8")


# ===========================================================================
# 4. TestCryptographicIdentities
# ===========================================================================

class TestCryptographicIdentities:
    def test_xor_involution_property(self):
        m = b"Cryptographic Invariant Test"
        k = generate_otp_key(len(m))
        c = xor_bytes(m, k)
        recovered = xor_bytes(c, k)
        assert recovered == m

    def test_xor_identity_element(self):
        m = b"Identity Element Test"
        zero_key = bytes(len(m))  # All zeros
        assert xor_bytes(m, zero_key) == m

    def test_xor_self_inverse(self):
        m = b"Self Inverse Test"
        zero_key = bytes(len(m))
        assert xor_bytes(m, m) == zero_key

    def test_xor_commutativity(self):
        a = secrets.token_bytes(32)
        b = secrets.token_bytes(32)
        assert xor_bytes(a, b) == xor_bytes(b, a)

    def test_two_time_pad_key_cancellation(self):
        m1 = b"Message Number One: Attack at dawn!"
        m2 = b"Message Number Two: Retreat at once"
        key = generate_otp_key(len(m1))

        c1 = xor_bytes(m1, key)
        c2 = xor_bytes(m2, key)

        c1_xor_c2 = xor_bytes(c1, c2)
        m1_xor_m2 = xor_bytes(m1, m2)

        # C1 ^ C2 == M1 ^ M2
        assert c1_xor_c2 == m1_xor_m2


# ===========================================================================
# 5. TestTwoTimePadVulnerability
# ===========================================================================

class TestTwoTimePadVulnerability:
    def test_analyze_two_time_pad_basic(self):
        m1 = b"Top Secret Formula"
        m2 = b"Another Clear Text"
        k = generate_otp_key(len(m1))

        c1 = xor_bytes(m1, k)
        c2 = xor_bytes(m2, k)

        analysis = analyze_two_time_pad(c1, c2)
        assert isinstance(analysis, TwoTimePadAnalysis)
        assert analysis.xor_stream == xor_bytes(m1, m2)
        assert analysis.overlap_length == len(m1)
        assert "Two-Time Pad Key Cancellation Proof" in analysis.key_cancelled_proof
        assert len(analysis.sample_traces) == min(16, len(m1))
        assert analysis.sample_traces[0]["c1_val"] == c1[0]
        assert analysis.sample_traces[0]["c2_val"] == c2[0]

    def test_analyze_two_time_pad_unequal_lengths(self):
        c1 = b"Longer Ciphertext"
        c2 = b"Short"
        analysis = analyze_two_time_pad(c1, c2)
        assert analysis.overlap_length == 5
        assert len(analysis.xor_stream) == 5
        assert analysis.xor_stream == xor_bytes(c1[:5], c2)

    def test_analyze_two_time_pad_empty(self):
        analysis = analyze_two_time_pad(b"", b"")
        assert analysis.overlap_length == 0
        assert analysis.xor_stream == b""
        assert len(analysis.sample_traces) == 0

    def test_analyze_two_time_pad_hex_inputs(self):
        c1 = b"Alpha"
        c2 = b"Omega"
        analysis = analyze_two_time_pad(c1.hex(), c2.hex())
        assert analysis.c1_bytes == c1
        assert analysis.c2_bytes == c2


# ===========================================================================
# 6. TestCribDragging
# ===========================================================================

class TestCribDragging:
    def test_readability_score_english(self):
        # Plain English sentences must score >= 0.75
        s1 = english_readability_score(b"the confidential mission")
        s2 = english_readability_score(b"the secret attack is planned")
        s3 = english_readability_score(b"meet at midnight in the park")

        assert s1 >= 0.75, f"Expected s1 >= 0.75, got {s1}"
        assert s2 >= 0.75, f"Expected s2 >= 0.75, got {s2}"
        assert s3 >= 0.75, f"Expected s3 >= 0.75, got {s3}"

    def test_readability_score_random(self):
        # Pure random bytes must score <= 0.30
        for _ in range(10):
            rand_bytes = secrets.token_bytes(30)
            score = english_readability_score(rand_bytes)
            assert score <= 0.30, f"Random bytes scored too high: {score}"

    def test_readability_score_unprintable(self):
        unprintable = b"hello\x00\x01\x02world\xff\xfe"
        score = english_readability_score(unprintable)
        assert score < 0.30
        res = drag_crib(unprintable, "hello", offset=0)
        assert res.candidates[0].is_printable is False

    def test_drag_crib_known_position(self):
        m1 = b"the secret recipe is oregano"
        m2 = b"meet at midnight in the park"
        key = generate_otp_key(len(m1))
        c1 = xor_bytes(m1, key)
        c2 = xor_bytes(m2, key)
        xor_stream = xor_bytes(c1, c2)

        # Crib "the secret" (10 bytes) at offset 0
        res = drag_crib(xor_stream, "the secret", offset=0)
        assert isinstance(res, CribDragResult)
        assert len(res.candidates) == 1
        cand = res.candidates[0]
        assert cand.offset == 0
        assert cand.revealed_bytes == b"meet at mi"
        assert cand.revealed_text == "meet at mi"
        assert cand.is_printable is True
        assert cand.score >= 0.75

    def test_drag_crib_all_offsets(self):
        m1 = b"the secret recipe is oregano"
        m2 = b"meet at midnight in the park"
        key = generate_otp_key(len(m1))
        c1 = xor_bytes(m1, key)
        c2 = xor_bytes(m2, key)
        xor_stream = xor_bytes(c1, c2)

        crib = "the secret"
        res = drag_crib(xor_stream, crib)
        assert res.best_candidate is not None
        # Best candidate should be offset 0 where "meet at mi" is uncovered
        assert res.best_candidate.offset == 0
        assert res.best_candidate.revealed_text == "meet at mi"

    def test_drag_crib_out_of_bounds_offset(self):
        stream = b"0123456789"
        crib = "test"
        with pytest.raises(ValueError, match="out of bounds"):
            drag_crib(stream, crib, offset=-1)
        with pytest.raises(ValueError, match="out of bounds"):
            drag_crib(stream, crib, offset=7)  # 7 + 4 = 11 > 10

    def test_drag_crib_longer_than_stream(self):
        stream = b"short"
        crib = "longer than stream"
        res = drag_crib(stream, crib)
        assert len(res.candidates) == 0
        assert res.best_candidate is None


# ===========================================================================
# 7. TestAutomatedCribDragAttack
# ===========================================================================

class TestAutomatedCribDragAttack:
    def test_auto_crib_drag_attack_finds_words(self):
        m1 = "the secret plan is finalized"
        m2 = "meet at dawn for coffee test"
        key = generate_otp_key(len(m1))
        c1 = xor_bytes(m1.encode(), key)
        c2 = xor_bytes(m2.encode(), key)

        result = auto_crib_drag_attack(c1, c2, top_n=15)
        assert isinstance(result, AutoCribDragResult)
        assert result.overlap_length == len(m1)
        assert len(result.top_candidates) > 0
        assert result.tested_crib_count == len(DEFAULT_CRIB_DICTIONARY)

        # Check that common words were dragged and top candidate has high score
        top = result.top_candidates[0]
        assert top.score >= 0.65
        assert top.is_printable is True

        # Ensure reconstructed snippets contain decoded characters
        assert any(ch != "." for ch in result.reconstructed_m1_snippet)
        assert any(ch != "." for ch in result.reconstructed_m2_snippet)

    def test_auto_crib_drag_custom_dictionary(self):
        m1 = "alpha beta gamma delta epsilon"
        m2 = "secret cipher message payload!"
        key = generate_otp_key(len(m1))
        c1 = xor_bytes(m1.encode(), key)
        c2 = xor_bytes(m2.encode(), key)

        custom_dict = ["alpha", "secret", "cipher", "delta"]
        result = auto_crib_drag_attack(c1, c2, dictionary=custom_dict, top_n=5)
        assert result.tested_crib_count == 4
        assert len(result.top_candidates) <= 5

    def test_auto_crib_drag_ranking_order(self):
        m1 = "information security pedagogy"
        m2 = "understanding the one time pad"
        key = generate_otp_key(len(m1))
        c1 = xor_bytes(m1.encode(), key)
        c2 = xor_bytes(m2.encode(), key)

        result = auto_crib_drag_attack(c1, c2, top_n=10)
        cands = result.top_candidates
        for i in range(len(cands) - 1):
            assert cands[i].score >= cands[i + 1].score


# ===========================================================================
# 8. TestEdgeCasesAndValidation
# ===========================================================================

class TestEdgeCasesAndValidation:
    def test_single_quote_and_unprintable_trace_formatting(self):
        enc = encrypt_otp(b"It's \x00\xff")
        # Check trace for single quote
        quote_trace = enc.traces[2]  # "'"
        assert quote_trace.p_char == r"'\''"
        # Check trace for null byte
        null_trace = enc.traces[5]  # \x00
        assert null_trace.p_char == r"'\x00'"
        # Check trace for 0xff byte
        ff_trace = enc.traces[6]  # \xff
        assert ff_trace.p_char == r"'\xff'"

    def test_type_error_validations(self):
        with pytest.raises(TypeError, match="Plaintext must be str or bytes"):
            encrypt_otp(12345)  # type: ignore

        with pytest.raises(TypeError, match="Key must be bytes or None"):
            encrypt_otp("hello", key="string_key")  # type: ignore

        with pytest.raises(TypeError, match="ciphertext must be bytes or hex str"):
            decrypt_otp(12345, key=b"key")  # type: ignore

        with pytest.raises(TypeError, match="Key must be bytes"):
            decrypt_otp(b"data", key="string_key")  # type: ignore

        with pytest.raises(TypeError, match="xor_stream must be bytes or hex str"):
            drag_crib(12345, "crib")  # type: ignore

        with pytest.raises(TypeError, match="crib must be str or bytes"):
            drag_crib(b"stream", 12345)  # type: ignore

    def test_drag_crib_polymorphism_and_empty(self):
        # Hex stream input and bytes crib on valid two-message XOR stream
        m1 = b"the first message here"
        m2 = b"and second message now"
        stream = xor_bytes(m1, m2)
        res = drag_crib(stream.hex(), b"the first ")
        assert res.best_candidate is not None
        assert res.best_candidate.offset == 0
        assert res.best_candidate.revealed_bytes == b"and second"

        # Explicit offset with hex stream: guessing m1[10:17] ("message") reveals m2[10:17] (" messag")
        res_explicit = drag_crib(stream.hex(), b"message", offset=10)
        assert res_explicit.candidates[0].offset == 10
        assert res_explicit.candidates[0].revealed_bytes == b" messag"

        # Empty stream and empty crib
        empty_res1 = drag_crib(b"", "test")
        assert empty_res1.candidates == []
        empty_res2 = drag_crib(b"hello", "")
        assert empty_res2.candidates == []

    def test_auto_crib_drag_attack_empty_and_fallback(self):
        # Empty ciphertexts
        res_empty = auto_crib_drag_attack(b"", b"")
        assert res_empty.overlap_length == 0
        assert res_empty.top_candidates == []

        # Empty dictionary
        res_no_dict = auto_crib_drag_attack(b"hello", b"world", dictionary=[])
        assert res_no_dict.tested_crib_count == 0
        assert res_no_dict.top_candidates == []

        # Random bytes without clean English: tests fallback snippet generation
        c1 = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        c2 = b"\x80\x81\x82\x83\x84\x85\x86\x87"
        res_fallback = auto_crib_drag_attack(c1, c2, dictionary=["the", "and"])
        assert len(res_fallback.top_candidates) > 0
        assert len(res_fallback.reconstructed_m1_snippet) == 8

    def test_readability_all_unprintable(self):
        all_unprintable = bytes([0x00, 0x01, 0x02, 0x03, 0x04])
        assert english_readability_score(all_unprintable) == 0.0
        assert english_readability_score(b"") == 0.0

    def test_xor_bytes_unequal_lengths(self):
        b1 = b"abcde"
        b2 = b"123"
        result = xor_bytes(b1, b2)
        assert len(result) == 3
        assert result == bytes([b1[i] ^ b2[i] for i in range(3)])

    def test_frozen_dataclass_immutability(self):
        from dataclasses import FrozenInstanceError

        btrace = BitXORTrace(bit_index=7, bit_p=1, bit_k=0, bit_c=1, formula="1 ^ 0 = 1")
        with pytest.raises(FrozenInstanceError):
            btrace.bit_c = 0  # type: ignore

        ent = EntropyAnalysis(data_length=10, entropy=5.0)
        with pytest.raises(FrozenInstanceError):
            ent.entropy = 6.0  # type: ignore

    def test_perfect_secrecy_notes_content(self):
        enc = encrypt_otp("Test Secrecy Notes")
        assert "Shannon's Perfect Secrecy Theorem" in enc.perfect_secrecy_notes
        assert "Truly Random Key" in enc.perfect_secrecy_notes
        assert "Key Length Match" in enc.perfect_secrecy_notes
        assert "Absolute One-Time Use" in enc.perfect_secrecy_notes

