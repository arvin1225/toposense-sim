# Architecture

## Field synthesis

The ideal normalized Stokes loop is generated through a two-component Jones field. With circular components `E_R`, `E_L`,

`S1 = 2 Re(E_R E_L*) / I`,  
`S2 = 2 Im(E_R E_L*) / I`,  
`S3 = (|E_R|² − |E_L|²) / I`.

The registered phase contains an integer winding plus low- and high-mode modulations. The dense ideal loop (`2048` points) defines projected-winding truth. A periodic Fourier transfer

`H(k) = exp[−(|k|/k_c)^4]`

models finite angular-mode support. Residual projected carrier represents uncompensated zero-order/polarization background. Dense received winding is logged separately from ideal winding.

## Polarimetric receiver

At each requested angle, a residual 3×3 Stokes transform and calibration bias are applied. For axis `j`, paired analyzer counts follow

`N_j+ ~ Poisson(P(1+S_j)/2)`,  
`N_j− ~ Poisson(P(1−S_j)/2)`,

with additive Gaussian read noise. The receiver estimates `(N+−N−)/(N++N−)`, normalizes the vector and attaches an angular error radius that combines a photon term, read-noise term, calibration-residual bound and angular-jitter bound.

Measurement noise is deterministic for `(family, seed, nominal angle)`, so an actively revisited location produces the same evidence and every acquisition replays exactly.

## Equal-budget acquisition

Uniform methods receive 32 nominally equispaced attempts. The adaptive method starts from 12 locations and assigns each cyclic interval the observed score

`gap / nominal_gap + |phase_step|/π + 0.8(error_i+error_j)/min_radius`.

It adds the midpoint (then deterministic irrational-fraction alternatives if already attempted) of the highest-score interval until 32 attempts are spent. Missing-sector attempts count against the budget.

## Certificate

The projected polygon provides an observed winding and cyclic principal phase increments. For each edge, the certificate combines endpoint measurement chords with either a global or local interpolation radius. Local slopes are estimated from observed phase motion but capped by the registered mode envelope.

Release requires:

- positive projected-origin clearance on every edge;
- phase increments below the uncertainty-reduced branch budget;
- integer closure and nontrivial sampling;
- a registered measurement model;
- Fourier residual, edge-mode, finite-NA, gap and dropout observability limits;
- a separate radius `>0.50` before releasing observed winding zero.

The last gate addresses a key ambiguity: a translated non-zero loop can become a smooth, integer-looking zero loop after receiver transfer.

## Audit artifact

Each row stores ideal/received/observed/released winding, decision, correctness, acquisition cost, uncertainty coverage, geometric margins, support diagnostics, topology-change truth, all sampled receiver factors and serialized gates. The manifest records code/data/summary hashes and the registered 32-sample budget.
