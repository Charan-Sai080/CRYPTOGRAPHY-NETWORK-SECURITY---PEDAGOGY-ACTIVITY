"""Digital Signature Algorithm (DSA) Engine & Ephemeral Nonce-Reuse Exploit.

Pedagogical, cryptographically rigorous pure-Python 3.12+ implementation of:
1. FIPS 186-4 Domain Parameter Management & Key Pair Generation.
2. Traced Subgroup Generator Derivation & Dynamic Domain Generation.
3. Traced Signing Engine with SHA-256 and FIPS 186-4 Resampling.
4. Traced Signature Verification & Interactive Tampering Detection.
5. Ephemeral Nonce k Reuse Cryptanalytic Exploit (Sony PS3 Exploit).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Any

from backend.core.number_theory import (
    is_prime,
    mod_inverse,
    sha256_digest_int,
)


# ---------------------------------------------------------------------------
# Exceptions Hierarchy
# ---------------------------------------------------------------------------


class DSAError(Exception):
    """Base exception for all DSA cryptographic operations."""
    pass


class InvalidDomainParametersError(DSAError):
    """Raised when DSA domain parameters (p, q, g) are mathematically invalid."""
    pass


class DomainParameterError(InvalidDomainParametersError):
    """Alias for InvalidDomainParametersError."""
    pass


class InvalidKeyError(DSAError):
    """Raised when a DSA public or private key is malformed or out of bounds."""
    pass


class KeyValidationError(InvalidKeyError):
    """Alias for InvalidKeyError."""
    pass


class DSASignatureError(DSAError):
    """Raised when signature generation fails or invalid signature inputs are provided."""
    pass


class ResamplingFailureError(DSASignatureError):
    """Raised if maximum resampling attempts are exceeded without generating valid (r, s)."""
    pass


class DSAVerificationError(DSAError):
    """Raised when an unrecoverable error occurs during signature verification."""
    pass


class DSACryptanalysisError(DSAError):
    """Raised when cryptanalytic exploit fails or prerequisites are not met."""
    pass


# ---------------------------------------------------------------------------
# Pedagogical Reference Texts & Proofs
# ---------------------------------------------------------------------------

DSA_MATHEMATICAL_PROOF: str = """
Algebraic Correctness Proof of DSA Signature Verification:

1. Signing Equations:
   During signature generation:
       r = (g^k mod p) mod q
       s = k^(-1) * (z + x * r) mod q

2. Inverting s modulo q:
   Let w = s^(-1) mod q.
   Multiplying both sides by k and w:
       k = w * (z + x * r) mod q
       k = (z * w + x * r * w) mod q

3. Subgroup Projection:
   Define:
       u1 = (z * w) mod q
       u2 = (r * w) mod q
   Then:
       k = (u1 + x * u2) mod q
   Which implies:
       k = u1 + x * u2 + j * q   for some integer j.

4. Exponentiation over Cyclic Subgroup of Order q in Z_p*:
   By construction of DSA domain parameters, g^q = 1 mod p, and y = g^x mod p:
       g^k mod p = g^(u1 + x * u2 + j * q) mod p
                 = (g^u1 * (g^x)^u2 * (g^q)^j) mod p
                 = (g^u1 * y^u2 * (1)^j) mod p
                 = (g^u1 * y^u2) mod p

5. Modulo q Reduction:
   Taking modulo q of both sides:
       v = ((g^u1 * y^u2) mod p) mod q = (g^k mod p) mod q = r.

Therefore, the verification identity v == r holds if and only if the signature (r, s)
was generated with the private key x corresponding to the public key y = g^x mod p
over message digest z.
""".strip()

SONY_PS3_HISTORICAL_CONTEXT: str = """
Historical Context: The 2010 Sony PlayStation 3 Nonce-Reuse Disaster (fail0verflow):

In December 2010 at the 27th Chaos Communication Congress (27C3) in Berlin, the fail0verflow
hacker research collective presented an exploit that completely dismantled the security
architecture of the Sony PlayStation 3 console.

The PlayStation 3 used ECDSA (the elliptic-curve analogue of DSA) to cryptographically sign
executable packages and firmware updates. According to the standard (FIPS 186-4), every single
signature must be generated using a freshly sampled, cryptographically secure random ephemeral
nonce k.

Sony's engineers made the catastrophic error of hardcoding a static, constant value for k
across distinct signing operations. Because k remained identical between signatures of different
payloads (M1, M2):
1. Both signatures produced the exact same ephemeral component r (r1 = r2).
2. Subtracting the two signature equations cancelled out the private key term:
       s1 - s2 = k^(-1) * (z1 - z2) mod q
3. An attacker easily calculated the secret nonce:
       k = (z1 - z2) * (s1 - s2)^(-1) mod q
4. Once k was exposed, the private master code-signing key x was extracted immediately:
       x = (s1 * k - z1) * r^(-1) mod q

