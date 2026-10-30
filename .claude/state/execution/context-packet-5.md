# Context Packet 5: Milestone 5 Digital Signature Algorithm (DSA) Engine & Nonce-Reuse Exploit

## 1. Task Goal
Implement the Digital Signature Algorithm (DSA) adhering to FIPS 186-4 specifications, Domain Parameter Management, Subgroup Generator Derivation, Cryptographically Secure Key Pair Generation, Traced Signing with SHA-256 and Resampling, Traced Signature Verification, Interactive Single-Bit Tampering Detection, and Ephemeral Nonce-Reuse Cryptanalytic Exploit (the classic Sony PS3 exploit) in pure Python 3.12+ with exhaustive pedagogical step traces and a comprehensive Pytest 8.x test suite.

## 2. Granular Sub-Milestones
* **M5.1: FIPS 186-4 Domain Parameter & Key Pair Generation Engine**:
  - Prime modulus $p$ and prime subprime divisor $q$ such that $q \mid (p - 1)$.
  - Generator $g = h^{(p - 1)/q} \pmod p > 1$ with $1 < h < p - 1$ and $g^q \equiv 1 \pmod p$.
  - Domain presets catalog: FIPS 186-4 standard 1024-bit/160-bit group (NIST CAVP validated), Educational 10-bit group ($p=607, q=101, g=64$), Educational 16-bit group ($p=34439, q=257, g=31028$), and Educational 24-bit group ($p=9044107, q=65537, g=5759125$).
  - Dynamic domain generator: `generate_dsa_domain(p_bits, q_bits)`.
  - Cryptographically secure key generation: Private key $x \in [1, q - 1]$ via CSPRNG (`secrets.randbelow(q - 1) + 1`), Public key $y = g^x \pmod p$.
  - Structured models: `DSADomainParams`, `DSAPublicKey`, `DSAPrivateKey`, `DSAKeyPair`.
  - Detailed Context: [context-packet-5.1.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-5.1.md)

* **M5.2: Traced Signing Engine with SHA-256 and FIPS 186-4 Resampling**:
  - Hash truncation: $z = \text{leftmost } \min(\text{bit\_length}(q), 256) \text{ bits of SHA-256}(M)$ via `sha256_digest_int(M, bit_limit=q.bit_length())`.
  - Ephemeral secret selection $k \in [1, q - 1]$ via CSPRNG (with optional deterministic `seed_k`).
  - Ephemeral component: $r = (g^k \pmod p) \pmod q$. If $r == 0$, resample $k$.
  - Inversion and signature component: $k^{-1} = \text{mod\_inverse}(k, q)$, $s = (k^{-1} \cdot (z + x \cdot r)) \pmod q$. If $s == 0$, resample $k$.
  - Tracing & result models: `DSASignature`, `DSASignTrace` capturing complete step-by-step arithmetic and retry counts.
  - Detailed Context: [context-packet-5.2.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-5.2.md)

* **M5.3: Traced Verification Engine & Interactive Tampering Detection**:
  - Boundary validation: verify $0 < r < q$ and $0 < s < q$; reject signature otherwise.
  - Inversion: $w = s^{-1} \pmod q = \text{mod\_inverse}(s, q)$.
  - Subgroup projections: $u_1 = (z \cdot w) \pmod q$, $u_2 = (r \cdot w) \pmod q$.
  - Verification point: $v = ((g^{u_1} \cdot y^{u_2}) \pmod p) \pmod q$.
  - Signature validity: Valid iff $v == r$.
  - Tracing & result models: `DSAVerifyTrace`, `DSAVerificationResult`.
  - Interactive tampering detector: demonstrates failure when 1 bit of message or signature components ($r, s$) is altered.
  - Detailed Context: [context-packet-5.3.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-5.3.md)

