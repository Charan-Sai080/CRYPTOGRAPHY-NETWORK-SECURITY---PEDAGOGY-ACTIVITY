# Context Packet 8.4: Comprehensive Project Documentation & Hosting Guide (`README.md`)

## 1. Goal
Author a comprehensive, publication-grade, pedagogy-first `README.md` in the repository root. The document serves as the primary syllabus guide for educators and students, a technical reference for cryptographic algorithms and exploits, an API manual, and a complete operations runbook.

---

## 2. Allowed Files
* `README.md` (repo root)

---

## 3. Required Sections & Detailed Content Specifications

### 3.1 Badges & Title
* Badges: Python 3.12, Node 22, React 18, FastAPI 0.115+, Tailwind CSS, Docker, Pytest 282/282 Passing, License MIT.
* Clear project summary: "Interactive Cryptography & Network Security Pedagogical Platform".

### 3.2 Pedagogical Vision & Philosophy
* Bridging abstract mathematical number theory and practical exploit demonstration.
* Emphasis on transparent, traced execution over black-box abstractions.
* 4 pillars designed to demonstrate:
  1. Information-Theoretic vs Computational Security (OTP vs Public Key).
  2. Pseudo-Randomness pitfalls in Cryptography (LCG vs CSPRNG).
  3. Homomorphic properties and malleable ciphertexts (ElGamal).
  4. Nonce catastrophies in real-world authentication (DSA Sony PS3 exploit).

### 3.3 System Architecture
* Mermaid architecture flowchart illustrating:
  - React 18 + TypeScript + Tailwind CSS Frontend SPA
  - FastAPI 0.115+ REST API Gateway
  - Core Cryptographic Engines (`otp.py`, `lcg.py`, `elgamal.py`, `dsa.py`)
  - Foundational Number Theory Engine (`number_theory.py`)
* Technology stack comparison table detailing versions and responsibilities.

### 3.4 Deep-Dive: The Four Cryptographic Pillars
Include rigorous mathematical formulas (LaTeX/KaTeX) and exploit mechanics for each pillar:
1. **Pillar 1: One-Time Pad (OTP) & Key Reuse**
   - Vernam Cipher definition: $C = P \oplus K$
   - Shannon's Theorem of Perfect Secrecy: $H(M|C) = H(M)$ when $H(K) \ge H(M)$ and $K$ is uniformly distributed.
   - Shannon Entropy calculation: $H(X) = -\sum_{i=1}^n P(x_i) \log_2 P(x_i)$ with 8.0 bits/byte ideal.
   - Two-Time Pad Vulnerability: Keystream cancellation $C_1 \oplus C_2 = P_1 \oplus P_2$.
   - Automated Crib-Dragging Algorithm with English unigram/bigram frequency scoring.
2. **Pillar 2: Linear Congruential Generator (LCG) & Lattice Analysis**
   - Recurrence relation: $X_{n+1} = (a X_n + c) \pmod m$
   - Hull-Dobell Theorem conditions for full period $m$:
     1. $\gcd(c, m) = 1$
     2. Every prime factor $q \mid m$ divides $(a - 1)$
     3. If $4 \mid m$, then $4 \mid (a - 1)$
   - Floyd's Cycle-Finding Algorithm (Tortoise and Hare) detecting period $\lambda$ and start $\mu$.
   - Pearson's Chi-Square ($\chi^2$) Uniformity Goodness-of-Fit test with Wilson-Hilferty transformation.
   - Marsaglia's Theorem: Proving $d$-dimensional random vectors fall on at most $(d! \cdot m)^{1/d}$ hyperplanes.
   - Algebraic State Reconstruction Attack: Recovering parameters $(a, c)$ from 3 consecutive outputs.
3. **Pillar 3: ElGamal Public-Key Cryptosystem & Homomorphism**
   - Keypair generation over $\mathbb{Z}_p^*$: $x \in [2, p - 2]$, $y = g^x \pmod p$.
   - Traced Encryption: Ephemeral nonce $k$, $c_1 = g^k \pmod p$, $c_2 = m \cdot y^k \pmod p$.
   - Traced Decryption: $s = c_1^x \pmod p$, $m = c_2 \cdot s^{-1} \pmod p$.
   - Multiplicative Homomorphism:
     $$E(m_1) \cdot E(m_2) = (c_{1,1} \cdot c_{1,2} \pmod p, c_{2,1} \cdot c_{2,2} \pmod p) = E(m_1 \cdot m_2 \pmod p)$$
   - Ephemeral Nonce-Reuse Exploit: Recovering plaintext without the private key when $c_{1,a} = c_{1,b}$:
     $$m_b = m_a \cdot c_{2,b} \cdot (c_{2,a})^{-1} \pmod p$$
