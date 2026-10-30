# Context Packet 7.5: Digital Signature Algorithm (DSA) Lab UI Spec

## 1. Goal
Deliver an interactive, pedagogy-rich laboratory interface for the Digital Signature Algorithm (DSA) in `frontend/src/pages/DSALabPage.tsx` and accompanying components. The lab guides students through FIPS 186-4 parameter generation ($(p, q, g)$), key pair generation, SHA-256 hash digest truncation, traced signature generation with $k$-resampling, step-by-step signature verification with complete LaTeX proof, real-time single-bit document tampering detection, and the historic Sony PlayStation 3 nonce-reuse master key extraction exploit.

---

## 2. Allowed Files
* `frontend/src/types/dsa.ts`
* `frontend/src/api/dsaApi.ts`
* `frontend/src/components/visualizers/TamperIndicator.tsx`
* `frontend/src/components/labs/dsa/DomainKeygenCard.tsx`
* `frontend/src/components/labs/dsa/DocumentSignerCard.tsx`
* `frontend/src/components/labs/dsa/VerificationProofCard.tsx`
* `frontend/src/components/labs/dsa/TamperSimulatorCard.tsx`
* `frontend/src/components/labs/dsa/SonyPs3ExploitCard.tsx`
* `frontend/src/pages/DSALabPage.tsx`

---

## 3. Strict Interface Contracts (`frontend/src/types/dsa.ts`)

```typescript
export interface DSAPreset {
  name: string;
  p: number | string;
  q: number | string;
  g: number | string;
  p_str: string;
  q_str: string;
  g_str: string;
  p_bits: number;
  q_bits: number;
}

export interface DSADomainGenerateRequest {
  p_bits?: number;
  q_bits?: number;
  seed?: number;
}

export interface DSADomainGenerateResponse {
  p: number | string;
  q: number | string;
  g: number | string;
  p_str: string;
  q_str: string;
  g_str: string;
  p_bits: number;
  q_bits: number;
  steps: string[];
}

export interface DSAPublicKey {
  p: number | string;
  q: number | string;
  g: number | string;
  y: number | string;
  p_str: string;
  q_str: string;
  g_str: string;
  y_str: string;
}

export interface DSAPrivateKey {
  p: number | string;
  q: number | string;
  g: number | string;
  x: number | string;
  p_str: string;
  q_str: string;
  g_str: string;
  x_str: string;
}

export interface DSAKeyGenerateRequest {
  p?: number | string;
  q?: number | string;
  g?: number | string;
  preset_name?: string;
  seed?: number;
}

export interface DSAKeyGenerateResponse {
  public_key: DSAPublicKey;
  private_key: DSAPrivateKey;
}

export interface DSASignTrace {
  step_number: number;
  step_name: string;
  description: string;
  formula: string;
  computed_values: Record<string, string | number>;
}

export interface DSASignRequest {
  message: string;
  private_key: DSAPrivateKey;
  k?: number | string;
}

export interface DSASignResponse {
  message: string;
  sha256_full_hex: string;
  truncated_hash_z: number | string;
  truncated_hash_z_str: string;
  ephemeral_k: number | string;
  ephemeral_k_str: string;
  r: number | string;
  s: number | string;
  r_str: string;
  s_str: string;
  resampled_k_count: number;
  traces: DSASignTrace[];
}

export interface DSAVerifyTrace {
  step_number: number;
  step_name: string;
  formula: string;
  computed_values: Record<string, string | number>;
  description: string;
}

export interface DSAVerifyRequest {
  message: string;
  r: number | string;
  s: number | string;
  public_key: DSAPublicKey;
}

export interface DSAVerifyResponse {
  is_valid: boolean;
  message: string;
  sha256_full_hex: string;
  truncated_hash_z_str: string;
  w_str: string;
  u1_str: string;
  u2_str: string;
  v_str: string;
  r_str: string;
  algebraic_proof_latex: string;
  traces: DSAVerifyTrace[];
  verdict_explanation: string;
}

export interface DSATamperRequest {
  original_message: string;
  tampered_message?: string;
  flip_bit_index?: number;
  r: number | string;
  s: number | string;
  mutate_signature?: boolean;
  public_key: DSAPublicKey;
}

export interface DSATamperResponse {
  tampered_message: string;
  original_hash_z_str: string;
  tampered_hash_z_str: string;
  hashes_match: boolean;
  tampered_r_str: string;
  tampered_s_str: string;
  computed_v_str: string;
  expected_r_str: string;
  signature_valid: boolean;
  discrepancy_explanation: string;
}

export interface DSANonceReuseExploitRequest {
  message1: string;
  r1: number | string;
  s1: number | string;
  message2: string;
  r2: number | string;
  s2: number | string;
  public_key: DSAPublicKey;
}

export interface DSANonceReuseExploitResponse {
  is_r_identical: boolean;
  recovered_k_str: string;
  recovered_x_str: string;
  actual_public_y_str: string;
  reconstructed_public_y_str: string;
  keys_match: boolean;
  derivation_latex: string;
  exploit_successful: boolean;
  commentary: string;
}
```

---

## 4. API Client Integration (`frontend/src/api/dsaApi.ts`)
* Calls endpoints:
  - `GET /dsa/presets`: Loads FIPS 186-4 standard and educational DSA presets.
  - `POST /dsa/generate-domain`: Dynamically generates prime $p$, prime divisor $q$, and subgroup generator $g$.
  - `POST /dsa/generate-keys`: Generates DSA key pair ($x, y = g^x \pmod p$).
  - `POST /dsa/sign`: Traced signature engine with SHA-256 truncation.
  - `POST /dsa/verify`: Traced verification engine with intermediate variables ($w, u_1, u_2, v$).
  - `POST /dsa/detect-tampering`: Single-bit tampering simulator.
  - `POST /dsa/exploit-nonce-reuse`: PlayStation 3 private key extraction exploit.

