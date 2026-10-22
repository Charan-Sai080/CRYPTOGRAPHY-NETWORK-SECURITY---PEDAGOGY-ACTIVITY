"""
Core Number Theory & Mathematical Engine.

This module provides high-precision number theory primitives required for:
- One-Time Pad (entropy, bitwise transformations)
- Linear Congruential Generator (GCD, prime factorization, coprimality)
- ElGamal Cryptosystem (safe primes, primitive roots, modular inverse, square-and-multiply)
- Digital Signature Algorithm (subgroup parameters, modular inversion, SHA-256 truncation)

Every primitive provides explicit, structured calculation traces for educational display.
"""

from __future__ import annotations

import hashlib
import math
import secrets
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# 1. Extended Euclidean Algorithm (EEA)
# ---------------------------------------------------------------------------

@dataclass
class EEAStep:
    step: int
    q: int
    r: int
    s: int
    t: int
    equation: str


@dataclass
class EEAResult:
    a: int
    b: int
    gcd: int
    x: int  # Bezout coefficient for a
    y: int  # Bezout coefficient for b
    steps: list[EEAStep] = field(default_factory=list)
    identity_verified: bool = False
    formula: str = ""


def extended_gcd(a: int, b: int) -> EEAResult:
    """Computes the Greatest Common Divisor gcd(a, b) and Bezout coefficients (x, y)

    such that:
        a * x + b * y = gcd(a, b)

    Maintains a full tabular step trace for pedagogy.
    """
    orig_a, orig_b = a, b
    
    # Handle non-negative inputs
    sign_a = -1 if a < 0 else 1
    sign_b = -1 if b < 0 else 1
    a, b = abs(a), abs(b)

    # Initial states
    # r_{k-2}, r_{k-1}
    r_prev, r_curr = a, b
    s_prev, s_curr = 1, 0
    t_prev, t_curr = 0, 1

    steps: list[EEAStep] = []
    
    step_num = 0
    steps.append(EEAStep(
        step=step_num,
        q=0,
        r=r_prev,
        s=s_prev,
        t=t_prev,
        equation=f"{a}*({s_prev}) + {b}*({t_prev}) = {r_prev}"
    ))

    if b != 0:
        step_num += 1
        steps.append(EEAStep(
            step=step_num,
            q=0,
            r=r_curr,
            s=s_curr,
            t=t_curr,
            equation=f"{a}*({s_curr}) + {b}*({t_curr}) = {r_curr}"
        ))

    while r_curr != 0:
        q = r_prev // r_curr
        r_next = r_prev % r_curr
        s_next = s_prev - q * s_curr
        t_next = t_prev - q * t_curr

        r_prev, r_curr = r_curr, r_next
        s_prev, s_curr = s_curr, s_next
        t_prev, t_curr = t_curr, t_next

        step_num += 1
        steps.append(EEAStep(
            step=step_num,
            q=q,
            r=r_prev,
            s=s_prev,
            t=t_prev,
            equation=f"{a}*({s_prev}) + {b}*({t_prev}) = {r_prev}"
        ))

    gcd_val = r_prev
    x = s_prev * sign_a
    y = t_prev * sign_b
    identity_ok = (orig_a * x + orig_b * y == gcd_val)

    return EEAResult(
        a=orig_a,
        b=orig_b,
        gcd=gcd_val,
        x=x,
        y=y,
        steps=steps,
        identity_verified=identity_ok,
        formula=f"{orig_a} * ({x}) + {orig_b} * ({y}) = {gcd_val}"
    )


# ---------------------------------------------------------------------------
# 2. Modular Multiplicative Inverse
# ---------------------------------------------------------------------------

@dataclass
class ModInverseResult:
    a: int
    m: int
    inverse: int | None
    is_coprime: bool
    gcd: int
    eea_result: EEAResult
    explanation: str
    verification: str


