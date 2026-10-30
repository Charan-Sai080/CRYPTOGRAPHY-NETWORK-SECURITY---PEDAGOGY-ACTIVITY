# Context Packet 7.2: One-Time Pad (OTP) Lab UI Spec

## 1. Goal
Deliver an interactive, pedagogy-first laboratory interface for the One-Time Pad in `frontend/src/pages/OTPLabPage.tsx` and accompanying components. The lab guides students from foundational concepts (CSPRNG key generation, Shannon entropy, bitwise XOR truth tables) through to advanced cryptanalysis (Two-Time Pad key cancellation, interactive crib-dragging, and automated dictionary-based plaintext recovery).

---

## 2. Allowed Files
* `frontend/src/types/otp.ts`
* `frontend/src/api/otpApi.ts`
* `frontend/src/components/visualizers/ShannonEntropyGauge.tsx`
* `frontend/src/components/visualizers/BitTruthTable.tsx`
* `frontend/src/components/labs/otp/KeyGenCard.tsx`
* `frontend/src/components/labs/otp/EncryptDecryptCard.tsx`
* `frontend/src/components/labs/otp/ByteVisualizer.tsx`
* `frontend/src/components/labs/otp/TwoTimePadSandbox.tsx`
* `frontend/src/components/labs/otp/CribDragSlider.tsx`
* `frontend/src/components/labs/otp/DictionaryAttackView.tsx`
* `frontend/src/pages/OTPLabPage.tsx`

---

## 3. Strict Interface Contracts (`frontend/src/types/otp.ts`)

```typescript
export interface BitXORTrace {
  bit_index: number;
  plain_bit: number;
  key_bit: number;
  cipher_bit: number;
  equation: string;
}

export interface ByteOTPTrace {
  byte_index: number;
  plain_char: string;
  plain_byte: number;
  plain_hex: string;
  plain_bin: string;
  key_byte: number;
  key_hex: string;
  key_bin: string;
  cipher_byte: number;
  cipher_hex: string;
  cipher_bin: string;
  bit_traces: BitXORTrace[];
}

export interface EntropyMetric {
  entropy: number;
  max_possible_entropy: number;
  relative_entropy: number;
  interpretation: string;
}

export interface OTPKeyGenerateRequest {
  length: number;
  encoding?: 'hex' | 'base64' | 'ascii';
}

export interface OTPKeyGenerateResponse {
  key_hex: string;
  key_base64: string;
  key_ascii: string;
  length: number;
  entropy: EntropyMetric;
}

export interface OTPEncryptRequest {
  plaintext: string;
  key: string;
  key_format?: 'hex' | 'base64' | 'ascii';
}

export interface OTPEncryptResponse {
  ciphertext_hex: string;
  ciphertext_base64: string;
  length: number;
  traces: ByteOTPTrace[];
  plaintext_entropy: EntropyMetric;
  ciphertext_entropy: EntropyMetric;
  perfect_secrecy_notes: string;
}

export interface OTPDecryptRequest {
  ciphertext: string;
  key: string;
  ciphertext_format?: 'hex' | 'base64';
  key_format?: 'hex' | 'base64' | 'ascii';
}

export interface OTPDecryptResponse {
  plaintext_utf8: string;
  plaintext_hex: string;
  length: number;
  traces: ByteOTPTrace[];
}

export interface TwoTimePadAnalyzeRequest {
  ciphertext1: string;
  ciphertext2: string;
  format?: 'hex' | 'base64';
}

export interface TwoTimePadAnalyzeResponse {
  c1_xor_c2_hex: string;
  c1_xor_c2_bytes: number[];
  length: number;
  algebraic_proof: string;
  vulnerability_explanation: string;
}

export interface CribDragCandidate {
  position: number;
  crib: string;
  recovered_candidate_raw: string;
  recovered_candidate_printable: string;
  readability_score: number;
  is_likely_english: boolean;
}

export interface CribDragRequest {
  c1_xor_c2_hex: string;
  crib?: string;
  run_automated_dictionary?: boolean;
}

export interface CribDragResponse {
  c1_xor_c2_hex: string;
  crib_used?: string;
  manual_candidates: CribDragCandidate[];
  automated_candidates: CribDragCandidate[];
  top_recommendation?: CribDragCandidate;
}
```

---

## 4. API Client Integration (`frontend/src/api/otpApi.ts`)
* Calls endpoints:
  - `POST /otp/generate-key`: CSPRNG key generator.
  - `POST /otp/encrypt`: Traced XOR encryption.
  - `POST /otp/decrypt`: Traced XOR decryption.
  - `POST /otp/analyze-two-time-pad`: Computes $C_1 \oplus C_2$ and key cancellation.
  - `POST /otp/crib-drag`: Interactive & dictionary crib-dragging.
  - `POST /otp/entropy`: Computes Shannon entropy on arbitrary strings.

