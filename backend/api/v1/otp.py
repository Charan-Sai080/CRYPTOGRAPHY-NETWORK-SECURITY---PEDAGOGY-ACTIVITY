from __future__ import annotations

import base64
from fastapi import APIRouter

from backend.api.schemas.otp import (
    BitXORTraceSchema,
    ByteOTPTraceSchema,
    CribDragCandidateSchema,
    CribDragRequest,
    CribDragResponse,
    EntropyRequest,
    EntropyResponse,
    OTPDecryptRequest,
    OTPDecryptResponse,
    OTPEncryptRequest,
    OTPEncryptResponse,
    OTPKeyGenerateRequest,
    OTPKeyGenerateResponse,
    TwoTimePadAnalyzeRequest,
    TwoTimePadAnalyzeResponse,
)
from backend.core.otp import (
    analyze_two_time_pad,
    calculate_shannon_entropy,
    decrypt_otp,
    drag_crib,
    encrypt_otp,
    format_byte_truth_table,
    generate_otp_key,
    xor_bytes,
)

router = APIRouter(prefix="/otp", tags=["One-Time Pad"])


def _decode_bytes(value: str, fmt: str) -> bytes:
    """Decodes input string according to the specified encoding format."""
    if fmt == "hex":
        try:
            return bytes.fromhex(value)
        except (ValueError, TypeError) as err:
            raise ValueError(f"Invalid hexadecimal string: {value}") from err
    elif fmt == "base64":
        try:
            return base64.b64decode(value)
        except Exception as err:
            raise ValueError(f"Invalid base64 string: {value}") from err
    elif fmt in ("ascii", "text", "raw"):
        return value.encode("utf-8")
    raise ValueError(f"Unsupported encoding format: {fmt}")


@router.post("/generate-key", response_model=OTPKeyGenerateResponse)
async def generate_key(req: OTPKeyGenerateRequest) -> OTPKeyGenerateResponse:
    """Generates a CSPRNG cryptographically secure key of requested length."""
    key_bytes = generate_otp_key(req.length)
    entropy_res = calculate_shannon_entropy(key_bytes)
    return OTPKeyGenerateResponse(
        key_hex=key_bytes.hex(),
        key_base64=base64.b64encode(key_bytes).decode("ascii"),
        length=len(key_bytes),
        entropy=entropy_res.entropy,
    )


@router.post("/encrypt", response_model=OTPEncryptResponse)
async def encrypt(req: OTPEncryptRequest) -> OTPEncryptResponse:
    """Encrypts plaintext with an optional custom or auto-generated CSPRNG key."""
    key_bytes: bytes | None = None
    if req.key is not None:
        key_bytes = _decode_bytes(req.key, req.key_format)

    res = encrypt_otp(req.plaintext, key=key_bytes)

    byte_traces = [
        ByteOTPTraceSchema(
            byte_index=t.byte_index,
            char_m=t.p_char,
            byte_m_val=t.p_val,
            byte_m_bin=t.p_bin,
            byte_k_val=t.k_val,
            byte_k_bin=t.k_bin,
            byte_c_val=t.c_val,
            byte_c_bin=t.c_bin,
            byte_c_hex=t.c_hex,
            bit_traces=[
                BitXORTraceSchema(
                    bit_index=bt.bit_index,
                    bit_m=bt.bit_p,
                    bit_k=bt.bit_k,
                    bit_c=bt.bit_c,
                    equation=bt.formula,
                )
                for bt in t.bit_traces
            ],
        )
        for t in res.traces
    ]

    truth_table = format_byte_truth_table(res.traces[0]) if res.traces else ""

    return OTPEncryptResponse(
        plaintext_ascii=req.plaintext,
        key_hex=res.key_hex,
        key_base64=base64.b64encode(res.key_bytes).decode("ascii"),
        ciphertext_hex=res.ciphertext_hex,
        ciphertext_base64=res.ciphertext_base64,
        length=len(res.ciphertext_bytes),
        entropy_plaintext=res.plaintext_entropy.entropy,
        entropy_key=res.key_entropy.entropy,
        entropy_ciphertext=res.ciphertext_entropy.entropy,
        byte_traces=byte_traces,
        truth_table=truth_table,
    )