With Sony's root private key compromised, attackers could forge valid signatures for any custom
firmware or homebrew application. Sony could not revoke the key without breaking compatibility
with all existing legit game discs and software, permanently defeating the console's security.
""".strip()

DSA_NONCE_REUSE_ALGEBRAIC_PROOF: str = """
Algebraic Derivation of Private Key Recovery via Nonce Reuse:

Given two distinct messages M1 and M2 with truncated integer hashes z1 != z2 mod q,
signed using the same private key x and identical ephemeral nonce k:

1. Signatures Produced:
       (r, s1) where s1 = k^(-1) * (z1 + x * r) mod q
       (r, s2) where s2 = k^(-1) * (z2 + x * r) mod q

2. Difference of Signatures:
       s1 - s2 = k^(-1) * (z1 + x * r) - k^(-1) * (z2 + x * r) (mod q)
       s1 - s2 = k^(-1) * ((z1 + x * r) - (z2 + x * r)) (mod q)
       s1 - s2 = k^(-1) * (z1 - z2) (mod q)

3. Ephemeral Nonce k Recovery:
       k * (s1 - s2) = (z1 - z2) (mod q)
       k = (z1 - z2) * (s1 - s2)^(-1) (mod q)

4. Private Key x Extraction:
   Using either signature equation (e.g., s1):
       s1 * k = z1 + x * r (mod q)
       x * r = s1 * k - z1 (mod q)
       x = (s1 * k - z1) * r^(-1) (mod q)

5. Verification:
       Compute y_derived = g^x mod p and verify y_derived == y_public.
