# Context Packet 6: Milestone 6 FastAPI Backend REST API & Test Suite

## 1. Task Goal
Build a production-grade, fully typed, asynchronous REST API layer using FastAPI 0.115+ and Pydantic v2 for the Cryptography Pedagogy Platform. The backend exposes all underlying number theory and cryptographic engines developed in Milestones 1–5 (One-Time Pad, Linear Congruential Generator, ElGamal Cryptosystem, and Digital Signature Algorithm) through clean, educational, well-documented REST endpoints under `/api/v1/*`, complemented by an exhaustive end-to-end integration test suite (`backend/tests/test_api.py`).

## 2. Granular Sub-Milestones
* **M6.1: FastAPI App Architecture, CORS Middleware, Global Error Handlers, and Base Schemas**:
  - FastAPI application entry point (`backend/main.py`) with title `"CNS Cryptography Pedagogy API"`, version `"1.0.0"`, and custom Swagger (`/docs`) / ReDoc (`/redoc`) metadata.
  - Permissive Cross-Origin Resource Sharing (CORS) middleware enabling seamless frontend development (`http://localhost:5173`, `http://localhost:3000`, `*`).
  - Global exception handlers translating domain exceptions (`DSAError`, `ElGamalError`, `ValueError`, `KeyError`) and FastAPI `RequestValidationError` into structured, consistent HTTP error responses (`ErrorResponse`).
  - System health check (`GET /api/v1/health`) and root status (`GET /`).
  - Base Pydantic models and common schemas in `backend/api/schemas/common.py`.
  - Master v1 API Router in `backend/api/v1/router.py`.
  - Detailed Context: [context-packet-6.1.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-6.1.md)

* **M6.2: One-Time Pad REST Router (`/api/v1/otp/*`) with Typed Pydantic Models**:
  - Key generation endpoint: CSPRNG key generation with format selection (hex, base64, ascii).
  - Traced encryption & decryption endpoints: bit-by-bit and byte-by-byte inspection traces, Shannon entropy analysis.
  - Two-Time Pad vulnerability analysis endpoint: identical key reuse detection and XOR cancel-out proof ($C_1 \oplus C_2 = P_1 \oplus P_2$).
  - Crib-dragging cryptanalysis endpoints: targeted position dragging and automated dictionary-based crib-dragging with English readability scoring.
  - Shannon entropy calculator endpoint for arbitrary text/byte inputs.
  - Router: `backend/api/v1/otp.py`, Schemas: `backend/api/schemas/otp.py`.
  - Detailed Context: [context-packet-6.2.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-6.2.md)

* **M6.3: Linear Congruential Generator REST Router (`/api/v1/lcg/*`) with Typed Pydantic Models**:
  - Catalog endpoint for pre-configured historical and standard presets (ANSI C, POSIX, MINSTD, Borland, Numerical Recipes, etc.).
  - Sequence generation endpoint with step-by-step arithmetic traces ($X_{n+1} = (a \cdot X_n + c) \pmod m$) and normalized floats $U_n \in [0, 1)$.
  - Hull-Dobell theorem validator endpoint with detailed breakdown of all 3 conditions and prime factor trees.
  - Floyd's cycle-finding (tortoise-and-hare) endpoint detecting empirical period $\lambda$ and start $\mu$.
  - Chi-square ($\chi^2$) uniformity goodness-of-fit test endpoint with observed/expected bins and p-value verdict.
  - Marsaglia lattice endpoint generating 2D/3D hyperplane coordinates and theoretical bound $\lfloor(d! \cdot m)^{1/d}\rfloor$.
  - Algebraic state reconstruction endpoint cracking LCG internal states from consecutive outputs.
  - Router: `backend/api/v1/lcg.py`, Schemas: `backend/api/schemas/lcg.py`.
  - Detailed Context: [context-packet-6.3.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-6.3.md)

* **M6.4: ElGamal Cryptosystem REST Router (`/api/v1/elgamal/*`) with Typed Pydantic Models**:
  - Domain presets catalog endpoint (educational small primes and RFC 2409 1024-bit MODP group).
  - Dynamic educational safe prime domain generator endpoint ($(p, g)$ with step logs).
  - Key pair generator endpoint ($x \in [2, p - 2]$, $y = g^x \pmod p$) with optional deterministic seeding.
  - Traced encryption endpoint for integers and arbitrary UTF-8 text strings with chunking, emitting detailed block traces ($s = y^k \pmod p, c_1 = g^k \pmod p, c_2 = m \cdot s \pmod p$).
  - Traced decryption endpoint with modular inversion steps ($s = c_1^x \pmod p, s^{-1} \pmod p, m = c_2 \cdot s^{-1} \pmod p$).
  - Multiplicative homomorphism demonstration endpoint proving $E(m_1) \cdot E(m_2) = E(m_1 \cdot m_2 \pmod p)$.
  - Known-plaintext ephemeral nonce-reuse exploit endpoint recovering $m_2$ when $c_{1,a} = c_{1,b}$.
  - Router: `backend/api/v1/elgamal.py`, Schemas: `backend/api/schemas/elgamal.py`.
  - Detailed Context: [context-packet-6.4.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-6.4.md)

