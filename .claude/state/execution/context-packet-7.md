# Context Packet 7: Milestone 7 Interactive Frontend Web Application

## 1. Task Goal
Architect and deliver a modern, highly interactive, and pedagogically rich Single Page Application (SPA) using React 18+, TypeScript 5.x, and Tailwind CSS. The frontend connects to the FastAPI backend (`http://localhost:8000/api/v1`) to provide intuitive visual sandboxes for all four cryptographic pillars:
1. **One-Time Pad (OTP) & Two-Time Pad Cryptanalysis**
2. **Linear Congruential Generator (LCG) Parameter Explorer & Marsaglia Lattice**
3. **ElGamal Public-Key Cryptosystem & Multiplicative Homomorphism**
4. **Digital Signature Algorithm (DSA) & Nonce-Reuse Exploit (Sony PS3)**

The application must feature a persistent Dark/Light theme, interactive mathematical rendering via KaTeX, dynamic Canvas/SVG graphs and scatter plots, live step-by-step calculation traces, and real-time vulnerability sandboxes.

---

## 2. Granular Sub-Milestones
* **M7.1: Frontend Scaffolding, Tailwind Setup, Theme System, Header/Nav/Layout, API Base**:
  - Vite + React + TypeScript + Tailwind CSS configuration.
  - Theme provider with dark/light mode toggle and `localStorage` persistence.
  - Global responsive layout (`AppLayout`), navigation bar, active lab indicators, mobile menu, and backend health status polling (`/api/v1/health`).
  - Typed Axios API client base (`baseURL: http://localhost:8000/api/v1`) with error interceptors and timeout handling.
  - Reusable foundational UI component library (`Card`, `Badge`, `Button`, `MathFormula`, `AlertBanner`, `SkeletonLoader`).
  - Interactive Course Syllabus & Dashboard Hub (`DashboardPage.tsx`).
  - Context: [context-packet-7.1.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-7.1.md)

* **M7.2: One-Time Pad Lab UI**:
  - CSPRNG key generator with Shannon entropy gauge (0.0 to 8.0 bits/byte with classification).
  - Traced encryption/decryption sandbox with live bit-by-bit truth table ($A \oplus B = C$) and interactive byte grid visualizer.
  - Two-Time Pad vulnerability demonstration showing key cancellation ($C_1 \oplus C_2 = P_1 \oplus P_2$).
  - Interactive crib-dragging slider and automated dictionary-based crib-dragging attack with English readability scoring.
  - Context: [context-packet-7.2.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-7.2.md)

* **M7.3: Linear Congruential Generator (LCG) Lab UI**:
  - Parameter configuration ($m, a, c, X_0$) with historical standard presets dropdown (ANSI C, POSIX, MINSTD, Borland, etc.).
  - Hull-Dobell theorem validator with condition-by-condition breakdown and prime factors tree.
  - Floyd's cycle-finding (tortoise-and-hare) empirical period visualizer.
  - Chi-Square uniformity goodness-of-fit histogram with observed vs expected bins and p-value verdict.
  - Marsaglia 2D and 3D hyperplane lattice scatter plots (Canvas/SVG) demonstrating hyperplane lattice bounds $\lfloor(d! \cdot m)^{1/d}\rfloor$.
  - Algebraic LCG state cracker playground recovering $(a, c)$ from consecutive outputs.
  - Context: [context-packet-7.3.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-7.3.md)

* **M7.4: ElGamal Cryptosystem Lab UI**:
  - Domain presets (RFC 2409 1024-bit MODP group) and educational safe prime generator ($p = 2q + 1$).
  - Interactive Alice & Bob key exchange architectural diagram.
  - Traced single-integer and multi-block UTF-8 text encryption/decryption with KaTeX formulas.
  - Multiplicative Homomorphism multiplier playground demonstrating $E(m_1) \cdot E(m_2) = E(m_1 \cdot m_2 \pmod p)$.
  - Ephemeral Nonce Reuse cryptanalysis exploit recovering plaintext without private key.
  - Context: [context-packet-7.4.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-7.4.md)

