# Milestones: Cryptography Pedagogy Platform

## Milestone 1: Mathematical Foundations Core Engine
* Extended Euclidean Algorithm (GCD and modular inverse).
* Miller-Rabin primality test (probabilistic and deterministic for small sets).
* Safe prime and primitive root generators.
* Fast modular exponentiation with pedagogical trace extraction.

## Milestone 2: One-Time Pad (OTP) Engine
* True random key generation (CSPRNG).
* Bitwise and byte-level XOR encryption and decryption.
* Shannon entropy and perfect secrecy mathematical explanation.
* Two-Time Pad vulnerability demonstration and crib-dragging analyzer.
* 100% test coverage with edge cases.

## Milestone 3: Linear Congruential Generator (LCG) Engine
* LCG sequence generation with standard presets (ANSI C, POSIX, MINSTD, etc.).
* Hull-Dobell theorem validator for full period verification.
* Floyd's cycle-finding algorithm for empirical period calculation.
* Chi-square goodness-of-fit uniformity test.
* 2D/3D lattice hyperplane point generation.

## Milestone 4: ElGamal Cryptosystem Engine
* Small educational prime generation vs RFC MODP standard groups.
* Key generation: $(p, g, x) \to y$.
* Encryption and decryption with step-by-step arithmetic traces.
* Arbitrary text message chunking and numerical encoding.
* Multiplicative homomorphic property demonstration.
* Ephemeral key $k$ reuse vulnerability demonstration.

## Milestone 5: Digital Signature Algorithm (DSA) Engine
* FIPS 186-4 parameter generation ($(p, q, g)$).
* Private/public key generation ($(x, y)$).
* Signing process with SHA-256 and $k$-resampling.
* Verification process with detailed intermediate variables ($w, u_1, u_2, v$).
* Real-time document tampering detector.
* Sony PS3 nonce-reuse private key recovery exploit.

## Milestone 6: Backend API Layer (FastAPI)
* Fully typed Pydantic models for requests, responses, and calculation traces.
* Clean REST API routing under `/api/v1/*`.
* CORS middleware, error handling, and auto-generated Swagger/OpenAPI docs.
* Comprehensive test suite (`pytest`) covering happy paths, edge cases, and failure modes.

## Milestone 7: Interactive Pedagogical Frontend
* React + TypeScript + Tailwind CSS user interface.
* 4 dedicated interactive labs for OTP, LCG, ElGamal, and DSA.
* Live parameter tuning, canvas/SVG cycle diagrams, 2D/3D scatter plots, and vulnerability sandboxes.

## Milestone 8: Packaging & Deployment Readiness
* Production build configuration and multi-stage Dockerfile.
* Unified single-command runner for local and hosted execution.
* Pedagogical user guide and documentation.