---

## 5. UI Components & Layout Specification

### Section 1: Domain & Key Pair Setup (`DomainKeygenCard.tsx`)
- **Preset Selection**:
  - Educational Small (10-bit / 16-bit / 24-bit primes for instant step tracing).
  - FIPS 186-4 Standard Group (1024-bit prime $p$, 160-bit prime $q$).
- **Subgroup Verification Badge**:
  - Confirms $q \mid (p - 1)$ and $g^q \equiv 1 \pmod p$ with green verification checkmark.
- **Key Pair Generator**:
  - Private key $x \in [1, q - 1]$ (with secret masking).
  - Public key $y = g^x \pmod p$.
  - Displays large integers safely using monospace string formats (`p_str`, `q_str`, `g_str`, `y_str`).

### Section 2: Document Signing Interface (`DocumentSignerCard.tsx`)
- **Document Text Area**:
  - Default text: `"Transfer $5,000 to Bob's Account - Authorization ID #8841"`.
- **Ephemeral Nonce $k$ Controls**:
  - Random CSPRNG selection or manual entry for repeatable classroom demonstrations.
- **Traced Signing Steps**:
  - Step 1: Compute full SHA-256 digest (256-bit hex).
  - Step 2: Truncate hash to leftmost $\min(\text{bit\_len}(q), 256)$ bits to form $z$.
  - Step 3: Compute $r = (g^k \pmod p) \pmod q$. If $r = 0$, highlight FIPS 186-4 resampling loop.
  - Step 4: Compute modular inverse $k^{-1} \pmod q$.
  - Step 5: Compute signature component $s = k^{-1}(z + x \cdot r) \pmod q$. If $s = 0$, highlight resampling.
  - Displays final digital signature $(r, s)$.

### Section 3: Verification Engine & LaTeX Proof (`VerificationProofCard.tsx`)
- **Step-by-Step Mathematical Pipeline**:
  - Bound Check: $0 < r < q$ and $0 < s < q$.
  - Inversion: $w \equiv s^{-1} \pmod q$.
  - Scalar 1: $u_1 \equiv (z \cdot w) \pmod q$.
  - Scalar 2: $u_2 \equiv (r \cdot w) \pmod q$.
  - Intermediate: $v \equiv ((g^{u_1} \cdot y^{u_2}) \pmod p) \pmod q$.
  - Equivalence Check: $v \stackrel{?}{=} r$.
- **KaTeX Verification Proof Accordion**:
  $$v \equiv g^{u_1} y^{u_2} \equiv g^{z w} g^{x r w} \equiv g^{(z + x r) w} \equiv g^{(z + x r) s^{-1}} \equiv g^k \equiv r \pmod q$$
  Providing students with a complete algebraic justification of why DSA is sound.

### Section 4: Real-Time Tampering Simulator (`TamperSimulatorCard.tsx`, `TamperIndicator.tsx`)
- **Interactive Mutation Controls**:
  - Flip Bit in Document: Single-click button flips the $i$-th bit of the text (e.g. changing `"$5,000"` to `"&5,000"`).
  - Mutate Signature: Adds $+1$ to signature component $r$ or $s$.
- **Live Discrepancy Indicator**:
  - Visual color transition: turns from Emerald Green ("VALID SIGNATURE") to Crimson Red ("TAMPER DETECTED / SIGNATURE FORGERY").
  - Side-by-side comparison of original SHA-256 vs tampered SHA-256 (highlighting the avalanche effect where 1 changed bit mutates over 50% of the digest).
  - Displays divergence between computed $v$ and expected $r$.

### Section 5: Sony PS3 Nonce-Reuse Exploit Playground (`SonyPs3ExploitCard.tsx`)
- **Historical Background Callout**:
  - In 2010, the fail0verflow team discovered that the Sony PlayStation 3 firmware signed packages with DSA using a *constant, hardcoded ephemeral nonce $k$*.
- **Exploit Workflow**:
  - Signs two distinct messages $M_1$ and $M_2$ with the identical nonce $k$.
  - Both signatures exhibit identical $r_1 = r_2 = r$.
  - Algebraic Private Key Extraction Sandbox:
    1. $s_1 - s_2 \equiv k^{-1}(z_1 - z_2) \pmod q$
    2. Recovers ephemeral secret: $k \equiv (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod q$
    3. Recovers master private key: $x \equiv (s_1 \cdot k - z_1) \cdot r^{-1} \pmod q$
- **"Execute PS3 Exploit" Button**:
  - Recovers $k$ and $x$ instantly.
  - Computes $y_{\text{reconstructed}} = g^{x_{\text{recovered}}} \pmod p$ and confirms 100% equivalence with the public key $y$.
  - Displays security warning: *Reusing an ephemeral nonce even ONCE completely exposes the signer's private master key to any passive observer!*

---

## 6. Edge Cases & Error Handling
1. **Zero Resampling**: If $r = 0$ or $s = 0$, the backend resamples $k$. The UI shows an informational notification indicating that a resample occurred per FIPS 186-4 section 4.6.
2. **Invalid Signature Range**: If user alters $r \ge q$ or $s \ge q$, the verification engine flags this before modular exponentiation as a range check violation.
3. **Exact String Serialization**: All values for $p, q, g, y, r, s$ for the 1024-bit preset must be copied or passed as strings to prevent JavaScript floating-point truncation.
