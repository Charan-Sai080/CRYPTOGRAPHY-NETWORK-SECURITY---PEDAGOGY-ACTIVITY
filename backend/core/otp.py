"""
One-Time Pad (OTP) Engine & Two-Time Pad Cryptanalysis.

This module provides:
1. Core One-Time Pad symmetric encryption/decryption with full bitwise/byte-wise
   pedagogical execution traces and truth tables.
2. Empirical Shannon Entropy analysis (H(X) = -sum(P(x) * log2(P(x)))) over byte frequencies.
3. Shannon's Perfect Secrecy theorem educational explanations.
4. Two-Time Pad (key-reuse) vulnerability analysis demonstrating key cancellation:
   C1 ^ C2 = (M1 ^ K) ^ (M2 ^ K) = M1 ^ M2.
5. English readability scoring heuristic and interactive/automated crib-dragging cryptanalysis.
"""

from __future__ import annotations

import base64
import collections
import math
import secrets
import string
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Default English Crib Dictionary for Cryptanalysis
# ---------------------------------------------------------------------------

DEFAULT_CRIB_DICTIONARY: list[str] = [
    # Most common English words & phrases with spaces
    " the ", " that ", " with ", " have ", " this ", " from ", " they ", " will ",
    " would ", " there ", " their ", " what ", " about ", " which ", " when ",
    " make ", " can ", " time ", " just ", " know ", " take ", " people ", " into ",
    " year ", " your ", " good ", " some ", " could ", " them ", " other ", " than ",
    " then ", " now ", " look ", " only ", " come ", " its ", " over ", " think ",
    " also ", " back ", " after ", " use ", " two ", " how ", " our ", " work ",
    " first ", " well ", " way ", " even ", " new ", " want ", " because ", " any ",
    " these ", " give ", " day ", " most ", " us ",
    # High-frequency words without surrounding spaces
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can", "had", "her",
    "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new",
    "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put", "say",
    "she", "too", "use",
    # Domain & pedagogy specific cribs
    "secret", "attack", "hello", "password", "confidential", "message", "transfer",
    "meeting", "location", "tomorrow", "mission", "security", "cryptography",
]

# Educational explanation of Shannon's Perfect Secrecy Theorem
PERFECT_SECRECY_EXPLANATION: str = (
    "Shannon's Perfect Secrecy Theorem (1949):\n"
    "An encryption scheme achieves information-theoretic perfect secrecy if and only if "
    "the ciphertext provides zero information about the plaintext: P(M = m | C = c) = P(M = m), "
    "or equivalently H(M | C) = H(M).\n\n"
    "In the One-Time Pad, ciphertext C = M ⊕ K. For any fixed ciphertext c and any candidate message m, "
    "there exists a unique key k = m ⊕ c that maps m to c. If the key K is chosen uniformly at random "
    "from the key space {0, 1}^n (where n = |M|), every key has probability 1 / (2^n). "
    "Consequently, every candidate plaintext m is equally likely to have produced c, "
    "regardless of the adversary's computational power.\n\n"
    "Three Invariant Conditions Required for Perfect Secrecy:\n"
    "1. Truly Random Key: The key must be generated from a uniform random source (CSPRNG or physical entropy).\n"
    "2. Key Length Match: The key length must be at least the message length (|K| >= |M|).\n"
    "3. Absolute One-Time Use: The key must NEVER be reused. If a key is reused across two messages (C1 = M1 ⊕ K, C2 = M2 ⊕ K), "
    "the key cancels out (C1 ⊕ C2 = M1 ⊕ M2), completely destroying perfect secrecy and enabling crib-dragging cryptanalysis."
)

TWO_TIME_PAD_PROOF: str = (
    "Two-Time Pad Key Cancellation Proof:\n"
    "Let M1 and M2 be two plaintexts encrypted with the identical one-time pad key K:\n"
    "    C1 = M1 ⊕ K\n"
    "    C2 = M2 ⊕ K\n\n"
    "An eavesdropper intercepting C1 and C2 computes their bitwise XOR:\n"
    "    C1 ⊕ C2 = (M1 ⊕ K) ⊕ (M2 ⊕ K)\n"
    "            = M1 ⊕ M2 ⊕ (K ⊕ K)    [By Associativity and Commutativity of XOR]\n"
    "            = M1 ⊕ M2 ⊕ 0           [By Self-Inverse Property: K ⊕ K = 0]\n"
    "            = M1 ⊕ M2               [By Identity Property: X ⊕ 0 = X]\n\n"
    "Result: The secret key K is completely eliminated! The XOR sum of the two ciphertexts "
    "equals the XOR sum of the two plaintext messages (C1 ⊕ C2 = M1 ⊕ M2). "
    "This allows an attacker to employ frequency analysis and crib-dragging to completely "
    "recover both original plaintext messages."
)