@router.post("/decrypt", response_model=OTPDecryptResponse)
async def decrypt(req: OTPDecryptRequest) -> OTPDecryptResponse:
    """Decrypts ciphertext using the supplied OTP key and emits bitwise traces."""
    c_bytes = _decode_bytes(req.ciphertext, req.ciphertext_format)
    k_bytes = _decode_bytes(req.key, req.key_format)

    res = decrypt_otp(c_bytes, k_bytes)

    byte_traces = [
        ByteOTPTraceSchema(
            byte_index=t.byte_index,
            char_m=t.p_char,
            byte_m_val=t.p_val,
            byte_m_bin=t.p_bin,
            byte_k_val=t.k_val,
            byte_k_bin=t.k_bin,
            byte_c_val=t.c_val,
            byte_c_bin=t.c_bin,
            byte_c_hex=t.c_hex,
            bit_traces=[
                BitXORTraceSchema(
                    bit_index=bt.bit_index,
                    bit_m=bt.bit_p,
                    bit_k=bt.bit_k,
                    bit_c=bt.bit_c,
                    equation=bt.formula,
                )
                for bt in t.bit_traces
            ],
        )
        for t in res.traces
    ]

    recovered_str = res.decrypted_text if res.decrypted_text is not None else res.decrypted_bytes.decode("latin1", errors="replace")
    is_ascii = all(b < 128 for b in res.decrypted_bytes)

    return OTPDecryptResponse(
        recovered_ascii=recovered_str,
        recovered_hex=res.decrypted_hex,
        ciphertext_hex=res.ciphertext_hex,
        key_hex=res.key_hex,
        length=len(res.decrypted_bytes),
        is_valid_ascii=is_ascii,
        byte_traces=byte_traces,
    )


@router.post("/two-time-pad/analyze", response_model=TwoTimePadAnalyzeResponse)
async def analyze_two_time_pad_endpoint(req: TwoTimePadAnalyzeRequest) -> TwoTimePadAnalyzeResponse:
    """Analyzes two ciphertexts encrypted under the same key proving C1 ^ C2 = P1 ^ P2."""
    c1_bytes = _decode_bytes(req.c1, req.input_format)
    c2_bytes = _decode_bytes(req.c2, req.input_format)

    analysis = analyze_two_time_pad(c1_bytes, c2_bytes)

    derived_p2_ascii: str | None = None
    if req.p1_known is not None:
        p1_bytes = req.p1_known.encode("utf-8")
        derived_p2_bytes = xor_bytes(analysis.xor_stream, p1_bytes)
        derived_p2_ascii = derived_p2_bytes.decode("utf-8", errors="replace")

    proof_steps = [
        "1. Intercept ciphertexts: C1 = P1 ⊕ K, C2 = P2 ⊕ K",
        "2. Compute bitwise XOR difference: C1 ⊕ C2 = (P1 ⊕ K) ⊕ (P2 ⊕ K)",
        "3. Apply XOR commutativity and associativity: C1 ⊕ C2 = P1 ⊕ P2 ⊕ (K ⊕ K)",
        "4. Apply XOR self-inverse property (K ⊕ K = 0): C1 ⊕ C2 = P1 ⊕ P2 ⊕ 0",
        "5. Apply XOR identity property (X ⊕ 0 = X): C1 ⊕ C2 = P1 ⊕ P2",
        "6. Algebraic key cancellation confirmed: Secret key K is eliminated from the XOR stream.",
    ]
    if req.p1_known is not None:
        proof_steps.append(
            f"7. Known-plaintext recovery: P2 = (C1 ⊕ C2) ⊕ P1 = '{derived_p2_ascii}'"
        )

    ent_c1 = calculate_shannon_entropy(c1_bytes).entropy
    ent_c2 = calculate_shannon_entropy(c2_bytes).entropy
    ent_diff = calculate_shannon_entropy(analysis.xor_stream).entropy

    return TwoTimePadAnalyzeResponse(
        c1_hex=analysis.c1_hex,
        c2_hex=analysis.c2_hex,
        xor_diff_hex=analysis.xor_hex,
        length=analysis.overlap_length,
        proof_steps=proof_steps,
        p1_known_ascii=req.p1_known,
        derived_p2_ascii=derived_p2_ascii,
        shannon_entropy_c1=ent_c1,
        shannon_entropy_c2=ent_c2,
        shannon_entropy_diff=ent_diff,
    )