def mod_inverse(a: int, m: int) -> ModInverseResult:
    """Calculates the modular multiplicative inverse a^(-1) mod m such that:

        (a * a^(-1)) = 1 (mod m)

    Requires gcd(a, m) == 1. Returns a complete pedagogical trace.
    """
    if m <= 0:
        raise ValueError("Modulus m must be a positive integer greater than 0.")
    
    if m == 1:
        # Modulo 1 ring is degenerate: 1 mod 1 is 0
        eea = extended_gcd(a, m)
        return ModInverseResult(
            a=a,
            m=m,
            inverse=0,
            is_coprime=True,
            gcd=1,
            eea_result=eea,
            explanation="Modulus m=1 is trivial; 0 mod 1 = 0.",
            verification="(a * 0) % 1 == 0"
        )

    # Normalize a mod m
    norm_a = a % m
    eea = extended_gcd(norm_a, m)

    if eea.gcd != 1:
        return ModInverseResult(
            a=a,
            m=m,
            inverse=None,
            is_coprime=False,
            gcd=eea.gcd,
            eea_result=eea,
            explanation=f"Modular inverse does not exist because gcd({a}, {m}) = {eea.gcd} != 1 (they are not coprime).",
            verification="No inverse exists in Z_m."
        )

    # Bezout coefficient x satisfies: norm_a * x + m * y = 1
    # Hence norm_a * x = 1 (mod m)
    inv = eea.x % m
    verify_val = (norm_a * inv) % m
    
    return ModInverseResult(
        a=a,
        m=m,
        inverse=inv,
        is_coprime=True,
        gcd=1,
        eea_result=eea,
        explanation=f"From Extended Euclidean Algorithm: {norm_a}*({eea.x}) + {m}*({eea.y}) = 1. Therefore {a}^(-1) = {inv} mod {m}.",
        verification=f"({a} * {inv}) mod {m} = {verify_val} (Success)"
    )


# ---------------------------------------------------------------------------
# 3. Traced Fast Modular Exponentiation (Square-and-Multiply)
# ---------------------------------------------------------------------------

@dataclass
class ModPowStep:
    step_index: int
    bit_index: int
    bit_value: int
    action: str
    current_acc_before: int
    current_acc_after: int
    formula: str


@dataclass
class ModPowResult:
    base: int
    exponent: int
    modulus: int
    result: int
    binary_exponent: str
    bit_length: int
    steps: list[ModPowStep] = field(default_factory=list)


def mod_pow(base: int, exp: int, mod: int) -> ModPowResult:
    """Computes (base^exp) % mod using the binary Square-and-Multiply algorithm,

    recording an exhaustive pedagogical trace of each bit operation.
    """
    if mod <= 0:
        raise ValueError("Modulus must be positive.")
    if exp < 0:
        raise ValueError("Negative exponents require modular inverse computation; pass non-negative exp.")

    if mod == 1:
        return ModPowResult(
            base=base,
            exponent=exp,
            modulus=mod,
            result=0,
            binary_exponent="0",
            bit_length=1,
            steps=[]
        )

    if exp == 0:
        return ModPowResult(
            base=base,
            exponent=exp,
            modulus=mod,
            result=1 % mod,
            binary_exponent="0",
            bit_length=1,
            steps=[]
        )

    bin_exp = bin(exp)[2:]  # e.g., '1011'
    acc = 1
    steps: list[ModPowStep] = []
    step_idx = 1

    # Traverse bits from MSB (left) to LSB (right)
    for i, bit_char in enumerate(bin_exp):
        bit_val = int(bit_char)
        
        # 1. Square step
        before_sq = acc
        after_sq = (acc * acc) % mod
        acc = after_sq
        steps.append(ModPowStep(
            step_index=step_idx,
            bit_index=i,
            bit_value=bit_val,
            action="Square",
            current_acc_before=before_sq,
            current_acc_after=after_sq,
            formula=f"({before_sq}^2) mod {mod} = {after_sq}"
        ))
        step_idx += 1

        # 2. Multiply step if bit is 1
        if bit_val == 1:
            before_mul = acc
            after_mul = (acc * (base % mod)) % mod
            acc = after_mul
            steps.append(ModPowStep(
                step_index=step_idx,
                bit_index=i,
                bit_value=bit_val,
                action="Multiply (bit=1)",
                current_acc_before=before_mul,
                current_acc_after=after_mul,
                formula=f"({before_mul} * {base % mod}) mod {mod} = {after_mul}"
            ))
            step_idx += 1

    return ModPowResult(
        base=base,
        exponent=exp,
        modulus=mod,
        result=acc,
        binary_exponent=bin_exp,
        bit_length=len(bin_exp),
        steps=steps
    )


