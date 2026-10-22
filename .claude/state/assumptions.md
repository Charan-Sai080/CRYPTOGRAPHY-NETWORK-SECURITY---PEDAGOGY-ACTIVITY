# Project Assumptions & Clarifications: Cryptography Pedagogy Platform

## Clarified Requirements
1. **Prime Size Strategy**:
   - Hybrid Dual-Range: Educational mode with small primes (8–32 bits) for visual step-by-step arithmetic inspection, plus standard RFC 3526 MODP groups (512-bit / 1024-bit) for real cryptographic simulations.
2. **Pedagogical Step Tracing**:
   - Always trace: Core mathematical primitives and algorithms always construct and return a structured execution trace (equations, step-by-step tabular iterations, bitwise state, and explanations) for pedagogical rendering.
3. **Repository Layout**:
   - Clean Separation:
     - `backend/`: `backend/core/` (pure math primitives), `backend/api/` (FastAPI endpoints & schemas), `backend/tests/` (pytest test suite).
     - `frontend/`: React + TypeScript + Tailwind CSS application with dark/light mode toggle.
4. **Environment**:
   - Miniconda/Miniforge environment `cns-pedagogy` (Python 3.12.15) at `/Users/charancherry/miniforge3/envs/cns-pedagogy`.
   - Node.js v23+ for frontend tooling.
