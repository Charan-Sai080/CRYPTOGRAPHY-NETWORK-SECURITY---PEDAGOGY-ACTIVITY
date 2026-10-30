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
- [x] Set up FastAPI project structure with CORS and error handlers.
- [x] Create Pydantic models for OTP, LCG, ElGamal, and DSA endpoints.
- [x] Implement routes under `/api/v1/otp/*`.
- [x] Implement routes under `/api/v1/lcg/*`.
- [x] Implement routes under `/api/v1/elgamal/*`.
- [x] Implement routes under `/api/v1/dsa/*`.
- [x] Automated pytest suite covering API routes with 100% endpoint pass rate (37/37 passing, 282/282 overall).

## Milestone 7: Frontend Web Application
- [ ] **M7.1: Frontend Scaffolding, Tailwind Setup, Theme System, Header/Nav/Layout, API Base**
  - [ ] Initialize Vite + React + TypeScript + Tailwind CSS in `frontend/`.
  - [ ] Implement `ThemeContext` (Dark/Light mode with `localStorage` persistence).
  - [ ] Build responsive `AppLayout`, `Navbar` with API health polling, and `Footer`.
  - [ ] Configure typed Axios API base client (`baseURL: http://localhost:8000/api/v1`) with error interceptors.
  - [ ] Build reusable UI component library (`Card`, `Badge`, `Button`, `MathFormula` with KaTeX, `AlertBanner`, `SkeletonLoader`).
  - [ ] Implement `DashboardPage` highlighting the 4 pedagogical pillars and syllabus.
- [ ] **M7.2: One-Time Pad Lab UI**
  - [ ] Implement CSPRNG key generator with encoding formats (hex, base64, ascii).
  - [ ] Implement Shannon entropy radial gauge ($0.0 - 8.0$ bits/byte) with mathematical interpretation.
  - [ ] Implement traced encryption/decryption sandbox with live bit-by-bit truth table and byte visualizer.
  - [ ] Implement Two-Time Pad vulnerability sandbox showing key cancellation ($C_1 \oplus C_2 = P_1 \oplus P_2$).
  - [ ] Implement interactive crib-dragging slider and automated dictionary-based plaintext recovery.
- [ ] **M7.3: Linear Congruential Generator (LCG) Lab UI**
  - [ ] Implement parameter form ($m, a, c, X_0$) with historical presets dropdown.
  - [ ] Implement step-by-step arithmetic trace inspector table ($X_{n+1} = (a X_n + c) \pmod m$).
  - [ ] Implement Hull-Dobell theorem validator with condition-by-condition cards and prime factors visualizer.
  - [ ] Implement Floyd's cycle-finding (tortoise-and-hare) empirical period and cycle start visualizer.
  - [ ] Implement Chi-Square uniformity goodness-of-fit bar chart with observed vs expected bins and p-value.
  - [ ] Implement Marsaglia 2D and 3D hyperplane lattice scatter plots (Canvas/SVG) with theoretical bounds.
  - [ ] Implement algebraic LCG state cracker playground.
- [ ] **M7.4: ElGamal Cryptosystem Lab UI**
  - [ ] Implement domain presets dropdown (RFC 2409 1024-bit group, educational primes) and safe prime generator.
  - [ ] Implement Alice & Bob interactive key exchange architectural diagram.
  - [ ] Implement traced single-integer and multi-block UTF-8 text encryption/decryption with KaTeX formulas.
  - [ ] Implement multiplicative homomorphism multiplier playground ($E(m_1) \cdot E(m_2) = E(m_1 \cdot m_2 \pmod p)$).
  - [ ] Implement ephemeral nonce reuse cryptanalysis exploit sandbox ($c_{1,a} = c_{1,b}$).
- [ ] **M7.5: Digital Signature Algorithm (DSA) Lab UI**
  - [ ] Implement FIPS 186-4 standard and educational domain parameter selector & key pair generator.
  - [ ] Implement document signing interface with SHA-256 hash truncation and FIPS 186-4 resampling trace.
  - [ ] Implement step-by-step signature verification with complete LaTeX proof.
  - [ ] Implement real-time single-bit document and signature tampering simulator with divergence detector.
  - [ ] Implement Sony PS3 Nonce-Reuse Private Key Extraction playground ($k = (z_1 - z_2)(s_1 - s_2)^{-1} \pmod q$).
- [ ] **M7.6: Frontend Production Build, Type-check, and Integration Verification**
  - [ ] Configure Vite production build and asset bundling.
  - [ ] Validate strict TypeScript compilation (`tsc --noEmit`) with 0 errors.
  - [ ] Verify Tailwind CSS purging and responsive layouts across mobile, tablet, and desktop viewports.
  - [ ] Perform end-to-end integration smoke testing against FastAPI backend endpoints.

## Milestone 8: Deployment & Packaging
- [ ] Create multi-stage Dockerfile bundling FastAPI backend and built frontend assets.
- [ ] Verify production container startup and test suite execution.
- [ ] Provide hosting guides and README documentation.
