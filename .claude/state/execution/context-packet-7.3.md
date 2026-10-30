# Context Packet 7.3: Linear Congruential Generator (LCG) Lab UI Spec

## 1. Goal
Deliver a comprehensive, interactive laboratory interface for the Linear Congruential Generator in `frontend/src/pages/LCGLabPage.tsx` and related components. The lab enables students to explore pseudorandom number generation, mathematically verify the Hull-Dobell Theorem, observe Floyd's cycle-finding algorithm in action, test statistical uniformity via Chi-Square goodness-of-fit, inspect Marsaglia's lattice hyperplanes in 2D and 3D, and execute algebraic state reconstruction cryptanalysis.

---

## 2. Allowed Files
* `frontend/src/types/lcg.ts`
* `frontend/src/api/lcgApi.ts`
* `frontend/src/components/visualizers/LatticePlot2D.tsx`
* `frontend/src/components/visualizers/LatticePlot3D.tsx`
* `frontend/src/components/visualizers/CycleGraph.tsx`
* `frontend/src/components/labs/lcg/ParameterForm.tsx`
* `frontend/src/components/labs/lcg/StepTraceTable.tsx`
* `frontend/src/components/labs/lcg/HullDobellCard.tsx`
* `frontend/src/components/labs/lcg/FloydCycleCard.tsx`
* `frontend/src/components/labs/lcg/ChiSquareChart.tsx`
* `frontend/src/components/labs/lcg/MarsagliaLatticeCard.tsx`
* `frontend/src/components/labs/lcg/LcgCrackerCard.tsx`
* `frontend/src/pages/LCGLabPage.tsx`

---

## 3. Strict Interface Contracts (`frontend/src/types/lcg.ts`)

```typescript
export interface LCGPreset {
  name: string;
  description: string;
  m: number;
  a: number;
  c: number;
  default_seed: number;
  period_notes: string;
}

export interface LCGStepTrace {
  step: number;
  current_x: number;
  next_x: number;
  multiplier_product: number;
  sum_with_c: number;
  quotient: number;
  remainder: number;
  normalized_u: number;
  equation: string;
}

export interface LCGGenerateRequest {
  m?: number;
  a?: number;
  c?: number;
  seed?: number;
  preset_name?: string;
  count?: number;
}

export interface LCGGenerateResponse {
  m: number;
  a: number;
  c: number;
  seed: number;
  count: number;
  sequence: number[];
  normalized_sequence: number[];
  traces: LCGStepTrace[];
}

export interface HullDobellCondition {
  condition_id: number;
  name: string;
  passed: boolean;
  explanation: string;
  details: Record<string, unknown>;
}

export interface HullDobellRequest {
  m: number;
  a: number;
  c: number;
}

export interface HullDobellResponse {
  m: number;
  a: number;
  c: number;
  has_full_period: boolean;
  conditions: HullDobellCondition[];
  prime_factors_m: number[];
  verdict: string;
}

export interface FloydStepTrace {
  step: number;
  tortoise_val: number;
  hare_val: number;
  are_equal: boolean;
}

export interface CycleDetectRequest {
  m?: number;
  a?: number;
  c?: number;
  seed?: number;
  preset_name?: string;
  max_steps?: number;
}

export interface CycleDetectResponse {
  period_lambda: number;
  cycle_start_mu: number;
  total_steps_run: number;
  cycle_detected: boolean;
  is_full_period: boolean;
  trace_sample: FloydStepTrace[];
  explanation: string;
}

export interface ChiSquareBin {
  bin_index: number;
  lower_bound: number;
  upper_bound: number;
  observed_count: number;
  expected_count: number;
  chi_contribution: number;
}

export interface ChiSquareRequest {
  m?: number;
  a?: number;
  c?: number;
  seed?: number;
  preset_name?: string;
  sample_size?: number;
  bins?: number;
  alpha?: number;
}

export interface ChiSquareResponse {
  chi_square_stat: number;
  p_value: number;
  degrees_of_freedom: number;
  alpha: number;
  is_uniform: boolean;
  verdict: string;
  bins: ChiSquareBin[];
}

export interface LatticePoint2D {
  x: number;
  y: number;
}

export interface LatticePoint3D {
  x: number;
  y: number;
  z: number;
}

export interface MarsagliaLatticeRequest {
  m?: number;
  a?: number;
  c?: number;
  seed?: number;
  preset_name?: string;
  count?: number;
}

export interface MarsagliaLatticeResponse {
  m: number;
  a: number;
  c: number;
  points_2d: LatticePoint2D[];
  points_3d: LatticePoint3D[];
  theoretical_bound_2d: number;
  theoretical_bound_3d: number;
  hyperplane_explanation: string;
}

export interface LCGCrackRequest {
  outputs: number[];
  m?: number;
}

export interface LCGCrackResponse {
  recovered_a?: number;
  recovered_c?: number;
  recovered_m?: number;
  success: boolean;
  steps: string[];
  explanation: string;
}
```

---

## 4. API Client Integration (`frontend/src/api/lcgApi.ts`)
* Calls endpoints:
  - `GET /lcg/presets`: Loads catalog of standard historical presets.
  - `POST /lcg/generate`: Sequence generator with per-step quotient/remainder traces.
  - `POST /lcg/hull-dobell`: Exact 3-condition validator.
  - `POST /lcg/cycle-detect`: Floyd's tortoise-and-hare cycle finder.
  - `POST /lcg/chi-square`: Uniformity test with observed/expected bins.
  - `POST /lcg/marsaglia-lattice`: 2D/3D hyperplane coordinates and Marsaglia bounds.
  - `POST /lcg/crack`: Algebraic state reconstruction from consecutive outputs.

