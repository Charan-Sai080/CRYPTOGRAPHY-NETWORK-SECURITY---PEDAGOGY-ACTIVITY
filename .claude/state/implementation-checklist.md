# Implementation Checklist: Pedagogy Platform

## Milestone 1: Math Core
- [x] Implement Extended Euclidean Algorithm (`ext_gcd(a, b) -> (g, x, y)`).
- [x] Implement modular inverse (`mod_inverse(a, m) -> int`).
- [x] Implement Miller-Rabin primality test (`is_prime(n, k=40) -> bool`).
- [x] Implement safe prime generator (`generate_safe_prime(bits) -> (p, q)`).
- [x] Implement primitive root generator (`find_primitive_root(p) -> int`).
- [x] Implement traced modular exponentiation (`mod_pow_traced(base, exp, mod) -> (result, trace)`).
- [x] Unit tests for all mathematical primitives (34/34 passing).

## Milestone 2: One-Time Pad (OTP)
- [x] Implement CSPRNG key generator (`generate_otp_key(length) -> bytes`).
- [x] Implement byte-level XOR encryption and decryption.
- [x] Implement ASCII/UTF-8 and Hex/Base64 serialization.
- [x] Implement length validation and Shannon perfect secrecy explanation.
- [x] Implement Two-Time Pad vulnerability analyzer (crib-dragging demonstration).
- [x] Unit tests covering edge cases (52/52 passing, 86/86 total).

## Milestone 3: Linear Congruential Generator (LCG)
- [x] Implement configurable LCG generator (`next_lcg(x, a, c, m)`).
- [x] Implement library of standard presets (ANSI C, POSIX, MINSTD, Borland).
- [x] Implement Hull-Dobell theorem validator (`verify_hull_dobell(a, c, m) -> (is_full, details)`).
- [x] Implement Floyd's cycle-finding algorithm (`find_cycle(a, c, m, x0) -> (period, cycle_start)`).
- [x] Implement Chi-square uniformity test (`chi_square_uniformity(sequence, m, bins)`).
- [x] Implement 2D and 3D hyperplane coordinate generator.
- [x] Unit tests for LCG algorithms and period checks (56/56 passing, 143/143 total).

## Milestone 4: ElGamal Cryptosystem
- [x] Implement domain parameter generation (educational small primes and RFC MODP groups).
- [x] Implement key pair generation (`generate_elgamal_keys(p, g) -> (priv, pub)`).
- [x] Implement encryption with calculation trace (`encrypt_elgamal(m, pub, p, g, k)`).
- [x] Implement decryption with calculation trace (`decrypt_elgamal(c1, c2, priv, p)`).
- [x] Implement message chunking for arbitrary text strings.
- [x] Implement multiplicative homomorphism demonstration.
- [x] Implement ephemeral key $k$ reuse vulnerability demonstration.
- [x] Unit tests for ElGamal cryptosystem and edge cases (61/61 passing, 204/204 total).

## Milestone 5: Digital Signature Algorithm (DSA)
- [x] Implement FIPS 186-4 parameter generator ($(p, q, g)$).
- [x] Implement key pair generation (`generate_dsa_keys(p, q, g) -> (priv, pub)`).
- [x] Implement signing with SHA-256 and $k$-resampling (`sign_dsa(message, priv, p, q, g, k)`).
- [x] Implement verification with calculation trace (`verify_dsa(message, r, s, pub, p, q, g)`).
- [x] Implement real-time document tampering detector.
- [x] Implement Sony PS3 style nonce-reuse private key recovery exploit.
- [x] Unit tests for DSA signing, verification, and tamper detection (41/41 passing, 245/245 total).

## Milestone 6: Backend API Layer (FastAPI)
- [ ] Set up FastAPI project structure with CORS and error handlers.
- [ ] Create Pydantic models for OTP, LCG, ElGamal, and DSA endpoints.
- [ ] Implement routes under `/api/v1/otp/*`.
- [ ] Implement routes under `/api/v1/lcg/*`.
- [ ] Implement routes under `/api/v1/elgamal/*`.
- [ ] Implement routes under `/api/v1/dsa/*`.
- [ ] Automated pytest suite covering API routes with 100% endpoint pass rate.

## Milestone 7: Frontend Web Application
- [ ] Set up modern React + TypeScript + Tailwind CSS project.
- [ ] Build global layout, navigation, and cryptographic pedagogy documentation syllabus.
- [ ] Build Lab 1: One-Time Pad Interactive Lab & Two-Time Pad Cracker.
- [ ] Build Lab 2: LCG Parameter Explorer, Cycle Visualizer, & 2D/3D Lattice Plot.
- [ ] Build Lab 3: ElGamal Key Exchange, Step-by-Step Math, & Homomorphic Playground.
- [ ] Build Lab 4: DSA Document Signer, Live Tamper Tester, & PS3 Nonce Exploit.

## Milestone 8: Deployment & Packaging
- [ ] Create multi-stage Dockerfile bundling FastAPI backend and built frontend assets.
- [ ] Verify production container startup and test suite execution.
- [ ] Provide hosting guides and README documentation.
