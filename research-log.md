# Research log

## 2026-08-10 — H2 value-of-information protocol lock

- Preserved the immutable H1 confirmation and opened a disjoint H2 study.
- Registered a 12-initial / 32-maximum acquisition comparison between the H1
  gap/phase heuristic and an observed-data-only value-of-information policy.
- Locked safety, paired-bootstrap utility, practical-effect and acquisition
  budget gates before implementing or inspecting H2 results.
- Added an independent direct Fourier-sum audit for the FFT finite-NA transfer;
  this checks numerical implementation consistency, not laboratory validity.
- Reserved seeds 500–599 for exploration and 2000–2099 for confirmation.

## 2026-08-10 — H2 exploratory falsification and amendment 01

- The first pure VOI pass on all 500 exploratory trials retained zero wrong
  releases but slightly regressed coverage (`0.174` versus `0.176`) and
  certified goodput (`-1.14%`) relative to H1 adaptive sampling. T6/T7 failed.
- Family results showed a gain on compound shift and losses on easier families,
  consistent with excessive concentration on the current limiting edge.
- A bounded exploratory comparison on seeds 500–549 selected a deterministic
  alternation of support-recovery and VOI steps. The rule is recorded in
  amendment 01 before implementation and before confirmatory seeds are opened.

## 2026-08-13 — amended H2 exploration frozen

- On the full 500-trial exploratory matrix, amended VOI made 93 correct and zero
  wrong releases; H1 adaptive made 88 correct and zero wrong releases.
- Paired goodput improved by `0.02322`, 95% bootstrap interval
  `[0.00464, 0.04644]`; T6 passed exploration.
- The relative gain was only `5.68%` and coverage gain only one percentage
  point, so the pre-registered practical-effect T7 failed exploration.
- Direct Fourier propagation agreed with the FFT path to `1.78e-15` and all
  audited winding labels matched. Code and policy are now frozen for H2
  confirmation.

## 2026-08-13 — frozen H2 confirmation

- Ran the unchanged 5-family × 100-seed × 6-method matrix, producing 3,000
  paired rows on seeds 2000–2099.
- VOI yielded 81 correct and one wrong release versus H1 adaptive's 75 correct
  and one wrong release. Relative certified-goodput gain was `8.0%`.
- T5 failed on the one wrong release; T6 failed because the paired 95% interval
  `[0.00000, 0.05573]` touched zero; T7 failed its practical-effect and safety
  conjunction. T8 and T9 passed.
- Independent validation passed every hash, completeness, budget, summary-count
  and deterministic-replay check. The negative `registered_success` outcome is
  preserved.

## 2026-08-03 — bootstrap and protocol lock

- Separated this project from the earlier dependency-free `topocert` reference: TopoSense-Sim must model Jones/Stokes field synthesis, finite NA, Poisson–Gaussian polarimetry, calibration residual, sample dropout and acquisition cost.
- Restricted the scientific object to projected winding of a closed Stokes boundary loop. A full 2D skyrmion degree remains out of scope.
- Registered held-out compositions, baselines, adaptive policy budget, seed partitions, paired metrics and failure gates before result generation.

## 2026-08-03 — exploratory inner loop E1–E3 (seeds 0–99 only)

- E1 found an underpowered failure model: unconditional polygon decoding made only 1 wrong release in 200 composed trials. The registered receiver compositions did not move the projected loop across the origin often enough to study selective safety.
- E2 strengthened the already registered finite-NA residual carrier / projected leakage factor while preserving ideal dense winding. Unconditional false release rose to 38%, but the first zero-mode gate still released 16 wrong high-mode/NA cases.
- E3 added an observed-data-only zero-mode separation gate. A zero winding requires an independent projected-radius margin because a translated non-zero loop can appear smooth and trivially closed. Two failures remained at radii `0.443` and `0.460`; the threshold was frozen at `0.50` after this falsification.
- Final exploratory matrix: 5 families × 100 seeds × 10 methods = 5,000 rows. Unconditional false release was `0.364`; adaptive support-aware false release was `0/500`, one-sided 95% Wilson upper bound `0.00538`.
- Adaptive certified goodput was `0.3622` bits/acquisition versus `0.1347` for the global certificate, `168.97%` relative improvement; paired difference `0.2275`, 95% interval `[0.1764, 0.2879]`.
- T4 failed in exploration: support gating removed all compared wrong releases but cost `0.325` absolute coverage, above the registered `0.15` limit. This is preserved rather than relaxed.
- Outer-loop decision: freeze code, thresholds and support gates before opening confirmation seeds.

## 2026-08-03 — frozen confirmation (seeds 1000–1099)

- Ran the locked 5-family × 100-seed × 10-method matrix once, producing 5,000 rows.
- Independent validation passed CSV/summary hashes, row count, seed range, method/family completeness, 32-sample budget, symbol balance, oracle control, exact field replay and exact selected-row replay.
- T1 passed: unconditional polygon false-release probability was `0.372` (`186/500`).
- T2 passed: adaptive support-aware wrong releases were `0/500`; one-sided 95% Wilson upper bound `0.00538`.
- T3 passed: adaptive certified goodput was `0.3622` versus `0.1207` bits/acquisition for the global certificate, exactly `200%` relative improvement. Paired difference `0.2415`, 95% interval `[0.1858, 0.3019]`.
- Active acquisition improved coverage over the uniform support certificate from `0.122` to `0.156` at the same maximum 32-location budget, without a wrong release.
- T4 failed: the support gate eliminated wrong releases relative to adaptive local/no-support (`0.068 → 0.000`) but cost `0.320` absolute coverage on the registered target families, exceeding `0.15`.
