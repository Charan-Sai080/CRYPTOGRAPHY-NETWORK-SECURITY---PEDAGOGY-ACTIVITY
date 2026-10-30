from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas.dsa import (
    DSADomainGenerateRequest,
    DSADomainGenerateResponse,
    DSAKeyGenerateRequest,
    DSAKeyGenerateResponse,
    DSANonceReuseExploitRequest,
    DSANonceReuseExploitResponse,
    DSAPresetSchema,
    DSAPrivateKeySchema,
    DSAPublicKeySchema,
    DSASignRequest,
    DSASignResponse,
    DSASignTraceSchema,
    DSATamperRequest,
    DSATamperResponse,
    DSAVerifyRequest,
    DSAVerifyResponse,
    DSAVerifyTraceSchema,
)
from backend.core.dsa import (
    DSADomainParams,
    DSAPrivateKey,
    DSAPublicKey,
    DSASignature,
    DSASignatureError,
    detect_tampering,
    dsa_exploit_nonce_reuse,
    generate_dsa_domain,
    generate_dsa_key_pair,
    get_dsa_preset,
    list_dsa_presets,
    sign_message,
    verify_message,
)

router = APIRouter(prefix="/dsa", tags=["Digital Signature Algorithm"])


@router.get("/presets", response_model=list[DSAPresetSchema])
async def get_presets() -> list[DSAPresetSchema]:
    """Lists pre-configured FIPS 186-4 standard and educational DSA presets."""
    presets = list_dsa_presets()
    return [
        DSAPresetSchema(
            name=p.name,
            p=p.p,
            q=p.q,
            g=p.g,
            p_str=str(p.p),
            q_str=str(p.q),
            g_str=str(p.g),
            p_bits=p.p_bits,
            q_bits=p.q_bits,
        )
        for p in presets
    ]


@router.post("/generate-domain", response_model=DSADomainGenerateResponse)
async def generate_domain(req: DSADomainGenerateRequest) -> DSADomainGenerateResponse:
    """Generates dynamic educational DSA domain parameters (p, q, g) with search logs."""
    domain, logs = generate_dsa_domain(p_bits=req.p_bits, q_bits=req.q_bits)
    return DSADomainGenerateResponse(
        p=domain.p,
        q=domain.q,
        g=domain.g,
        p_str=str(domain.p),
        q_str=str(domain.q),
        g_str=str(domain.g),
        p_bits=domain.p_bits,
        q_bits=domain.q_bits,
        logs=logs,
    )


@router.post("/generate-keys", response_model=DSAKeyGenerateResponse)
async def generate_keys(req: DSAKeyGenerateRequest) -> DSAKeyGenerateResponse:
    """Generates DSA asymmetric key pair using CSPRNG or deterministic seed."""
    if req.preset_name is not None:
        domain = get_dsa_preset(req.preset_name)
    else:
        if req.p is None or req.q is None or req.g is None:
            raise ValueError("Modulus 'p', subprime 'q', and generator 'g' are required when preset_name is omitted.")
        domain = DSADomainParams(p=req.p, q=req.q, g=req.g)

    kp = generate_dsa_key_pair(domain, seed_x=req.seed_x)
    pub = kp.public_key
    priv = kp.private_key

    return DSAKeyGenerateResponse(
        public_key=DSAPublicKeySchema(
            p=pub.p,
            q=pub.q,
            g=pub.g,
            y=pub.y,
            p_str=str(pub.p),
            q_str=str(pub.q),
            g_str=str(pub.g),
            y_str=str(pub.y),
        ),
        private_key=DSAPrivateKeySchema(
            p=priv.p,
            q=priv.q,
            g=priv.g,
            x=priv.x,
            p_str=str(priv.p),
            q_str=str(priv.q),
            g_str=str(priv.g),
            x_str=str(priv.x),
        ),
    )


@router.post("/sign", response_model=DSASignResponse)
async def sign(req: DSASignRequest) -> DSASignResponse:
    """Signs message string adhering to FIPS 186-4 with SHA-256 and resampling."""
    priv = DSAPrivateKey(p=req.p, q=req.q, g=req.g, x=req.x)
    res = sign_message(req.message, priv, seed_k=req.seed_k)
    tr = res.trace

    trace_schema = DSASignTraceSchema(
        message=str(tr.message),
        hash_hex=tr.message_hash_hex,
        hash_int=tr.z,
        k=tr.k,
        r=tr.r,
        s=tr.s,
        k_inv=tr.k_inv,
        p=req.p,
        q=req.q,
        g=req.g,
        x=req.x,
        formula_r=tr.r_formula,
        formula_s=tr.s_formula,
        resample_count=tr.attempts,
    )

    return DSASignResponse(
        r=res.signature.r,
        s=res.signature.s,
        r_str=str(res.signature.r),
        s_str=str(res.signature.s),
        hash_hex=tr.message_hash_hex,
        hash_int=tr.z,
        trace=trace_schema,
    )