# ---------------------------------------------------------------------------
# Data Models (Frozen Dataclasses)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BitXORTrace:
    bit_index: int       # Bit position: 7 (MSB) down to 0 (LSB)
    bit_p: int           # Plaintext bit (0 or 1)
    bit_k: int           # Key bit (0 or 1)
    bit_c: int           # Ciphertext bit: bit_p ^ bit_k
    formula: str         # Pedagogical formula, e.g. "1 ^ 0 = 1"


@dataclass(frozen=True)
class ByteOTPTrace:
    byte_index: int
    p_char: str          # Printable ASCII character or hex escape (e.g., "'A'" or "'\\x00'")
    p_val: int           # Plaintext byte integer value [0, 255]
    p_bin: str           # 8-bit binary string with leading zeros, e.g. "01000001"
    p_hex: str           # 2-character lowercase hex string, e.g. "41"
    k_val: int           # Key byte integer value [0, 255]
    k_bin: str           # 8-bit binary string with leading zeros, e.g. "10110010"
    k_hex: str           # 2-character lowercase hex string, e.g. "b2"
    c_val: int           # Ciphertext byte integer: p_val ^ k_val
    c_bin: str           # 8-bit binary string with leading zeros, e.g. "11110011"
    c_hex: str           # 2-character lowercase hex string, e.g. "f3"
    c_char: str          # Printable ASCII character or hex escape
    bit_traces: list[BitXORTrace] = field(default_factory=list)


@dataclass(frozen=True)
class EntropyAnalysis:
    data_length: int
    entropy: float                 # Shannon entropy in bits per byte [0.0, 8.0]
    max_entropy: float = 8.0       # Theoretical maximum for 8-bit bytes (log2(256) = 8.0)
    entropy_ratio: float = 0.0     # Normalized entropy ratio: entropy / 8.0 in [0.0, 1.0]
    frequencies: dict[int, int] = field(default_factory=dict)  # Byte value -> occurrence count
    is_near_maximal: bool = False  # True if entropy >= 7.5 or uniform
    explanation: str = ""          # Pedagogical explanation of the observed entropy


@dataclass(frozen=True)
class OTPEncryptionResult:
    plaintext_bytes: bytes
    key_bytes: bytes
    ciphertext_bytes: bytes
    plaintext_hex: str
    key_hex: str
    ciphertext_hex: str
    ciphertext_base64: str
    traces: list[ByteOTPTrace] = field(default_factory=list)
    plaintext_entropy: EntropyAnalysis = field(default_factory=lambda: EntropyAnalysis(0, 0.0))
    key_entropy: EntropyAnalysis = field(default_factory=lambda: EntropyAnalysis(0, 0.0))
    ciphertext_entropy: EntropyAnalysis = field(default_factory=lambda: EntropyAnalysis(0, 0.0))
    perfect_secrecy_notes: str = ""


@dataclass(frozen=True)
class OTPDecryptionResult:
    ciphertext_bytes: bytes
    key_bytes: bytes
    decrypted_bytes: bytes
    decrypted_text: str | None     # Decoded UTF-8 string, or None if raw non-UTF8 binary
    ciphertext_hex: str
    key_hex: str
    decrypted_hex: str
    traces: list[ByteOTPTrace] = field(default_factory=list)
    is_valid_utf8: bool = True


@dataclass(frozen=True)
class TwoTimePadAnalysis:
    c1_bytes: bytes
    c2_bytes: bytes
    xor_stream: bytes
    c1_hex: str
    c2_hex: str
    xor_hex: str
    overlap_length: int
    key_cancelled_proof: str
    sample_traces: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class CribDragCandidate:
    offset: int
    crib: str
    crib_bytes: bytes
    revealed_bytes: bytes
    revealed_text: str          # Printable string (printable chars kept, non-printable formatted as '.' or escape)
    score: float                # Natural language readability score in [0.0, 1.0]
    is_printable: bool          # True if all revealed bytes are in ASCII printable range [0x20, 0x7E]
    is_likely_english: bool     # True if score >= 0.65 and is_printable