---

## 5. UI Components & Layout Specification

### Section 1: OTP Fundamentals & Key Generator (`KeyGenCard.tsx`, `ShannonEntropyGauge.tsx`)
- **Key Length Slider / Input**: Select length from 1 to 256 bytes (default 16 bytes).
- **Format Toggle**: Hex, Base64, or ASCII view.
- **Generate Button**: Dispatches CSPRNG generation request with instant animation.
- **Shannon Entropy Gauge**:
  - Radial SVG / Canvas semi-circle gauge rendering $H(X) = -\sum p(x) \log_2 p(x)$.
  - Color-coded value: Red ($< 4.0$, low entropy), Yellow ($4.0 - 7.0$), Green ($> 7.5$, true cryptographic uniform distribution).
  - Displays numerical entropy (e.g. `7.89 / 8.00 bits/byte`) and mathematical note: "Shannon Perfect Secrecy holds only when $H(K) \approx 8.00$ bits/byte and $L_K \ge L_M$".

### Section 2: Traced Encryption & Live Bit Truth Table (`EncryptDecryptCard.tsx`, `ByteVisualizer.tsx`, `BitTruthTable.tsx`)
- **Plaintext & Key Input Fields**:
  - Auto-fills generated key or allows custom key entry.
  - Live character count comparison: if $\text{len}(K) < \text{len}(M)$, display warning badge: "VULNERABILITY: Key is shorter than message! OTP requires $|K| \ge |M|$".
- **Interactive Byte Grid**:
  - Each byte of Plaintext, Key, and Ciphertext displayed in aligned columns.
  - Hovering or clicking on a byte highlights that exact byte and opens the **Bit-by-Bit XOR Truth Table Drawer**:
    - Shows the 8 bits of $M_i$, $K_i$, and $C_i$.
    - Mathematical formula for each bit: $m_j \oplus k_j = c_j$.
    - Bitwise logic indicator (e.g. `1 ⊕ 0 = 1`, `1 ⊕ 1 = 0`).

### Section 3: Two-Time Pad Vulnerability Sandbox (`TwoTimePadSandbox.tsx`)
- **Message 1 & Message 2 Inputs**:
  - Pre-filled with pedagogical default messages:
    - Message 1: `"Attack at dawn tomorrow!"`
    - Message 2: `"Retreat to southern base"`
  - Encrypted with the *identical* one-time pad key $K$.
- **XOR Key Cancellation Visualizer**:
  - KaTeX mathematical derivation:
    $$C_1 \oplus C_2 = (P_1 \oplus K) \oplus (P_2 \oplus K) = P_1 \oplus P_2 \oplus (K \oplus K) = P_1 \oplus P_2$$
  - Displays resulting hex byte stream of $C_1 \oplus C_2$.
  - Highlights critical pedagogical takeaway: *The secret key has completely vanished from the equation! Eve now holds the pure XOR sum of both plaintexts.*

### Section 4: Crib-Dragging Sandbox (`CribDragSlider.tsx`, `DictionaryAttackView.tsx`)
- **Interactive Crib-Dragging Slider**:
  - User types a guessed crib (e.g. `" the "`, `"attack"`, `"base"`).
  - A horizontal position slider drags the crib across the byte stream:
    - At position $i$, computes $P_{2, candidate} = (C_1 \oplus C_2)[i : i + \text{len}(\text{crib})] \oplus \text{crib}$.
    - Renders the resulting recovered ASCII fragment.
    - Highlights printable vs non-printable characters (green for valid English ASCII letters/spaces, red for control characters).
- **Automated Dictionary Attack**:
  - "Run Dictionary Attack" button queries `/api/v1/otp/crib-drag` with standard dictionary words.
  - Displays a ranked list of high-scoring candidates based on English character frequency and bi-gram statistics.
  - "Apply Candidate" button reveals the decrypted segment in Message 1 and Message 2.

---

## 6. Edge Cases & Error Handling
1. **Key Length Mismatch**: If the user tries to encrypt a 20-character plaintext with a 10-byte key without padding, the frontend alerts the user with an educational explanation of why OTP fails when keys are shorter than the message.
2. **Non-Hex Input in Decrypt Mode**: Validates hex strings (even length, characters `0-9, a-f, A-F`) before dispatching API request to avoid unhandled exceptions.
3. **Empty Crib Drag**: If the crib input is empty or longer than the ciphertext XOR stream, disable the slider and guide the user with a tooltip.
