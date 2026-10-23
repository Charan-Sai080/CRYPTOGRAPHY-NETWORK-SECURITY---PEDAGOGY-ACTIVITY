# Context Packet 2.3: Comprehensive Pytest 8.x Test Suite & Cryptographic Identities

## 1. Goal
Implement an exhaustive, modern Pytest 8.x unit test suite in `backend/tests/test_otp.py` covering 100% of the functions, dataclasses, validation rules, cryptographic invariants, and error paths introduced in Milestone 2 (`backend/core/otp.py`).

## 2. Allowed Files
* `backend/tests/test_otp.py`

## 3. Test Architecture & Structure

The test suite must be organized into clear, focused test classes adhering to Python 3.12+ and Pytest 8.x conventions:

```python
import pytest
import math
import secrets
from backend.core.otp import (
    BitXORTrace,
    ByteOTPTrace,
    EntropyAnalysis,
    OTPEncryptionResult,
    OTPDecryptionResult,
    TwoTimePadAnalysis,
    CribDragCandidate,
    CribDragResult,
    AutoCribDragResult,
    DEFAULT_CRIB_DICTIONARY,
    generate_otp_key,
    calculate_shannon_entropy,
    encrypt_otp,
    decrypt_otp,
    format_byte_truth_table,
    xor_bytes,
    analyze_two_time_pad,
    english_readability_score,
    drag_crib,
    auto_crib_drag_attack,
)
```

### Required Test Classes:
1. `TestOTPKeyGeneration`:
   - `test_generate_otp_key_length`: Verifies exact returned byte count for sizes: 0, 1, 16, 32, 256.
   - `test_generate_otp_key_randomness`: Verifies successive calls produce distinct, high-entropy keys.
   - `test_generate_otp_key_negative_length`: Verifies `ValueError` is raised for negative lengths.
2. `TestShannonEntropy`:
   - `test_zero_entropy_constant_bytes`: Constant sequences (e.g. `b"A" * 128` or `bytes([42] * 50)`) evaluate to exactly `0.0`.
   - `test_maximal_entropy_uniform_distribution`: Uniform array containing all 256 byte values `bytes(range(256))` evaluates to `8.0` bits/byte.
   - `test_two_symbol_entropy`: Alternating sequence `b"AB" * 64` evaluates to `1.0` bit/byte.
   - `test_four_symbol_entropy`: Sequence `b"ABCD" * 32` evaluates to `2.0` bits/byte.
   - `test_empty_data_entropy`: Empty `b""` returns `0.0` without divide-by-zero or math domain errors.
   - `test_entropy_explanation`: Verifies explanation string is present and describes information density.
3. `TestOTPEncryptionDecryption`:
   - `test_otp_roundtrip_ascii`: ASCII text encrypts and decrypts to original string.
   - `test_otp_roundtrip_unicode_and_emojis`: Verifies UTF-8 preservation for strings like `"Hello 🌍! Cryptographie sécurisée 🔑"`.
   - `test_otp_roundtrip_raw_bytes`: Binary byte sequences (including `\x00`, `\xff`, null bytes) roundtrip losslessly.
   - `test_otp_traces_structure`: Verifies each byte has 8 `BitXORTrace` elements, with bit 7 to bit 0, correct binary strings, and valid XOR truth tables ($p \oplus k = c$).
   - `test_truth_table_formatter`: Verifies `format_byte_truth_table` generates formatted ASCII output containing bit rows.
   - `test_hex_and_base64_outputs`: Verifies `plaintext_hex`, `key_hex`, `ciphertext_hex`, and `ciphertext_base64` match standard library codecs (`bytes.fromhex`, `base64.b64decode`).
   - `test_key_longer_than_plaintext`: Longer key is automatically sliced to plaintext length without error.
   - `test_key_shorter_than_plaintext`: Key shorter than plaintext raises `ValueError`.
   - `test_empty_plaintext`: Encrypting and decrypting empty input (`""` or `b""`) produces empty results safely.
   - `test_ciphertext_as_hex_string`: `decrypt_otp` cleanly accepts hex string input.
   - `test_invalid_hex_string`: Malformed hex string raises `ValueError`.
   - `test_wrong_key_decryption`: Decrypting with an incorrect key yields garbled output and sets `is_valid_utf8` appropriately.
4. `TestCryptographicIdentities`:
   - `test_xor_involution_property`: $(M \oplus K) \oplus K = M$.
   - `test_xor_identity_element`: $M \oplus 0 = M$.
   - `test_xor_self_inverse`: $M \oplus M = 0$.
   - `test_xor_commutativity`: $A \oplus B = B \oplus A$.
   - `test_two_time_pad_key_cancellation`: $C_1 \oplus C_2 == M_1 \oplus M_2$ where $C_1 = M_1 \oplus K$ and $C_2 = M_2 \oplus K$.
5. `TestTwoTimePadVulnerability`:
   - `test_analyze_two_time_pad_basic`: Computes $C_1 \oplus C_2$ and validates proof string and sample traces.
   - `test_analyze_two_time_pad_unequal_lengths`: Correctly slices to overlapping length `min(len(c1), len(c2))`.
   - `test_analyze_two_time_pad_empty`: Empty inputs handled safely.
6. `TestCribDragging`:
   - `test_readability_score_english`: Clean English strings (`"the confidential mission"`) score $\ge 0.75$.
   - `test_readability_score_random`: Random bytes score $\le 0.30$.
   - `test_readability_score_unprintable`: Bytes containing unprintable control codes score low and flag `is_printable = False`.
   - `test_drag_crib_known_position`: Encrypt two messages $M_1 = \text{"the secret recipe is oregano"}$ and $M_2 = \text{"meet at midnight in the park"}$ with the same key. Dragging crib `"the secret"` at offset 0 produces `"meet at mi"`.
   - `test_drag_crib_all_offsets`: Sliding a crib across all offsets identifies the true offset with highest score.
   - `test_drag_crib_out_of_bounds_offset`: Offset $< 0$ or exceeding available space raises `ValueError`.
   - `test_drag_crib_longer_than_stream`: Crib longer than stream returns empty candidates list.
7. `TestAutomatedCribDragAttack`:
   - `test_auto_crib_drag_attack_finds_words`: Encrypt two English sentences with the same key. Auto crib drag attack successfully finds dictionary words and includes true plaintexts among top matches.
   - `test_auto_crib_drag_custom_dictionary`: Custom dictionary parameter is respected.
   - `test_auto_crib_drag_ranking_order`: Candidates in `top_candidates` are sorted strictly descending by `score`.

## 4. Acceptance Criteria
1. **Pytest 8.x Execution**: All tests pass when run via `pytest backend/tests/test_otp.py`.
2. **Zero Failures & Zero Regressions**: All tests pass cleanly without errors, warnings, or regressions in existing `test_number_theory.py`.
3. **Comprehensive Coverage**: At least 25 dedicated test methods covering all branches, edge cases, and cryptographic identities.
4. **Deterministic Behavior**: Tests are fully deterministic; randomized tests use fixed seeds or bounded properties (e.g., verifying entropy ranges rather than brittle exact values).

## 5. Edge Cases
* **Empty inputs**: Tested across all functions (`b""`, `""`, zero lengths).
* **Boundary indices**: Offset 0, final possible offset (`len(stream) - len(crib)`), and out-of-bounds offsets (`-1`, `len(stream)`).
* **Binary edge cases**: Bytes `0x00`, `0xFF`, non-ASCII Latin-1 (`0xE9`), and Unicode 4-byte characters.
* **Type polymorphism**: Functions tested with both `str` and `bytes` inputs.