# ---------------------------------------------------------------------------
# 4. Miller-Rabin Primality Test
# ---------------------------------------------------------------------------

@dataclass
class MillerRabinRound:
    round_index: int
    base_a: int
    d: int
    s: int
    x_init: int
    passed: bool
    reason: str
    chain: list[int] = field(default_factory=list)


@dataclass
class PrimalityResult:
    n: int
    is_prime: bool
    method: str
    d: int = 0
    s: int = 0
    rounds_executed: int = 0
    rounds: list[MillerRabinRound] = field(default_factory=list)
    confidence: float = 0.0
    summary: str = ""


# Deterministic bases for numbers up to 2^64
DETERMINISTIC_BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def is_prime(n: int, k: int = 40) -> PrimalityResult:
    """Tests if n is prime using the Miller-Rabin probabilistic or deterministic primality test.

    Decomposes n - 1 = 2^s * d where d is odd.
    Returns complete step trace for every witness round.
    """
    if n <= 1:
        return PrimalityResult(
            n=n,
            is_prime=False,
            method="Trivial boundary check",
            summary=f"{n} is not prime by definition (primes are integers >= 2)."
        )
    if n in (2, 3):
        return PrimalityResult(
            n=n,
            is_prime=True,
            method="Trivial boundary check",
            summary=f"{n} is prime."
        )
    if n % 2 == 0:
        return PrimalityResult(
            n=n,
            is_prime=False,
            method="Trivial parity check",
            summary=f"{n} is even and > 2, hence composite (divisible by 2)."
        )

    # Factor out powers of 2 from n - 1: n - 1 = 2^s * d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # Select bases
    if n < 3_825_123_056_546_413_051:
        # Deterministic coverage
        bases = [b for b in DETERMINISTIC_BASES if b < n]
        method_str = "Miller-Rabin (Deterministic)"
    else:
        # Randomized coverage
        bases = []
        for _ in range(k):
            a_cand = secrets.randbelow(n - 3) + 2
            if a_cand not in bases:
                bases.append(a_cand)
        method_str = f"Miller-Rabin ({len(bases)} probabilistic rounds)"

    rounds: list[MillerRabinRound] = []
    all_passed = True

    for idx, a in enumerate(bases, start=1):
        # Compute a^d mod n
        x = pow(a, d, n)
        chain = [x]

        if x == 1 or x == n - 1:
            rounds.append(MillerRabinRound(
                round_index=idx,
                base_a=a,
                d=d,
                s=s,
                x_init=x,
                passed=True,
                reason=f"a^d mod n = {x} (matches 1 or n-1)",
                chain=chain
            ))
            continue

        round_passed = False
        for r_step in range(1, s):
            x = pow(x, 2, n)
            chain.append(x)
            if x == n - 1:
                round_passed = True
                break

        if round_passed:
            rounds.append(MillerRabinRound(
                round_index=idx,
                base_a=a,
                d=d,
                s=s,
                x_init=chain[0],
                passed=True,
                reason=f"Squaring chain reached n - 1: {chain}",
                chain=chain
            ))
        else:
            all_passed = False
            rounds.append(MillerRabinRound(
                round_index=idx,
                base_a=a,
                d=d,
                s=s,
                x_init=chain[0],
                passed=False,
                reason=f"Witness to compositeness! Chain did not reach n-1: {chain}",
                chain=chain
            ))
            break  # Definite composite found

    confidence = 1.0 if (not all_passed or "Deterministic" in method_str) else (1.0 - (0.25 ** len(rounds)))

    return PrimalityResult(
        n=n,
        is_prime=all_passed,
        method=method_str,
        d=d,
        s=s,
        rounds_executed=len(rounds),
        rounds=rounds,
        confidence=confidence,
        summary=(
            f"{n} is confirmed prime with confidence {confidence * 100:.6f}%."
            if all_passed else
            f"{n} is proven composite (witness base {rounds[-1].base_a})."
        )
    )