@router.post("/verify", response_model=DSAVerifyResponse)
async def verify(req: DSAVerifyRequest) -> DSAVerifyResponse:
    """Verifies DSA signature with boundary checks and modular exponentiation steps."""
    pub = DSAPublicKey(p=req.p, q=req.q, g=req.g, y=req.y)

    try:
        sig = DSASignature(r=req.r, s=req.s, q=req.q)
        ver_res = verify_message(req.message, sig, pub)
    except DSASignatureError as err:
        return DSAVerifyResponse(
            is_valid=False,
            reason=str(err),
            v=None,
            r=req.r,
            trace=None,
        )

    trace_schema: DSAVerifyTraceSchema | None = None
    if ver_res.trace is not None:
        tr = ver_res.trace
        trace_schema = DSAVerifyTraceSchema(
            message=str(tr.message),
            hash_int=tr.z,
            r=tr.r,
            s=tr.s,
            w=tr.w,
            u1=tr.u1,
            u2=tr.u2,
            v=tr.v,
            is_valid=tr.is_valid,
            p=req.p,
            q=req.q,
            g=req.g,
            y=req.y,
            formula_w=tr.w_formula,
            formula_u1=tr.u1_formula,
            formula_u2=tr.u2_formula,
            formula_v=tr.v_formula,
        )

    return DSAVerifyResponse(
        is_valid=ver_res.is_valid,
        reason=ver_res.reason,
        v=ver_res.trace.v if ver_res.trace else None,
        r=req.r,
        trace=trace_schema,
    )


@router.post("/detect-tampering", response_model=DSATamperResponse)
async def detect_tampering_endpoint(req: DSATamperRequest) -> DSATamperResponse:
    """Simulates single-bit tampering on message or signature components (r, s)."""
    priv = DSAPrivateKey(p=req.p, q=req.q, g=req.g, x=req.x)
    pub = DSAPublicKey(p=req.p, q=req.q, g=req.g, y=req.y)

    sign_res = sign_message(req.message, priv, seed_k=req.seed_k)
    orig_sig = sign_res.signature

    if req.tamper_target == "message":
        tamper_type = "message_bit_flip"
    elif req.tamper_target == "r":
        tamper_type = "signature_r_alter"
    else:
        tamper_type = "signature_s_alter"

    res = detect_tampering(
        req.message,
        orig_sig,
        pub,
        tamper_type=tamper_type,
        bit_index=req.bit_index,
    )

    tampered_msg = str(res.tampered_value if tamper_type == "message_bit_flip" else req.message)
    tampered_sig = {
        "r": res.tampered_value if tamper_type == "signature_r_alter" else orig_sig.r,
        "s": res.tampered_value if tamper_type == "signature_s_alter" else orig_sig.s,
    }

    return DSATamperResponse(
        tamper_detected=res.detected,
        tamper_type=res.tamper_type,
        bit_flipped=req.bit_index,
        original_message=req.message,
        tampered_message=tampered_msg,
        original_signature={"r": orig_sig.r, "s": orig_sig.s},
        tampered_signature=tampered_sig,
        original_verification=res.original_valid,
        tampered_verification=res.tampered_valid,
    )


@router.post("/exploit-nonce-reuse", response_model=DSANonceReuseExploitResponse)
async def exploit_nonce_reuse_endpoint(req: DSANonceReuseExploitRequest) -> DSANonceReuseExploitResponse:
    """Executes Sony PS3 exploit extracting private key x from reused ephemeral nonce k."""
    pub = DSAPublicKey(p=req.p, q=req.q, g=req.g, y=req.y)
    sig1 = DSASignature(r=req.r1, s=req.s1, q=req.q)
    sig2 = DSASignature(r=req.r2, s=req.s2, q=req.q)

    res = dsa_exploit_nonce_reuse(
        sig1=sig1,
        sig2=sig2,
        m1=req.m1,
        m2=req.m2,
        public_key=pub,
    )

    return DSANonceReuseExploitResponse(
        is_exploit_applicable=res.is_key_recovered,
        recovered_k=res.recovered_k,
        recovered_x=res.recovered_x,
        recovered_k_str=str(res.recovered_k),
        recovered_x_str=str(res.recovered_x),
        is_valid_private_key=res.is_key_recovered,
        public_key_matched=res.public_key_verified,
        steps=res.step_trace,
        proof_summary=res.algebraic_proof,
        historical_context=res.historical_context,
    )