* **M6.5: Digital Signature Algorithm REST Router (`/api/v1/dsa/*`) with Typed Pydantic Models**:
  - Domain presets catalog endpoint (FIPS 186-4 1024/160-bit group, educational 10, 16, 24-bit groups).
  - Dynamic educational DSA domain parameter generator endpoint ($(p, q, g)$ with Miller-Rabin search logs).
  - Key pair generator endpoint ($x \in [1, q - 1], y = g^x \pmod p$).
  - Traced signature generation endpoint with SHA-256 digest truncation and FIPS 186-4 $r=0, s=0$ resampling.
  - Traced signature verification endpoint computing $w, u_1, u_2, v$ and checking $v == r$.
  - Interactive single-bit tampering detection endpoint simulating message and signature component alterations.
  - Sony PS3 ephemeral nonce-reuse private key recovery exploit endpoint.
  - Router: `backend/api/v1/dsa.py`, Schemas: `backend/api/schemas/dsa.py`.
  - Detailed Context: [context-packet-6.5.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-6.5.md)

* **M6.6: Comprehensive FastAPI End-to-End Test Suite (`backend/tests/test_api.py`)**:
  - Full suite of automated pytest integration tests using `fastapi.testclient.TestClient` / `httpx`.
  - 100% route coverage testing all endpoints across OTP, LCG, ElGamal, and DSA routers.
  - Comprehensive negative test cases: invalid schemas (422), domain constraint violations (400), malformed parameters, and boundary conditions.
  - Zero regressions across existing core unit test suites (245/245 existing tests passing).
  - Detailed Context: [context-packet-6.6.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-6.6.md)

## 3. Directory Layout
```
backend/
├── main.py                     # App instance, CORS, exception handlers, router registration
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py          # Master v1 router aggregating all sub-routers
│   │   ├── otp.py             # One-Time Pad REST router (/api/v1/otp/*)
│   │   ├── lcg.py             # LCG REST router (/api/v1/lcg/*)
│   │   ├── elgamal.py         # ElGamal REST router (/api/v1/elgamal/*)
│   │   └── dsa.py             # DSA REST router (/api/v1/dsa/*)
│   └── schemas/
│       ├── __init__.py
│       ├── common.py          # Generic error models, health status, base schemas
│       ├── otp.py             # OTP request & response Pydantic models
│       ├── lcg.py             # LCG request & response Pydantic models
│       ├── elgamal.py         # ElGamal request & response Pydantic models
│       └── dsa.py             # DSA request & response Pydantic models
├── core/                       # Core mathematical & cryptographic engines (M1-M5)
└── tests/
    ├── test_number_theory.py
    ├── test_otp.py
    ├── test_lcg.py
    ├── test_elgamal.py
    ├── test_dsa.py
    └── test_api.py            # Comprehensive FastAPI API integration test suite
```

## 4. Architectural Rules & Implementation Standards
1. **Pydantic v2 Adherence**: Use `model_config = ConfigDict(populate_by_name=True)` or `Field(...)` with descriptive titles, descriptions, and examples.
2. **Deterministic Large Integer Serialization**: When numbers exceed JavaScript's `Number.MAX_SAFE_INTEGER` ($2^{53} - 1$), schemas must provide string representations (e.g. `p_str`, `y_str` or `int` serializable to JSON) to prevent frontend precision loss.
3. **Trace Preservation**: All response schemas must preserve the rich pedagogical trace models produced by `backend.core` (`EEAStep`, `BitXORTrace`, `LCGStepTrace`, `ElGamalEncryptTrace`, `DSASignTrace`, etc.).
4. **Clean Error Mapping**: Any domain exception (such as `DSAError`, `ElGamalError`, `ValueError`) thrown during parameter validation or execution must be intercepted by FastAPI exception handlers and translated to an HTTP 400 Bad Request with a structured `ErrorResponse`.
5. **No Production Logic Duplication**: Router functions must act solely as request/response adapters over `backend.core` functions and classes.