""".strip()


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DSADomainParams:
    """Represents public DSA cyclic subgroup domain parameters (p, q, g)."""
    p: int                          # Prime modulus p
    q: int                          # Prime subprime divisor q (order of subgroup)
    g: int                          # Generator g of order q in Z_p*
    name: str = "Custom Domain"     # Descriptive identifier
    p_bits: int = field(init=False) # Bit length of p
    q_bits: int = field(init=False) # Bit length of q

    def __post_init__(self) -> None:
        if not isinstance(self.p, int) or self.p <= 2:
            raise InvalidDomainParametersError(f"Modulus p must be an integer > 2, got {self.p}")
        if not is_prime(self.p).is_prime:
            raise InvalidDomainParametersError(f"Modulus p must be a prime number, got {self.p}")
        if not isinstance(self.q, int) or self.q <= 1:
            raise InvalidDomainParametersError(f"Subgroup divisor q must be an integer > 1, got {self.q}")
        if not is_prime(self.q).is_prime:
            raise InvalidDomainParametersError(f"Subgroup divisor q must be a prime number, got {self.q}")
        if (self.p - 1) % self.q != 0:
            raise InvalidDomainParametersError(f"Subgroup order q ({self.q}) must divide p - 1 ({self.p - 1})")
        if not isinstance(self.g, int) or not (1 < self.g < self.p):
            raise InvalidDomainParametersError(
                f"Generator g must be in range [2, p - 1] ([2, {self.p - 1}]), got {self.g}"
            )
        if pow(self.g, self.q, self.p) != 1:
            raise InvalidDomainParametersError(
                f"Generator g of order q must satisfy g^q mod p == 1, got {pow(self.g, self.q, self.p)}"
            )
        object.__setattr__(self, "p_bits", self.p.bit_length())
        object.__setattr__(self, "q_bits", self.q.bit_length())


@dataclass(frozen=True)
class DSAPublicKey:
    """DSA public key component (p, q, g, y)."""
    p: int
    q: int
    g: int
    y: int                          # y = g^x mod p

    def __post_init__(self) -> None:
        if not (1 < self.y < self.p):
            raise InvalidKeyError(f"Public key y must satisfy 1 < y < p, got {self.y}")


@dataclass(frozen=True)
class DSAPrivateKey:
    """DSA private key component (p, q, g, x)."""
    p: int
    q: int
    g: int
    x: int                          # x in [1, q - 1]

    def __post_init__(self) -> None:
        if not (1 <= self.x < self.q):
            raise InvalidKeyError(f"Private key x must satisfy 1 <= x < q, got {self.x}")


@dataclass(frozen=True)
class DSAKeyPair:
    """Encapsulates a matched DSA keypair with domain metadata."""
    public_key: DSAPublicKey
    private_key: DSAPrivateKey
    domain_params: DSADomainParams


@dataclass(frozen=True)
class DSASignature:
    """Represents a DSA digital signature pair (r, s)."""
    r: int                          # r = (g^k mod p) mod q
    s: int                          # s = k^-1 * (z + x * r) mod q
    q: int                          # Subgroup modulus q for boundary validation

    def __post_init__(self) -> None:
        if not (0 < self.r < self.q):
            raise DSASignatureError(f"Signature component r must satisfy 0 < r < q, got {self.r}")
        if not (0 < self.s < self.q):
            raise DSASignatureError(f"Signature component s must satisfy 0 < s < q, got {self.s}")


@dataclass(frozen=True)
class DSASignTrace:
    """Exhaustive step-by-step arithmetic trace for a DSA signing operation."""
    message: str | bytes
    message_hash_hex: str           # Full SHA-256 hex digest
    z: int                          # Truncated integer hash value
    k: int                          # Ephemeral nonce k in [1, q - 1]
    k_inv: int                      # k^-1 mod q
    gk_mod_p: int                   # g^k mod p
    r: int                          # (g^k mod p) mod q
    xr_mod_q: int                   # (x * r) mod q
    z_plus_xr: int                  # (z + x * r)
    s: int                          # (k_inv * (z + x * r)) mod q
    r_formula: str                  # e.g., "r = (g^k mod p) mod q = (64^29 mod 607) mod 101 = 81"
    s_formula: str                  # e.g., "s = (k^-1 * (z + x * r)) mod q = (7^1 * (12 + 42 * 81)) mod 101 = 65"
    attempts: int                   # Number of resampling attempts required
    domain_name: str                # Domain preset name


@dataclass(frozen=True)
class DSASignResult:
    """Encapsulates the signature and its educational arithmetic trace."""
    signature: DSASignature
    trace: DSASignTrace


@dataclass(frozen=True)
class DSAVerifyTrace:
    """Detailed step-by-step arithmetic trace for a DSA verification operation."""
    message: str | bytes
    z: int                          # Truncated hash integer
    r: int                          # Signature r
    s: int                          # Signature s
    w: int                          # w = s^-1 mod q
    u1: int                         # u1 = (z * w) mod q
    u2: int                         # u2 = (r * w) mod q
    gu1_mod_p: int                  # g^u1 mod p
    yu2_mod_p: int                  # y^u2 mod p
    v: int                          # v = ((g^u1 * y^u2) mod p) mod q
    is_valid: bool                  # True iff v == r
    w_formula: str                  # Step formula string
    u1_formula: str                 # Step formula string
    u2_formula: str                 # Step formula string
    v_formula: str                  # Step formula string
    verification_formula: str       # Comparison formula string
    mathematical_proof: str = ""    # LaTeX/algebraic proof that g^u1 * y^u2 == g^k mod p


@dataclass(frozen=True)
class DSAVerificationResult:
    """High-level verification result encapsulating boolean status and trace."""
    is_valid: bool
    reason: str
    trace: DSAVerifyTrace | None = None


@dataclass(frozen=True)
class TamperDetectionResult:
    """Comparative report demonstrating tampering detection."""
    tamper_type: str                # "message_bit_flip", "signature_r_alter", "signature_s_alter"
    original_valid: bool
    tampered_valid: bool
    detected: bool                  # True if tampered signature was successfully rejected
    original_value: Any
    tampered_value: Any
    original_v: int | None
    tampered_v: int | None
    explanation: str


@dataclass(frozen=True)
class DSANonceReuseExploitResult:
    """Comprehensive diagnostic record of private key recovery via nonce reuse."""
    m1: str | bytes
    m2: str | bytes
    z1: int                          # Truncated hash integer for message 1
    z2: int                          # Truncated hash integer for message 2
    shared_r: int                    # Shared r = r1 == r2
    s1: int                          # Signature component s1
    s2: int                          # Signature component s2
    recovered_k: int                 # Recovered ephemeral nonce k
    recovered_x: int                 # Extracted private key x
    is_key_recovered: bool           # True if algebraic derivation succeeded
    public_key_verified: bool        # True if g^x mod p == public_key.y
    step_trace: list[str] = field(default_factory=list)
    algebraic_proof: str = ""
    historical_context: str = ""


# ---------------------------------------------------------------------------
# Pre-Verified Domain Presets
# ---------------------------------------------------------------------------

FIPS_186_4_1024_160_MODULUS = int(
    "A8F9CD201E5E35D892F85F80E4DB2599A5676A3B1D4F190330ED3256B26D0E80"
    "A0E49A8FFFAAAD2A24F472D2573241D4D6D6C7480C80B4C67BB4479C15ADA7EA"
    "8424D2502FA01472E760241713DAB025AE1B02E1703A1435F62DDF4EE4C1B664"
    "066EB22F2E3BF28BB70A2A76E4FD5EBE2D1229681B5B06439AC9C7E9D8BDE283",
    16,
)
FIPS_186_4_1024_160_DIVISOR = int("F85F0F83AC4DF7EA0CDF8F469BFEEAEA14156495", 16)
FIPS_186_4_1024_160_GENERATOR = int(
    "2B3152FF6C62F14622B8F48E59F8AF46883B38E79B8C74DEEAE9DF131F8B856E"
    "3AD6C8455DAB87CC0DA8AC973417CE4F7878557D6CDF40B35B4A0CA3EB310C6A"
    "95D68CE284AD4E25EA28591611EE08B8444BD64B25F3F7C572410DDFB39CC728"
    "B9C936F85F419129869929CDB909A6A3A99BBE089216368171BD0BA81DE4FE33",
    16,
)

DSA_PRESETS: dict[str, DSADomainParams] = {
    "fips_186_4_1024_160": DSADomainParams(
        p=FIPS_186_4_1024_160_MODULUS,
        q=FIPS_186_4_1024_160_DIVISOR,
        g=FIPS_186_4_1024_160_GENERATOR,
        name="FIPS 186-4 Standard 1024/160-bit (NIST CAVP)",
    ),
    "educational_10": DSADomainParams(
        p=607,
        q=101,
        g=64,
        name="Educational 10-bit Group (p=607, q=101, g=64)",
    ),
    "educational_16": DSADomainParams(
        p=34439,
        q=257,
        g=31028,
        name="Educational 16-bit Group (p=34439, q=257, g=31028)",
    ),
    "educational_24": DSADomainParams(
        p=9044107,
        q=65537,
        g=5759125,
        name="Educational 24-bit Group (p=9044107, q=65537, g=5759125)",
    ),
}


# ---------------------------------------------------------------------------
# Domain Parameter & Key Pair Generation Engine
# ---------------------------------------------------------------------------


def derive_generator(p: int, q: int, h: int) -> int:
    """Derives a subgroup generator g = h^((p - 1)/q) mod p of order q in Z_p*."""
    if not isinstance(p, int) or p <= 2:
        raise InvalidDomainParametersError(f"Modulus p must be an integer > 2, got {p}")
    if not isinstance(q, int) or q <= 1:
        raise InvalidDomainParametersError(f"Subgroup divisor q must be an integer > 1, got {q}")
    if (p - 1) % q != 0:
        raise InvalidDomainParametersError(f"q ({q}) must divide p - 1 ({p - 1})")
    if not isinstance(h, int) or not (1 < h < p - 1):
        raise InvalidDomainParametersError(f"Base h must satisfy 1 < h < p - 1, got {h}")

    exp = (p - 1) // q
    g = pow(h, exp, p)
    if g <= 1:
        raise InvalidDomainParametersError(
            f"Derived generator g = {g} must be > 1. Choose a different base h."
        )
    return g


def verify_domain_params(domain: DSADomainParams) -> bool:
    """Verifies that p and q are prime, q | (p - 1), 1 < g < p, and g^q mod p == 1."""
    try:
        if not isinstance(domain.p, int) or domain.p <= 2:
            return False
        if not isinstance(domain.q, int) or domain.q <= 1:
            return False
        if (domain.p - 1) % domain.q != 0:
            return False
        if not (1 < domain.g < domain.p):
            return False
        if pow(domain.g, domain.q, domain.p) != 1:
            return False
        if not is_prime(domain.q).is_prime:
            return False
        if not is_prime(domain.p).is_prime:
            return False
        return True
    except Exception:
        return False


def generate_dsa_domain(p_bits: int = 16, q_bits: int = 8) -> tuple[DSADomainParams, list[str]]:
    """Generates dynamic educational DSA domain parameters (p, q, g) with pedagogical logs."""
    if q_bits >= p_bits:
        raise InvalidDomainParametersError(
            f"Modulus bit length p_bits ({p_bits}) must be strictly greater than subgroup bit length q_bits ({q_bits})"
        )
    if q_bits < 3 or p_bits < 4:
        raise InvalidDomainParametersError("Minimum supported bit lengths: p_bits >= 4, q_bits >= 3")

    logs: list[str] = []

    while True:
        # Generate random odd integer q of q_bits length
        q_cand = secrets.randbits(q_bits) | (1 << (q_bits - 1)) | 1
        if not is_prime(q_cand, k=25).is_prime:
            continue

        q = q_cand
        logs.append(f"Found prime subgroup order q = {q} ({q_bits} bits)")

        # Target range for p = k * q + 1
        min_p = 1 << (p_bits - 1)
        max_p = (1 << p_bits) - 1

        k_min = (min_p - 1 + q - 1) // q
        k_max = (max_p - 1) // q

        if k_min % 2 != 0:
            k_min += 1
        if k_max % 2 != 0:
            k_max -= 1

        if k_min > k_max:
            continue

        num_steps = (k_max - k_min) // 2 + 1
        found_p = False

        for _ in range(min(num_steps * 2, 500)):
            step_offset = secrets.randbelow(num_steps)
            k = k_min + 2 * step_offset
            p_cand = k * q + 1
            if min_p <= p_cand <= max_p and is_prime(p_cand, k=25).is_prime:
                p = p_cand
                logs.append(f"Derived prime modulus p = {p} ({p_bits} bits) with multiplier k = {k}")
                found_p = True
                break

        if not found_p:
            continue

        # Find generator g
        exp = (p - 1) // q
        g = None
        for h in range(2, p - 1):
            g_cand = pow(h, exp, p)
            if g_cand > 1:
                g = g_cand
                logs.append(f"Derived subgroup generator g = {g} using base h = {h}")
                logs.append(f"Verified g^q mod p = {pow(g, q, p)} == 1")
                break

        if g is not None:
            domain = DSADomainParams(
                p=p,
                q=q,
                g=g,
                name=f"Dynamic DSA Domain ({p_bits}/{q_bits}-bit)",
            )
            return domain, logs


def generate_key_pair(domain: DSADomainParams, seed_x: int | None = None) -> DSAKeyPair:
    """Generates a DSA key pair (public_key, private_key) using CSPRNG or deterministic seed."""
    if seed_x is not None:
        x = seed_x
    else:
        x = secrets.randbelow(domain.q - 1) + 1

    if not (1 <= x < domain.q):
        raise InvalidKeyError(f"Private key x must satisfy 1 <= x < q ({domain.q}), got {x}")

    y = pow(domain.g, x, domain.p)
    if not (1 < y < domain.p):
        raise InvalidKeyError(f"Public key y must satisfy 1 < y < p ({domain.p}), got {y}")

    pub = DSAPublicKey(p=domain.p, q=domain.q, g=domain.g, y=y)
    priv = DSAPrivateKey(p=domain.p, q=domain.q, g=domain.g, x=x)
    return DSAKeyPair(public_key=pub, private_key=priv, domain_params=domain)


def verify_key_pair(key_pair: DSAKeyPair) -> bool:
    """Verifies that private key x in [1, q - 1] and public key y == g^x mod p."""
    pub = key_pair.public_key
    priv = key_pair.private_key
    dom = key_pair.domain_params

    if not (pub.p == priv.p == dom.p):
        return False
    if not (pub.q == priv.q == dom.q):
        return False
    if not (pub.g == priv.g == dom.g):
        return False
    if not (1 <= priv.x < dom.q):
        return False
    if not (1 < pub.y < dom.p):
        return False
    return pow(pub.g, priv.x, pub.p) == pub.y


def get_dsa_preset(name: str) -> DSADomainParams:
    """Retrieves a pre-verified DSA domain preset by name."""
    if name not in DSA_PRESETS:
        raise KeyError(f"Unknown DSA preset '{name}'. Available presets: {list(DSA_PRESETS.keys())}")
    return DSA_PRESETS[name]


def list_dsa_presets() -> list[DSADomainParams]:
    """Lists all available pre-verified DSA domain presets."""
    return list(DSA_PRESETS.values())


# Aliases
generate_dsa_key_pair = generate_key_pair
verify_dsa_key_pair = verify_key_pair


# ---------------------------------------------------------------------------
# Traced Signing Engine
# ---------------------------------------------------------------------------


def generate_ephemeral_k(q: int, seed_k: int | None = None) -> int:
    """Generates an ephemeral secret nonce k in [1, q - 1] uniformly via CSPRNG or seed."""
    if seed_k is not None:
        k = seed_k
    else:
        k = secrets.randbelow(q - 1) + 1

    if not (1 <= k < q):
        raise DSASignatureError(f"Ephemeral nonce k must satisfy 1 <= k < q ({q}), got {k}")
    return k


def sign_hash_int(
    z: int,
    private_key: DSAPrivateKey,
    seed_k: int | None = None,
    max_attempts: int = 100,
    message_repr: str | bytes = "<hash-input>",
    domain_name: str = "Custom Domain",
    message_hash_hex: str = "",
) -> DSASignResult:
    """Signs a pre-hashed/truncated integer digest z with FIPS 186-4 resampling."""
    p = private_key.p
    q = private_key.q
    g = private_key.g
    x = private_key.x

    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        if attempts == 1 and seed_k is not None:
            k = seed_k
            if not (1 <= k < q):
                raise DSASignatureError(f"seed_k must satisfy 1 <= k < q, got {k}")
        else:
            k = generate_ephemeral_k(q)

        # 1. Ephemeral component r = (g^k mod p) mod q
        gk_mod_p = pow(g, k, p)
        r = gk_mod_p % q
        if r == 0:
            continue

        # 2. Invert k mod q
        inv_res = mod_inverse(k, q)
        if inv_res.inverse is None:
            continue
        k_inv = inv_res.inverse

        # 3. Signature component s = k^-1 * (z + x * r) mod q
        xr_mod_q = (x * r) % q
        z_plus_xr = z + x * r
        s = (k_inv * z_plus_xr) % q
        if s == 0:
            continue

        # Formulas for pedagogical display
        r_formula = f"r = (g^k mod p) mod q = ({g}^{k} mod {p}) mod {q} = {gk_mod_p} mod {q} = {r}"
        s_formula = f"s = (k^-1 * (z + x * r)) mod q = ({k_inv} * ({z} + {x} * {r})) mod {q} = {s}"

        signature = DSASignature(r=r, s=s, q=q)
        trace = DSASignTrace(
            message=message_repr,
            message_hash_hex=message_hash_hex or hex(z),
            z=z,
            k=k,
            k_inv=k_inv,
            gk_mod_p=gk_mod_p,
            r=r,
            xr_mod_q=xr_mod_q,
            z_plus_xr=z_plus_xr,
            s=s,
            r_formula=r_formula,
            s_formula=s_formula,
            attempts=attempts,
            domain_name=domain_name,
        )
        return DSASignResult(signature=signature, trace=trace)

    raise ResamplingFailureError(
        f"Exceeded maximum resampling attempts ({max_attempts}) without generating non-zero (r, s)"
    )


def sign_message(
    message: str | bytes,
    private_key: DSAPrivateKey,
    seed_k: int | None = None,
    max_attempts: int = 100,
    domain_name: str = "Custom Domain",
) -> DSASignResult:
    """Computes SHA-256, truncates to bit_length(q), and generates DSA signature (r, s)."""
    raw = message.encode("utf-8") if isinstance(message, str) else message
    full_hash_hex = hashlib.sha256(raw).hexdigest()
    q_bits = private_key.q.bit_length()
    z = sha256_digest_int(message, bit_limit=q_bits)

    return sign_hash_int(
        z=z,
        private_key=private_key,
        seed_k=seed_k,
        max_attempts=max_attempts,
        message_repr=message,
        domain_name=domain_name,
        message_hash_hex=full_hash_hex,
    )


# ---------------------------------------------------------------------------
# Traced Verification Engine & Interactive Tampering Detection
# ---------------------------------------------------------------------------


def verify_hash_int(
    z: int,
    signature: DSASignature,
    public_key: DSAPublicKey,
    message_repr: str | bytes = "<hash-input>",
) -> DSAVerificationResult:
    """Verifies a signature against a truncated hash digest integer z."""
    p = public_key.p
    q = public_key.q
    g = public_key.g
    y = public_key.y
    r = signature.r
    s = signature.s

    # Boundary check
    if not (0 < r < q) or not (0 < s < q):
        return DSAVerificationResult(
            is_valid=False,
            reason=f"Signature components out of bounds: 0 < r < q and 0 < s < q required (got r={r}, s={s}, q={q}).",
            trace=None,
        )

    # Invert s modulo q: w = s^-1 mod q
    inv_s_res = mod_inverse(s, q)
    if inv_s_res.inverse is None:
        return DSAVerificationResult(
            is_valid=False,
            reason=f"Signature component s has no modular inverse modulo q: {inv_s_res.explanation}",
            trace=None,
        )
    w = inv_s_res.inverse

    # Subgroup projections
    u1 = (z * w) % q
    u2 = (r * w) % q

    # Verification point
    gu1_mod_p = pow(g, u1, p)
    yu2_mod_p = pow(y, u2, p)
    v = ((gu1_mod_p * yu2_mod_p) % p) % q

    is_valid = (v == r)

    w_formula = f"w = s^-1 mod q = {s}^-1 mod {q} = {w}"
    u1_formula = f"u1 = (z * w) mod q = ({z} * {w}) mod {q} = {u1}"
    u2_formula = f"u2 = (r * w) mod q = ({r} * {w}) mod {q} = {u2}"
    v_formula = (
        f"v = ((g^u1 * y^u2) mod p) mod q = "
        f"(({g}^{u1} * {y}^{u2}) mod {p}) mod {q} = "
        f"(({gu1_mod_p} * {yu2_mod_p}) mod {p}) mod {q} = {v}"
    )
    verification_formula = f"v == r: {v} == {r} ({'Valid' if is_valid else 'Invalid: signature rejected'})"

    trace = DSAVerifyTrace(
        message=message_repr,
        z=z,
        r=r,
        s=s,
        w=w,
        u1=u1,
        u2=u2,
        gu1_mod_p=gu1_mod_p,
        yu2_mod_p=yu2_mod_p,
        v=v,
        is_valid=is_valid,
        w_formula=w_formula,
        u1_formula=u1_formula,
        u2_formula=u2_formula,
        v_formula=v_formula,
        verification_formula=verification_formula,
        mathematical_proof=DSA_MATHEMATICAL_PROOF,
    )

    return DSAVerificationResult(
        is_valid=is_valid,
        reason="Signature verified successfully." if is_valid else f"Verification failed: v ({v}) != r ({r}).",
        trace=trace,
    )


def verify_message(
    message: str | bytes,
    signature: DSASignature,
    public_key: DSAPublicKey,
) -> DSAVerificationResult:
    """Computes SHA-256(message), truncates to bit_length(q), and verifies signature."""
    z = sha256_digest_int(message, bit_limit=public_key.q.bit_length())
    return verify_hash_int(z, signature, public_key, message_repr=message)


def tamper_message_bit(message: str, bit_index: int = 0) -> str:
    """Flips exactly 1 bit in a UTF-8 message string for educational demonstration."""
    if not message:
        raise ValueError("Cannot tamper with an empty message string.")

    chars = list(message)
    char_idx = (bit_index // 7) % len(chars)
    bit_pos = bit_index % 7
    code = ord(chars[char_idx])
    new_code = code ^ (1 << bit_pos)

    # Avoid lone surrogate code point range (0xD800 - 0xDFFF)
    if 0xD800 <= new_code <= 0xDFFF:
        new_code ^= (1 << 13)

    chars[char_idx] = chr(new_code)
    return "".join(chars)


def tamper_signature_component(
    signature: DSASignature,
    component: str = "r",
    delta: int = 1,
) -> tuple[int, int]:
    """Mutates signature component r or s by adding delta."""
    if component.lower() == "r":
        new_r = (signature.r + delta) % signature.q
        if new_r == 0:
            new_r = 1
        return (new_r, signature.s)
    elif component.lower() == "s":
        new_s = (signature.s + delta) % signature.q
        if new_s == 0:
            new_s = 1
        return (signature.r, new_s)
    else:
        raise ValueError(f"Invalid signature component '{component}', must be 'r' or 's'")


def detect_tampering(
    message: str | bytes,
    signature: DSASignature,
    public_key: DSAPublicKey,
    tamper_type: str = "message_bit_flip",
) -> TamperDetectionResult:
    """Runs original and tampered verifications side-by-side to demonstrate failure."""
    orig_res = verify_message(message, signature, public_key)
    orig_valid = orig_res.is_valid
    orig_v = orig_res.trace.v if orig_res.trace else None

    if tamper_type == "message_bit_flip":
        msg_str = message if isinstance(message, str) else message.decode("utf-8", errors="surrogateescape")
        tampered_msg = tamper_message_bit(msg_str, bit_index=0)
        tamp_res = verify_message(tampered_msg, signature, public_key)
        orig_val = message
        tamp_val = tampered_msg
        tampered_v = tamp_res.trace.v if tamp_res.trace else None
        explanation = (
            f"Single-bit message corruption: Flipping bit 0 changed the message from '{orig_val}' to '{tamp_val}', "
            f"which altered the SHA-256 digest z. This mutated exponent u1 = (z * w) mod q, causing the "
            f"verification point v to evaluate to {tampered_v} != r ({signature.r})."
        )
    elif tamper_type == "signature_r_alter":
        tamp_r, tamp_s = tamper_signature_component(signature, component="r", delta=1)
        orig_val = signature.r
        tamp_val = tamp_r
        try:
            tamp_sig = DSASignature(r=tamp_r, s=tamp_s, q=signature.q)
            tamp_res = verify_message(message, tamp_sig, public_key)
            tampered_v = tamp_res.trace.v if tamp_res.trace else None
        except DSASignatureError:
            tamp_res = DSAVerificationResult(is_valid=False, reason="Tampered r is out of bounds", trace=None)
            tampered_v = None

        explanation = (
            f"Signature component r altered from {signature.r} to {tamp_r}. "
            f"This altered subgroup exponent u2 = (r * w) mod q and disrupted the equality "
            f"identity v == r (computed v = {tampered_v} != tampered r = {tamp_r})."
        )
    elif tamper_type == "signature_s_alter":
        tamp_r, tamp_s = tamper_signature_component(signature, component="s", delta=1)
        orig_val = signature.s
        tamp_val = tamp_s
        try:
            tamp_sig = DSASignature(r=tamp_r, s=tamp_s, q=signature.q)
            tamp_res = verify_message(message, tamp_sig, public_key)
            tampered_v = tamp_res.trace.v if tamp_res.trace else None
        except DSASignatureError:
            tamp_res = DSAVerificationResult(is_valid=False, reason="Tampered s is out of bounds", trace=None)
            tampered_v = None

        explanation = (
            f"Signature component s altered from {signature.s} to {tamp_s}. "
            f"This changed inverse w = s^-1 mod q, corrupting both exponents u1 and u2. "
            f"The resulting verification point v was {tampered_v} != r ({signature.r})."
        )
    else:
        raise ValueError(
            f"Unknown tamper_type '{tamper_type}'. Must be 'message_bit_flip', "
            f"'signature_r_alter', or 'signature_s_alter'."
        )

    detected = orig_valid and not tamp_res.is_valid
    return TamperDetectionResult(
        tamper_type=tamper_type,
        original_valid=orig_valid,
        tampered_valid=tamp_res.is_valid,
        detected=detected,
        original_value=orig_val,
        tampered_value=tamp_val,
        original_v=orig_v,
        tampered_v=tampered_v,
        explanation=explanation,
    )


# ---------------------------------------------------------------------------
# Ephemeral Nonce k Reuse Exploit (Sony PS3 Exploit)
# ---------------------------------------------------------------------------


def exploit_nonce_reuse_from_hashes(
    sig1: DSASignature,
    sig2: DSASignature,
    z1: int,
    z2: int,
    public_key: DSAPublicKey,
    m1_repr: str | bytes = "<hash-1>",
    m2_repr: str | bytes = "<hash-2>",
) -> DSANonceReuseExploitResult:
    """Recovers private key x from two signatures generated with identical nonce k."""
    q = public_key.q
    p = public_key.p
    g = public_key.g

    # 1. Validation checks
    if sig1.r != sig2.r:
        raise DSACryptanalysisError(
            f"Signatures do not share the same ephemeral component r (sig1.r={sig1.r}, sig2.r={sig2.r}). "
            f"Nonce reuse exploit requires r1 == r2."
        )

    if (z1 - z2) % q == 0:
        raise DSACryptanalysisError(
            f"Message digests are identical modulo q (z1 = {z1}, z2 = {z2}). "
            f"Difference z1 - z2 is 0 mod q, preventing linear nonce recovery."
        )

    if (sig1.s - sig2.s) % q == 0:
        raise DSACryptanalysisError(
            f"Signature components s1 and s2 are identical modulo q (s1={sig1.s}, s2={sig2.s}). "
            f"Cannot invert s1 - s2 mod q."
        )

    step_trace: list[str] = []
    shared_r = sig1.r
    step_trace.append(f"Confirmed identical ephemeral signature component r = {shared_r}.")

    # 2. Recover ephemeral secret k: k = (z1 - z2) * (s1 - s2)^(-1) mod q
    s_diff = (sig1.s - sig2.s) % q
    inv_s_res = mod_inverse(s_diff, q)
    if inv_s_res.inverse is None:
        raise DSACryptanalysisError(
            f"s1 - s2 ({s_diff}) is not invertible modulo q ({q}): {inv_s_res.explanation}"
        )
    s_diff_inv = inv_s_res.inverse

    z_diff = (z1 - z2) % q
    recovered_k = (z_diff * s_diff_inv) % q
    step_trace.append(
        f"Derived ephemeral nonce k = (z1 - z2) * (s1 - s2)^-1 mod q = "
        f"({z_diff} * {s_diff_inv}) mod {q} = {recovered_k}."
    )

    # 3. Recover private key x: x = (s1 * k - z1) * r^(-1) mod q
    inv_r_res = mod_inverse(shared_r, q)
    if inv_r_res.inverse is None:
        raise DSACryptanalysisError(
            f"Shared r ({shared_r}) is not invertible modulo q ({q}): {inv_r_res.explanation}"
        )
    r_inv = inv_r_res.inverse

    recovered_x = ((sig1.s * recovered_k - z1) * r_inv) % q
    step_trace.append(
        f"Derived private key x = (s1 * k - z1) * r^-1 mod q = "
        f"(({sig1.s} * {recovered_k} - {z1}) * {r_inv}) mod {q} = {recovered_x}."
    )

    # 4. Verify recovered key matches public key
    y_recovered = pow(g, recovered_x, p)
    public_key_verified = (y_recovered == public_key.y)
    step_trace.append(
        f"Verification against public key: g^x mod p = {g}^{recovered_x} mod {p} = {y_recovered} "
        f"({'MATCHES public key y' if public_key_verified else 'MISMATCH with public key y'})."
    )

    if not public_key_verified:
        raise DSACryptanalysisError(
            f"Recovered private key x={recovered_x} produced public key y={y_recovered}, "
            f"which does not match expected public key y={public_key.y}."
        )

    return DSANonceReuseExploitResult(
        m1=m1_repr,
        m2=m2_repr,
        z1=z1,
        z2=z2,
        shared_r=shared_r,
        s1=sig1.s,
        s2=sig2.s,
        recovered_k=recovered_k,
        recovered_x=recovered_x,
        is_key_recovered=True,
        public_key_verified=public_key_verified,
        step_trace=step_trace,
        algebraic_proof=DSA_NONCE_REUSE_ALGEBRAIC_PROOF,
        historical_context=SONY_PS3_HISTORICAL_CONTEXT,
    )


def exploit_nonce_reuse(
    sig1: DSASignature,
    sig2: DSASignature,
    m1: str | bytes,
    m2: str | bytes,
    public_key: DSAPublicKey,
) -> DSANonceReuseExploitResult:
    """Hashes messages m1 and m2, extracts nonce k, and instantly recovers private key x."""
    q_bits = public_key.q.bit_length()
    z1 = sha256_digest_int(m1, bit_limit=q_bits)
    z2 = sha256_digest_int(m2, bit_limit=q_bits)

    return exploit_nonce_reuse_from_hashes(
        sig1=sig1,
        sig2=sig2,
        z1=z1,
        z2=z2,
        public_key=public_key,
        m1_repr=m1,
        m2_repr=m2,
    )


# Alias
dsa_exploit_nonce_reuse = exploit_nonce_reuse
