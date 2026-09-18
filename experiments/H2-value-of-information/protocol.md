# H2 protocol — value-of-information angular acquisition

Status: **locked before implementation or H2 outcome inspection**  
Lock date: 2026-08-10

## Research question

At the same hard budget of 32 analyzer locations, can an observed-data-only
value-of-information (VOI) policy improve the rate of safe projected-winding
releases over the H1 gap/phase heuristic without increasing false releases?

The target remains the winding of a synthetic closed Stokes boundary. This is
not a full two-dimensional topological-degree claim and is not a laboratory
receiver validation.

## Frozen methods

All adaptive methods start with the same 12 uniformly spaced locations and may
attempt at most 20 additional locations.

1. `uniform_support_certificate`: non-adaptive 32-location control.
2. `adaptive_support_certificate`: the frozen H1 gap/phase/uncertainty policy.
3. `voi_support_certificate`: candidate selection by predicted reduction in
   the worst certificate deficit per attempted acquisition.
4. `voi_no_support`: ablation of the registered spectral-support gate.
5. `voi_global_support`: ablation replacing local interpolation bounds by the
   global registered-mode bound.
6. `oracle_dense`: diagnostic upper control; never an operational method.

The VOI scorer may use only already measured Stokes vectors, registered error
bounds, attempted/dropout history and analyzer locations. It may not read the
ideal field, received dense field, true winding, family name or hidden receiver
parameters when choosing the next location.

## Frozen evaluation

- Families: `blur_crosstalk`, `low_photon_bias`, `high_mode_na`,
  `sector_dropout`, `compound_shift`.
- Exploratory seeds: 500–599 (not valid for confirmation claims).
- Confirmatory seeds: 2000–2099, 100 seeds per family.
- Pairing key: `(family, seed)`.
- Maximum attempts: 32 for every non-oracle method.
- Primary safety metric: false-release probability and one-sided 95% Wilson
  upper bound.
- Primary utility metric: certified goodput in correct released bits per
  attempted analyzer location.
- Secondary metrics: coverage, conditional error, certificate margin, valid
  samples, dropout count, and acquisition concentration.

## Registered hypotheses

- **T5 safety:** `voi_support_certificate` has zero observed wrong releases and
  a one-sided 95% Wilson upper bound at most 1% over 500 trials.
- **T6 value:** paired mean certified-goodput difference of VOI minus the H1
  adaptive policy is positive, with a 95% paired bootstrap lower endpoint above
  zero.
- **T7 practical effect:** VOI improves pooled coverage by at least 3 percentage
  points or pooled certified goodput by at least 10%, while satisfying T5.
- **T8 budget:** no operational row exceeds 32 attempted locations and the
  paired methods use the same maximum acquisition budget.
- **T9 propagation audit:** an independent direct Fourier-sum implementation
  reproduces the FFT finite-NA received Jones field with maximum complex error
  below `1e-10` and identical dense received winding on a registered audit grid.

T6 and T7 may fail. Thresholds will not be relaxed after confirmatory outcomes
are opened.

## VOI mechanism fixed before confirmation

For each unsampled candidate created by splitting an observed angular interval,
the policy predicts the post-split local interpolation uncertainty using linear
complex interpolation of the measured projected Stokes value. Candidate value
is the reduction in the maximum of two endpoint certificate deficits, divided
by one attempted acquisition, plus a fixed exploration term for large gaps and
attempt-adjacent dropout boundaries. The scorer is deterministic; ties are
resolved by wrapped angle.

Candidate fractions are fixed at `0.5, 0.382, 0.618, 0.25, 0.75`; scoring
weights and numerical constants must be recorded in code and the artifact
manifest before the first confirmatory run.

## Independent propagation audit

The production path uses NumPy FFTs. The audit path must construct the same
integer Fourier basis and finite-NA transfer explicitly with matrix products;
it must not call `fft`, `ifft`, or the production helper. Agreement establishes
implementation consistency, not physical validity. TorchOptics is treated as a
future external-integration reference rather than a hidden runtime dependency.

## Falsification and reporting

- Any wrong VOI release falsifies the observed-zero-error part of T5.
- Wilson and paired-bootstrap calculations are reported even when a hypothesis
  fails.
- H1 results remain immutable; H2 writes to a separate artifact directory.
- All failed hypotheses and family-specific regressions remain in the report.

