# Context Packet 7.1: Frontend Scaffolding, Tailwind Setup, Theme System, Header/Nav/Layout, API Base

## 1. Goal
Establish the foundational frontend client architecture in `frontend/`, configuring Vite, React 18+, TypeScript 5.x, and Tailwind CSS. Deliver a persistent Dark/Light theme system, a responsive navigation shell with active lab routing, an API health indicator polling the FastAPI backend (`http://localhost:8000/api/v1/health`), a typed Axios API client base, a reusable UI design kit, and the central pedagogical Course Dashboard (`DashboardPage.tsx`).

---

## 2. Allowed Files
* `frontend/package.json`
* `frontend/tsconfig.json`
* `frontend/tsconfig.node.json`
* `frontend/vite.config.ts`
* `frontend/tailwind.config.js`
* `frontend/postcss.config.js`
* `frontend/index.html`
* `frontend/src/main.tsx`
* `frontend/src/App.tsx`
* `frontend/src/index.css`
* `frontend/src/types/api.ts`
* `frontend/src/api/client.ts`
* `frontend/src/context/ThemeContext.tsx`
* `frontend/src/components/common/Navbar.tsx`
* `frontend/src/components/common/Footer.tsx`
* `frontend/src/components/common/ThemeToggle.tsx`
* `frontend/src/components/common/Card.tsx`
* `frontend/src/components/common/Badge.tsx`
* `frontend/src/components/common/Button.tsx`
* `frontend/src/components/common/MathFormula.tsx`
* `frontend/src/components/common/AlertBanner.tsx`
* `frontend/src/components/common/SkeletonLoader.tsx`
* `frontend/src/components/layout/AppLayout.tsx`
* `frontend/src/components/layout/PageHeader.tsx`
* `frontend/src/pages/DashboardPage.tsx`

---

## 3. Strict Interface Contracts & Types (`frontend/src/types/api.ts`)

```typescript
export interface ErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  error: string;
  detail: string;
  timestamp: string;
  errors?: ErrorDetail[];
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  modules: {
    number_theory: string;
    otp: string;
    lcg: string;
    elgamal: string;
    dsa: string;
  };
}

export interface RootResponse {
  app: string;
  version: string;
  docs_url: string;
  redoc_url: string;
  endpoints_prefix: string;
}

export type Theme = 'dark' | 'light';

export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}
```

---

## 4. API Client Specification (`frontend/src/api/client.ts`)
* Uses `axios` with `baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'`.
* Default timeout: `15000` ms.
* Response Interceptor:
  - Extracts and formats backend `ErrorResponse` when HTTP 400 or 422 is returned.
  - Generates clear fallback error message if server is offline / unreachable (Network Error).

```typescript
import axios, { AxiosError } from 'axios';
import { ErrorResponse, HealthResponse } from '../types/api';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

export function parseApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<ErrorResponse>;
    if (axiosErr.response?.data?.detail) {
      return axiosErr.response.data.detail;
    }
    if (axiosErr.message === 'Network Error') {
      return 'Cannot connect to backend server at http://localhost:8000. Is FastAPI running?';
    }
    return axiosErr.message;
  }
  return String(error);
}
```

---

## 5. Component Architecture & Detailed Responsibilities

### A. Theme Management (`ThemeContext.tsx` & `ThemeToggle.tsx`)
- Reads initial preference from `localStorage.getItem('cns_theme')`. If unset, defaults to system preference via `window.matchMedia('(prefers-color-scheme: dark)').matches`.
- Adds/removes the `dark` class on `document.documentElement`.
- Provides quick 1-click toggle button displaying Sun icon (in dark mode) or Moon icon (in light mode) with smooth transition.

### B. Shell & Layout (`AppLayout.tsx`, `Navbar.tsx`, `Footer.tsx`)
- Sticky top navigation bar with:
  - Platform brand logo & title: "CNS Pedagogy Platform".
  - Nav links for each lab with active route highlights:
    - **Dashboard / Syllabus** (`/`)
    - **Lab 1: One-Time Pad** (`/otp`)
    - **Lab 2: LCG & Lattice** (`/lcg`)
    - **Lab 3: ElGamal Cryptosystem** (`/elgamal`)
    - **Lab 4: DSA & Sony PS3 Exploit** (`/dsa`)
  - Live API status badge:
    - Green dot: "Backend Connected (v1.0.0)"
    - Amber/Red dot: "Backend Disconnected / Error" (with tooltip)
  - Theme toggle switch.
  - Mobile hamburger drawer for smaller viewports.
- Responsive footer displaying academic course credits, MIT license badge, and link to interactive Swagger docs (`http://localhost:8000/docs`).

### C. Foundational UI Components
1. `Card`: Styled container with customizable title, subtitle, action buttons, dark/light surface tokens, and rounded borders.
2. `Badge`: Variant-based pill indicator (`default`, `success`, `warning`, `danger`, `info`, `math`).
3. `Button`: Accessible button component with loading spinner state, icon support, and variants (`primary`, `secondary`, `danger`, `outline`, `ghost`).
4. `MathFormula`: Robust KaTeX renderer for inline ($...$) and block ($$...$$) LaTeX expressions with fallback text rendering if KaTeX fails.
5. `AlertBanner`: Dismissable banner for errors, security warnings, and educational tips.
6. `SkeletonLoader`: Animated placeholder for API fetch latency states.

### D. Central Course Dashboard (`DashboardPage.tsx`)
- Hero section welcoming students to the Cryptography & Network Security Pedagogy Activity.
- Four interactive Pillar Cards displaying:
  - Title, icon, and mathematical description.
  - Key learning objectives (e.g. Information-theoretic secrecy vs computational secrecy, pseudo-randomness & hyperplanes, discrete logarithms, signature forgery & nonce reuse).
  - Direct "Launch Lab" action button with route transition.
- Cryptographic Reference Syllabus listing theorems explored:
  - Claude Shannon's Perfect Secrecy Theorem ($H(M|C) = H(M)$)
  - Hull-Dobell Theorem for Full Periodicity ($m, a, c$)
  - Marsaglia's Hyperplane Theorem ($\le (d! \cdot m)^{1/d}$)
  - Diffie-Hellman / ElGamal Multiplicative Homomorphism ($E(m_1) \cdot E(m_2)$)
  - FIPS 186-4 Resampling & Nonce-Reuse Private Key Extraction (Sony PS3)

---

## 6. Edge Cases & Resilience
1. **Backend Offline on Startup**: The frontend must load cleanly without crashing. The API health badge should turn red with "Offline" and display an educational banner advising the student to run `uvicorn backend.main:app --reload`.
2. **Local Storage Unavailable**: In private browsing modes or restricted environments, gracefully catch `localStorage` exceptions and fall back to in-memory state without crashing.
3. **KaTeX Formula Errors**: If an invalid LaTeX string is passed to `MathFormula`, it must catch the render error and display the raw LaTeX formula in a monospace tag instead of crashing the React component tree.
