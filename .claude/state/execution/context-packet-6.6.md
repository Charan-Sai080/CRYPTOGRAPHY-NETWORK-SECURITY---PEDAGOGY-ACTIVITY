# Context Packet 6.6: Comprehensive FastAPI End-to-End Test Suite (`backend/tests/test_api.py`)

## 1. Goal
Implement an exhaustive end-to-end integration test suite in `backend/tests/test_api.py` validating all FastAPI endpoints across the platform using `fastapi.testclient.TestClient`.

The test suite must provide:
1. **System & Middleware Testing**:
   - `GET /`: Validates root metadata, OpenAPI/ReDoc documentation links, and version strings.
   - `GET /api/v1/health`: Confirms service health, server timestamp, and active status for all 5 core cryptographic modules.
   - CORS validation: Validates preflight `OPTIONS` and standard response headers for cross-origin access control.
   - Global Error Handling: Validates HTTP 422 Unprocessable Entity formatting on malformed payloads, and HTTP 400 Bad Request on cryptographic constraint violations.
2. **One-Time Pad Endpoints Testing** (`/api/v1/otp/*`):
   - Key generation (valid byte lengths, formatting, entropy bounds).
   - Encrypt/decrypt roundtrips (verifying exact plaintext recovery and truth table traces).
   - Error cases (key length mismatch, malformed hex).
   - Two-Time Pad analysis (verifying XOR difference, entropy calculations, and known-plaintext derivation).
   - Crib-dragging (targeted offset extraction and automated dictionary search).
   - Entropy analysis (standalone information-theoretic randomness evaluation).
3. **Linear Congruential Generator Endpoints Testing** (`/api/v1/lcg/*`):
   - Preset listing (verifying all standard presets).
   - Sequence generation and step trace verification.
   - Hull-Dobell theorem validator (testing full-period vs non-full period parameter sets).
   - Floyd cycle detection (empirical period $\lambda$ and start $\mu$).
   - Chi-Square uniformity test (testing uniform and non-uniform distributions).
   - Marsaglia lattice point generation (2D and 3D coordinate checks and hyperplane upper bound calculation).
   - State reconstruction cracking (recovering $a$ and $c$ from consecutive values).
4. **ElGamal Cryptosystem Endpoints Testing** (`/api/v1/elgamal/*`):
   - Presets listing (educational and standard MODP groups).
   - Dynamic domain parameter generation ($p = 2q + 1$ safe prime search).
   - Key pair generation ($x, y$).
   - Single integer encryption/decryption roundtrip.
   - Multi-block arbitrary text chunking and decryption roundtrip.
   - Multiplicative homomorphism verification ($E(m_1) \cdot E(m_2) = E(m_1 \cdot m_2 \pmod p)$).
   - Ephemeral nonce-reuse known-plaintext exploit ($m_2 = m_1 \cdot c_{2,b} \cdot c_{2,a}^{-1} \pmod p$).
5. **Digital Signature Algorithm Endpoints Testing** (`/api/v1/dsa/*`):
   - Presets listing (FIPS 186-4 and educational groups).
   - Dynamic domain parameter generation ($p, q, g$).
   - Key pair generation ($x, y$).
   - Signing message with SHA-256 truncation and resampling checks.
   - Verification of valid and forged/tampered signatures.
   - Interactive single-bit tampering simulation (message, $r$, and $s$ bit flips).
   - Sony PS3 nonce-reuse exploit (algebraic recovery of private key $x$ from identical nonces).

## 2. Allowed Files
* `backend/tests/test_api.py`
* `backend/tests/__init__.py`

## 3. Test Structure & TestClient Patterns

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestAppArchitectureAndHealth:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "CNS Cryptography Pedagogy API"
        assert "docs_url" in data

    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["modules"]["otp"] == "active"
        assert data["modules"]["dsa"] == "active"

    def test_cors_headers(self):
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_validation_error_handler_422(self):
        response = client.post("/api/v1/otp/generate-key", json={"length": -5})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data or "errors" in data

    def test_domain_error_handler_400(self):
        # Triggering a domain error like key mismatch or out of bounds
        response = client.post(
            "/api/v1/otp/decrypt",
            json={
                "ciphertext": "0011",
                "key": "00",
                "ciphertext_format": "hex",
                "key_format": "hex",
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestOTPEndpoints:
    def test_generate_key(self):
        ...

    def test_encrypt_decrypt_roundtrip(self):
        ...

    def test_two_time_pad_analyze(self):
        ...

    def test_crib_drag_targeted_and_auto(self):
        ...

    def test_entropy_calculation(self):
        ...


class TestLCGEndpoints:
    def test_list_presets(self):
        ...

    def test_generate_sequence(self):
        ...

    def test_hull_dobell_validation(self):
        ...

    def test_cycle_detection_floyd(self):
        ...

    def test_uniformity_test_chi_square(self):
        ...

    def test_marsaglia_lattice_points(self):
        ...

    def test_crack_lcg(self):
        ...


class TestElGamalEndpoints:
    def test_list_presets(self):
        ...

    def test_generate_domain(self):
        ...

    def test_generate_keys(self):
        ...

    def test_encrypt_decrypt_integer(self):
        ...

    def test_encrypt_decrypt_text_blocks(self):
        ...

    def test_homomorphic_multiplication(self):
        ...

    def test_exploit_nonce_reuse(self):
        ...


class TestDSAEndpoints:
    def test_list_presets(self):
        ...

    def test_generate_domain(self):
        ...

    def test_generate_keys(self):
        ...

    def test_sign_and_verify(self):
        ...

    def test_detect_tampering(self):
        ...

    def test_sony_ps3_nonce_reuse_exploit(self):
        ...
```

## 4. Acceptance Criteria
1. Test suite runs smoothly via `pytest backend/tests/test_api.py`.
2. Every endpoint across all routers (`/api/v1/otp/*`, `/api/v1/lcg/*`, `/api/v1/elgamal/*`, `/api/v1/dsa/*`, `/api/v1/health`, `/`) is tested with at least one positive test case and relevant negative/error cases.
3. Every test asserts response status codes (200, 400, 422), response models structure, and mathematical validity of returned outputs.
4. Total test suite passes cleanly with 0 failures, 0 warnings, and 100% endpoint pass rate.