@router.post("/two-time-pad/crib-drag", response_model=CribDragResponse)
async def crib_drag_endpoint(req: CribDragRequest) -> CribDragResponse:
    """Performs targeted or automated crib-dragging cryptanalysis over C1 ^ C2."""
    c1_bytes = _decode_bytes(req.c1, req.input_format)
    c2_bytes = _decode_bytes(req.c2, req.input_format)

    overlap = min(len(c1_bytes), len(c2_bytes))
    xor_stream = xor_bytes(c1_bytes[:overlap], c2_bytes[:overlap])

    if req.position is not None:
        drag_res = drag_crib(xor_stream, req.crib, offset=req.position)
        if drag_res.candidates:
            cand = drag_res.candidates[0]
            cand_schema = CribDragCandidateSchema(
                position=cand.offset,
                crib=cand.crib,
                revealed_text=cand.revealed_text,
                readability_score=cand.score,
                is_likely_english=cand.is_likely_english,
            )
            return CribDragResponse(
                c1_hex=c1_bytes.hex(),
                c2_hex=c2_bytes.hex(),
                crib=req.crib,
                position=req.position,
                single_result=cand_schema,
                candidates=[cand_schema],
                best_candidate=cand_schema,
                summary=f"Crib '{req.crib}' dragged at position {req.position} with readability score {cand.score:.4f}.",
            )
        else:
            return CribDragResponse(
                c1_hex=c1_bytes.hex(),
                c2_hex=c2_bytes.hex(),
                crib=req.crib,
                position=req.position,
                single_result=None,
                candidates=[],
                best_candidate=None,
                summary=f"Crib '{req.crib}' could not be placed at position {req.position}.",
            )
    else:
        drag_res = drag_crib(xor_stream, req.crib)
        candidates = [
            CribDragCandidateSchema(
                position=c.offset,
                crib=c.crib,
                revealed_text=c.revealed_text,
                readability_score=c.score,
                is_likely_english=c.is_likely_english,
            )
            for c in drag_res.candidates
            if c.score >= req.min_readability_score
        ]
        candidates.sort(key=lambda x: x.readability_score, reverse=True)

        best_cand: CribDragCandidateSchema | None = None
        if candidates:
            best_cand = candidates[0]
        elif drag_res.best_candidate:
            best_cand = CribDragCandidateSchema(
                position=drag_res.best_candidate.offset,
                crib=drag_res.best_candidate.crib,
                revealed_text=drag_res.best_candidate.revealed_text,
                readability_score=drag_res.best_candidate.score,
                is_likely_english=drag_res.best_candidate.is_likely_english,
            )

        return CribDragResponse(
            c1_hex=c1_bytes.hex(),
            c2_hex=c2_bytes.hex(),
            crib=req.crib,
            position=None,
            single_result=None,
            candidates=candidates,
            best_candidate=best_cand,
            summary=f"Scanned {len(drag_res.candidates)} offsets for crib '{req.crib}'. Identified {len(candidates)} candidate(s) exceeding readability threshold {req.min_readability_score}.",
        )


@router.post("/entropy", response_model=EntropyResponse)
async def calculate_entropy_endpoint(req: EntropyRequest) -> EntropyResponse:
    """Computes Shannon entropy, frequency distributions, and randomness metrics."""
    data_bytes = _decode_bytes(req.data, req.input_format)
    analysis = calculate_shannon_entropy(data_bytes)

    n = len(data_bytes)
    freq_table = {f"0x{b:02x}": count for b, count in sorted(analysis.frequencies.items())}
    prob_table = {f"0x{b:02x}": round(count / n, 6) for b, count in sorted(analysis.frequencies.items())} if n > 0 else {}

    verdict = (
        "High Randomness (Cryptographic Quality)"
        if analysis.is_near_maximal
        else "Low Randomness (Structured / Redundant Data)"
    )

    return EntropyResponse(
        entropy=analysis.entropy,
        max_entropy=analysis.max_entropy,
        efficiency=analysis.entropy_ratio,
        length=analysis.data_length,
        unique_symbols=len(analysis.frequencies),
        verdict=verdict,
        frequency_table=freq_table,
        probability_table=prob_table,
    )
