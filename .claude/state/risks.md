# Risk Analysis & Mitigation: Cryptography Pedagogy Platform

## Identified Risks

### Risk 1: Large Modulus Computation & Primality Generation Latency
* **Impact**: Generating 1024/2048-bit primes on the fly can take several seconds to minutes in pure Python, causing HTTP request timeouts.
* **Mitigation**:
  * Provide pre-computed, verified safe primes and standard RFC 3526 / RFC 7919 MODP groups for instant, deterministic security-mode demonstrations.
  * For educational custom primes, restrict prime generation to small/medium bit-lengths ($16-64$ bits) with instant Miller-Rabin validation.

### Risk 2: High Point-Density Browser Freezes during LCG Visualization
* **Impact**: Generating and plotting $100,000+$ points on an interactive 2D/3D canvas can degrade client performance.
* **Mitigation**:
  * The backend caps visualization point arrays to a maximum of $2,000$ representative successive points for rendering.
  * Full statistical analysis ($\chi^2$, period) is computed on the entire sequence server-side without streaming unneeded points to the client.

### Risk 3: Nonce Reuse and Zero-Division in DSA / ElGamal
* **Impact**: If $r = 0 \bmod q$ or $s = 0 \bmod q$ during DSA signing, or $\gcd(k, p-1) \ne 1$ in ElGamal, the algorithm fails mathematically.
* **Mitigation**:
  * Implement strict while-loops that automatically regenerate $k$ if degenerate values appear, fully adhering to FIPS 186-4 specifications.
  * Return explicit, clear validation messages if a user manually chooses an invalid nonce in interactive mode.

### Risk 4: Pedagogical Over-Complexity
* **Impact**: Learners may be overwhelmed by raw numbers without mathematical context.
* **Mitigation**:
  * Every API response includes both the computed numerical values and a structured `calculation_steps` array detailing the formula used, variable substitution, and intermediate values.