@dataclass(frozen=True)
class CribDragResult:
    xor_stream_length: int
    crib: str
    candidates: list[CribDragCandidate] = field(default_factory=list)
    best_candidate: CribDragCandidate | None = None


@dataclass(frozen=True)
class AutoCribDragResult:
    overlap_length: int
    xor_stream_hex: str
    tested_crib_count: int
    top_candidates: list[CribDragCandidate] = field(default_factory=list)
    reconstructed_m1_snippet: str = ""
    reconstructed_m2_snippet: str = ""
    attack_summary: str = ""


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _format_byte_char(val: int) -> str:
    """Formats a single byte integer into a readable quoted character or hex escape."""
    if 0x20 <= val <= 0x7E:
        ch = chr(val)
        if ch == "'":
            return r"'\''"
        return f"'{ch}'"
    return f"'\\x{val:02x}'"


def _coerce_to_bytes(data: bytes | str, name: str = "data") -> bytes:
    """Coerces a bytes or hexadecimal string input into bytes."""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        try:
            return bytes.fromhex(data)
        except (ValueError, TypeError) as err:
            raise ValueError("Invalid hexadecimal string.") from err
    raise TypeError(f"{name} must be bytes or hex str, got {type(data).__name__}")


# ---------------------------------------------------------------------------
# Core OTP Engine Functions
# ---------------------------------------------------------------------------

def generate_otp_key(length: int) -> bytes:
    """Generates a cryptographically secure random key of specified byte length using CSPRNG.

    Raises:
        ValueError: If length < 0.
    """
    if length < 0:
        raise ValueError("Key length must be non-negative.")
    return secrets.token_bytes(length)


def calculate_shannon_entropy(data: bytes) -> EntropyAnalysis:
    """Calculates empirical Shannon entropy H(X) = -sum(P(x) * log2(P(x))) over byte frequencies.

    Returns an EntropyAnalysis object with entropy value in [0.0, 8.0], byte frequencies,
    ratio against 8-bit maximum, and a pedagogical explanation.
    """
    n = len(data)
    if n == 0:
        return EntropyAnalysis(
            data_length=0,
            entropy=0.0,
            max_entropy=8.0,
            entropy_ratio=0.0,
            frequencies={},
            is_near_maximal=False,
            explanation="Empty data sequence has zero Shannon entropy (no information or uncertainty).",
        )

    freqs = collections.Counter(data)
    entropy_val = -sum((count / n) * math.log2(count / n) for count in freqs.values())

    # Snap to exact integers for canonical distributions (e.g. 1.0, 2.0, 8.0)
    if abs(entropy_val - round(entropy_val)) < 1e-12:
        entropy_clean = float(round(entropy_val))
    else:
        entropy_clean = round(entropy_val, 6)

    ratio = round(entropy_clean / 8.0, 4)
    is_near_max = bool(entropy_clean >= 7.5)

    if entropy_clean == 0.0:
        explanation = (
            "Zero entropy (0.00 bits/byte): completely deterministic with no uncertainty. "
            "A single byte value repeats throughout the entire sequence."
        )
    elif is_near_max:
        explanation = (
            f"Near-maximal entropy ({entropy_clean:.4f} bits/byte, {ratio * 100:.1f}% of 8.0 max): "
            "indicates high randomness and uniform information density characteristic of "
            "cryptographic keys or properly encrypted ciphertexts."
        )
    else:
        explanation = (
            f"Moderate entropy ({entropy_clean:.4f} bits/byte, {ratio * 100:.1f}% of 8.0 max): "
            "indicates structured, redundant data characteristic of natural language, "
            "source code, or uncompressed file formats."
        )

    return EntropyAnalysis(
        data_length=n,
        entropy=entropy_clean,
        max_entropy=8.0,
        entropy_ratio=ratio,
        frequencies=dict(freqs),
        is_near_maximal=is_near_max,
        explanation=explanation,
    )


