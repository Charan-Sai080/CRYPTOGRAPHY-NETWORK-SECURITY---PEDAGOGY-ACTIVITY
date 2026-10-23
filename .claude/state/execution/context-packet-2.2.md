# Context Packet 2.2: Two-Time Pad (Key Reuse) Vulnerability Engine & Automated Crib-Dragging Cryptanalysis

## 1. Goal
Implement the Two-Time Pad (Key Reuse) Vulnerability Engine and Automated Crib-Dragging Cryptanalysis in `backend/core/otp.py` in pure Python 3.12+.
The implementation must provide:
1. Two-Time Pad key cancellation demonstration ($C_1 \oplus C_2 = (M_1 \oplus K) \oplus (M_2 \oplus K) = M_1 \oplus M_2$).
2. Interactive manual crib-dragging: slides a candidate word across an XOR stream at a specific offset or across all valid offsets, computing the corresponding plaintext characters of the co-ciphered message.
3. Natural English readability scoring heuristic ($[0.0, 1.0]$) evaluating ASCII printability, unigram letter frequencies (ETAOIN SHRDLU), punctuation, whitespace, and common English bigrams.
4. Automated crib-dragging attack iterating an extensive built-in dictionary of common English words/phrases across $C_1 \oplus C_2$, ranking candidate alignments, and reconstructing candidate plaintexts for both messages.

## 2. Allowed Files
* `backend/core/otp.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
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


@dataclass
class CribDragCandidate:
    offset: int
    crib: str
    crib_bytes: bytes
    revealed_bytes: bytes
    revealed_text: str          # Printable string (printable chars kept, non-printable formatted as '.' or escape)
    score: float                # Natural language readability score in [0.0, 1.0]
    is_printable: bool          # True if all revealed bytes are in ASCII printable range [0x20, 0x7E]
    is_likely_english: bool     # True if score >= 0.65 and is_printable


@dataclass
class CribDragResult:
    xor_stream_length: int
    crib: str
    candidates: list[CribDragCandidate] = field(default_factory=list)
    best_candidate: CribDragCandidate | None = None


@dataclass
class AutoCribDragResult:
    overlap_length: int
    xor_stream_hex: str
    tested_crib_count: int
    top_candidates: list[CribDragCandidate] = field(default_factory=list)
    reconstructed_m1_snippet: str
    reconstructed_m2_snippet: str
    attack_summary: str


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
    "meeting", "location", "tomorrow", "mission", "security", "cryptography"
]


def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    """Computes bitwise XOR between two byte sequences up to min(len(b1), len(b2))."""


def analyze_two_time_pad(
    c1: bytes | str,
    c2: bytes | str
) -> TwoTimePadAnalysis:
    """Demonstrates key cancellation when two ciphertexts are encrypted with identical key.
    
    Computes:
        C1 ^ C2 = (M1 ^ K) ^ (M2 ^ K) = M1 ^ M2 ^ (K ^ K) = M1 ^ M2
    Accepts raw bytes or hex strings for c1 and c2.
    """


def english_readability_score(data: bytes) -> float:
    """Calculates a natural language plausibility score in [0.0, 1.0] for a byte sequence.
    
    Evaluates:
    - Proportion of ASCII printable characters (space through tilde: 0x20 to 0x7E)
    - Penalties for unprintable control bytes or extended characters
    - Relative frequencies of top English characters (ETAOIN SHRDLU)
    - Plausible whitespace and punctuation ratios
    """


def drag_crib(
    xor_stream: bytes | str,
    crib: str | bytes,
    offset: int | None = None
) -> CribDragResult:
    """Slides a crib string/bytes across an XOR stream or evaluates at an explicit offset.
    
    At each offset i:
        revealed_bytes = xor_stream[i : i + len(crib_bytes)] ^ crib_bytes
    Computes candidate readability scores and identifies best candidate.
    
    Raises:
        ValueError: If offset is out of range (offset < 0 or offset + len(crib) > len(xor_stream)).
    """


def auto_crib_drag_attack(
    c1: bytes | str,
    c2: bytes | str,
    dictionary: list[str] | None = None,
    top_n: int = 15
) -> AutoCribDragResult:
    """Executes an automated crib-dragging attack across C1 ^ C2 using a dictionary.
    
    Slides every dictionary word across all valid offsets, ranks candidate decryptions
    by readability score, removes duplicates, and constructs reconstructed snippets.
    """
```

## 4. Acceptance Criteria
1. **Key Elimination Invariant**:
   - `xor_bytes(c1, c2)` must strictly equal `xor_bytes(m1, m2)` when $C_1 = M_1 \oplus K$ and $C_2 = M_2 \oplus K$.
   - The analysis result must include a mathematical proof string and tabular sample traces showing $(c_{1,i} \oplus c_{2,i}) = (m_{1,i} \oplus m_{2,i})$.
2. **Crib Dragging Mathematics**:
   - For an XOR stream $S = M_1 \oplus M_2$, guessing $M_1[i : i + L] = \text{crib}$ produces $M_2[i : i + L] = S[i : i + L] \oplus \text{crib}$.
   - If offset is `None`, slides the crib across all valid offsets $i \in [0, \text{len}(S) - L]$.
   - If offset is specified, evaluates precisely at offset $i$.
3. **Readability Scoring Fidelity**:
   - Normal English phrases (e.g. `b"the secret attack is planned"`) must score $\ge 0.80$.
   - Pure pseudorandom bytes (e.g. `secrets.token_bytes(30)`) must score $\le 0.30$.
   - Unprintable characters must be flagged (`is_printable = False`) and penalized proportionally in `score`.
4. **Automated Cryptanalysis Effectiveness**:
   - When given two English plaintexts encrypted with the same key, `auto_crib_drag_attack` must successfully find words from the default dictionary (e.g., `"the"`, `"with"`, `"secret"`) and rank them in the top candidates.
   - Candidates must be deduplicated and sorted in descending order by `score`.
5. **Robust String/Bytes Polymorphism**:
   - All functions accept either raw `bytes` or hexadecimal `str` inputs for ciphertexts and XOR streams.

## 5. Edge Cases
* **Crib Exceeding Stream Length**: If `len(crib_bytes) > len(xor_stream)`, `drag_crib` returns a `CribDragResult` with empty `candidates` list and `best_candidate = None` without raising an exception.
* **Empty Streams or Cribs**: If `xor_stream` or `crib` is empty, returns empty candidate list safely.
* **Unequal Ciphertext Lengths**: `analyze_two_time_pad` and `auto_crib_drag_attack` automatically truncate to the overlap length `min(len(c1), len(c2))` and clearly report `overlap_length`.
* **Explicit Offset Out of Bounds**: If an explicit `offset` is passed to `drag_crib` that is negative or satisfies `offset + len(crib_bytes) > len(xor_stream)`, raises `ValueError(f"Offset {offset} is out of bounds for stream length {len(xor_stream)} and crib length {len(crib_bytes)}.")`.
* **Non-ASCII Characters in Revealed Bytes**: Revealed bytes outside printable ASCII range [0x20, 0x7E] are converted in `revealed_text` using readable dot `.` substitution or hexadecimal escapes to avoid terminal rendering corruption.
* **Malformed Hex Input**: Raises `ValueError("Invalid hexadecimal string.")` if hex strings contain invalid characters or odd number of hex digits.
