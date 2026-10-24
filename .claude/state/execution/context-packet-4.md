# Context Packet 4: Milestone 4 ElGamal Public-Key Cryptosystem & Multiplicative Homomorphism

## 1. Task Goal
Implement the ElGamal Public-Key Cryptosystem, Domain Parameter Management, Key Pair Generation, Traced Encryption & Decryption, Multi-Block Arbitrary Text Chunking, Multiplicative Homomorphic Multiplication Engine, and Ephemeral Nonce-Reuse Cryptanalytic Exploit in pure Python 3.12+ with exhaustive pedagogical step traces and a comprehensive Pytest 8.x test suite.

## 2. Granular Sub-Milestones
* **M4.1: Domain Parameter & Key Pair Generation Engine**: Domain parameter setup (Educational primes 16-bit to 32-bit, RFC 2409 1024-bit MODP group, custom safe prime generator $p = 2q + 1$), primitive root verification over $\mathbb{Z}_p^*$, secure key generation ($x \in [2, p - 2]$, $y = g^x \pmod p$), structured key models (`ElGamalDomainParams`, `ElGamalPublicKey`, `ElGamalPrivateKey`, `ElGamalKeyPair`), and integrity verification. Detailed Context: [context-packet-4.1.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-4.1.md)
* **M4.2: Traced Encryption & Decryption Engine with Arbitrary Text Chunking**: Ephemeral nonce generation ($k \in [2, p - 2]$ with $\gcd(k, p - 1) = 1$), ciphertext computation ($c_1 = g^k \pmod p$, shared secret $s = y^k \pmod p$, $c_2 = (m \cdot s) \pmod p$), decryption with modular inversion ($s = c_1^x \pmod p$, $s^{-1} = \text{mod\_inverse}(s, p)$, $m = (c_2 \cdot s^{-1}) \pmod p$), exhaustive pedagogical step traces, and multi-block UTF-8 text chunking and reconstruction. Detailed Context: [context-packet-4.2.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-4.2.md)
* **M4.3: Multiplicative Homomorphism & Nonce-Reuse Exploit Demonstrations**: Multiplicative homomorphic property ($E(m_1) \cdot E(m_2) = (c_{1,a} \cdot c_{1,b} \pmod p, c_{2,a} \cdot c_{2,b} \pmod p) = E(m_1 \cdot m_2 \pmod p)$) with decryption proof, and Ephemeral Nonce-Reuse Exploit (given $c_{1,a} = c_{1,b}$ and known plaintext $m_1$, compute $m_2 = (m_1 \cdot c_{2,b} \cdot c_{2,a}^{-1}) \pmod p$ without the private key). Detailed Context: [context-packet-4.3.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-4.3.md)
* **M4.4: Comprehensive Pytest 8.x Test Suite**: Exhaustive unit test suite covering domain parameter validation, key generation, encryption/decryption roundtrips, arbitrary text chunking, homomorphic properties, cryptanalytic nonce reuse, and edge-case exceptions in `backend/tests/test_elgamal.py`. Detailed Context: [context-packet-4.4.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-4.4.md)

## 3. Allowed Files
* `backend/core/elgamal.py`
* `backend/core/__init__.py`
* `backend/tests/test_elgamal.py`
* `backend/tests/__init__.py`

## 4. Key Architectural Deliverables
* **Domain Parameter & Key Management (`ElGamalDomainParams`, `ElGamalPublicKey`, `ElGamalPrivateKey`, `ElGamalKeyPair`, `DOMAIN_PRESETS`)**:
  - Encapsulates prime modulus $p$, generator $g$, group bit size, and optional subprime $q$.
  - Presets catalog: RFC 2409 1024-bit MODP group, educational 16-bit, 20-bit, 24-bit safe prime, and 32-bit safe prime groups.
  - Safe prime generation utility deriving $p = 2q + 1$ with confirmed primitive root $g$.
  - Structured key pair generation with cryptographically secure random exponent $x \in [2, p - 2]$ via `secrets.randbelow`.
* **Traced Encryption & Decryption Engine (`encrypt_integer`, `decrypt_integer`, `encrypt_message`, `decrypt_message`)**:
  - Ephemeral nonce selection $k \in [2, p - 2]$ such that $\gcd(k, p - 1) = 1$.
  - Ephemeral component $c_1 = g^k \pmod p$, shared secret $s = y^k \pmod p$, and masked component $c_2 = (m \cdot s) \pmod p$.
  - Decryption via shared secret recovery $s = c_1^x \pmod p$, inverse $s^{-1} = \text{mod\_inverse}(s, p)$, and plaintext extraction $m = (c_2 \cdot s^{-1}) \pmod p$.
  - Comprehensive per-step arithmetic trace records (`ElGamalEncryptTrace`, `ElGamalDecryptTrace`) capturing intermediate exponentiations, inversions, and latex-style pedagogical formula strings.
  - Block chunking via `string_to_int_blocks` and `int_blocks_to_string` ensuring any UTF-8 message of arbitrary length can be encrypted and decrypted.
* **Homomorphic Multiplication Engine (`multiply_ciphertexts`, `demonstrate_multiplicative_homomorphism`)**:
  - Implements component-wise modular multiplication $(c_{1,a} \cdot c_{1,b} \pmod p, c_{2,a} \cdot c_{2,b} \pmod p)$.
  - Proves that decrypting the product ciphertext yields $(m_1 \cdot m_2) \pmod p$ without revealing individual plaintexts.
  - Generates detailed mathematical proofs and verification records.
* **Ephemeral Nonce-Reuse Exploit Engine (`exploit_nonce_reuse`)**:
  - Detects duplicate ephemeral nonces ($c_{1,a} == c_{1,b}$).
  - Executes known-plaintext attack: recovers unknown message $m_2 = (m_1 \cdot c_{2,b} \cdot c_{2,a}^{-1}) \pmod p$ without knowledge of the private key $x$.
  - Computes plaintext quotient $m_1 \cdot m_2^{-1} \pmod p$ even when neither plaintext is initially known.
* **Exhaustive Pytest 8.x Suite (`backend/tests/test_elgamal.py`)**:
  - Tests parameter boundary validation, key generation entropy and validity, traced calculations, text chunking round-trips, homomorphic multiplication, and cryptanalytic exploit verification.

## 5. Acceptance Criteria
1. Strictly typed with dataclasses and modern Python 3.12+ syntax (`int | None`, `tuple[int, int]`, `list[T]`).
2. Pure Python standard library implementation: zero external dependencies beyond `backend.core.number_theory`.
3. Clear domain exception hierarchy (`ElGamalError`, `InvalidDomainParametersError`, `InvalidKeyError`, `EncryptionError`, `DecryptionError`, `CryptanalysisError`).
4. Full pedagogical traceability: all encryption and decryption operations provide structured trace objects suitable for educational UI visualization.
5. All tests in `backend/tests/test_elgamal.py` pass cleanly with 100% functional coverage, and zero regressions in `test_number_theory.py`, `test_otp.py`, or `test_lcg.py`.
