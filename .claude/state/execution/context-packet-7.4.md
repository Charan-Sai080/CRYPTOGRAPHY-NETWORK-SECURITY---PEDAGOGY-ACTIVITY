# Context Packet 7.4: ElGamal Cryptosystem Lab UI Spec

## 1. Goal
Deliver an interactive, mathematically rigorous laboratory interface for the ElGamal Public-Key Cryptosystem in `frontend/src/pages/ElGamalLabPage.tsx` and accompanying components. The lab illustrates asymmetric cryptography principles, discrete logarithm hardness, Diffie-Hellman key agreement, traced encryption/decryption of arbitrary UTF-8 messages, multiplicative homomorphic encryption, and the critical vulnerability of ephemeral nonce reuse.

---

## 2. Allowed Files
* `frontend/src/types/elgamal.ts`
* `frontend/src/api/elgamalApi.ts`
* `frontend/src/components/visualizers/KeyExchangeDiagram.tsx`
* `frontend/src/components/labs/elgamal/DomainKeygenCard.tsx`
* `frontend/src/components/labs/elgamal/EncryptDecryptCard.tsx`
* `frontend/src/components/labs/elgamal/TextChunkingVisualizer.tsx`
* `frontend/src/components/labs/elgamal/HomomorphismPlayground.tsx`
* `frontend/src/components/labs/elgamal/NonceReuseExploitCard.tsx`
* `frontend/src/pages/ElGamalLabPage.tsx`

---

## 3. Strict Interface Contracts (`frontend/src/types/elgamal.ts`)

```typescript
export interface ElGamalPreset {
  name: string;
  description: string;
  p: number | string;
  g: number | string;
  p_bits: number;
  is_safe_prime: boolean;
  q?: number | string;
}

export interface ElGamalDomainGenerateRequest {
  bits?: number;
  seed?: number;
}

export interface ElGamalDomainGenerateResponse {
  p: number;
  g: number;
  q: number;
  bits: number;
  search_steps: string[];
}

export interface ElGamalKeyGenerateRequest {
  p?: number | string;
  g?: number | string;
  preset_name?: string;
  seed?: number;
}

export interface ElGamalPublicKey {
  p: number | string;
  g: number | string;
  y: number | string;
  p_str?: string;
  g_str?: string;
  y_str?: string;
}

export interface ElGamalPrivateKey {
  p: number | string;
  g: number | string;
  x: number | string;
  p_str?: string;
  g_str?: string;
  x_str?: string;
}

export interface ElGamalKeyGenerateResponse {
  public_key: ElGamalPublicKey;
  private_key: ElGamalPrivateKey;
}

export interface ElGamalEncryptTrace {
  step_name: string;
  formula: string;
  values: Record<string, string | number>;
  description: string;
}

export interface ElGamalCiphertextBlock {
  c1: number | string;
  c2: number | string;
  c1_str?: string;
  c2_str?: string;
  block_index: number;
  trace: ElGamalEncryptTrace[];
}

export interface ElGamalEncryptRequest {
  plaintext: string;
  public_key: ElGamalPublicKey;
  is_integer?: boolean;
  k?: number | string;
}

export interface ElGamalEncryptResponse {
  ciphertext_blocks: ElGamalCiphertextBlock[];
  total_blocks: number;
  block_size_bytes: number;
  summary: string;
}

export interface ElGamalDecryptTrace {
  step_name: string;
  formula: string;
  values: Record<string, string | number>;
  description: string;
}

export interface ElGamalDecryptRequest {
  ciphertext_blocks: ElGamalCiphertextBlock[];
  private_key: ElGamalPrivateKey;
  is_integer?: boolean;
}

export interface ElGamalDecryptResponse {
  plaintext: string;
  plaintext_integer?: number;
  traces: ElGamalDecryptTrace[];
}

export interface HomomorphicMultiplyRequest {
  m1: number;
  m2: number;
  public_key: ElGamalPublicKey;
  private_key: ElGamalPrivateKey;
  k1?: number;
  k2?: number;
}

export interface HomomorphicMultiplyResponse {
  m1: number;
  m2: number;
  expected_product_mod_p: number;
  c1_block_m1: ElGamalCiphertextBlock;
  c2_block_m2: ElGamalCiphertextBlock;
  multiplied_c1: number | string;
  multiplied_c2: number | string;
  decrypted_product: number;
  is_homomorphism_verified: boolean;
  algebraic_proof: string;
}

export interface NonceReuseExploitRequest {
  c1_a: number | string;
  c2_a: number | string;
  c1_b: number | string;
  c2_b: number | string;
  known_m1: number;
  p: number | string;
}

export interface NonceReuseExploitResponse {
  recovered_m2: number;
  is_c1_identical: boolean;
  proof_steps: string[];
  explanation: string;
}
```

---

## 4. API Client Integration (`frontend/src/api/elgamalApi.ts`)
* Calls endpoints:
  - `GET /elgamal/presets`: Catalog of educational small primes and RFC 2409 standard groups.
  - `POST /elgamal/generate-domain`: Safe prime $(p = 2q + 1)$ and generator $g$ search.
  - `POST /elgamal/generate-keys`: Asymmetric key pair generator ($x, y = g^x \pmod p$).
  - `POST /elgamal/encrypt`: Traced encryption supporting integer and arbitrary UTF-8 chunked text.
  - `POST /elgamal/decrypt`: Traced decryption using modular inversion.
  - `POST /elgamal/homomorphic-multiply`: Ciphertext multiplier playground.
  - `POST /elgamal/exploit-nonce-reuse`: Ephemeral nonce reuse exploit.

---

## 5. UI Components & Layout Specification

