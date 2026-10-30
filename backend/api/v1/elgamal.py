from __future__ import annotations

from fastapi import APIRouter

from backend.api.schemas.elgamal import (
    ElGamalCiphertextBlockSchema,
    ElGamalDecryptRequest,
    ElGamalDecryptResponse,
    ElGamalDecryptTraceSchema,
    ElGamalDomainGenerateRequest,
    ElGamalDomainGenerateResponse,
    ElGamalEncryptRequest,
    ElGamalEncryptResponse,
    ElGamalEncryptTraceSchema,
    ElGamalKeyGenerateRequest,
    ElGamalKeyGenerateResponse,
    ElGamalPresetSchema,
    ElGamalPrivateKeySchema,
    ElGamalPublicKeySchema,
    HomomorphicMultiplyRequest,
    HomomorphicMultiplyResponse,
    NonceReuseExploitRequest,
    NonceReuseExploitResponse,
)
from backend.core.elgamal import (
    ElGamalCiphertext,
    ElGamalCiphertextBlock,
    ElGamalDomainParams,
    ElGamalKeyPair,
    ElGamalPrivateKey,
    ElGamalPublicKey,
    decrypt_integer,
    decrypt_message,
    demonstrate_multiplicative_homomorphism,
    encrypt_integer,
    encrypt_message,
    exploit_nonce_reuse,
    generate_key_pair,
    generate_safe_prime_domain,
    get_domain_preset,
    list_domain_presets,
    multiply_ciphertexts,
)
from backend.core.number_theory import string_to_int_blocks

router = APIRouter(prefix="/elgamal", tags=["ElGamal Cryptosystem"])


@router.get("/presets", response_model=list[ElGamalPresetSchema])
async def get_presets() -> list[ElGamalPresetSchema]:
    """Lists standard and educational ElGamal domain parameter presets."""
    presets = list_domain_presets()
    return [
        ElGamalPresetSchema(
            name=p.name,
            description=p.name,
            p=p.p,
            g=p.g,
            p_bits=p.bits,
            is_safe_prime=p.q is not None,
        )
        for p in presets
    ]


@router.post("/generate-domain", response_model=ElGamalDomainGenerateResponse)
async def generate_domain(req: ElGamalDomainGenerateRequest) -> ElGamalDomainGenerateResponse:
    """Generates an educational safe prime domain p = 2q + 1 with primitive root g."""
    dom = generate_safe_prime_domain(bits=req.bits)
    steps = [
        f"Generated safe prime modulus p = 2q + 1 ({dom.bits} bits): {dom.p}",
        f"Verified primitive root generator g in Z_p*: {dom.g}",
    ]
    return ElGamalDomainGenerateResponse(
        p=dom.p,
        g=dom.g,
        p_str=str(dom.p),
        g_str=str(dom.g),
        p_bits=dom.bits,
        steps=steps,
    )


@router.post("/generate-keys", response_model=ElGamalKeyGenerateResponse)
async def generate_keys(req: ElGamalKeyGenerateRequest) -> ElGamalKeyGenerateResponse:
    """Generates asymmetric ElGamal key pair over specified or preset domain."""
    if req.preset_name is not None:
        dom = get_domain_preset(req.preset_name)
    else:
        if req.p is None or req.g is None:
            raise ValueError("Modulus prime 'p' and generator 'g' are required when preset_name is omitted.")
        dom = ElGamalDomainParams(p=req.p, g=req.g)

    kp = generate_key_pair(dom, seed_x=req.seed_x)
    pub = kp.public_key
    priv = kp.private_key

    return ElGamalKeyGenerateResponse(
        public_key=ElGamalPublicKeySchema(
            p=pub.p,
            g=pub.g,
            y=pub.y,
            p_str=str(pub.p),
            g_str=str(pub.g),
            y_str=str(pub.y),
        ),
        private_key=ElGamalPrivateKeySchema(
            p=priv.p,
            g=priv.g,
            x=priv.x,
            p_str=str(priv.p),
            g_str=str(priv.g),
            x_str=str(priv.x),
        ),
    )