def encrypt_otp(
    plaintext: str | bytes,
    key: bytes | None = None,
) -> OTPEncryptionResult:
    """Encrypts plaintext using One-Time Pad (byte-wise XOR) with detailed pedagogical traces.

    If key is None, generates a fresh CSPRNG key matching plaintext length.
    If key is provided and longer than plaintext, slices key to plaintext length.

    Raises:
        ValueError: If key is provided but len(key) < len(plaintext).
        TypeError: If plaintext is not str or bytes.
    """
    if isinstance(plaintext, str):
        p_bytes = plaintext.encode("utf-8")
    elif isinstance(plaintext, bytes):
        p_bytes = plaintext
    else:
        raise TypeError(f"Plaintext must be str or bytes, got {type(plaintext).__name__}")

    p_len = len(p_bytes)

    if key is None:
        key_bytes = generate_otp_key(p_len)
    elif isinstance(key, bytes):
        if len(key) < p_len:
            raise ValueError(
                f"Key length ({len(key)}) must be at least plaintext length ({p_len}) for One-Time Pad."
            )
        key_bytes = key[:p_len]
    else:
        raise TypeError(f"Key must be bytes or None, got {type(key).__name__}")

    c_bytes = bytes(p ^ k for p, k in zip(p_bytes, key_bytes))

    traces: list[ByteOTPTrace] = []
    for i in range(p_len):
        pv = p_bytes[i]
        kv = key_bytes[i]
        cv = c_bytes[i]

        bit_traces = [
            BitXORTrace(
                bit_index=b,
                bit_p=(pv >> b) & 1,
                bit_k=(kv >> b) & 1,
                bit_c=(cv >> b) & 1,
                formula=f"{(pv >> b) & 1} ^ {(kv >> b) & 1} = {(cv >> b) & 1}",
            )
            for b in range(7, -1, -1)
        ]

        traces.append(
            ByteOTPTrace(
                byte_index=i,
                p_char=_format_byte_char(pv),
                p_val=pv,
                p_bin=f"{pv:08b}",
                p_hex=f"{pv:02x}",
                k_val=kv,
                k_bin=f"{kv:08b}",
                k_hex=f"{kv:02x}",
                c_val=cv,
                c_bin=f"{cv:08b}",
                c_hex=f"{cv:02x}",
                c_char=_format_byte_char(cv),
                bit_traces=bit_traces,
            )
        )

    return OTPEncryptionResult(
        plaintext_bytes=p_bytes,
        key_bytes=key_bytes,
        ciphertext_bytes=c_bytes,
        plaintext_hex=p_bytes.hex(),
        key_hex=key_bytes.hex(),
        ciphertext_hex=c_bytes.hex(),
        ciphertext_base64=base64.b64encode(c_bytes).decode("ascii"),
        traces=traces,
        plaintext_entropy=calculate_shannon_entropy(p_bytes),
        key_entropy=calculate_shannon_entropy(key_bytes),
        ciphertext_entropy=calculate_shannon_entropy(c_bytes),
        perfect_secrecy_notes=PERFECT_SECRECY_EXPLANATION,
    )


def decrypt_otp(
    ciphertext: bytes | str,
    key: bytes,
) -> OTPDecryptionResult:
    """Decrypts ciphertext using One-Time Pad key (C ^ K) with detailed pedagogical traces.

    Accepts raw bytes or a hex-encoded string for ciphertext.
    If key is longer than ciphertext, slices key to ciphertext length.

    Raises:
        ValueError: If len(key) < len(ciphertext), or if ciphertext is an invalid hex string.
        TypeError: If key is not bytes.
    """
    c_bytes = _coerce_to_bytes(ciphertext, name="ciphertext")

    if not isinstance(key, bytes):
        raise TypeError(f"Key must be bytes, got {type(key).__name__}")

    c_len = len(c_bytes)
    if len(key) < c_len:
        raise ValueError(
            f"Key length ({len(key)}) must be at least ciphertext length ({c_len}) for One-Time Pad."
        )

    key_bytes = key[:c_len]
    d_bytes = bytes(c ^ k for c, k in zip(c_bytes, key_bytes))

    try:
        decrypted_text: str | None = d_bytes.decode("utf-8")
        is_valid_utf8 = True
    except UnicodeDecodeError:
        decrypted_text = None
        is_valid_utf8 = False

    traces: list[ByteOTPTrace] = []
    for i in range(c_len):
        cv = c_bytes[i]
        kv = key_bytes[i]
        dv = d_bytes[i]

        bit_traces = [
            BitXORTrace(
                bit_index=b,
                bit_p=(dv >> b) & 1,
                bit_k=(kv >> b) & 1,
                bit_c=(cv >> b) & 1,
                formula=f"{(dv >> b) & 1} ^ {(kv >> b) & 1} = {(cv >> b) & 1}",
            )
            for b in range(7, -1, -1)
        ]

        traces.append(
            ByteOTPTrace(
                byte_index=i,
                p_char=_format_byte_char(dv),
                p_val=dv,
                p_bin=f"{dv:08b}",
                p_hex=f"{dv:02x}",
                k_val=kv,
                k_bin=f"{kv:08b}",
                k_hex=f"{kv:02x}",
                c_val=cv,
                c_bin=f"{cv:08b}",
                c_hex=f"{cv:02x}",
                c_char=_format_byte_char(cv),
                bit_traces=bit_traces,
            )
        )

    return OTPDecryptionResult(
        ciphertext_bytes=c_bytes,
        key_bytes=key_bytes,
        decrypted_bytes=d_bytes,
        decrypted_text=decrypted_text,
        ciphertext_hex=c_bytes.hex(),
        key_hex=key_bytes.hex(),
        decrypted_hex=d_bytes.hex(),
        traces=traces,
        is_valid_utf8=is_valid_utf8,
    )