### Section 1: Domain & Key Pair Setup (`DomainKeygenCard.tsx`)
- **Presets Selector**:
  - Educational Small (16-bit: $p=65537$ or 24-bit primes for instant mental calculation and small-step KaTeX display).
  - Standard RFC 2409 1024-bit MODP Group (for real-world scale demonstration).
- **Safe Prime Generator Controls**:
  - Slider for bit length (12 to 32 bits).
  - "Generate Safe Prime" button. Shows Miller-Rabin candidate search log and primitive root verification.
- **Key Pair Generator**:
  - Generates private key $x \in [2, p - 2]$.
  - Computes public key $y = g^x \pmod p$ via fast square-and-multiply.
  - Clean card displaying Public Key $(p, g, y)$ (shareable) and Private Key $x$ (with show/hide secret toggle).

### Section 2: Alice, Bob & Eve Key Exchange Diagram (`KeyExchangeDiagram.tsx`)
- Visual architectural diagram showing:
  - **Alice (Receiver)**: Generates domain $(p, g)$ and private key $x$, publishes $y$.
  - **Bob (Sender)**: Chooses plaintext $m$ and ephemeral secret $k$, calculates shared secret $s = y^k \pmod p$, produces ciphertext $(c_1 = g^k, c_2 = m \cdot s \pmod p)$.
  - **Insecure Public Channel**: Eve intercepts $(c_1, c_2, y, p, g)$ but cannot recover $s$ without solving Discrete Logarithm $\log_g y$ or $\log_g c_1$ (Computational Diffie-Hellman Problem).
  - **Alice Decryption**: Computes shared secret $s = c_1^x = (g^k)^x = g^{kx} = y^k \pmod p$, inverts $s^{-1}$, recovers $m = c_2 \cdot s^{-1} \pmod p$.

### Section 3: Traced Encryption & Text Chunking (`EncryptDecryptCard.tsx`, `TextChunkingVisualizer.tsx`)
- **Mode Toggle**: "Single Integer ($m < p$)" vs "Arbitrary Text Message".
- For text messages:
  - Automatically calculates maximum block size: $\text{chunk\_bytes} = \lfloor(\text{bit\_length}(p) - 1) / 8\rfloor$.
  - Displays **Text Chunking Visualizer**: shows how the input string (e.g. `"Hello World"`) is sliced into byte slices, converted to big-endian integers $< p$, and encrypted individually.
- **Step-by-Step KaTeX Trace**:
  - Step 1: Ephemeral nonce selection $k$.
  - Step 2: Shared secret computation $s = y^k \pmod p$.
  - Step 3: Ephemeral public key $c_1 = g^k \pmod p$.
  - Step 4: Masked plaintext $c_2 = (m \cdot s) \pmod p$.
  - Decryption trace showing modular inversion of $s$ via Extended Euclidean Algorithm and exact reconstruction.

### Section 4: Multiplicative Homomorphism Playground (`HomomorphismPlayground.tsx`)
- Inputs for two integer plaintexts $m_1$ and $m_2$ (e.g. $m_1 = 7, m_2 = 11$).
- "Encrypt Separately" button generates $(c_{1,a}, c_{2,a})$ and $(c_{1,b}, c_{2,b})$.
- "Multiply Ciphertexts" button performs component-wise modular multiplication:
  $$c_{1, \text{prod}} = (c_{1,a} \cdot c_{1,b}) \pmod p, \quad c_{2, \text{prod}} = (c_{2,a} \cdot c_{2,b}) \pmod p$$
- Decrypts $C_{\text{prod}}$ and verifies:
  $$\text{Decrypt}(C_{\text{prod}}) = (m_1 \cdot m_2) \pmod p$$
- Educational callout explaining how multiplicative homomorphism powers zero-knowledge proofs, verifiable secret ballot tallying, and privacy-preserving cloud computing.

### Section 5: Ephemeral Nonce Reuse Exploit Sandbox (`NonceReuseExploitCard.tsx`)
- Demonstrates catastrophic failure mode when an implementation reuses ephemeral nonce $k$ for two distinct messages $m_1$ and $m_2$.
- Displays two ciphertexts having identical $c_1$ component ($c_{1,a} = c_{1,b} = g^k \pmod p$).
- Attack Sandbox:
  - Eve knows plaintext $m_1$ (e.g. standard protocol greeting or HTTP header).
  - Eve observes $c_{2,a} \equiv m_1 \cdot s \pmod p$ and $c_{2,b} \equiv m_2 \cdot s \pmod p$.
  - Eve cancels the shared secret: $\frac{c_{2,b}}{c_{2,a}} \equiv \frac{m_2 \cdot s}{m_1 \cdot s} \equiv \frac{m_2}{m_1} \pmod p$.
  - Eve solves: $m_2 \equiv m_1 \cdot c_{2,b} \cdot (c_{2,a})^{-1} \pmod p$.
- "Execute Exploit" button triggers recovery and reveals $m_2$ instantly without knowing private key $x$!

---

## 6. Edge Cases & Error Handling
1. **Message Greater Than Modulus ($m \ge p$)**: In single integer mode, validate that $1 \le m < p$. Display inline warning explaining that modular reduction $\pmod p$ causes non-reversible ambiguity if $m \ge p$.
2. **Text Chunking with Small Modulus**: If modulus $p < 256$, chunk size is 0 bytes. Display alert explaining that public-key cryptography requires $p > 256$ to represent at least 1 byte per block.
3. **Large Integer Precision Loss**: 1024-bit RFC keys cannot fit into JavaScript `Number`. Render all values using `p_str`, `y_str`, `c1_str`, `c2_str` properties.