---

## 5. UI Components & Layout Specification

### Section 1: Parameter Form & Preset Library (`ParameterForm.tsx`)
- **Standard Presets Dropdown**: Loads presets dynamically (`ANSI C`, `POSIX`, `MINSTD`, `Borland C++`, `Numerical Recipes`, `Educational Small (m=16)`).
- Selecting a preset auto-populates parameters and updates contextual notes (e.g. "Borland rand(): $m=2^{31}, a=22695477, c=1$").
- Input fields for custom parameters: Modulus $m$, Multiplier $a$, Increment $c$, Seed $X_0$, and Sequence count $N$.
- Instant "Quick Validate" chip showing whether the current parameter set achieves full period or has defects.

### Section 2: Hull-Dobell Theorem Validator (`HullDobellCard.tsx`)
- Displays the mathematical formulation:
  $$X_{n+1} \equiv (a X_n + c) \pmod m \text{ has full period } m \iff \begin{cases} 1.\; \gcd(c, m) = 1 \\ 2.\; \forall p \in \mathbb{P}, p \mid m \implies p \mid (a - 1) \\ 3.\; 4 \mid m \implies 4 \mid (a - 1) \end{cases}$$
- **Condition-by-Condition Cards**:
  - Condition 1: Coprimality ($\gcd(c, m) = 1$). Shows exact GCD and coprimality check badge.
  - Condition 2: Prime factor divisibility. Shows prime factor decomposition of $m$ and checks if each prime divides $(a - 1)$.
  - Condition 3: Divisibility by 4. Shows modulo 4 checks for $m$ and $(a - 1)$.
- Prime factors visualizer pill row (e.g. $m=1024 \to 2^{10}$, $m=60 \to [2, 3, 5]$).
- Big verdict badge: Green "Full Period $m$ Guaranteed" or Red "Defective Period / Early Repeat".

### Section 3: Floyd's Cycle-Finding Visualizer (`FloydCycleCard.tsx`, `CycleGraph.tsx`)
- Displays empirical results:
  - Detected Period $\lambda$ (number of steps in recurring loop).
  - Cycle Start $\mu$ (transient tail before repeating).
- **Interactive Stepper / Cycle Graph**:
  - Interactive slider or "Step Forward" button animating the Tortoise ($X_i$) at speed 1 and Hare ($X_{2i}$) at speed 2.
  - Highlights meeting point where $X_i = X_{2i}$.
  - Comparative badge: Displays $\lambda$ side-by-side with theoretical maximum period $m$.

### Section 4: Chi-Square Uniformity Test (`ChiSquareChart.tsx`)
- Interactive Bar Histogram:
  - Bins along the X-axis dividing $[0, 1)$ or $[0, m)$.
  - Blue bars: Observed counts $O_i$.
  - Dashed horizontal line: Expected uniform baseline $E_i = N/k$.
- Statistical Metrics panel:
  - $\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$
  - Degrees of freedom $df = k - 1$
  - p-value calculated via Wilson-Hilferty transformation.
  - Significance verdict: "Pass: Uniform distribution hypothesis accepted ($p > 0.05$)" or "Fail: Statistically non-uniform ($p \le 0.05$)".

### Section 5: Marsaglia Hyperplane Lattice Visualizer (`MarsagliaLatticeCard.tsx`, `LatticePlot2D.tsx`, `LatticePlot3D.tsx`)
- **2D Scatter Plot Canvas/SVG**:
  - Plots points $(X_n, X_{n+1})$ normalized to $[0, 1) \times [0, 1)$.
  - Clearly demonstrates how poorly chosen multipliers cause points to coalesce into parallel linear stripes (planes) rather than filling the space.
  - Displays Marsaglia theoretical bound: $k \le \sqrt{2! \cdot m} = \sqrt{2m}$ hyperplanes.
- **3D Scatter Plot Canvas**:
  - Plots points $(X_n, X_{n+1}, X_{n+2})$ in an interactive 3D orthographic or perspective projection.
  - Supports mouse drag to rotate the 3D cube, revealing the exact viewing angles where 3D hyperplanes align into planar sheets.
  - Marsaglia 3D bound: $k \le \sqrt[3]{6m}$.
  - Educational commentary explaining why standard LCGs are fatally flawed for cryptographic key generation and Monte Carlo simulations.

### Section 6: Algebraic State Cracker Sandbox (`LcgCrackerCard.tsx`)
- Sandbox simulating an attacker observing consecutive pseudo-random outputs $X_0, X_1, X_2$.
- Step-by-step algebraic solver:
  - $X_1 - X_0 \equiv a (X_0 - X_{-1}) \pmod m$
  - Solves $a \equiv (X_2 - X_1) \cdot (X_1 - X_0)^{-1} \pmod m$
  - Then solves $c \equiv X_1 - a \cdot X_0 \pmod m$
- Button "Crack LCG": Emits step-by-step mathematical trace and reconstructs future values $X_3, X_4$, proving that LCGs are completely predictable.

---

## 6. Edge Cases & Error Handling
1. **Large Modulus Canvas Overflow**: When $m = 2^{31} - 1$, generating $1,000,000$ points directly would freeze the browser. Cap the scatter plot sample to $5,000$ points with an informational badge "Displaying first 5,000 points for real-time 60fps rendering".
2. **Singular Matrix / Non-Invertible Diff in Cracker**: When $(X_1 - X_0)$ is not coprime to $m$, handle the exception cleanly and show an educational note on why composite moduli require the GCD-based modular solver.
3. **Canvas Unresponsive on Mobile**: Ensure the 2D and 3D Canvas visualizers are responsive with touch listeners and automatic window resize handlers.