4. **Pillar 4: Digital Signature Algorithm (DSA) & Sony PS3 Exploit**
   - FIPS 186-4 Domain Parameters: $(p, q, g)$ where $q \mid (p - 1)$ and $g = h^{(p-1)/q} \pmod p > 1$.
   - Traced Signing: Ephemeral $k$, hash truncation $z$, $r = (g^k \pmod p) \pmod q$, $s = k^{-1}(z + x r) \pmod q$.
   - Traced Verification: $w = s^{-1} \pmod q$, $u_1 = z w \pmod q$, $u_2 = r w \pmod q$, $v = (g^{u_1} y^{u_2} \pmod p) \pmod q$, valid iff $v == r$.
   - Interactive Document & Signature Bit-Tampering Simulator.
   - The Sony PlayStation 3 fail0verflow Nonce-Reuse Exploit (2010):
     $$k = (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$$
     $$x = (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$$

### 3.5 Quickstart Guide
* **Mode 1: Unified Orchestration Script (`run.sh`)**
  - Dev: `./run.sh dev`
  - Prod: `./run.sh prod`
  - Test: `./run.sh test`
  - Docker: `./run.sh docker`
* **Mode 2: Docker Compose**
  - `docker compose up --build`
  - Container health checks and port mapping.
* **Mode 3: Manual Local Setup**
  - Backend: `pip install -r backend/requirements.txt && uvicorn backend.main:app --reload`
  - Frontend: `cd frontend && npm install && npm run dev`

### 3.6 API Reference Table
* Complete markdown table documenting all endpoints:
  - `GET /` & `GET /api/v1/health`
  - OTP routes: `/api/v1/otp/generate-key`, `/api/v1/otp/encrypt`, `/api/v1/otp/decrypt`, `/api/v1/otp/two-time-pad-analyze`, `/api/v1/otp/crib-drag`, `/api/v1/otp/crib-drag-auto`, `/api/v1/otp/entropy`
  - LCG routes: `/api/v1/lcg/presets`, `/api/v1/lcg/generate`, `/api/v1/lcg/hull-dobell`, `/api/v1/lcg/cycle`, `/api/v1/lcg/chi-square`, `/api/v1/lcg/marsaglia`, `/api/v1/lcg/crack`
  - ElGamal routes: `/api/v1/elgamal/presets`, `/api/v1/elgamal/generate-domain`, `/api/v1/elgamal/generate-keys`, `/api/v1/elgamal/encrypt`, `/api/v1/elgamal/decrypt`, `/api/v1/elgamal/homomorphic-multiply`, `/api/v1/elgamal/nonce-reuse-exploit`
  - DSA routes: `/api/v1/dsa/presets`, `/api/v1/dsa/generate-domain`, `/api/v1/dsa/generate-keys`, `/api/v1/dsa/sign`, `/api/v1/dsa/verify`, `/api/v1/dsa/tamper-simulate`, `/api/v1/dsa/nonce-reuse-exploit`

### 3.7 Test Suite Execution
* Backend Pytest: `pytest backend/tests -v` (282 tests passing, 100% route and primitive coverage).
* Frontend Verification: `cd frontend && npm run type-check && npm run build`.

### 3.8 Production Hosting & Cloud Deployment
* Cloud Deployment guidelines:
  - Container deployment on AWS ECS / AWS App Runner / Google Cloud Run / DigitalOcean App Platform.
  - Reverse proxy Nginx / Caddy SSL termination example configuration.
  - Security recommendations (HTTPS enforcement, CORS origin lockdown in production, worker sizing).

---

## 4. Verification and Acceptance Criteria
1. **Completeness**: All required sections, mathematical derivations, exploit proofs, API endpoints, and setup instructions are present.
2. **Formatting**: Clean Markdown with GitHub-flavored alerts, KaTeX equations, and Mermaid diagrams.
3. **Accuracy**: Code examples, endpoints, and commands match repository paths and configurations exactly.
