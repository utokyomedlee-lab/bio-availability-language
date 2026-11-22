# BAL v0.4.0 — Parameter Estimation and Global Sensitivity

## Independence
BAL remains an independent language, package, runtime, repository and release line.
This increment extends the v0.3.0 mathematical core without importing or depending on BPL.

## Development increment
- `bal.fitting.availability`: validated normalized core equation.
- `bal.fitting.fit_alpha_beta`: dependency-free damped Gauss-Newton least-squares
  estimation of positive alpha and beta from observations (a, m, b, y).
- `bal.sensitivity.sobol_indices`: Monte Carlo first-order (S1) and total-order (ST)
  Sobol indices for independent uniform input ranges.
- Unit tests use synthetic observations with known generating parameters.

## Scientific interpretation
Parameter estimates depend on experimental design. Strong parameter correlation or
narrow input ranges can make estimates poorly identifiable. Report residuals and
experimental design with estimates; synthetic test recovery is not clinical validation.

Sobol indices quantify variance contribution under the specified input ranges and
independence assumptions. They are not universal biological constants. Increase
sample size and compare estimates to assess Monte Carlo convergence. Correlated
inputs require a different sensitivity framework.

## Data contract
Fitting records require finite numeric fields a, m, b and observed y:
0 <= a <= 1, 0 <= m < 1, b > 0, y >= 0.
Sensitivity ranges define exactly a, m, b, alpha and beta; ranges must be finite,
non-degenerate and respect the model domain.

## Verification
Run from the extracted v0.3.0 source root after adding the new modules:
```bash
python -m unittest tests.test_v04_analysis -v
```
The tests use synthetic data only. Experimental validation requires curated
observations, units, protocol metadata, uncertainty estimates and independent review.
