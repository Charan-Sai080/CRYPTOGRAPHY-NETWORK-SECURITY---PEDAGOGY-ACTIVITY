# Context Packet 2: Milestone 2 One-Time Pad Engine & Two-Time Pad Cryptanalysis

## 1. Task Goal
Implement the One-Time Pad (OTP) Engine and Two-Time Pad Key-Reuse Cryptanalysis in pure Python 3.12+, providing full pedagogical step-by-step traces, Shannon entropy measurements, truth tables, automated crib-dragging cryptanalysis, and a comprehensive Pytest 8.x test suite.

## 2. Granular Sub-Milestones
* **M2.1**: Core OTP Engine with Byte/Bit XOR, CSPRNG Key Generation, and Pedagogical Execution Traces (bit-by-bit truth table, byte-by-byte inspection, Shannon entropy analysis). Detailed Context: [context-packet-2.1.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-2.1.md)
* **M2.2**: Two-Time Pad (Key Reuse) Vulnerability Engine & Automated Crib-Dragging Cryptanalysis (algebraic key cancellation proof, English readability heuristics, interactive and automated crib dragging). Detailed Context: [context-packet-2.2.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-2.2.md)
* **M2.3**: Comprehensive Pytest 8.x Test Suite & Cryptographic Identities (normal paths, edge cases, length mismatches, algebraic identities, 100% test coverage). Detailed Context: [context-packet-2.3.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-2.3.md)

## 3. Allowed Files
* `backend/core/otp.py`
* `backend/core/__init__.py`
* `backend/tests/test_otp.py`
* `backend/tests/__init__.py`

## 4. Key Architectural Deliverables
* **CSPRNG Key Generation (`generate_otp_key(length) -> bytes`)**: Cryptographically secure keys generated via `secrets.token_bytes`.
* **Shannon Entropy Engine (`calculate_shannon_entropy(data) -> EntropyAnalysis`)**: Computes $H(X) = -\sum P(x) \log_2 P(x)$, byte frequencies, and pedagogical notes explaining Shannon's Perfect Secrecy theorem.
* **OTP Encryption & Tracing (`encrypt_otp(plaintext, key=None) -> OTPEncryptionResult`)**: Traces every byte and every bit (8 `BitXORTrace` entries per byte from MSB to LSB), outputs hex, base64, and formatted truth tables.
* **OTP Decryption (`decrypt_otp(ciphertext, key) -> OTPDecryptionResult`)**: Symmetric decryption with trace reconstruction and UTF-8 validation.
* **Two-Time Pad Analysis (`analyze_two_time_pad(c1, c2) -> TwoTimePadAnalysis`)**: Proves key cancellation: $C_1 \oplus C_2 = M_1 \oplus M_2$.
* **Crib-Dragging Engine (`drag_crib(xor_stream, crib, offset=None) -> CribDragResult`)**: Slides crib across XOR stream and computes candidate plaintexts.
* **English Readability Heuristic (`english_readability_score(data) -> float`)**: Evaluates natural language plausibility $[0.0, 1.0]$ based on ASCII printability, ETAOIN SHRDLU frequency distribution, and punctuation.
* **Automated Crib-Dragging Attack (`auto_crib_drag_attack(c1, c2, dictionary, top_n) -> AutoCribDragResult`)**: Evaluates common English cribs against $C_1 \oplus C_2$ and ranks candidate decrypted snippets.
* **Pytest 8.x Test Suite (`backend/tests/test_otp.py`)**: Covers all normal paths, edge cases, key length mismatches, and cryptographic identities with complete test coverage.

## 5. Acceptance Criteria
1. Strictly typed with dataclasses and modern Python 3.12+ type annotations (`int | None`, `str | bytes`, `list[T]`).
2. Pedagogical transparency: every encryption/decryption produces structured bit/byte traces and truth tables.
3. Cryptographic correctness: Involution $(M \oplus K) \oplus K = M$ and Key Cancellation $C_1 \oplus C_2 = M_1 \oplus M_2$ verified.
4. All unit tests pass using `pytest backend/tests/test_otp.py` without warnings or regressions.
