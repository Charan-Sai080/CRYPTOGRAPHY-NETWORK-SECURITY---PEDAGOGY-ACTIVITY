# Context Packet 4.3: Multiplicative Homomorphism & Nonce-Reuse Exploit Demonstrations

## 1. Goal
Implement the Multiplicative Homomorphic Property engine and Ephemeral Nonce-Reuse Cryptanalytic Exploit in `backend/core/elgamal.py` in pure Python 3.12+.

The implementation must provide:
1. **Multiplicative Homomorphic Multiplication**:
   - Given two valid ciphertexts $E(m_1) = (c_{1,a}, c_{2,a})$ and $E(m_2) = (c_{1,b}, c_{2,b})$, compute the component-wise product modulo $p$:
     $$C_{\text{prod}} = (c_{1,a} \cdot c_{1,b} \pmod p, c_{2,a} \cdot c_{2,b} \pmod p)$$
   - Verify that decrypting $C_{\text{prod}}$ using private key $x$ yields $(m_1 \cdot m_2) \pmod p$ without any knowledge of the secret key during the multiplication operation.
   - Generate detailed step traces and complete mathematical derivation text explaining why homomorphism holds over cyclic groups $\mathbb{Z}_p^*$.
2. **Ephemeral Nonce $k$ Reuse Exploit (Known-Plaintext Cryptanalysis)**:
   - Validate that if two ciphertexts share the identical ephemeral component $c_{1,a} == c_{1,b}$, an eavesdropper immediately detects nonce reuse.
   - Known-Plaintext Attack: Given known $m_1$, compute:
     $$m_2 = (m_1 \cdot c_{2,b} \cdot c_{2,a}^{-1}) \pmod p$$
     where $c_{2,a}^{-1} = \text{mod\_inverse}(c_{2,a}, p)$.
   - Plaintext Ratio Leakage: Even without knowing $m_1$, compute the plaintext quotient $m_1 \cdot m_2^{-1} \equiv c_{2,a} \cdot c_{2,b}^{-1} \pmod p$.
   - Produce pedagogical diagnostic steps explaining why nonce reuse fatally undermines semantic security (IND-CPA).

## 2. Allowed Files
* `backend/core/elgamal.py`
* `backend/core/__init__.py`

## 3. Strict Data Contracts & Signatures

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.elgamal import (
    ElGamalCiphertextBlock,
    ElGamalError,
    ElGamalKeyPair,
    decrypt_integer,
    encrypt_integer,
)
from backend.core.number_theory import mod_inverse


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class CryptanalysisError(ElGamalError):
    """Raised when cryptanalytic exploit fails or prerequisites are not met."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
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


@dataclass
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


# ---------------------------------------------------------------------------
# Homomorphism & Exploit Functions
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
    ...


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
    ...


def recover_plaintext_ratio(
    c_a: tuple[int, int] | ElGamalCiphertextBlock,
    c_b: tuple[int, int] | ElGamalCiphertextBlock,
    p: int,
) -> int:
    """Computes the ratio (m1 * m2^-1) mod p from two ciphertexts sharing the same nonce k.

    c2_a * c2_b^-1 = (m1 * s) * (m2 * s)^-1 = m1 * m2^-1 mod p.
    """
    ...


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
    ...
```

## 4. Implementation Details & Pedagogical Requirements
1. **Mathematical Proof of Multiplicative Homomorphism**:
   - Let Alice have public key $y = g^x \pmod p$.
   - Bob encrypts $m_1$:
     $$c_{1,a} = g^{k_1} \pmod p, \quad c_{2,a} = m_1 \cdot y^{k_1} \pmod p$$
   - Bob encrypts $m_2$:
     $$c_{1,b} = g^{k_2} \pmod p, \quad c_{2,b} = m_2 \cdot y^{k_2} \pmod p$$
   - The product ciphertext is:
     $$c_{1,\text{prod}} = (c_{1,a} \cdot c_{1,b}) \pmod p = (g^{k_1} \cdot g^{k_2}) \pmod p = g^{k_1 + k_2} \pmod p$$
     $$c_{2,\text{prod}} = (c_{2,a} \cdot c_{2,b}) \pmod p = (m_1 y^{k_1} \cdot m_2 y^{k_2}) \pmod p = (m_1 \cdot m_2) \cdot y^{k_1 + k_2} \pmod p$$
   - Upon decryption with private key $x$:
     $$s_{\text{prod}} = (c_{1,\text{prod}})^x \pmod p = (g^{k_1 + k_2})^x = y^{k_1 + k_2} \pmod p$$
     $$s_{\text{prod}}^{-1} = \text{mod\_inverse}(s_{\text{prod}}, p)$$
     $$m_{\text{recovered}} = (c_{2,\text{prod}} \cdot s_{\text{prod}}^{-1}) \pmod p \equiv (m_1 \cdot m_2) \pmod p$$
   - This holds even when $(m_1 \cdot m_2) \ge p$; the decrypted result will be $(m_1 \cdot m_2) \pmod p$.
2. **Mathematical Proof of Nonce Reuse Vulnerability**:
   - Suppose the sender uses identical nonce $k$ for $m_1$ and $m_2$:
     $$c_{1,a} = g^k \pmod p, \quad c_{2,a} = m_1 \cdot y^k \pmod p$$
     $$c_{1,b} = g^k \pmod p, \quad c_{2,b} = m_2 \cdot y^k \pmod p$$
   - An eavesdropper observes $c_{1,a} = c_{1,b}$.
   - The ratio of $c_{2,b}$ to $c_{2,a}$ is:
     $$\frac{c_{2,b}}{c_{2,a}} \equiv \frac{m_2 \cdot y^k}{m_1 \cdot y^k} \equiv \frac{m_2}{m_1} \pmod p$$
   - Thus, with known plaintext $m_1$:
     $$m_2 \equiv m_1 \cdot \frac{c_{2,b}}{c_{2,a}} \equiv (m_1 \cdot c_{2,b} \cdot c_{2,a}^{-1}) \pmod p$$
   - The eavesdropper recovers $m_2$ completely without any discrete log calculation and without the private key $x$.
   - If $c_{1,a} \ne c_{1,b}$, `exploit_nonce_reuse` must raise `CryptanalysisError("Nonce reuse attack failed: c1_a ({c1_a}) and c1_b ({c1_b}) do not match. The nonces were distinct.")`.
