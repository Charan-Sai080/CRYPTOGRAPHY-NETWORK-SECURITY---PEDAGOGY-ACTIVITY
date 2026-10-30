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
- [x] **M7.1: Frontend Scaffolding, Tailwind Setup, Theme System, Header/Nav/Layout, API Base**
  - [x] Initialize Vite + React + TypeScript + Tailwind CSS in `frontend/`.
  - [x] Implement `ThemeContext` (Dark/Light mode with `localStorage` persistence).
  - [x] Build responsive `AppLayout`, `Navbar` with API health polling, and `Footer`.
  - [x] Configure typed Axios API base client (`baseURL: http://localhost:8000/api/v1`) with error interceptors.
  - [x] Build reusable UI component library (`Card`, `Badge`, `Button`, `MathFormula` with KaTeX, `AlertBanner`, `SkeletonLoader`).
  - [x] Implement `DashboardPage` highlighting the 4 pedagogical pillars and syllabus.
- [x] **M7.2: One-Time Pad Lab UI**
  - [x] Implement CSPRNG key generator with encoding formats (hex, base64, ascii).
  - [x] Implement Shannon entropy radial gauge ($0.0 - 8.0$ bits/byte) with mathematical interpretation.
  - [x] Implement traced encryption/decryption sandbox with live bit-by-bit truth table and byte visualizer.
  - [x] Implement Two-Time Pad vulnerability sandbox showing key cancellation ($C_1 \oplus C_2 = P_1 \oplus P_2$).
  - [x] Implement interactive crib-dragging slider and automated dictionary-based plaintext recovery.
- [x] **M7.3: Linear Congruential Generator (LCG) Lab UI**
  - [x] Implement parameter form ($m, a, c, X_0$) with historical presets dropdown.
  - [x] Implement step-by-step arithmetic trace inspector table ($X_{n+1} = (a X_n + c) \pmod m$).
  - [x] Implement Hull-Dobell theorem validator with condition-by-condition cards and prime factors visualizer.
  - [x] Implement Floyd's cycle-finding (tortoise-and-hare) empirical period and cycle start visualizer.
  - [x] Implement Chi-Square uniformity goodness-of-fit bar chart with observed vs expected bins and p-value.
  - [x] Implement Marsaglia 2D and 3D hyperplane lattice scatter plots (Canvas/SVG) with theoretical bounds.
  - [x] Implement algebraic LCG state cracker playground.
- [x] **M7.4: ElGamal Cryptosystem Lab UI**
  - [x] Implement domain presets dropdown (RFC 2409 1024-bit group, educational primes) and safe prime generator.
  - [x] Implement Alice & Bob interactive key exchange architectural diagram.
  - [x] Implement traced single-integer and multi-block UTF-8 text encryption/decryption with KaTeX formulas.
  - [x] Implement multiplicative homomorphism multiplier playground ($E(m_1) \cdot E(m_2) = E(m_1 \cdot m_2 \pmod p)$).
  - [x] Implement ephemeral nonce reuse cryptanalysis exploit sandbox ($c_{1,a} = c_{1,b}$).
- [x] **M7.5: Digital Signature Algorithm (DSA) Lab UI**
  - [x] Implement FIPS 186-4 standard and educational domain parameter selector & key pair generator.
  - [x] Implement document signing interface with SHA-256 hash truncation and FIPS 186-4 resampling trace.
  - [x] Implement step-by-step signature verification with complete LaTeX proof.
  - [x] Implement real-time single-bit document and signature tampering simulator with divergence detector.
  - [x] Implement Sony PS3 Nonce-Reuse Private Key Extraction playground ($k = (z_1 - z_2)(s_1 - s_2)^{-1} \pmod q$).
- [x] **M7.6: Frontend Production Build, Type-check, and Integration Verification**
  - [x] Configure Vite production build and asset bundling.
  - [x] Validate strict TypeScript compilation (`tsc --noEmit`) with 0 errors.
  - [x] Verify Tailwind CSS purging and responsive layouts across mobile, tablet, and desktop viewports.
  - [x] Perform end-to-end integration smoke testing against FastAPI backend endpoints.

## Milestone 8: Packaging, Containerization (Docker), Production Serving & Deployment Guide
- [x] **M8.1: Unified Frontend Production Static File Serving via FastAPI**
  - [x] Configure `backend/main.py` to resolve `frontend/dist` directory safely.
  - [x] Mount `/assets` static directory to `frontend/dist/assets` using `StaticFiles`.
  - [x] Implement HTTP content negotiation on `GET /` to return `frontend/dist/index.html` for browser requests while preserving typed `RootResponse` JSON for API clients and tests.
  - [x] Implement catch-all SPA routing fallback returning `index.html` for direct browser navigation.
  - [x] Ensure all 282 backend tests continue passing with zero regressions.
- [x] **M8.2: Multi-Stage Production Dockerfile and docker-compose.yml**
  - [x] Implement multi-stage `Dockerfile` (`node:22-alpine` builder -> `python:3.12-slim` runner).
  - [x] Create non-root system user `appuser` (UID 10001) for container runtime security.
  - [x] Pin backend production dependencies in `backend/requirements.txt`.
  - [x] Configure container health check targeting `GET /api/v1/health`.
  - [x] Create `docker-compose.yml` for unified single-command deployment (`docker compose up --build`).
  - [x] Create comprehensive `.dockerignore` file.
- [x] **M8.3: Universal Orchestration Startup Script (`run.sh`)**
  - [x] Implement executable bash script `run.sh` with `set -euo pipefail` and clean signal handling.
  - [x] Support `./run.sh dev` for simultaneous FastAPI backend and Vite frontend development with auto-cleanup.
  - [x] Support `./run.sh prod` for frontend production build and unified FastAPI serving on port 8000.
  - [x] Support `./run.sh test` for backend pytest suite (282 tests) and frontend typecheck & build.
  - [x] Support `./run.sh docker` for Docker compose startup.
  - [x] Implement CLI help menu with colored diagnostic logging.
- [x] **M8.4: Comprehensive Project Documentation & Hosting Guide (`README.md`)**
  - [x] Author badges, vision, and pedagogy-first course syllabus overview.
  - [x] Document mathematical foundations and KaTeX formulas for all 4 pillars (OTP, LCG, ElGamal, DSA).
  - [x] Document real-world vulnerabilities and mathematical proofs (Two-Time Pad, Marsaglia hyperplanes, ElGamal nonce reuse, Sony PS3 fail0verflow private key recovery).
  - [x] Add system architecture Mermaid diagrams and technology stack comparison.
  - [x] Document complete REST API reference table for all 24+ endpoints.
  - [x] Document local dev, unified production, and Docker setup quickstarts.
  - [x] Document production cloud deployment options and reverse proxy guidelines.

