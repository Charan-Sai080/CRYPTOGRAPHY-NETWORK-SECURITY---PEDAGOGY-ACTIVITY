"""Comprehensive End-to-End Test Suite for FastAPI REST API (Milestone 6).

Covers:
- System & Middleware: Root, Health, CORS, Global Error Handlers (400, 422, 500)
- One-Time Pad (OTP): Keygen, Traced Encrypt/Decrypt, Two-Time Pad, Crib-Dragging, Entropy
- Linear Congruential Generator (LCG): Presets, Traced Generation, Hull-Dobell, Floyd Cycle, Chi-Square, Marsaglia, Cracking
- ElGamal Cryptosystem: Presets, Domain Gen, Key Gen, Traced Integer/Text Encrypt/Decrypt, Homomorphism, Nonce-Reuse Exploit
- Digital Signature Algorithm (DSA): Presets, Domain Gen, Key Gen, Traced Sign/Verify, Bit Tampering, Sony PS3 Nonce Exploit
"""

from __future__ import annotations

import base64
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# =============================================================================
# 1. System, Middleware, Health, & Error Handlers
# =============================================================================


class TestAppArchitectureAndHealth:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "CNS Cryptography Pedagogy API"
        assert data["version"] == "1.0.0"
        assert data["docs_url"] == "/docs"
        assert data["redoc_url"] == "/redoc"
        assert data["endpoints_prefix"] == "/api/v1"

    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert data["modules"]["number_theory"] == "active"
        assert data["modules"]["otp"] == "active"
        assert data["modules"]["lcg"] == "active"
        assert data["modules"]["elgamal"] == "active"
        assert data["modules"]["dsa"] == "active"

    def test_cors_preflight(self):
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

    def test_root_html_content_negotiation(self):
        """Web browsers sending Accept: text/html receive index.html or fallback."""
        response = client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
        assert response.status_code == 200
        from backend.main import FRONTEND_DIST_DIR
        if (FRONTEND_DIST_DIR / "index.html").is_file():
            assert "text/html" in response.headers.get("content-type", "")
        else:
            data = response.json()
            assert data["app"] == "CNS Cryptography Pedagogy API"

    def test_spa_client_side_routing_fallback(self):
        """Non-API routes like /otp or /lcg serve index.html when dist is present."""
        from backend.main import FRONTEND_DIST_DIR
        response = client.get("/otp", headers={"Accept": "text/html"})
        if (FRONTEND_DIST_DIR / "index.html").is_file():
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
        else:
            assert response.status_code == 404

    def test_spa_api_routes_not_intercepted(self):
        """Unmatched /api/* routes must return 404 error rather than index.html."""
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "HTTPException"
        assert data["detail"] == "Endpoint not found"

    def test_static_asset_or_favicon_serving(self):
        """Static files in frontend/dist are served directly."""
        from backend.main import FRONTEND_DIST_DIR
        if (FRONTEND_DIST_DIR / "favicon.svg").is_file():
            response = client.get("/favicon.svg")
            assert response.status_code == 200

    def test_validation_error_handler_422(self):
        # Negative length violates ge=1
        response = client.post("/api/v1/otp/generate-key", json={"length": -5})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "ValidationError"
        assert len(data["errors"]) > 0
        assert any("length" in str(err["loc"]) for err in data["errors"])

    def test_domain_error_handler_400(self):
        # Key shorter than ciphertext triggers ValueError in core OTP
        response = client.post(
            "/api/v1/otp/decrypt",
            json={
                "ciphertext": "00112233",
                "key": "00",
                "ciphertext_format": "hex",
                "key_format": "hex",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"] in ("ValueError", "DomainError")
        assert "Key length" in data["detail"]


# =============================================================================
# 2. One-Time Pad REST Endpoints (/api/v1/otp/*)
# =============================================================================


class TestOTPEndpoints:
    def test_generate_key_success(self):
        response = client.post("/api/v1/otp/generate-key", json={"length": 32, "format": "hex"})
        assert response.status_code == 200
        data = response.json()
        assert data["length"] == 32
        assert len(bytes.fromhex(data["key_hex"])) == 32
        assert len(base64.b64decode(data["key_base64"])) == 32
        assert 0.0 <= data["entropy"] <= 8.0

    def test_generate_key_invalid_length(self):
        # ge=1 violated
        response = client.post("/api/v1/otp/generate-key", json={"length": 0})
        assert response.status_code == 422

    def test_encrypt_auto_key_and_decrypt_roundtrip(self):
        plaintext = "TOP SECRET MESSAGE"
        enc_res = client.post(
            "/api/v1/otp/encrypt",
            json={"plaintext": plaintext, "key": None, "key_format": "hex"},
        )
        assert enc_res.status_code == 200
        enc_data = enc_res.json()
        assert enc_data["plaintext_ascii"] == plaintext
        assert enc_data["length"] == len(plaintext.encode("utf-8"))
        assert len(enc_data["byte_traces"]) == len(plaintext.encode("utf-8"))
        assert "Byte Trace" in enc_data["truth_table"]

        key_hex = enc_data["key_hex"]
        ct_hex = enc_data["ciphertext_hex"]

        # Decrypt with hex key
        dec_res = client.post(
            "/api/v1/otp/decrypt",
            json={
                "ciphertext": ct_hex,
                "key": key_hex,
                "ciphertext_format": "hex",
                "key_format": "hex",
            },
        )
        assert dec_res.status_code == 200
        dec_data = dec_res.json()
        assert dec_data["recovered_ascii"] == plaintext
        assert dec_data["is_valid_ascii"] is True
        assert dec_data["length"] == len(plaintext.encode("utf-8"))

    def test_encrypt_with_custom_ascii_key(self):
        plaintext = "ATTACK AT DAWN"
        key = "MYSECRETKEY123"
        enc_res = client.post(
            "/api/v1/otp/encrypt",
            json={"plaintext": plaintext, "key": key, "key_format": "ascii"},
        )
        assert enc_res.status_code == 200
        enc_data = enc_res.json()

        # Decrypt with ascii key
        dec_res = client.post(
            "/api/v1/otp/decrypt",
            json={
                "ciphertext": enc_data["ciphertext_base64"],
                "key": key,
                "ciphertext_format": "base64",
                "key_format": "ascii",
            },
        )
        assert dec_res.status_code == 200
        assert dec_res.json()["recovered_ascii"] == plaintext

    def test_encrypt_decrypt_malformed_inputs(self):
        # Malformed hex ciphertext
        response = client.post(
            "/api/v1/otp/decrypt",
            json={
                "ciphertext": "NOT_A_HEX_STRING",
                "key": "aabbcc",
                "ciphertext_format": "hex",
                "key_format": "hex",
            },
        )
        assert response.status_code == 400

    def test_two_time_pad_analyze(self):
        key = "SECRETKEY123456"
        p1 = "HELLO ALICE 123"
        p2 = "BYEBYE BOB  456"

        enc1 = client.post("/api/v1/otp/encrypt", json={"plaintext": p1, "key": key, "key_format": "ascii"}).json()
        enc2 = client.post("/api/v1/otp/encrypt", json={"plaintext": p2, "key": key, "key_format": "ascii"}).json()

        c1_hex = enc1["ciphertext_hex"]
        c2_hex = enc2["ciphertext_hex"]

        response = client.post(
            "/api/v1/otp/two-time-pad/analyze",
            json={
                "c1": c1_hex,
                "c2": c2_hex,
                "input_format": "hex",
                "p1_known": p1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["length"] == len(p1)
        assert data["p1_known_ascii"] == p1
        assert data["derived_p2_ascii"] == p2
        assert len(data["proof_steps"]) >= 6

    def test_crib_drag_targeted_and_automated(self):
        key = "A_VERY_SECRET_KEY_123"
        p1 = "the secret meeting is"
        p2 = "attack at dawn today "

        enc1 = client.post("/api/v1/otp/encrypt", json={"plaintext": p1, "key": key, "key_format": "ascii"}).json()
        enc2 = client.post("/api/v1/otp/encrypt", json={"plaintext": p2, "key": key, "key_format": "ascii"}).json()

        # 1. Targeted crib drag at offset 0
        resp_targeted = client.post(
            "/api/v1/otp/two-time-pad/crib-drag",
            json={
                "c1": enc1["ciphertext_hex"],
                "c2": enc2["ciphertext_hex"],
                "input_format": "hex",
                "crib": "the ",
                "position": 0,
            },
        )
        assert resp_targeted.status_code == 200
        target_data = resp_targeted.json()
        assert target_data["single_result"] is not None
        assert target_data["single_result"]["position"] == 0
        assert target_data["single_result"]["revealed_text"].startswith("atta")

        # 2. Automated crib drag
        resp_auto = client.post(
            "/api/v1/otp/two-time-pad/crib-drag",
            json={
                "c1": enc1["ciphertext_hex"],
                "c2": enc2["ciphertext_hex"],
                "input_format": "hex",
                "crib": "attack",
                "position": None,
                "min_readability_score": 0.1,
            },
        )
        assert resp_auto.status_code == 200
        auto_data = resp_auto.json()
        assert len(auto_data["candidates"]) > 0

    def test_shannon_entropy(self):
        # Constant data -> entropy 0.0
        resp_const = client.post("/api/v1/otp/entropy", json={"data": "AAAAAAA", "input_format": "text"})
        assert resp_const.status_code == 200
        assert resp_const.json()["entropy"] == 0.0
        assert resp_const.json()["unique_symbols"] == 1

        # High entropy hex bytes
        resp_rand = client.post(
            "/api/v1/otp/entropy",
            json={"data": "0123456789abcdef", "input_format": "hex"},
        )
        assert resp_rand.status_code == 200
        data = resp_rand.json()
        assert data["entropy"] > 2.0
        assert len(data["frequency_table"]) > 0
        assert len(data["probability_table"]) > 0


# =============================================================================
# 3. Linear Congruential Generator REST Endpoints (/api/v1/lcg/*)
# =============================================================================


class TestLCGEndpoints:
    def test_list_presets(self):
        response = client.get("/api/v1/lcg/presets")
        assert response.status_code == 200
        presets = response.json()
        assert len(presets) >= 7
        preset_names = {p["name"] for p in presets}
        assert "ansi_c" in preset_names
        assert "posix_rand48" in preset_names
        assert "minstd" in preset_names
        assert "small_educational" in preset_names

    def test_generate_sequence_with_preset(self):
        response = client.post(
            "/api/v1/lcg/generate",
            json={"preset_name": "ansi_c", "count": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["values"]) == 10
        assert len(data["normalized"]) == 10
        assert len(data["traces"]) == 10
        assert all(0.0 <= u < 1.0 for u in data["normalized"])
        assert data["traces"][0]["step"] == 1
        assert "mod" in data["traces"][0]["formula"]

    def test_generate_sequence_with_custom_parameters(self):
        response = client.post(
            "/api/v1/lcg/generate",
            json={"m": 16, "a": 5, "c": 1, "seed": 1, "count": 5},
        )
        assert response.status_code == 200
        data = response.json()
        # X1 = (5*1 + 1) % 16 = 6
        assert data["values"][0] == 6

    def test_hull_dobell_validation(self):
        # ANSI C satisfies Hull-Dobell
        resp_full = client.post("/api/v1/lcg/hull-dobell", json={"preset_name": "ansi_c"})
        assert resp_full.status_code == 200
        assert resp_full.json()["is_full_period"] is True
        assert resp_full.json()["condition_1"]["satisfied"] is True
        assert resp_full.json()["condition_2"]["satisfied"] is True
        assert resp_full.json()["condition_3"]["satisfied"] is True

        # small_broken violates Hull-Dobell
        resp_broken = client.post("/api/v1/lcg/hull-dobell", json={"preset_name": "small_broken"})
        assert resp_broken.status_code == 200
        assert resp_broken.json()["is_full_period"] is False

    def test_cycle_detection_floyd(self):
        response = client.post(
            "/api/v1/lcg/cycle-detect",
            json={"preset_name": "small_educational", "max_steps": 100},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == 16
        assert data["cycle_start"] == 0
        assert data["is_full_period"] is True
        assert len(data["sample_cycle"]) == 16

    def test_uniformity_test_chi_square(self):
        response = client.post(
            "/api/v1/lcg/uniformity-test",
            json={"preset_name": "ansi_c", "count": 1000, "num_bins": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["degrees_of_freedom"] == 9
        assert len(data["bins"]) == 10
        assert "p_value_approx" in data

    def test_marsaglia_lattice(self):
        # 2D points
        resp_2d = client.post(
            "/api/v1/lcg/marsaglia-lattice",
            json={"preset_name": "small_educational", "count": 50, "dimension": 2},
        )
        assert resp_2d.status_code == 200
        data_2d = resp_2d.json()
        assert data_2d["dimension"] == 2
        assert len(data_2d["points_2d"]) > 0
        assert len(data_2d["points_3d"]) == 0
        assert data_2d["theoretical_max_hyperplanes"] > 0

        # 3D points
        resp_3d = client.post(
            "/api/v1/lcg/marsaglia-lattice",
            json={"preset_name": "small_educational", "count": 50, "dimension": 3},
        )
        assert resp_3d.status_code == 200
        data_3d = resp_3d.json()
        assert data_3d["dimension"] == 3
        assert len(data_3d["points_3d"]) > 0
        assert len(data_3d["points_2d"]) == 0

    def test_crack_lcg(self):
        # Outputs from m=16, a=5, c=1, seed=1: [1, 6, 15, 12, 13]
        response = client.post(
            "/api/v1/lcg/crack",
            json={"outputs": [1, 6, 15, 12], "m": 16},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_successful"] is True
        assert data["recovered_a"] == 5
        assert data["recovered_c"] == 1
        assert data["predicted_next"] == 13


# =============================================================================
# 4. ElGamal Cryptosystem REST Endpoints (/api/v1/elgamal/*)
# =============================================================================


class TestElGamalEndpoints:
    def test_list_presets(self):
        response = client.get("/api/v1/elgamal/presets")
        assert response.status_code == 200
        presets = response.json()
        assert len(presets) >= 4
        names = [p["name"] for p in presets]
        assert any("16-bit" in n for n in names)

    def test_generate_domain(self):
        response = client.post("/api/v1/elgamal/generate-domain", json={"bits": 16})
        assert response.status_code == 200
        data = response.json()
        assert data["p"] > 2
        assert data["g"] >= 2
        assert data["p_bits"] >= 15
        assert len(data["steps"]) >= 2

    def test_generate_keys(self):
        response = client.post(
            "/api/v1/elgamal/generate-keys",
            json={"preset_name": "educational_16", "seed_x": 12345},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["public_key"]["p"] == 65537
        assert data["public_key"]["g"] == 3
        assert data["private_key"]["x"] == 12345
        assert int(data["public_key"]["y"]) == pow(3, 12345, 65537)

    def test_encrypt_decrypt_single_integer(self):
        # Generate keys
        keys = client.post(
            "/api/v1/elgamal/generate-keys",
            json={"preset_name": "educational_16", "seed_x": 12345},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        # Encrypt integer
        enc_res = client.post(
            "/api/v1/elgamal/encrypt",
            json={"p": pub["p"], "g": pub["g"], "y": pub["y"], "message_int": 42, "seed_k": 7},
        )
        assert enc_res.status_code == 200
        enc_data = enc_res.json()
        assert enc_data["is_multi_block"] is False
        assert enc_data["c1"] is not None
        assert enc_data["c2"] is not None
        assert enc_data["single_trace"] is not None

        # Decrypt integer
        dec_res = client.post(
            "/api/v1/elgamal/decrypt",
            json={"p": priv["p"], "x": priv["x"], "c1": enc_data["c1"], "c2": enc_data["c2"]},
        )
        assert dec_res.status_code == 200
        dec_data = dec_res.json()
        assert dec_data["is_multi_block"] is False
        assert dec_data["recovered_int"] == 42
        assert dec_data["single_trace"] is not None

    def test_encrypt_decrypt_chunked_text(self):
        keys = client.post(
            "/api/v1/elgamal/generate-keys",
            json={"preset_name": "educational_16", "seed_x": 12345},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        msg = "HELLO ELGAMAL CRYPTOSYSTEM"
        enc_res = client.post(
            "/api/v1/elgamal/encrypt",
            json={"p": pub["p"], "g": pub["g"], "y": pub["y"], "message_text": msg},
        )
        assert enc_res.status_code == 200
        enc_data = enc_res.json()
        assert enc_data["is_multi_block"] is True
        assert len(enc_data["blocks"]) > 1

        # Decrypt text blocks
        dec_res = client.post(
            "/api/v1/elgamal/decrypt",
            json={"p": priv["p"], "x": priv["x"], "blocks": enc_data["blocks"]},
        )
        assert dec_res.status_code == 200
        dec_data = dec_res.json()
        assert dec_data["is_multi_block"] is True
        assert dec_data["recovered_text"] == msg

    def test_homomorphic_multiplication(self):
        keys = client.post(
            "/api/v1/elgamal/generate-keys",
            json={"preset_name": "educational_16", "seed_x": 12345},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        m1 = 15
        m2 = 25
        response = client.post(
            "/api/v1/elgamal/homomorphic-multiply",
            json={
                "p": pub["p"],
                "g": pub["g"],
                "y": pub["y"],
                "x": priv["x"],
                "m1": m1,
                "m2": m2,
                "seed_k1": 11,
                "seed_k2": 13,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_verified"] is True
        assert data["expected_product"] == (m1 * m2) % pub["p"]
        assert data["decrypted_product"] == data["expected_product"]

    def test_exploit_nonce_reuse(self):
        keys = client.post(
            "/api/v1/elgamal/generate-keys",
            json={"preset_name": "educational_16", "seed_x": 12345},
        ).json()
        pub = keys["public_key"]

        # Encrypt two distinct messages with identical ephemeral nonce k=17
        m1 = 100
        m2 = 200
        k = 17
        enc1 = client.post(
            "/api/v1/elgamal/encrypt",
            json={"p": pub["p"], "g": pub["g"], "y": pub["y"], "message_int": m1, "seed_k": k},
        ).json()
        enc2 = client.post(
            "/api/v1/elgamal/encrypt",
            json={"p": pub["p"], "g": pub["g"], "y": pub["y"], "message_int": m2, "seed_k": k},
        ).json()

        assert enc1["c1"] == enc2["c1"]

        # Run exploit
        response = client.post(
            "/api/v1/elgamal/exploit-nonce-reuse",
            json={
                "p": pub["p"],
                "c1_a": enc1["c1"],
                "c2_a": enc1["c2"],
                "c1_b": enc2["c1"],
                "c2_b": enc2["c2"],
                "m1_known": m1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_attack_applicable"] is True
        assert data["recovered_m2"] == m2

    def test_exploit_nonce_reuse_mismatched_c1(self):
        response = client.post(
            "/api/v1/elgamal/exploit-nonce-reuse",
            json={
                "p": 65537,
                "c1_a": 10,
                "c2_a": 20,
                "c1_b": 30,  # Different c1
                "c2_b": 40,
                "m1_known": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_attack_applicable"] is False
        assert data["c1_identical"] is False


# =============================================================================
# 5. Digital Signature Algorithm REST Endpoints (/api/v1/dsa/*)
# =============================================================================


class TestDSAEndpoints:
    def test_list_presets(self):
        response = client.get("/api/v1/dsa/presets")
        assert response.status_code == 200
        presets = response.json()
        assert len(presets) >= 4
        names = [p["name"] for p in presets]
        assert any("FIPS 186-4" in n for n in names)
        assert any("Educational 10-bit" in n for n in names)

    def test_generate_domain(self):
        response = client.post("/api/v1/dsa/generate-domain", json={"p_bits": 16, "q_bits": 8})
        assert response.status_code == 200
        data = response.json()
        assert data["p"] > 2
        assert data["q"] > 1
        assert (data["p"] - 1) % data["q"] == 0
        assert pow(data["g"], data["q"], data["p"]) == 1
        assert len(data["logs"]) > 0

    def test_generate_keys(self):
        response = client.post(
            "/api/v1/dsa/generate-keys",
            json={"preset_name": "educational_10", "seed_x": 42},
        )
        assert response.status_code == 200
        data = response.json()
        pub = data["public_key"]
        priv = data["private_key"]
        assert pub["p"] == 607
        assert pub["q"] == 101
        assert priv["x"] == 42
        assert pub["y"] == pow(pub["g"], 42, pub["p"])

    def test_sign_and_verify(self):
        keys = client.post(
            "/api/v1/dsa/generate-keys",
            json={"preset_name": "educational_10", "seed_x": 42},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        msg = "CNS Cryptography Pedagogy"
        sign_res = client.post(
            "/api/v1/dsa/sign",
            json={
                "message": msg,
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "x": priv["x"],
                "seed_k": 13,
            },
        )
        assert sign_res.status_code == 200
        sig_data = sign_res.json()
        assert sig_data["r"] > 0
        assert sig_data["s"] > 0
        assert "r_str" in sig_data
        assert sig_data["trace"]["formula_r"].startswith("r =")

        # Verify signature
        ver_res = client.post(
            "/api/v1/dsa/verify",
            json={
                "message": msg,
                "r": sig_data["r"],
                "s": sig_data["s"],
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "y": pub["y"],
            },
        )
        assert ver_res.status_code == 200
        ver_data = ver_res.json()
        assert ver_data["is_valid"] is True
        assert ver_data["v"] == sig_data["r"]
        assert ver_data["trace"] is not None
        assert ver_data["trace"]["is_valid"] is True

    def test_verify_tampered_signature(self):
        keys = client.post(
            "/api/v1/dsa/generate-keys",
            json={"preset_name": "educational_10", "seed_x": 42},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        msg = "Original Message"
        sig_data = client.post(
            "/api/v1/dsa/sign",
            json={
                "message": msg,
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "x": priv["x"],
                "seed_k": 13,
            },
        ).json()

        # Tampered message
        ver_res = client.post(
            "/api/v1/dsa/verify",
            json={
                "message": "Forged Message",
                "r": sig_data["r"],
                "s": sig_data["s"],
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "y": pub["y"],
            },
        )
        assert ver_res.status_code == 200
        assert ver_res.json()["is_valid"] is False

    def test_detect_tampering_endpoint(self):
        keys = client.post(
            "/api/v1/dsa/generate-keys",
            json={"preset_name": "educational_10", "seed_x": 42},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        # Tamper message bit
        tamp_msg = client.post(
            "/api/v1/dsa/detect-tampering",
            json={
                "message": "Authentic Message",
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "x": priv["x"],
                "y": pub["y"],
                "tamper_target": "message",
                "bit_index": 0,
                "seed_k": 17,
            },
        )
        assert tamp_msg.status_code == 200
        data_msg = tamp_msg.json()
        assert data_msg["tamper_detected"] is True
        assert data_msg["original_verification"] is True
        assert data_msg["tampered_verification"] is False

        # Tamper signature component r
        tamp_r = client.post(
            "/api/v1/dsa/detect-tampering",
            json={
                "message": "Authentic Message",
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "x": priv["x"],
                "y": pub["y"],
                "tamper_target": "r",
            },
        )
        assert tamp_r.status_code == 200
        assert tamp_r.json()["tamper_detected"] is True

        # Tamper signature component s
        tamp_s = client.post(
            "/api/v1/dsa/detect-tampering",
            json={
                "message": "Authentic Message",
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "x": priv["x"],
                "y": pub["y"],
                "tamper_target": "s",
            },
        )
        assert tamp_s.status_code == 200
        assert tamp_s.json()["tamper_detected"] is True

    def test_sony_ps3_nonce_reuse_exploit(self):
        keys = client.post(
            "/api/v1/dsa/generate-keys",
            json={"preset_name": "educational_10", "seed_x": 42},
        ).json()
        pub = keys["public_key"]
        priv = keys["private_key"]

        m1 = "Firmware Package 3.55"
        m2 = "Homebrew Payload Custom"
        reused_k = 29

        sig1 = client.post(
            "/api/v1/dsa/sign",
            json={"message": m1, "p": pub["p"], "q": pub["q"], "g": pub["g"], "x": priv["x"], "seed_k": reused_k},
        ).json()
        sig2 = client.post(
            "/api/v1/dsa/sign",
            json={"message": m2, "p": pub["p"], "q": pub["q"], "g": pub["g"], "x": priv["x"], "seed_k": reused_k},
        ).json()

        assert sig1["r"] == sig2["r"]

        exploit_res = client.post(
            "/api/v1/dsa/exploit-nonce-reuse",
            json={
                "m1": m1,
                "r1": sig1["r"],
                "s1": sig1["s"],
                "m2": m2,
                "r2": sig2["r"],
                "s2": sig2["s"],
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "y": pub["y"],
            },
        )
        assert exploit_res.status_code == 200
        data = exploit_res.json()
        assert data["is_exploit_applicable"] is True
        assert data["recovered_k"] == reused_k
        assert data["recovered_x"] == 42
        assert data["public_key_matched"] is True
        assert len(data["steps"]) > 0
        assert "Sony PlayStation 3" in data["historical_context"]

    def test_sony_ps3_nonce_reuse_mismatched_r_error(self):
        keys = client.post(
            "/api/v1/dsa/generate-keys",
            json={"preset_name": "educational_10", "seed_x": 42},
        ).json()
        pub = keys["public_key"]

        # Different r values -> domain error 400
        response = client.post(
            "/api/v1/dsa/exploit-nonce-reuse",
            json={
                "m1": "Msg 1",
                "r1": 10,
                "s1": 20,
                "m2": "Msg 2",
                "r2": 15,
                "s2": 25,
                "p": pub["p"],
                "q": pub["q"],
                "g": pub["g"],
                "y": pub["y"],
            },
        )
        assert response.status_code == 400
        assert "DSACryptanalysisError" in response.json()["error"]
