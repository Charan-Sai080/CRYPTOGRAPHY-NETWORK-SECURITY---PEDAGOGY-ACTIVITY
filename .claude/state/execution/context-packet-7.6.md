# Context Packet 7.6: Frontend Production Build, Type-check, and Integration Verification

## 1. Goal
Establish automated build, static type validation, and integration verification pipelines for the frontend application in `frontend/`. Ensure zero TypeScript compilation errors, complete asset bundling via Vite, Tailwind CSS purging, responsive multi-breakpoint layout stability, and seamless API communication with the FastAPI backend.

---

## 2. Allowed Files
* `frontend/package.json`
* `frontend/tsconfig.json`
* `frontend/tsconfig.node.json`
* `frontend/vite.config.ts`
* `frontend/tailwind.config.js`
* `frontend/index.html`

---

## 3. Strict Quality & Verification Criteria

### A. TypeScript Type-Checking (`tsc --noEmit`)
* TypeScript compilation must pass with `strict: true` and **zero type errors**.
* Disallow implicit `any`, unused local variables, and missing property definitions.
* Verification Command:
  ```bash
  cd frontend && npm run type-check # executes: tsc --noEmit
  ```

### B. Production Bundle & Asset Optimization (`vite build`)
* Production build must compile cleanly into `frontend/dist/`.
* CSS optimization: Tailwind CSS must purge unused utility classes, producing an optimized CSS bundle.
* Asset hashing: JavaScript and CSS bundles must have content-hashed filenames for cache busting.
* Verification Command:
  ```bash
  cd frontend && npm run build
  ```

### C. Responsive UI & Visual Verification
* Ensure all 4 labs and dashboard render cleanly without horizontal scrollbar overflow or clipping across:
  - Mobile viewports (width: 375px - 767px): Single-column cards, collapsable trace accordions, scrollable tables.
  - Tablet viewports (width: 768px - 1023px): Two-column grids where appropriate.
  - Desktop viewports (width: $\ge 1024px$): Multi-column side-by-side interactive sandboxes.
* Theme toggle verification: Switching between dark mode (`bg-slate-950`) and light mode (`bg-slate-50`) must update all text, card backgrounds, borders, KaTeX equations, and SVG/Canvas charts without contrast anomalies.

### D. End-to-End API Integration Smoke Check
* Ensure frontend API services connect properly to FastAPI endpoints:
  - Health endpoint: `GET /api/v1/health` reports status `healthy`.
  - OTP endpoints: `/api/v1/otp/generate-key`, `/api/v1/otp/encrypt`, `/api/v1/otp/crib-drag`.
  - LCG endpoints: `/api/v1/lcg/presets`, `/api/v1/lcg/hull-dobell`, `/api/v1/lcg/marsaglia-lattice`.
  - ElGamal endpoints: `/api/v1/elgamal/presets`, `/api/v1/elgamal/encrypt`, `/api/v1/elgamal/homomorphic-multiply`.
  - DSA endpoints: `/api/v1/dsa/presets`, `/api/v1/dsa/sign`, `/api/v1/dsa/verify`, `/api/v1/dsa/detect-tampering`.

---

## 4. Edge Cases & Resilience Checklist
1. **Network Latency & Pending Requests**: All buttons triggering asynchronous API calls must show loading spinners and enter disabled state to prevent duplicate submissions.
2. **Backend Error Handling**: Any 400 Bad Request or 422 Unprocessable Entity returned by the backend must be caught by Axios interceptors and rendered in user-friendly inline alert banners rather than unhandled promise rejections.
3. **Empty Data States**: Before the user clicks "Generate" or "Encrypt", cards must display helpful instructional placeholders or default pedagogical examples rather than empty blank containers.