# ---------------------------------------------------------------------------
# 5. Prime Factorization & Hull-Dobell Helpers
# ---------------------------------------------------------------------------

def distinct_prime_factors(n: int) -> list[int]:
    """Returns the sorted list of distinct prime factors of integer n."""
    factors: list[int] = []
    curr = abs(n)
    if curr <= 1:
        return []

    # Check 2
    if curr % 2 == 0:
        factors.append(2)
        while curr % 2 == 0:
            curr //= 2

    # Check odd divisors up to sqrt(curr)
    d = 3
    while d * d <= curr:
        if curr % d == 0:
            factors.append(d)
            while curr % d == 0:
                curr //= d
        d += 2

    if curr > 1:
        factors.append(curr)

    return factors


# ---------------------------------------------------------------------------
# 6. Primitive Root Generator
# ---------------------------------------------------------------------------

@dataclass
class CandidateTest:
    candidate: int
    is_primitive: bool
    checks: list[dict[str, Any]]


@dataclass
class PrimitiveRootResult:
    p: int
    phi: int
    prime_factors_phi: list[int]
    primitive_root: int | None
    candidates_tested: list[CandidateTest] = field(default_factory=list)
    explanation: str = ""


def find_primitive_root(p: int, max_candidates: int = 50) -> PrimitiveRootResult:
    """Finds a primitive root modulo prime p with complete verification step logs.

    For prime p, the order of Z_p* is phi(p) = p - 1.
    An element g is a primitive root iff for every prime factor q of p - 1:
        g^((p - 1)/q) != 1 (mod p)
    """
    if p <= 1:
        raise ValueError("p must be a prime > 1")

    phi = p - 1
    factors = distinct_prime_factors(phi)

    tested: list[CandidateTest] = []
    found_root: int | None = None

    for g in range(2, min(p, 2 + max_candidates)):
        checks = []
        is_root = True

        for q in factors:
            exp = phi // q
            val = pow(g, exp, p)
            checks.append({
                "factor_q": q,
                "exponent": exp,
                "val": val,
                "passed": (val != 1)
            })
            if val == 1:
                is_root = False
                break

        tested.append(CandidateTest(
            candidate=g,
            is_primitive=is_root,
            checks=checks
        ))

        if is_root:
            found_root = g
            break

    explanation = (
        f"Found primitive root g = {found_root} for prime {p}. For all prime factors of phi(p)={factors}, "
        f"g^((p-1)/q) mod p != 1."
        if found_root is not None else
        f"No primitive root found within first {max_candidates} candidates."
    )

    return PrimitiveRootResult(
        p=p,
        phi=phi,
        prime_factors_phi=factors,
        primitive_root=found_root,
        candidates_tested=tested,
        explanation=explanation
    )


# ---------------------------------------------------------------------------
# 7. Safe Prime Generator
# ---------------------------------------------------------------------------