def format_byte_truth_table(trace: ByteOTPTrace) -> str:
    """Renders an ASCII text truth table for the 8 bit-by-bit XOR operations of a byte trace."""
    header = (
        f"Byte Trace [Index {trace.byte_index}]: "
        f"P={trace.p_char} (0x{trace.p_hex}, {trace.p_bin}) ⊕ "
        f"K=0x{trace.k_hex} ({trace.k_bin}) = "
        f"C={trace.c_char} (0x{trace.c_hex}, {trace.c_bin})\n"
        f"{'Bit':^5} | {'P Bit':^7} | {'K Bit':^7} | {'C Bit (P^K)':^13} | {'Formula':^11}\n"
        f"{'-'*5}-+-{'-'*7}-+-{'-'*7}-+-{'-'*13}-+-{'-'*11}"
    )
    rows = [
        f"{bt.bit_index:^5} | {bt.bit_p:^7} | {bt.bit_k:^7} | {bt.bit_c:^13} | {bt.formula:^11}"
        for bt in trace.bit_traces
    ]
    return header + "\n" + "\n".join(rows)


# ---------------------------------------------------------------------------
# Two-Time Pad & Cryptanalysis Functions
# ---------------------------------------------------------------------------

def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    """Computes bitwise XOR between two byte sequences up to min(len(b1), len(b2))."""
    return bytes(x ^ y for x, y in zip(b1, b2))


def analyze_two_time_pad(
    c1: bytes | str,
    c2: bytes | str,
) -> TwoTimePadAnalysis:
    """Demonstrates key cancellation when two ciphertexts are encrypted with identical key.

    Computes:
        C1 ^ C2 = (M1 ^ K) ^ (M2 ^ K) = M1 ^ M2 ^ (K ^ K) = M1 ^ M2
    Accepts raw bytes or hex strings for c1 and c2.

    Raises:
        ValueError: If hex string is malformed.
    """
    c1_bytes = _coerce_to_bytes(c1, name="c1")
    c2_bytes = _coerce_to_bytes(c2, name="c2")

    overlap_length = min(len(c1_bytes), len(c2_bytes))
    c1_sub = c1_bytes[:overlap_length]
    c2_sub = c2_bytes[:overlap_length]
    xor_stream = xor_bytes(c1_sub, c2_sub)

    sample_traces: list[dict[str, Any]] = []
    for i in range(min(16, overlap_length)):
        b1 = c1_sub[i]
        b2 = c2_sub[i]
        xv = xor_stream[i]
        sample_traces.append({
            "index": i,
            "c1_val": b1,
            "c1_hex": f"{b1:02x}",
            "c1_bin": f"{b1:08b}",
            "c2_val": b2,
            "c2_hex": f"{b2:02x}",
            "c2_bin": f"{b2:08b}",
            "xor_val": xv,
            "xor_hex": f"{xv:02x}",
            "xor_bin": f"{xv:08b}",
            "formula": f"0x{b1:02x} ^ 0x{b2:02x} = 0x{xv:02x}",
        })

    return TwoTimePadAnalysis(
        c1_bytes=c1_bytes,
        c2_bytes=c2_bytes,
        xor_stream=xor_stream,
        c1_hex=c1_bytes.hex(),
        c2_hex=c2_bytes.hex(),
        xor_hex=xor_stream.hex(),
        overlap_length=overlap_length,
        key_cancelled_proof=TWO_TIME_PAD_PROOF,
        sample_traces=sample_traces,
    )


