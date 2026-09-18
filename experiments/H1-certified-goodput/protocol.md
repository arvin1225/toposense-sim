# Frozen protocol — finite-noise certified goodput

Status: **LOCKED BEFORE IMPLEMENTATION RESULTS**  
Date: 2026-08-03

## Research question

Can adaptive angular acquisition and a support-aware winding certificate improve correct released information per acquisition under held-out optical/sensor composition shift, while preserving a stringent false-release bound?

## Physical object and receiver

- Two coherent polarization components with registered azimuthal mode indices synthesize a Jones boundary field.
- Dense ideal Stokes evaluation (`≥2048` angular points) defines the projected-winding ground truth.
- The receiver applies periodic finite-NA mode attenuation, a residual 3×3 polarimetric calibration transform, six Poisson analyzer counts (`±S1`, `±S2`, `±S3`), Gaussian read noise, angular jitter and optional missing sectors.
- Each observed normalized Stokes sample carries a conservative angular-error radius derived without using the true winding.
- The released object is the winding of `S1 + iS2` around the origin, not an arbitrary 2D skyrmion degree.

## Fitting/calibration families

Only exploratory seeds `0–499` may be used for mechanism development and uncertainty-envelope calibration:

`nominal`, `shot_only`, `blur_only`, `crosstalk_only`, `jitter_only`.

## Held-out confirmatory families

Exactly five compositions, seeds `1000–1099` per family:

1. `blur_crosstalk`;
2. `low_photon_bias`;
3. `high_mode_na`;
4. `sector_dropout`;
5. `compound_shift`.

Windings `{-2,-1,0,1,2}` are assigned deterministically and in balance. No confirmatory label, family row or aggregate may tune a bound, threshold, weight or policy.

## Acquisition budget

- maximum 32 angular sample locations per trial;
- uniform methods receive 32 nominally equispaced locations;
- adaptive method starts with 12 locations and adds at most 20 locations one at a time;
- the next interval is selected from observed data only by the smallest robust phase/clearance surplus, with deterministic tie breaking;
- per-location analyzer photon budget is identical across methods; `samples_used` is always reported.

## Compared methods

1. `polygon_unconditional`: always release the finite-sample polygon winding;
2. `margin_only`: release when sampled projected radius exceeds the measurement radius;
3. `global_certificate`: one global measurement and interpolation bound plus phase/closure gates;
4. `local_certificate`: interval-specific measurement/interpolation bounds, no optical-support gate;
5. `adaptive_support_certificate`: active interval refinement plus local certificate, finite-NA mode-support and missing-sector observability gates;
6. `oracle_dense`: dense ideal diagnostic only; excluded from deployable comparisons.

## Metrics

- `false_release_probability = wrong_releases / all_trials`;
- `conditional_error = wrong_releases / releases`;
- `coverage = releases / all_trials`;
- `certified_goodput = correct_releases × log2(5) / all_trials` bits/acquisition;
- erasure rate, mean samples used and support-violation rate.

All deployable comparisons are paired by `(family, seed)`. Confidence limits use family-stratified bootstrap; T2 additionally uses a one-sided 95% Wilson upper bound.

## Registered gates

- **T1:** pooled unconditional false-release probability is at least `0.05`.
- **T2:** adaptive support-aware certificate's one-sided 95% Wilson upper bound on false-release probability is at most `0.01`.
- **T3:** while T2 holds, adaptive certified goodput is at least `20%` above the global certificate at the same maximum sample budget, and the paired bootstrap interval for the difference is entirely above zero.
- **T4 (secondary):** on pooled `high_mode_na` + `sector_dropout`, adding the support gate reduces false release by at least `50%` relative to the local certificate while losing at most `0.15` absolute coverage.

The registered study succeeds only if T2 and T3 pass. T1 describes the motivating failure mechanism and may fail. T4 is secondary.

## Mandatory ablations and controls

- no adaptive refinement;
- no support gate;
- no calibration-residual term;
- global instead of interval-specific uncertainty;
- zero-noise/identity-calibration positive control;
- zero projected-clearance and deliberately aliased high-winding negative controls;
- exact seed replay and split-disjointness check.

## Disproof and reporting

The study fails if the false-release upper bound exceeds 1%, goodput improvement is below 20%, the paired interval crosses zero, or any integrity control fails. Failed gates remain visible in the README, figures and interactive receiver. No post-result relabeling of an erasure as a correct decode is allowed.