* **M7.5: Digital Signature Algorithm (DSA) Lab UI**:
  - FIPS 186-4 standard and educational domain parameter selector & key pair generator.
  - Document signing interface with SHA-256 digest truncation and FIPS 186-4 $r=0, s=0$ resampling trace.
  - Step-by-step signature verification engine with complete LaTeX algebraic proof.
  - Real-time single-bit document and signature tampering simulator with discrepancy detection.
  - Sony PS3 Nonce-Reuse Private Key Extraction playground recovering ephemeral $k$ and master private key $x$.
  - Context: [context-packet-7.5.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-7.5.md)

* **M7.6: Frontend Production Build, Type-check, and Integration Verification**:
  - Vite production bundling and asset hashing.
  - Zero TypeScript compiler errors (`tsc --noEmit`).
  - Tailwind purge and CSS bundle optimization.
  - Cross-browser and responsive layout verification.
  - Context: [context-packet-7.6.md](file:///Users/charancherry/dev/ccWorkSpace/CNS/.claude/state/execution/context-packet-7.6.md)

---

## 3. Directory Layout
```
frontend/
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── public/
│   └── favicon.svg
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── types/
    │   ├── api.ts              # Common API models (Error, Health, Status)
    │   ├── otp.ts              # OTP types mirroring backend/api/schemas/otp.py
    │   ├── lcg.ts              # LCG types mirroring backend/api/schemas/lcg.py
    │   ├── elgamal.ts          # ElGamal types mirroring backend/api/schemas/elgamal.py
    │   └── dsa.ts              # DSA types mirroring backend/api/schemas/dsa.py
    ├── api/
    │   ├── client.ts           # Axios instance with baseURL, interceptors, timeout
    │   ├── otpApi.ts           # OTP API service functions
    │   ├── lcgApi.ts           # LCG API service functions
    │   ├── elgamalApi.ts       # ElGamal API service functions
    │   └── dsaApi.ts           # DSA API service functions
    ├── context/
    │   └── ThemeContext.tsx    # Dark/Light theme state and provider
    ├── components/
    │   ├── common/
    │   │   ├── Navbar.tsx
    │   │   ├── Footer.tsx
    │   │   ├── ThemeToggle.tsx
    │   │   ├── Card.tsx
    │   │   ├── Badge.tsx
    │   │   ├── Button.tsx
    │   │   ├── MathFormula.tsx # KaTeX formula renderer
    │   │   ├── AlertBanner.tsx
    │   │   └── SkeletonLoader.tsx
    │   ├── layout/
    │   │   ├── AppLayout.tsx
    │   │   └── PageHeader.tsx
    │   ├── visualizers/
    │   │   ├── ShannonEntropyGauge.tsx
    │   │   ├── BitTruthTable.tsx
    │   │   ├── LatticePlot2D.tsx
    │   │   ├── LatticePlot3D.tsx
    │   │   ├── CycleGraph.tsx
    │   │   ├── KeyExchangeDiagram.tsx
    │   │   └── TamperIndicator.tsx
    │   └── labs/
    │       ├── otp/
    │       │   ├── KeyGenCard.tsx
    │       │   ├── EncryptDecryptCard.tsx
    │       │   ├── ByteVisualizer.tsx
    │       │   ├── TwoTimePadSandbox.tsx
    │       │   ├── CribDragSlider.tsx
    │       │   └── DictionaryAttackView.tsx
    │       ├── lcg/
    │       │   ├── ParameterForm.tsx
    │       │   ├── StepTraceTable.tsx
    │       │   ├── HullDobellCard.tsx
    │       │   ├── FloydCycleCard.tsx
    │       │   ├── ChiSquareChart.tsx
    │       │   ├── MarsagliaLatticeCard.tsx
    │       │   └── LcgCrackerCard.tsx
    │       ├── elgamal/
    │       │   ├── DomainKeygenCard.tsx
    │       │   ├── EncryptDecryptCard.tsx
    │       │   ├── TextChunkingVisualizer.tsx
    │       │   ├── HomomorphismPlayground.tsx
    │       │   └── NonceReuseExploitCard.tsx
    │       └── dsa/
    │           ├── DomainKeygenCard.tsx
    │           ├── DocumentSignerCard.tsx
    │           ├── VerificationProofCard.tsx
    │           ├── TamperSimulatorCard.tsx
    │           └── SonyPs3ExploitCard.tsx
    └── pages/
        ├── DashboardPage.tsx
        ├── OTPLabPage.tsx
        ├── LCGLabPage.tsx
        ├── ElGamalLabPage.tsx
        └── DSALabPage.tsx
```

---

## 4. Design System & Theme Tokens
1. **Color Palette**:
   - **Dark Theme** (`class="dark"` on `<html>`):
     - Background: `bg-slate-950` (page), `bg-slate-900` (cards/surfaces)
     - Borders: `border-slate-800`
     - Text: `text-slate-100` (primary), `text-slate-400` (secondary), `text-slate-500` (muted)
   - **Light Theme**:
     - Background: `bg-slate-50` (page), `bg-white` (cards/surfaces)
     - Borders: `border-slate-200`
     - Text: `text-slate-900` (primary), `text-slate-600` (secondary), `text-slate-400` (muted)
   - **Cryptographic Semantic Accents**:
     - Key & Math Primitives: `indigo-600` / `indigo-400`
     - Ciphertext & Encrypted Data: `amber-600` / `amber-400`
     - Verified Signatures & Valid Status: `emerald-600` / `emerald-400`
     - Exploit / Tamper / Vulnerability: `rose-600` / `rose-400`
     - Entropy / Distributions: `violet-600` / `violet-400`
2. **Typography**:
   - UI: Modern system sans-serif (`Inter`, `system-ui`, `sans-serif`)
   - Data / Code: High-readability monospace (`JetBrains Mono`, `Fira Code`, `ui-monospace`, `monospace`) for hex bytes, bits, keys, and traces
   - Mathematics: KaTeX (`react-katex` or KaTeX auto-render) for formatted modular arithmetic, exponents, and matrices
3. **Responsive Breakpoints**:
   - Mobile: `< 768px` (single-column cards, collapsable trace drawers, horizontal scroll on tables)
   - Desktop / Tablet: `≥ 768px` / `≥ 1024px` (multi-column split visualizers, side-by-side sandbox panes)

---

## 5. Architectural & Technical Rules
1. **Strict TypeScript Typing**:
   - Enable `strict: true` in `tsconfig.json`.
   - Never use `any`. All API responses and request payloads must map directly to strong TypeScript interfaces mirroring backend Pydantic schemas.
2. **Large Integer Safety**:
   - Numbers that exceed JavaScript's `Number.MAX_SAFE_INTEGER` ($2^{53} - 1 \approx 9 \times 10^{15}$) such as 1024-bit RFC primes, 160-bit DSA subprime $q$, public keys $y$, and signature components $r, s$ must be handled and displayed via string properties (`p_str`, `q_str`, `g_str`, `r_str`, `s_str`, `y_str`).
   - Educational parameters ($\le 32$ bits) can be manipulated as standard JavaScript `number`.
3. **Component Modularity & Decoupling**:
   - Each Lab consists of independent, composable card components.
   - Heavy visualizers (e.g. 3D Marsaglia lattice) must handle canvas resizing gracefully and render fallback messages if WebGL/Canvas is unavailable.
4. **Graceful Error Feedback**:
   - Every API call must be protected with `try/catch`. When the backend returns HTTP 400 or HTTP 422, display the structured backend error detail (`detail` from `ErrorResponse`) directly in an inline dismissable `AlertBanner`.
5. **No State Pollution**:
   - User inputs in one tab or card must not cause unintended side-effects across unrelated components.