def english_readability_score(data: bytes) -> float:
    """Calculates a natural language plausibility score in [0.0, 1.0] for a byte sequence.

    Evaluates:
    - Proportion of ASCII printable characters (space through tilde: 0x20 to 0x7E)
    - Penalties for unprintable control bytes or extended characters
    - Relative frequencies of top English characters (ETAOIN SHRDLU)
    - Plausible whitespace and punctuation ratios
    """
    n = len(data)
    if n == 0:
        return 0.0

    printable_count = sum(1 for b in data if 0x20 <= b <= 0x7E)
    p_ratio = printable_count / n
    if p_ratio == 0.0:
        return 0.0

    letters = sum(1 for b in data if (65 <= b <= 90) or (97 <= b <= 122))
    spaces = sum(1 for b in data if b == 0x20)
    common_punct = sum(1 for b in data if chr(b) in ".,!?'\":;-")
    uncommon_syms = sum(
        1 for b in data
        if 0x20 <= b <= 0x7E and chr(b) not in string.ascii_letters and chr(b) not in " .,!?'\":;-"
    )

    # Relative English character frequency table (percentages)
    freq_map: dict[str, float] = {
        "e": 12.7, "t": 9.1, "a": 8.2, "o": 7.5, "i": 7.0, "n": 6.7,
        "s": 6.3, "h": 6.1, "r": 6.0, "d": 4.3, "l": 4.0, "u": 2.8,
        "c": 2.8, "m": 2.4, "w": 2.4, "f": 2.2, "g": 2.0, "y": 2.0,
        "p": 1.9, "b": 1.5, "v": 1.0, "k": 0.8, "j": 0.15, "x": 0.15,
        "q": 0.10, "z": 0.07, " ": 15.0,
    }

    char_score = 0.0
    for b in data:
        ch = chr(b).lower()
        if ch in freq_map:
            char_score += freq_map[ch]
        elif 0x20 <= b <= 0x7E:
            if chr(b) in ".,!?'\":;-":
                char_score += 2.0
            else:
                char_score -= 5.0
        else:
            char_score -= 20.0

    avg_char_score = max(0.0, char_score / n)
    norm_char_score = min(1.0, avg_char_score / 10.0)
    good_chars_ratio = (letters + spaces + common_punct) / n
    sym_penalty = (1.0 - (uncommon_syms / n)) ** 2

    final_score = (p_ratio ** 3) * sym_penalty * (0.6 * norm_char_score + 0.4 * good_chars_ratio)
    return max(0.0, min(1.0, round(final_score, 4)))


def drag_crib(
    xor_stream: bytes | str,
    crib: str | bytes,
    offset: int | None = None,
) -> CribDragResult:
    """Slides a crib string/bytes across an XOR stream or evaluates at an explicit offset.

    At each offset i:
        revealed_bytes = xor_stream[i : i + len(crib_bytes)] ^ crib_bytes
    Computes candidate readability scores and identifies best candidate.

    Raises:
        ValueError: If offset is out of bounds (offset < 0 or offset + len(crib) > len(xor_stream)).
        TypeError: If xor_stream or crib are of invalid types.
    """
    stream_bytes = _coerce_to_bytes(xor_stream, name="xor_stream")

    if isinstance(crib, str):
        crib_str = crib
        crib_bytes = crib.encode("utf-8")
    elif isinstance(crib, bytes):
        crib_bytes = crib
        crib_str = crib.decode("utf-8", errors="replace")
    else:
        raise TypeError(f"crib must be str or bytes, got {type(crib).__name__}")

    stream_len = len(stream_bytes)
    crib_len = len(crib_bytes)

    if offset is not None:
        if offset < 0 or offset + crib_len > stream_len or crib_len == 0:
            raise ValueError(
                f"Offset {offset} is out of bounds for stream length {stream_len} and crib length {crib_len}."
            )
        offsets = [offset]
    else:
        if crib_len > stream_len or stream_len == 0 or crib_len == 0:
            return CribDragResult(
                xor_stream_length=stream_len,
                crib=crib_str,
                candidates=[],
                best_candidate=None,
            )
        offsets = list(range(stream_len - crib_len + 1))

    candidates: list[CribDragCandidate] = []
    for off in offsets:
        sub = stream_bytes[off : off + crib_len]
        revealed = bytes(s ^ c for s, c in zip(sub, crib_bytes))
        score = english_readability_score(revealed)
        is_printable = all(0x20 <= b <= 0x7E for b in revealed)
        is_likely_english = bool(score >= 0.65 and is_printable)
        revealed_text = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in revealed)

        candidates.append(
            CribDragCandidate(
                offset=off,
                crib=crib_str,
                crib_bytes=crib_bytes,
                revealed_bytes=revealed,
                revealed_text=revealed_text,
                score=score,
                is_printable=is_printable,
                is_likely_english=is_likely_english,
            )
        )

    best_candidate = max(candidates, key=lambda c: c.score) if candidates else None

    return CribDragResult(
        xor_stream_length=stream_len,
        crib=crib_str,
        candidates=candidates,
        best_candidate=best_candidate,
    )


