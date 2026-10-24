"""ElGamal Public-Key Cryptosystem & Multiplicative Homomorphism Engine.

Pedagogical and mathematically rigorous pure-Python 3.12+ implementation of:
1. Domain parameter management & Sophie Germain safe prime generation.
2. Generator verification over cyclic groups Z_p*.
3. Asymmetric key pair generation with CSPRNG entropy.
4. Traced single-integer and chunked multi-block UTF-8 encryption and decryption.
5. Multiplicative homomorphism over ciphertext pairs.
6. Ephemeral nonce-reuse cryptanalysis (Known-Plaintext Attack & plaintext ratio leakage).
"""

from __future__ import annotations

import math
import secrets
from dataclasses import dataclass, field

from backend.core.number_theory import (
    RFC_2409_1024_MODP,
    distinct_prime_factors,
    generate_safe_prime,
    int_blocks_to_string,
    is_prime,
    mod_inverse,
    string_to_int_blocks,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ElGamalError(Exception):
    """Base exception for all ElGamal cryptographic operations."""
    pass


class InvalidDomainParametersError(ElGamalError):
    """Raised when domain parameters (p, g) are mathematically invalid."""
    pass


class DomainParameterError(InvalidDomainParametersError):
    """Alias for InvalidDomainParametersError."""
    pass


class InvalidKeyError(ElGamalError):
    """Raised when a public or private key is malformed or out of bounds."""
    pass


class KeyValidationError(InvalidKeyError):
    """Alias for InvalidKeyError."""
    pass


class EncryptionError(ElGamalError):
    """Raised when an encryption operation fails or inputs are invalid."""
    pass


class DecryptionError(ElGamalError):
    """Raised when a decryption operation fails or inputs are invalid."""
    pass


class CryptanalysisError(ElGamalError):
    """Raised when cryptanalytic exploit fails or prerequisites are not met."""
    pass


class NonceReuseError(CryptanalysisError):
    """Raised when nonce reuse attack fails or prerequisites are violated."""
    pass


class HomomorphismError(ElGamalError):
    """Raised when homomorphic multiplication fails or parameters are invalid."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ElGamalDomainParams:
    """Represents public ElGamal cyclic group domain parameters (p, g)."""
    p: int                          # Prime modulus p
    g: int                          # Generator g of Z_p*
    name: str = "Custom Domain"     # Descriptive identifier
    bits: int = field(init=False)   # Bit length of p
    q: int | None = None            # Sophie Germain factor if safe prime (p = 2q + 1)

    def __post_init__(self) -> None:
        if not isinstance(self.p, int) or self.p <= 2:
            raise InvalidDomainParametersError(f"Modulus p must be an integer > 2, got {self.p}")
        if not is_prime(self.p).is_prime:
            raise InvalidDomainParametersError(f"Modulus p must be a prime number, got {self.p}")
        if not isinstance(self.g, int) or not (2 <= self.g < self.p):
            raise InvalidDomainParametersError(
                f"Generator g must be in range [2, p - 1] ([2, {self.p - 1}]), got {self.g}"
            )
        object.__setattr__(self, "bits", self.p.bit_length())


@dataclass(frozen=True)
class ElGamalPublicKey:
    """Public key component for ElGamal encryption."""
    p: int
    g: int
    y: int                          # y = g^x mod p
    domain_name: str = "Custom Domain"

    def __post_init__(self) -> None:
        if not (2 <= self.y < self.p):
            raise InvalidKeyError(f"Public key y must be in range [2, p - 1] ([2, {self.p - 1}]), got {self.y}")


@dataclass(frozen=True)
class ElGamalPrivateKey:
    """Private key component for ElGamal decryption."""
    p: int
    g: int
    x: int                          # Private exponent x in [2, p - 2]
    domain_name: str = "Custom Domain"

    def __post_init__(self) -> None:
        if not (2 <= self.x <= self.p - 2):
            raise InvalidKeyError(f"Private key x must be in range [2, p - 2] ([2, {self.p - 2}]), got {self.x}")


@dataclass(frozen=True)
class ElGamalKeyPair:
    """Asymmetric key pair container."""
    public_key: ElGamalPublicKey
    private_key: ElGamalPrivateKey
    domain: ElGamalDomainParams


@dataclass(frozen=True)
class ElGamalCiphertextBlock:
    """A single ElGamal ciphertext pair (c1, c2)."""
    c1: int
    c2: int
    block_index: int = 0


@dataclass(frozen=True)
class ElGamalCiphertext:
    """Encapsulates one or more ciphertext blocks with domain metadata."""
    blocks: list[ElGamalCiphertextBlock]
    p: int
    g: int
    domain_name: str = "Custom Domain"
    total_blocks: int = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "total_blocks", len(self.blocks))

    def to_tuple_list(self) -> list[tuple[int, int]]:
        """Returns blocks as a list of (c1, c2) integer tuples."""
        return [(b.c1, b.c2) for b in self.blocks]


@dataclass(frozen=True)
class ElGamalEncryptTrace:
    """Detailed step-by-step arithmetic trace for a single encrypted block."""
    block_index: int
    m: int                          # Plaintext integer block
    k: int                          # Ephemeral nonce
    c1: int                         # c1 = g^k mod p
    shared_secret_s: int            # s = y^k mod p
    c2: int                         # c2 = (m * s) mod p
    c1_formula: str                 # e.g., "c1 = g^k mod p = 3^4519 mod 65537 = 31204"
    s_formula: str                  # e.g., "s = y^k mod p = 52319^4519 mod 65537 = 19448"
    c2_formula: str                 # e.g., "c2 = (m * s) mod p = (42 * 19448) mod 65537 = 29517"


@dataclass(frozen=True)
class ElGamalDecryptTrace:
    """Detailed step-by-step arithmetic trace for a single decrypted block."""
    block_index: int
    c1: int                         # Ephemeral key c1
    c2: int                         # Encrypted payload c2
    x: int                          # Private key exponent
    shared_secret_s: int            # s = c1^x mod p
    s_inverse: int                  # s^-1 mod p via Extended Euclidean Algorithm
    recovered_m: int                # m = (c2 * s^-1) mod p
    s_formula: str                  # e.g., "s = c1^x mod p = 31204^12345 mod 65537 = 19448"
    s_inv_formula: str              # e.g., "s^-1 = mod_inverse(19448, 65537) = 37882"
    m_formula: str                  # e.g., "m = (c2 * s^-1) mod p = (29517 * 37882) mod 65537 = 42"


@dataclass(frozen=True)
class ElGamalEncryptionResult:
    """Complete result of an encryption operation, including traces and metadata."""
    ciphertext: ElGamalCiphertext
    traces: list[ElGamalEncryptTrace]
    message_blocks: list[int]
    is_string_message: bool
    original_text: str | None = None


ElGamalMultiBlockResult = ElGamalEncryptionResult


@dataclass(frozen=True)
class ElGamalDecryptionResult:
    """Complete result of a decryption operation, including traces and decoded text."""
    recovered_blocks: list[int]
    plaintext_str: str | None
    traces: list[ElGamalDecryptTrace]
    is_verified: bool


@dataclass(frozen=True)
class HomomorphicMultiplicationResult:
    """Detailed record of homomorphic multiplication over ElGamal ciphertexts."""
    c1_a: int
    c2_a: int
    c1_b: int
    c2_b: int
    m1: int | None
    m2: int | None
    c1_product: int                # (c1_a * c1_b) mod p
    c2_product: int                # (c2_a * c2_b) mod p
    decrypted_product: int         # Decrypted plaintext from product ciphertext
    expected_product: int | None   # (m1 * m2) mod p
    is_homomorphism_verified: bool
    p: int
    step_trace: list[str] = field(default_factory=list)
    mathematical_proof: str = ""


@dataclass(frozen=True)
class NonceReuseExploitResult:
    """Detailed record of ephemeral nonce reuse cryptanalytic attack."""
    c1: int                        # Shared ephemeral component (c1_a == c1_b)
    c2_a: int                      # Ciphertext 2 of message A
    c2_b: int                      # Ciphertext 2 of message B
    known_m1: int                  # Known plaintext of message A
    recovered_m2: int              # Recovered plaintext of message B without private key
    actual_m2: int | None          # Actual plaintext (if known for verification)
    plaintext_ratio: int           # (m1 * m2^-1) mod p = (c2_a * c2_b^-1) mod p
    attack_successful: bool
    steps: list[str] = field(default_factory=list)
    explanation: str = ""


NonceReuseAttackResult = NonceReuseExploitResult


# ---------------------------------------------------------------------------
# Domain Presets Catalog
# ---------------------------------------------------------------------------


DOMAIN_PRESETS: dict[str, ElGamalDomainParams] = {
    "rfc_2409_1024": ElGamalDomainParams(
        p=RFC_2409_1024_MODP["prime"],
        g=RFC_2409_1024_MODP["generator"],
        name="RFC 2409 / 3526 1024-bit MODP Oakley Group 2",
    ),
    "educational_16": ElGamalDomainParams(
        p=65537,
        g=3,
        name="Educational 16-bit Group (Fermat F4 prime)",
    ),
    "educational_20": ElGamalDomainParams(
        p=1048583,
        g=2,
        name="Educational 20-bit Group",
    ),
    "educational_24": ElGamalDomainParams(
        p=16777259,
        g=2,
        name="Educational 24-bit Safe Prime Group",
        q=8388629,
    ),
    "educational_32": ElGamalDomainParams(
        p=4294967311,
        g=3,
        name="Educational 32-bit Safe Prime Group",
        q=2147483655,
    ),
}


# ---------------------------------------------------------------------------
# Domain & Key Generation Functions
# ---------------------------------------------------------------------------


def get_domain_preset(preset_key: str) -> ElGamalDomainParams:
    """Retrieves an ElGamal domain preset by its unique key."""
    if preset_key not in DOMAIN_PRESETS:
        raise KeyError(f"Domain preset '{preset_key}' not found. Available presets: {list(DOMAIN_PRESETS.keys())}")
    return DOMAIN_PRESETS[preset_key]


def list_domain_presets() -> list[ElGamalDomainParams]:
    """Returns a list of all registered ElGamal domain presets."""
    return list(DOMAIN_PRESETS.values())


def verify_primitive_root(g: int, p: int, q: int | None = None) -> bool:
    """Verifies whether g is a generator of Z_p*.

    If q is provided such that p = 2q + 1 is a safe prime, verifies:
      1. g^2 mod p != 1
      2. g^q mod p != 1
    Otherwise, computes prime factors of p - 1 and verifies g^((p-1)/f) mod p != 1.
    Recognizes pre-verified RFC 2409 parameters.
    """
    if not isinstance(p, int) or not isinstance(g, int) or p <= 2 or not (2 <= g < p):
        return False

    # Standard RFC Oakley Group 2 optimization
    if p == RFC_2409_1024_MODP["prime"] and g == RFC_2409_1024_MODP["generator"]:
        return True

    if not is_prime(p).is_prime:
        return False

    # Safe prime verification shortcut
    if q is not None:
        return (pow(g, 2, p) != 1) and (pow(g, q, p) != 1)

    # General prime verification via distinct prime factors of phi(p) = p - 1
    factors = distinct_prime_factors(p - 1)
    if not factors:
        return False

    for factor in factors:
        if pow(g, (p - 1) // factor, p) == 1:
            return False

    return True


def generate_safe_prime_domain(bits: int = 16) -> ElGamalDomainParams:
    """Generates a dynamic safe prime domain p = 2q + 1 with confirmed primitive root g."""
    p, q, _ = generate_safe_prime(bits)
    for g_cand in range(2, p):
        if pow(g_cand, 2, p) != 1 and pow(g_cand, q, p) != 1:
            return ElGamalDomainParams(
                p=p,
                g=g_cand,
                name=f"Custom Safe Prime ({bits}-bit)",
                q=q,
            )
    raise InvalidDomainParametersError(f"Failed to discover primitive root for safe prime p={p}")


def generate_key_pair(
    domain: ElGamalDomainParams,
    seed_x: int | None = None,
) -> ElGamalKeyPair:
    """Generates an asymmetric ElGamal key pair over the specified domain.

    If seed_x is provided, validates that 2 <= seed_x <= p - 2 and uses it as private key x.
    Otherwise, generates a cryptographically secure random integer x in [2, p - 2] via secrets.randbelow.
    Computes public key y = g^x mod p.
    """
    if seed_x is not None:
        if not (2 <= seed_x <= domain.p - 2):
            raise InvalidKeyError(
                f"Private key exponent x must be in range [2, p - 2] ([2, {domain.p - 2}]), got {seed_x}"
            )
        x = seed_x
    else:
        x = secrets.randbelow(domain.p - 3) + 2

    y = pow(domain.g, x, domain.p)
    public_key = ElGamalPublicKey(p=domain.p, g=domain.g, y=y, domain_name=domain.name)
    private_key = ElGamalPrivateKey(p=domain.p, g=domain.g, x=x, domain_name=domain.name)
    return ElGamalKeyPair(public_key=public_key, private_key=private_key, domain=domain)


def verify_key_pair(key_pair: ElGamalKeyPair) -> bool:
    """Validates consistency between public and private keys (y == g^x mod p)."""
    pk = key_pair.public_key
    sk = key_pair.private_key
    dom = key_pair.domain

    if pk.p != sk.p or pk.p != dom.p:
        return False
    if pk.g != sk.g or pk.g != dom.g:
        return False
    if not (2 <= sk.x <= dom.p - 2):
        return False
    if not (2 <= pk.y < dom.p):
        return False
    return pow(pk.g, sk.x, pk.p) == pk.y


# ---------------------------------------------------------------------------
# Core Encryption & Decryption Engine
# ---------------------------------------------------------------------------


def generate_ephemeral_nonce(p: int, custom_k: int | None = None) -> int:
    """Selects an ephemeral nonce k in [2, p - 2] such that gcd(k, p - 1) == 1.

    If custom_k is provided, validates that 2 <= custom_k <= p - 2 and gcd(custom_k, p - 1) == 1.
    """
    if custom_k is not None:
        if not (2 <= custom_k <= p - 2):
            raise EncryptionError(
                f"Ephemeral nonce k must be in range [2, p - 2] ([2, {p - 2}]), got {custom_k}"
            )
        if math.gcd(custom_k, p - 1) != 1:
            raise EncryptionError(
                f"Ephemeral nonce k={custom_k} must be coprime to p - 1 ({p - 1}), but gcd is {math.gcd(custom_k, p - 1)}"
            )
        return custom_k

    if p <= 3:
        raise EncryptionError(f"Modulus p={p} is too small to choose ephemeral nonce in [2, p - 2]")

    while True:
        k = secrets.randbelow(p - 3) + 2
        if math.gcd(k, p - 1) == 1:
            return k


def encrypt_integer(
    m: int,
    public_key: ElGamalPublicKey,
    k: int | None = None,
    block_index: int = 0,
) -> tuple[int, int, ElGamalEncryptTrace]:
    """Encrypts a single message integer m in [1, p - 1] under the public key.

    Returns:
        (c1, c2, trace)
    where:
        c1 = g^k mod p
        s  = y^k mod p
        c2 = (m * s) mod p
    """
    if not isinstance(m, int) or not (1 <= m < public_key.p):
        raise EncryptionError(
            f"Plaintext integer m={m} must be in range [1, p - 1] ([1, {public_key.p - 1}])"
        )

    k_val = generate_ephemeral_nonce(public_key.p, custom_k=k)
    c1 = pow(public_key.g, k_val, public_key.p)
    s = pow(public_key.y, k_val, public_key.p)
    c2 = (m * s) % public_key.p

    c1_formula = f"c1 = g^k mod p = {public_key.g}^{k_val} mod {public_key.p} = {c1}"
    s_formula = f"s = y^k mod p = {public_key.y}^{k_val} mod {public_key.p} = {s}"
    c2_formula = f"c2 = (m * s) mod p = ({m} * {s}) mod {public_key.p} = {c2}"

    trace = ElGamalEncryptTrace(
        block_index=block_index,
        m=m,
        k=k_val,
        c1=c1,
        shared_secret_s=s,
        c2=c2,
        c1_formula=c1_formula,
        s_formula=s_formula,
        c2_formula=c2_formula,
    )
    return c1, c2, trace


def decrypt_integer(
    c1: int,
    c2: int,
    private_key: ElGamalPrivateKey,
    block_index: int = 0,
) -> tuple[int, ElGamalDecryptTrace]:
    """Decrypts a single ciphertext pair (c1, c2) using the private key x.

    Returns:
        (recovered_m, trace)
    where:
        s     = c1^x mod p
        s_inv = mod_inverse(s, p)
        m     = (c2 * s_inv) mod p
    """
    if not isinstance(c1, int) or not (1 <= c1 < private_key.p):
        raise DecryptionError(
            f"Ciphertext component c1={c1} must be in range [1, p - 1] ([1, {private_key.p - 1}])"
        )
    if not isinstance(c2, int) or not (0 <= c2 < private_key.p):
        raise DecryptionError(
            f"Ciphertext component c2={c2} must be in range [0, p - 1] ([0, {private_key.p - 1}])"
        )

    s = pow(c1, private_key.x, private_key.p)
    inv_res = mod_inverse(s, private_key.p)
    if inv_res.inverse is None:
        raise DecryptionError(f"Modular inverse of shared secret s={s} does not exist mod {private_key.p}")
    s_inv = inv_res.inverse
    m = (c2 * s_inv) % private_key.p

    s_formula = f"s = c1^x mod p = {c1}^{private_key.x} mod {private_key.p} = {s}"
    s_inv_formula = f"s^-1 = mod_inverse({s}, {private_key.p}) = {s_inv}"
    m_formula = f"m = (c2 * s^-1) mod p = ({c2} * {s_inv}) mod {private_key.p} = {m}"

    trace = ElGamalDecryptTrace(
        block_index=block_index,
        c1=c1,
        c2=c2,
        x=private_key.x,
        shared_secret_s=s,
        s_inverse=s_inv,
        recovered_m=m,
        s_formula=s_formula,
        s_inv_formula=s_inv_formula,
        m_formula=m_formula,
    )
    return m, trace


def encrypt_message(
    text: str,
    public_key: ElGamalPublicKey,
    nonces: list[int] | None = None,
) -> ElGamalEncryptionResult:
    """Encrypts an arbitrary UTF-8 text message into chunked ElGamal ciphertext blocks."""
    if not isinstance(text, str):
        raise EncryptionError(f"Plaintext message must be a string, got {type(text)}")

    if text == "":
        empty_ct = ElGamalCiphertext(
            blocks=[],
            p=public_key.p,
            g=public_key.g,
            domain_name=public_key.domain_name,
        )
        return ElGamalEncryptionResult(
            ciphertext=empty_ct,
            traces=[],
            message_blocks=[],
            is_string_message=True,
            original_text=text,
        )

    message_blocks = string_to_int_blocks(text, public_key.p.bit_length())

    if nonces is not None:
        if len(nonces) != len(message_blocks):
            raise EncryptionError(
                f"Expected {len(message_blocks)} nonces for {len(message_blocks)} blocks, got {len(nonces)}"
            )

    blocks: list[ElGamalCiphertextBlock] = []
    traces: list[ElGamalEncryptTrace] = []

    for idx, m_val in enumerate(message_blocks):
        k_val = nonces[idx] if nonces is not None else None
        c1, c2, trace = encrypt_integer(m_val, public_key, k=k_val, block_index=idx)
        blocks.append(ElGamalCiphertextBlock(c1=c1, c2=c2, block_index=idx))
        traces.append(trace)

    ciphertext = ElGamalCiphertext(
        blocks=blocks,
        p=public_key.p,
        g=public_key.g,
        domain_name=public_key.domain_name,
    )

    return ElGamalEncryptionResult(
        ciphertext=ciphertext,
        traces=traces,
        message_blocks=message_blocks,
        is_string_message=True,
        original_text=text,
    )


def decrypt_message(
    ciphertext: ElGamalCiphertext,
    private_key: ElGamalPrivateKey,
) -> ElGamalDecryptionResult:
    """Decrypts an ElGamalCiphertext back into integer blocks and decodes UTF-8 string."""
    if ciphertext.p != private_key.p:
        raise DecryptionError(
            f"Ciphertext modulus p ({ciphertext.p}) does not match private key modulus p ({private_key.p})."
        )

    if len(ciphertext.blocks) == 0:
        return ElGamalDecryptionResult(
            recovered_blocks=[],
            plaintext_str="",
            traces=[],
            is_verified=True,
        )

    recovered_blocks: list[int] = []
    traces: list[ElGamalDecryptTrace] = []

    for block in ciphertext.blocks:
        m, trace = decrypt_integer(block.c1, block.c2, private_key, block_index=block.block_index)
        recovered_blocks.append(m)
        traces.append(trace)

    plaintext_str = int_blocks_to_string(recovered_blocks, private_key.p.bit_length())

    return ElGamalDecryptionResult(
        recovered_blocks=recovered_blocks,
        plaintext_str=plaintext_str,
        traces=traces,
        is_verified=True,
    )


# ---------------------------------------------------------------------------
# Homomorphic Multiplication Engine
# ---------------------------------------------------------------------------


def multiply_ciphertexts(
    c_a: tuple[int, int] | ElGamalCiphertextBlock,
    c_b: tuple[int, int] | ElGamalCiphertextBlock,
    p: int,
) -> tuple[int, int]:
    """Multiplies two ElGamal ciphertexts component-wise modulo p.

    Returns:
        (c1_prod, c2_prod) = ((c1_a * c1_b) mod p, (c2_a * c2_b) mod p)
    """
    if p <= 2:
        raise HomomorphismError(f"Modulus p must be > 2, got {p}")

    c1_a = c_a.c1 if isinstance(c_a, ElGamalCiphertextBlock) else c_a[0]
    c2_a = c_a.c2 if isinstance(c_a, ElGamalCiphertextBlock) else c_a[1]
    c1_b = c_b.c1 if isinstance(c_b, ElGamalCiphertextBlock) else c_b[0]
    c2_b = c_b.c2 if isinstance(c_b, ElGamalCiphertextBlock) else c_b[1]

    c1_prod = (c1_a * c1_b) % p
    c2_prod = (c2_a * c2_b) % p
    return c1_prod, c2_prod


def demonstrate_multiplicative_homomorphism(
    m1: int,
    m2: int,
    key_pair: ElGamalKeyPair,
    k1: int | None = None,
    k2: int | None = None,
) -> HomomorphicMultiplicationResult:
    """Demonstrates multiplicative homomorphism: E(m1) * E(m2) = E(m1 * m2 mod p).

    Encrypts m1 with k1, encrypts m2 with k2, multiplies ciphertexts component-wise,
    decrypts the product ciphertext with the private key, and verifies that the decrypted
    result equals (m1 * m2) mod p.
    """
    p = key_pair.domain.p
    c1_a, c2_a, trace_a = encrypt_integer(m1, key_pair.public_key, k=k1, block_index=0)
    c1_b, c2_b, trace_b = encrypt_integer(m2, key_pair.public_key, k=k2, block_index=1)

    c1_prod, c2_prod = multiply_ciphertexts((c1_a, c2_a), (c1_b, c2_b), p)
    decrypted_prod, trace_dec = decrypt_integer(c1_prod, c2_prod, key_pair.private_key, block_index=0)
    expected_prod = (m1 * m2) % p
    is_verified = (decrypted_prod == expected_prod)

    step_trace = [
        f"1. Encryption of m1={m1}: c1_a = {c1_a}, c2_a = {c2_a} (nonce k1={trace_a.k})",
        f"2. Encryption of m2={m2}: c1_b = {c1_b}, c2_b = {c2_b} (nonce k2={trace_b.k})",
        f"3. Component-wise multiplication of c1: ({c1_a} * {c1_b}) mod {p} = {c1_prod}",
        f"4. Component-wise multiplication of c2: ({c2_a} * {c2_b}) mod {p} = {c2_prod}",
        f"5. Product ciphertext: C_prod = ({c1_prod}, {c2_prod})",
        f"6. Decryption shared secret: s_prod = {c1_prod}^{key_pair.private_key.x} mod {p} = {trace_dec.shared_secret_s}",
        f"7. Decryption secret inverse: s_prod^-1 = {trace_dec.s_inverse}",
        f"8. Decrypted product plaintext: ({c2_prod} * {trace_dec.s_inverse}) mod {p} = {decrypted_prod}",
        f"9. Expected product: ({m1} * {m2}) mod {p} = {expected_prod}",
        f"10. Homomorphic verification: {'SUCCESS' if is_verified else 'FAILURE'}",
    ]

    mathematical_proof = (
        "Multiplicative Homomorphism in ElGamal:\n"
        "Let public key y = g^x mod p.\n"
        "Ciphertext 1: E(m1) = (c1_a, c2_a) = (g^k1 mod p, (m1 * y^k1) mod p)\n"
        "Ciphertext 2: E(m2) = (c1_b, c2_b) = (g^k2 mod p, (m2 * y^k2) mod p)\n\n"
        "Component-wise Multiplication:\n"
        "  c1_prod = (c1_a * c1_b) mod p = (g^k1 * g^k2) mod p = g^(k1 + k2) mod p\n"
        "  c2_prod = (c2_a * c2_b) mod p = ((m1 * y^k1) * (m2 * y^k2)) mod p = ((m1 * m2) * y^(k1 + k2)) mod p\n\n"
        "Decryption using Private Key x:\n"
        "  s_prod = (c1_prod)^x mod p = (g^(k1 + k2))^x mod p = y^(k1 + k2) mod p\n"
        "  s_prod^-1 = mod_inverse(s_prod, p)\n"
        "  m_prod = (c2_prod * s_prod^-1) mod p\n"
        "         = (((m1 * m2) * y^(k1 + k2)) * y^-(k1 + k2)) mod p\n"
        "         = (m1 * m2) mod p.\n\n"
        "Therefore, D(E(m1) * E(m2)) == (m1 * m2) mod p."
    )

    return HomomorphicMultiplicationResult(
        c1_a=c1_a,
        c2_a=c2_a,
        c1_b=c1_b,
        c2_b=c2_b,
        m1=m1,
        m2=m2,
        c1_product=c1_prod,
        c2_product=c2_prod,
        decrypted_product=decrypted_prod,
        expected_product=expected_prod,
        is_homomorphism_verified=is_verified,
        p=p,
        step_trace=step_trace,
        mathematical_proof=mathematical_proof,
    )


# ---------------------------------------------------------------------------
# Cryptanalytic Nonce-Reuse Exploit Engine
# ---------------------------------------------------------------------------


def recover_plaintext_ratio(
    c_a: tuple[int, int] | ElGamalCiphertextBlock,
    c_b: tuple[int, int] | ElGamalCiphertextBlock,
    p: int,
) -> int:
    """Computes the ratio (m1 * m2^-1) mod p from two ciphertexts sharing the same nonce k.

    c2_a * c2_b^-1 = (m1 * s) * (m2 * s)^-1 = m1 * m2^-1 mod p.
    """
    c1_a = c_a.c1 if isinstance(c_a, ElGamalCiphertextBlock) else c_a[0]
    c2_a = c_a.c2 if isinstance(c_a, ElGamalCiphertextBlock) else c_a[1]
    c1_b = c_b.c1 if isinstance(c_b, ElGamalCiphertextBlock) else c_b[0]
    c2_b = c_b.c2 if isinstance(c_b, ElGamalCiphertextBlock) else c_b[1]

    if c1_a != c1_b:
        raise CryptanalysisError(
            f"Nonce reuse attack failed: c1_a ({c1_a}) and c1_b ({c1_b}) do not match. The nonces were distinct."
        )

    inv_b = mod_inverse(c2_b, p)
    if inv_b.inverse is None:
        raise CryptanalysisError(f"Modular inverse of c2_b={c2_b} does not exist mod {p}")
    c2_b_inv = inv_b.inverse
    return (c2_a * c2_b_inv) % p


def exploit_nonce_reuse(
    c_a: tuple[int, int] | ElGamalCiphertextBlock,
    c_b: tuple[int, int] | ElGamalCiphertextBlock,
    known_m1: int,
    p: int,
    actual_m2: int | None = None,
) -> NonceReuseExploitResult:
    """Executes a Known-Plaintext Attack against ElGamal nonce reuse.

    Preconditions:
      - c1_a == c1_b (both ciphertexts were encrypted using the same ephemeral nonce k).
      - known_m1 in [1, p - 1] is known to the attacker.

    Computes:
      c2_a_inv = mod_inverse(c2_a, p)
      recovered_m2 = (known_m1 * c2_b * c2_a_inv) mod p

    Raises:
      CryptanalysisError: if c1_a != c1_b.
    """
    c1_a = c_a.c1 if isinstance(c_a, ElGamalCiphertextBlock) else c_a[0]
    c2_a = c_a.c2 if isinstance(c_a, ElGamalCiphertextBlock) else c_a[1]
    c1_b = c_b.c1 if isinstance(c_b, ElGamalCiphertextBlock) else c_b[0]
    c2_b = c_b.c2 if isinstance(c_b, ElGamalCiphertextBlock) else c_b[1]

    if c1_a != c1_b:
        raise CryptanalysisError(
            f"Nonce reuse attack failed: c1_a ({c1_a}) and c1_b ({c1_b}) do not match. The nonces were distinct."
        )

    if not isinstance(known_m1, int) or not (1 <= known_m1 < p):
        raise CryptanalysisError(
            f"Known plaintext m1={known_m1} must be in range [1, p - 1] ([1, {p - 1}])"
        )

    inv_a = mod_inverse(c2_a, p)
    if inv_a.inverse is None:
        raise CryptanalysisError(f"Modular inverse of c2_a={c2_a} does not exist mod {p}")
    c2_a_inv = inv_a.inverse
    recovered_m2 = (known_m1 * c2_b * c2_a_inv) % p

    inv_b = mod_inverse(c2_b, p)
    if inv_b.inverse is None:
        raise CryptanalysisError(f"Modular inverse of c2_b={c2_b} does not exist mod {p}")
    c2_b_inv = inv_b.inverse
    plaintext_ratio = (c2_a * c2_b_inv) % p

    attack_successful = (actual_m2 is None) or (recovered_m2 == actual_m2)

    steps = [
        f"1. Observed ciphertexts: C_A = ({c1_a}, {c2_a}) and C_B = ({c1_b}, {c2_b}).",
        f"2. Verified identical ephemeral component: c1_a == c1_b == {c1_a}, confirming nonce reuse (k_a == k_b).",
        f"3. Computed modular inverse of c2_a modulo {p}: c2_a^-1 = mod_inverse({c2_a}, {p}) = {c2_a_inv}.",
        f"4. Recovered message m2 = (m1 * c2_b * c2_a^-1) mod p = ({known_m1} * {c2_b} * {c2_a_inv}) mod {p} = {recovered_m2}.",
        f"5. Computed plaintext ratio (m1 * m2^-1) mod p = (c2_a * c2_b^-1) mod p = ({c2_a} * {c2_b_inv}) mod {p} = {plaintext_ratio}.",
    ]
    if actual_m2 is not None:
        steps.append(
            f"6. Verified against actual m2 ({actual_m2}): {'SUCCESS' if recovered_m2 == actual_m2 else 'FAILURE'}."
        )

    explanation = (
        "Cryptanalytic Vulnerability of Ephemeral Nonce Reuse in ElGamal:\n"
        "In ElGamal encryption, if the sender uses the same ephemeral nonce k for two distinct plaintexts m1 and m2, "
        "the ephemeral public key c1 = g^k mod p is identical for both ciphertexts.\n\n"
        "Consequently, the shared secret s = y^k mod p is identical for both encryptions:\n"
        "  c2_a = (m1 * s) mod p\n"
        "  c2_b = (m2 * s) mod p\n\n"
        "Taking their quotient modulo p eliminates the shared secret s entirely:\n"
        "  c2_b * c2_a^-1 = (m2 * s) * (m1 * s)^-1 = m2 * m1^-1 mod p\n\n"
        "If the attacker knows or guesses m1 (Known-Plaintext Attack), they can immediately compute:\n"
        "  m2 = (m1 * c2_b * c2_a^-1) mod p\n\n"
        "This completely breaks semantic security (IND-CPA) without needing the private key x "
        "or solving the Discrete Logarithm Problem."
    )

    return NonceReuseExploitResult(
        c1=c1_a,
        c2_a=c2_a,
        c2_b=c2_b,
        known_m1=known_m1,
        recovered_m2=recovered_m2,
        actual_m2=actual_m2,
        plaintext_ratio=plaintext_ratio,
        attack_successful=attack_successful,
        steps=steps,
        explanation=explanation,
    )
