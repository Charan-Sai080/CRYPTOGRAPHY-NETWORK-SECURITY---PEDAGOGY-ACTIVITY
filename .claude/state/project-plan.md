# Project Plan: Pedagogy Activity - Cryptography & Network Security

## 1. Project Goal
Develop a production-grade, interactive web platform demonstrating 4 core cryptographic concepts for an educational pedagogy activity:
1. **One-Time Pad (OTP)**: Symmetric encryption/decryption, bitwise XOR, Shannon perfect secrecy, and Two-Time Pad key-reuse attack.
2. **Linear Congruential Generator (LCG)**: Pseudorandom sequence generation, Hull-Dobell full-period verification, Floyd cycle detection, Chi-square statistical test, and 2D/3D lattice hyperplane visualization.
3. **ElGamal Public-Key Cryptosystem**: Key generation, encryption/decryption, step-by-step modular arithmetic walkthrough, multiplicative homomorphism, and ephemeral nonce-reuse attack.
4. **Digital Signature Algorithm (DSA)**: FIPS 186-4 parameter setup, signing, verification, interactive document tampering test, and Sony PS3 style nonce-reuse private key recovery.

## 2. Architecture & Methodology
* **Backend Environment**: Conda environment `cns-pedagogy` (Python 3.12.15) at `/Users/charancherry/miniforge3/envs/cns-pedagogy`.
* **Backend Architecture**: Python 3.12 / FastAPI / Pydantic with pure Python number theory primitives for full step-by-step pedagogical transparency.
* **Frontend Architecture & Visual Assets**:
  * React + TypeScript + Tailwind CSS with dark/light mode toggle.
  * Component primitives & blocks: shadcn/ui and Aceternity UI for cyber/pedagogy aesthetic.
  * Visualizations & Charts: Recharts and Plotly.js for 2D/3D LCG hyperplane lattice plots.
  * Icons: Lucide React (locks, keys, shields, binary nodes).
* **Testing**: Pytest with 100% edge-case coverage and known cryptographic test vectors.

## 3. Milestones
* **M1**: Number Theory & Mathematical Core Engine
* **M2**: One-Time Pad (OTP) Engine & Two-Time Pad Analysis
* **M3**: Linear Congruential Generator (LCG) & Statistical/Lattice Analysis
* **M4**: ElGamal Cryptosystem Engine & Homomorphic Demonstration
* **M5**: Digital Signature Algorithm (DSA) & Nonce-Reuse Exploit
* **M6**: FastAPI Backend REST API & Test Suite
* **M7**: Interactive Frontend Web Application & Educational Labs
* **M8**: Packaging, Containerization (Docker), & Deployment