def generate_safe_prime(bits: int) -> tuple[int, int, list[str]]:
    """Generates a safe prime p = 2q + 1 where both p and q are prime.

    Returns (p, q, trace_logs).
    """
    if bits < 4:
        raise ValueError("Bits must be at least 4.")

    logs = []
    attempts = 0

    while True:
        attempts += 1
        # Generate random odd integer q of length bits - 1
        q_cand = secrets.randbits(bits - 1) | (1 << (bits - 2)) | 1
        if not is_prime(q_cand, k=25).is_prime:
            continue

        p_cand = 2 * q_cand + 1
        if is_prime(p_cand, k=25).is_prime:
            logs.append(f"Generated Sophie Germain prime q = {q_cand} ({bits-1} bits).")
            logs.append(f"Derived safe prime p = 2*{q_cand} + 1 = {p_cand} ({bits} bits).")
            logs.append(f"Total candidate pairs evaluated: {attempts}.")
            return p_cand, q_cand, logs


# ---------------------------------------------------------------------------
# 8. Standard RFC MODP Groups (RFC 3526 / RFC 7919)
# ---------------------------------------------------------------------------

# Pre-verified RFC 2409 1024-bit MODP Group (Oakley Group 2)
RFC_2409_1024_MODP = {
    "name": "RFC 2409 / RFC 3526 1024-bit MODP Group",
    "bits": 1024,
    "generator": 2,
    "prime_hex": (
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
        "FFFFFFFFFFFFFFFF"
    ),
    "prime": int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
        "FFFFFFFFFFFFFFFF",
        16
    )
}

# Pre-verified educational small prime groups for instant visual demonstrations
EDUCATIONAL_MODP_GROUPS = [
    {"name": "Educational 16-bit", "bits": 16, "prime": 65537, "generator": 3},
    {"name": "Educational 20-bit", "bits": 20, "prime": 1048583, "generator": 2},
    {"name": "Educational 24-bit Safe Prime", "bits": 24, "prime": 16777259, "generator": 2},
    {"name": "Educational 32-bit Safe Prime", "bits": 32, "prime": 4294967311, "generator": 3},
]


# ---------------------------------------------------------------------------
# 9. Encoding & Hashing Helpers
# ---------------------------------------------------------------------------

def string_to_int_blocks(text: str, max_prime_bits: int) -> list[int]:
    """Encodes a UTF-8 text string into an array of integers, where each integer value

    is guaranteed to be strictly less than 2^(max_prime_bits - 1).
    This ensures that each block can be directly encrypted under ElGamal modulo p.
    """
    raw_bytes = text.encode("utf-8")
    # Reserve at least 1 byte safety margin so block integer < p
    chunk_size = max(1, (max_prime_bits - 1) // 8)
    
    blocks: list[int] = []
    for i in range(0, len(raw_bytes), chunk_size):
        chunk = raw_bytes[i:i + chunk_size]
        val = int.from_bytes(chunk, byteorder="big")
        blocks.append(val)
    return blocks


def int_blocks_to_string(blocks: list[int], max_prime_bits: int) -> str:
    """Decodes an array of block integers back into a UTF-8 string."""
    chunk_size = max(1, (max_prime_bits - 1) // 8)
    byte_chunks = bytearray()
    
    for val in blocks:
        # Determine exact bytes
        needed_bytes = (val.bit_length() + 7) // 8
        if needed_bytes == 0:
            # Zero block
            b = b"\x00"
        else:
            b = val.to_bytes(needed_bytes, byteorder="big")
        byte_chunks.extend(b)

    return byte_chunks.decode("utf-8", errors="replace")


def sha256_digest_int(message: str | bytes, bit_limit: int | None = None) -> int:
    """Computes SHA-256 of message and returns integer value.

    If bit_limit is specified, truncates to the leftmost bit_limit bits (per FIPS 186-4 DSA).
    """
    if isinstance(message, str):
        raw = message.encode("utf-8")
    else:
        raw = message
    h = hashlib.sha256(raw).digest()
    val = int.from_bytes(h, byteorder="big")
    if bit_limit is not None and bit_limit < 256:
        val >>= (256 - bit_limit)
    return val