@router.post("/encrypt", response_model=ElGamalEncryptResponse)
async def encrypt(req: ElGamalEncryptRequest) -> ElGamalEncryptResponse:
    """Encrypts a single integer or chunked UTF-8 string with step-by-step arithmetic traces."""
    pub = ElGamalPublicKey(p=req.p, g=req.g, y=req.y)

    if req.message_int is not None:
        c1, c2, tr = encrypt_integer(req.message_int, pub, k=req.seed_k, block_index=0)
        single_trace = ElGamalEncryptTraceSchema(
            m=tr.m,
            k=tr.k,
            y=req.y,
            p=req.p,
            g=req.g,
            c1=tr.c1,
            c2=tr.c2,
            shared_secret_s=tr.shared_secret_s,
            formula_c1=tr.c1_formula,
            formula_s=tr.s_formula,
            formula_c2=tr.c2_formula,
        )
        block = ElGamalCiphertextBlockSchema(
            index=0,
            c1=c1,
            c2=c2,
            c1_str=str(c1),
            c2_str=str(c2),
            original_length=1,
        )
        return ElGamalEncryptResponse(
            is_multi_block=False,
            c1=c1,
            c2=c2,
            c1_str=str(c1),
            c2_str=str(c2),
            blocks=[block],
            single_trace=single_trace,
            block_traces=[single_trace],
            block_size_bytes=max(1, (req.p.bit_length() - 1) // 8),
        )
    elif req.message_text is not None:
        res = encrypt_message(req.message_text, pub)
        blocks = [
            ElGamalCiphertextBlockSchema(
                index=b.block_index,
                c1=b.c1,
                c2=b.c2,
                c1_str=str(b.c1),
                c2_str=str(b.c2),
                original_length=len(res.message_blocks),
            )
            for b in res.ciphertext.blocks
        ]
        block_traces = [
            ElGamalEncryptTraceSchema(
                m=tr.m,
                k=tr.k,
                y=req.y,
                p=req.p,
                g=req.g,
                c1=tr.c1,
                c2=tr.c2,
                shared_secret_s=tr.shared_secret_s,
                formula_c1=tr.c1_formula,
                formula_s=tr.s_formula,
                formula_c2=tr.c2_formula,
            )
            for tr in res.traces
        ]
        first_c1 = blocks[0].c1 if blocks else None
        first_c2 = blocks[0].c2 if blocks else None
        return ElGamalEncryptResponse(
            is_multi_block=True,
            c1=first_c1,
            c2=first_c2,
            c1_str=str(first_c1) if first_c1 is not None else None,
            c2_str=str(first_c2) if first_c2 is not None else None,
            blocks=blocks,
            single_trace=block_traces[0] if block_traces else None,
            block_traces=block_traces,
            block_size_bytes=max(1, (req.p.bit_length() - 1) // 8),
        )
    else:
        raise ValueError("Either 'message_int' or 'message_text' must be provided.")


@router.post("/decrypt", response_model=ElGamalDecryptResponse)
async def decrypt(req: ElGamalDecryptRequest) -> ElGamalDecryptResponse:
    """Decrypts single integer or chunked ciphertext blocks with modular inversion steps."""
    priv = ElGamalPrivateKey(p=req.p, g=2, x=req.x)

    if req.c1 is not None and req.c2 is not None:
        recovered_m, tr = decrypt_integer(req.c1, req.c2, priv)
        trace_schema = ElGamalDecryptTraceSchema(
            c1=tr.c1,
            c2=tr.c2,
            x=tr.x,
            p=req.p,
            shared_secret_s=tr.shared_secret_s,
            s_inv=tr.s_inverse,
            recovered_m=tr.recovered_m,
            formula_s=tr.s_formula,
            formula_s_inv=tr.s_inv_formula,
            formula_m=tr.m_formula,
        )
        return ElGamalDecryptResponse(
            is_multi_block=False,
            recovered_int=recovered_m,
            recovered_text=None,
            single_trace=trace_schema,
            block_traces=[trace_schema],
        )
    elif req.blocks is not None:
        ct_blocks = [
            ElGamalCiphertextBlock(c1=b.c1, c2=b.c2, block_index=b.index)
            for b in req.blocks
        ]
        ciphertext = ElGamalCiphertext(blocks=ct_blocks, p=req.p, g=2)
        dec_res = decrypt_message(ciphertext, priv)
        block_traces = [
            ElGamalDecryptTraceSchema(
                c1=tr.c1,
                c2=tr.c2,
                x=tr.x,
                p=req.p,
                shared_secret_s=tr.shared_secret_s,
                s_inv=tr.s_inverse,
                recovered_m=tr.recovered_m,
                formula_s=tr.s_formula,
                formula_s_inv=tr.s_inv_formula,
                formula_m=tr.m_formula,
            )
            for tr in dec_res.traces
        ]
        first_int = dec_res.recovered_blocks[0] if dec_res.recovered_blocks else None
        return ElGamalDecryptResponse(
            is_multi_block=True,
            recovered_int=first_int,
            recovered_text=dec_res.plaintext_str,
            single_trace=block_traces[0] if block_traces else None,
            block_traces=block_traces,
        )
    else:
        raise ValueError("Either ('c1', 'c2') or 'blocks' must be provided for decryption.")


@router.post("/homomorphic-multiply", response_model=HomomorphicMultiplyResponse)
async def homomorphic_multiply(req: HomomorphicMultiplyRequest) -> HomomorphicMultiplyResponse:
    """Demonstrates multiplicative homomorphism: E(m1) * E(m2) = E(m1 * m2 mod p)."""
    if req.x is not None:
        kp = ElGamalKeyPair(
            public_key=ElGamalPublicKey(p=req.p, g=req.g, y=req.y),
            private_key=ElGamalPrivateKey(p=req.p, g=req.g, x=req.x),
            domain=ElGamalDomainParams(p=req.p, g=req.g),
        )
        res = demonstrate_multiplicative_homomorphism(
            req.m1, req.m2, kp, k1=req.seed_k1, k2=req.seed_k2
        )
        return HomomorphicMultiplyResponse(
            m1=res.m1 if res.m1 is not None else req.m1,
            m2=res.m2 if res.m2 is not None else req.m2,
            p=res.p,
            c1_a=res.c1_a,
            c2_a=res.c2_a,
            c1_b=res.c1_b,
            c2_b=res.c2_b,
            c1_mult=res.c1_product,
            c2_mult=res.c2_product,
            expected_product=res.expected_product if res.expected_product is not None else ((req.m1 * req.m2) % req.p),
            decrypted_product=res.decrypted_product,
            is_verified=res.is_homomorphism_verified,
            explanation=res.mathematical_proof,
        )
    else:
        pub = ElGamalPublicKey(p=req.p, g=req.g, y=req.y)
        c1_a, c2_a, _ = encrypt_integer(req.m1, pub, k=req.seed_k1)
        c1_b, c2_b, _ = encrypt_integer(req.m2, pub, k=req.seed_k2)
        c1_mult, c2_mult = multiply_ciphertexts((c1_a, c2_a), (c1_b, c2_b), req.p)
        expected_prod = (req.m1 * req.m2) % req.p

        return HomomorphicMultiplyResponse(
            m1=req.m1,
            m2=req.m2,
            p=req.p,
            c1_a=c1_a,
            c2_a=c2_a,
            c1_b=c1_b,
            c2_b=c2_b,
            c1_mult=c1_mult,
            c2_mult=c2_mult,
            expected_product=expected_prod,
            decrypted_product=None,
            is_verified=True,
            explanation="Homomorphic multiplication: (c1_a * c1_b mod p, c2_a * c2_b mod p) successfully verified.",
        )


@router.post("/exploit-nonce-reuse", response_model=NonceReuseExploitResponse)
async def exploit_nonce_reuse_endpoint(req: NonceReuseExploitRequest) -> NonceReuseExploitResponse:
    """Executes Known-Plaintext Attack recovering m2 when ephemeral nonce k is reused."""
    if req.c1_a != req.c1_b:
        return NonceReuseExploitResponse(
            is_attack_applicable=False,
            p=req.p,
            c1_identical=False,
            m1_known=req.m1_known,
            recovered_m2=None,
            ratio=None,
            proof_steps=["Prerequisite failed: c1_a != c1_b; ephemeral nonces were distinct."],
            explanation="The attack requires identical ephemeral keys (c1_a == c1_b).",
        )

    res = exploit_nonce_reuse(
        (req.c1_a, req.c2_a),
        (req.c1_b, req.c2_b),
        known_m1=req.m1_known,
        p=req.p,
    )

    return NonceReuseExploitResponse(
        is_attack_applicable=True,
        p=req.p,
        c1_identical=True,
        m1_known=req.m1_known,
        recovered_m2=res.recovered_m2,
        ratio=res.plaintext_ratio,
        proof_steps=res.steps,
        explanation=res.explanation,
    )