def auto_crib_drag_attack(
    c1: bytes | str,
    c2: bytes | str,
    dictionary: list[str] | None = None,
    top_n: int = 15,
) -> AutoCribDragResult:
    """Executes an automated crib-dragging attack across C1 ^ C2 using a dictionary.

    Slides every dictionary word across all valid offsets, ranks candidate decryptions
    by readability score, removes duplicates, and constructs reconstructed snippets.
    """
    c1_bytes = _coerce_to_bytes(c1, name="c1")
    c2_bytes = _coerce_to_bytes(c2, name="c2")

    overlap_length = min(len(c1_bytes), len(c2_bytes))
    xor_stream = xor_bytes(c1_bytes[:overlap_length], c2_bytes[:overlap_length])
    xor_stream_hex = xor_stream.hex()

    crib_dict = DEFAULT_CRIB_DICTIONARY if dictionary is None else dictionary

    if overlap_length == 0 or not crib_dict:
        return AutoCribDragResult(
            overlap_length=overlap_length,
            xor_stream_hex=xor_stream_hex,
            tested_crib_count=len(crib_dict),
            top_candidates=[],
            reconstructed_m1_snippet="",
            reconstructed_m2_snippet="",
            attack_summary="No overlap or empty dictionary; crib dragging could not be performed.",
        )

    all_candidates: list[CribDragCandidate] = []
    seen: set[tuple[int, bytes, str]] = set()

    for word in crib_dict:
        res = drag_crib(xor_stream, word)
        for cand in res.candidates:
            key = (cand.offset, cand.revealed_bytes, cand.crib)
            if key not in seen:
                seen.add(key)
                all_candidates.append(cand)

    # Sort descending by readability score, then printability and crib length
    all_candidates.sort(key=lambda c: (c.score, c.is_printable, len(c.crib)), reverse=True)
    top_candidates = all_candidates[:top_n]

    # Reconstruct message snippets from top candidates
    m1_arr = ["."] * overlap_length
    m2_arr = ["."] * overlap_length

    # First attempt filling using likely English candidates
    filled_any = False
    for cand in top_candidates:
        if cand.is_likely_english:
            for idx, (c_char, r_char) in enumerate(zip(cand.crib, cand.revealed_text)):
                pos = cand.offset + idx
                if pos < overlap_length:
                    if m1_arr[pos] == ".":
                        m1_arr[pos] = c_char
                    if m2_arr[pos] == ".":
                        m2_arr[pos] = r_char
            filled_any = True

    # Fallback to single best candidate if none were flagged as likely english
    if not filled_any and top_candidates:
        best = top_candidates[0]
        for idx, (c_char, r_char) in enumerate(zip(best.crib, best.revealed_text)):
            pos = best.offset + idx
            if pos < overlap_length:
                m1_arr[pos] = c_char
                m2_arr[pos] = r_char

    m1_snippet = "".join(m1_arr)
    m2_snippet = "".join(m2_arr)

    summary = (
        f"Automated Crib-Dragging Attack completed across {overlap_length} overlapping bytes.\n"
        f"Tested {len(crib_dict)} dictionary cribs; identified {len(all_candidates)} alignments.\n"
        f"Top {len(top_candidates)} candidates ranked by English readability score."
    )

    return AutoCribDragResult(
        overlap_length=overlap_length,
        xor_stream_hex=xor_stream_hex,
        tested_crib_count=len(crib_dict),
        top_candidates=top_candidates,
        reconstructed_m1_snippet=m1_snippet,
        reconstructed_m2_snippet=m2_snippet,
        attack_summary=summary,
    )