* **M5.4: Ephemeral Nonce $k$ Reuse Exploit (Sony PS3 Exploit)**:
  - Detect identical ephemeral nonces across distinct messages ($r_1 == r_2$ where $M_1 \neq M_2$).
  - Nonce recovery: $k = (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$.
  - Private key recovery: $x = (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$.
  - Complete algebraic derivation, step-by-step verification, and historical pedagogy documenting the 2010 PlayStation 3 fail0verflow ECDSA/DSA vulnerability.
  - Result model: `DSANonceReuseExploitResult`.
  - Detailed Context: [context-packet-5.4.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-5.4.md)

* **M5.5: Comprehensive Pytest 8.x Suite**:
  - Exhaustive unit test suite covering parameter validation, key generation, sign/verify roundtrips, edge-case resampling, single-bit tampering, and nonce-reuse cryptanalysis in `backend/tests/test_dsa.py`.
  - Detailed Context: [context-packet-5.5.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-5.5.md)

## 3. Allowed Files
* `backend/core/dsa.py`
* `backend/core/__init__.py`
* `backend/tests/test_dsa.py`
* `backend/tests/__init__.py`

## 4. Key Architectural Deliverables
* **Domain Parameter & Key Management (`DSADomainParams`, `DSAPublicKey`, `DSAPrivateKey`, `DSAKeyPair`, `DSA_PRESETS`)**:
  - Encapsulates prime modulus $p$, prime subgroup divisor $q$, and generator $g$.
  - Validates $q \mid (p - 1)$, $1 < g < p$, and $g^q \equiv 1 \pmod p$.
  - Presets catalog: Standard FIPS 186-4 1024/160-bit group, educational 10-bit, 16-bit, and 24-bit groups.
  - Generator derivation utility `derive_generator(p, q, h)` confirming $g = h^{(p-1)/q} \pmod p > 1$.
  - Dynamic prime generator `generate_dsa_domain(p_bits, q_bits)` using Miller-Rabin primality testing.
  - Key pair generator `generate_key_pair` with uniform random $x \in [1, q - 1]$ and $y = g^x \pmod p$.
* **Traced Signing Engine (`sign_message`, `sign_hash_int`, `generate_ephemeral_k`)**:
  - SHA-256 hashing and left-truncation to $N = \text{bit\_length}(q)$ bits.
  - Strict FIPS 186-4 resampling loop: if $r = (g^k \pmod p) \pmod q == 0$ or $s = (k^{-1}(z + xr)) \pmod q == 0$, a new $k$ is drawn.
  - Pedagogical trace object `DSASignTrace` recording message, hash digest, intermediate modular products, and LaTeX/formula explanations.
* **Traced Verification & Tampering Engine (`verify_message`, `verify_hash_int`, `detect_tampering`, `tamper_message_bit`, `tamper_signature_component`)**:
  - Verifies $0 < r < q$ and $0 < s < q$.
  - Computes $w = s^{-1} \pmod q$, $u_1 = (z \cdot w) \pmod q$, $u_2 = (r \cdot w) \pmod q$, and $v = ((g^{u_1} y^{u_2}) \pmod p) \pmod q$.
  - Signature valid iff $v == r$.
  - Interactive tampering detector generates comparative reports proving that flipping even 1 bit in the message or signature components ($r$ or $s$) causes verification failure.
* **Ephemeral Nonce-Reuse Exploit Engine (`exploit_nonce_reuse`)**:
  - Detects duplicate nonces $r_1 == r_2$ for messages $M_1 \neq M_2$.
  - Algebraically recovers $k = (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$.
  - Algebraically extracts private key $x = (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$.
  - Validates recovered $x$ against public key $y = g^x \pmod p$.
  - Generates full pedagogical proof and step traces.
* **Exhaustive Pytest 8.x Suite (`backend/tests/test_dsa.py`)**:
  - Unit tests covering all domain presets, random and seeded keys, signature generation, verification, resampling logic, tampering detection, and mathematical exploit verification.

## 5. Acceptance Criteria
1. Strictly typed with dataclasses and modern Python 3.12+ syntax (`int | None`, `tuple[int, int]`, `list[T]`).
2. Pure Python standard library implementation: zero external dependencies beyond `backend.core.number_theory`.
3. Clear domain exception hierarchy (`DSAError`, `InvalidDomainParametersError`, `InvalidKeyError`, `DSASignatureError`, `DSAVerificationError`, `DSACryptanalysisError`).
4. Full pedagogical traceability: all signing, verification, and exploit routines return structured trace objects formatted for educational visualization.
5. All tests in `backend/tests/test_dsa.py` pass cleanly with 100% functional coverage, and zero regressions across existing test suites (`test_number_theory.py`, `test_otp.py`, `test_lcg.py`, `test_elgamal.py`).
