# Context Packet 4.2: Traced Encryption & Decryption Engine with Arbitrary Text Chunking

## 1. Goal
Implement the core Encryption and Decryption engine for the ElGamal Public-Key Cryptosystem in `backend/core/elgamal.py` in pure Python 3.12+, supporting:
1. Single integer encryption & decryption with ephemeral nonce generation ($k \in [2, p - 2], \gcd(k, p - 1) = 1$).
2. Full pedagogical execution traces (`ElGamalEncryptTrace`, `ElGamalDecryptTrace`) capturing intermediate modular powers, shared secret derivation, modular inverse computation, and human-readable formula representations.
3. Multi-block arbitrary UTF-8 text message chunking and reconstruction via `string_to_int_blocks` and `int_blocks_to_string` from `backend.core.number_theory`.
4. Strict boundary validation ($1 \le m < p$, $2 \le k \le p - 2$, $\gcd(k, p - 1) = 1$, key matching).

## 2. Allowed Files
* `backend/core/elgamal.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

import math
import secrets
from dataclasses import dataclass, field
from typing import Any

from backend.core.elgamal import (
    ElGamalDomainParams,
    ElGamalError,
    ElGamalKeyPair,
    ElGamalPrivateKey,
    ElGamalPublicKey,
    InvalidKeyError,
)
from backend.core.number_theory import (
    extended_gcd,
    int_blocks_to_string,
    mod_inverse,
    mod_pow,
    string_to_int_blocks,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class EncryptionError(ElGamalError):
    """Raised when an encryption operation fails or inputs are invalid."""
    pass


class DecryptionError(ElGamalError):
    """Raised when a decryption operation fails or inputs are invalid."""
    pass


# ---------------------------------------------------------------------------
# Tracing & Result Models
# ---------------------------------------------------------------------------

@dataclass
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


@dataclass
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
class ElGamalCiphertextBlock:
    """A single ElGamal ciphertext pair (c1, c2)."""
    c1: int
    c2: int
    block_index: int = 0


@dataclass
class ElGamalCiphertext:
    """Encapsulates one or more ciphertext blocks with domain metadata."""
    blocks: list[ElGamalCiphertextBlock]
    p: int
    g: int
    domain_name: str = "Custom Domain"
    total_blocks: int = field(init=False)

    def __post_init__(self) -> None:
        self.total_blocks = len(self.blocks)

    def to_tuple_list(self) -> list[tuple[int, int]]:
        """Returns blocks as a list of (c1, c2) integer tuples."""
        return [(b.c1, b.c2) for b in self.blocks]


@dataclass
class ElGamalEncryptionResult:
    """Complete result of an encryption operation, including traces and metadata."""
    ciphertext: ElGamalCiphertext
    traces: list[ElGamalEncryptTrace]
    message_blocks: list[int]
    is_string_message: bool
    original_text: str | None = None


@dataclass
class ElGamalDecryptionResult:
    """Complete result of a decryption operation, including traces and decoded text."""
    recovered_blocks: list[int]
    plaintext_str: str | None
    traces: list[ElGamalDecryptTrace]
    is_verified: bool


# ---------------------------------------------------------------------------
# Core Encryption & Decryption Functions
# ---------------------------------------------------------------------------

def generate_ephemeral_nonce(p: int, custom_k: int | None = None) -> int:
    """Selects an ephemeral nonce k in [2, p - 2] such that gcd(k, p - 1) == 1.

    If custom_k is provided, validates that 2 <= custom_k <= p - 2 and gcd(custom_k, p - 1) == 1.
    """
    ...


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
    ...


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
    ...


def encrypt_message(
    text: str,
    public_key: ElGamalPublicKey,
    nonces: list[int] | None = None,
) -> ElGamalEncryptionResult:
    """Encrypts an arbitrary UTF-8 text message into chunked ElGamal ciphertext blocks.

    Uses string_to_int_blocks(text, public_key.p.bit_length()) to convert text
    into integer blocks m_i < p.
    """
    ...


def decrypt_message(
    ciphertext: ElGamalCiphertext,
    private_key: ElGamalPrivateKey,
) -> ElGamalDecryptionResult:
    """Decrypts an ElGamalCiphertext back into integer blocks and decodes UTF-8 string.

    Uses int_blocks_to_string(recovered_blocks, private_key.p.bit_length()).
    """
    ...
```

## 4. Implementation Details & Pedagogical Requirements
1. **Mathematical Invariant & Shared Secret**:
   - Alice's public key: $y = g^x \pmod p$.
   - Bob's ephemeral nonce: $k \in [2, p - 2]$ with $\gcd(k, p - 1) = 1$.
   - Ephemeral public key: $c_1 = g^k \pmod p$.
   - Shared secret:
     $$s = y^k \pmod p = (g^x)^k \pmod p = g^{x \cdot k} \pmod p$$
   - Ciphertext component:
     $$c_2 = (m \cdot s) \pmod p$$
   - Decryption:
     Alice receives $(c_1, c_2)$. Alice computes:
     $$s' = c_1^x \pmod p = (g^k)^x \pmod p = g^{k \cdot x} \pmod p = s$$
     Alice computes modular inverse $s^{-1} = \text{mod\_inverse}(s', p)$ using Extended Euclidean Algorithm.
     Plaintext is recovered as:
     $$m = (c_2 \cdot s^{-1}) \pmod p = ((m \cdot s) \cdot s^{-1}) \pmod p \equiv m \pmod p$$
2. **Pedagogical Formulas**:
   - Trace string for $c_1$: `"c1 = g^k mod p = {g}^{k} mod {p} = {c1}"`
   - Trace string for $s$: `"s = y^k mod p = {y}^{k} mod {p} = {s}"`
   - Trace string for $c_2$: `"c2 = (m * s) mod p = ({m} * {s}) mod {p} = {c2}"`
   - Decrypt trace for $s$: `"s = c1^x mod p = {c1}^{x} mod {p} = {s}"`
   - Decrypt trace for $s^{-1}$: `"s^-1 = mod_inverse({s}, {p}) = {s_inv}"`
   - Decrypt trace for $m$: `"m = (c2 * s^-1) mod p = ({c2} * {s_inv}) mod {p} = {m}"`
3. **Chunking Sizing Rules**:
   - `string_to_int_blocks(text, bits)` ensures that each integer block value $m_i$ fits inside $(bits - 1)$ bits, guaranteeing $1 \le m_i < 2^{bits - 1} < p$.
   - Handling empty string: if `text == ""`, returns `ElGamalEncryptionResult` with empty blocks and empty traces.
   - For `encrypt_integer`, validate $1 \le m < p$. If $m \le 0$ or $m \ge p$, raise `EncryptionError(f"Plaintext integer m={m} must be in range [1, p - 1] ([1, {public_key.p - 1}])")`.
4. **Modulus Matching**:
   - In `decrypt_message`, verify that `ciphertext.p == private_key.p`. If they do not match, raise `DecryptionError("Ciphertext modulus p does not match private key modulus p.")`.
