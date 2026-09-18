# Technical report

## Research question

Can equal-budget adaptive Stokes acquisition increase certified correct information under held-out optical/sensor compositions while keeping the false-release probability below a registered 1% upper bound?

## Study design

Source/exploratory development uses seeds below 500. Confirmation uses untouched seeds `1000–1099` in each of five families: blur–crosstalk, low-photon–bias, high-mode–NA, sector dropout and compound shift. Windings `−2…2` are balanced. Ten methods include unconditional and margin baselines, global/local certificates, support and acquisition ablations, the full adaptive receiver and a dense oracle diagnostic.

The primary safety metric is wrong releases divided by all trials. The primary utility metric is correct released symbols multiplied by `log2(5)` bits and divided by all trials. This rewards abstention only when it prevents an error; an always-erasing system has zero goodput.

## Falsification history

The initial receiver was too easy: only 0.5% exploratory unconditional errors. Strengthening the already registered finite-NA residual-carrier factor created the intended topology-change boundary but exposed 8% wrong releases in the first adaptive certificate. A class-conditional zero-mode separation gate reduced this to two wrong releases in 500. Their observed radii (`0.443`, `0.460`) falsified the 0.40 threshold; 0.50 was frozen before confirmation.

## Confirmatory evidence

- Unconditional polygon: `186/500` wrong releases (`37.2%`).
- Margin-only: `48/500` wrong releases (`9.6%`).
- Local certificate without support: `11/500` wrong releases (`2.2%`).
- Adaptive local certificate without support: `34/500` wrong releases (`6.8%`).
- Full adaptive support certificate: `0/500` wrong releases, coverage `15.6%`.

The adaptive certificate's one-sided 95% Wilson upper bound is `0.538%`, satisfying T2. Correct goodput is `0.3622`, compared with `0.1207` for the global certificate: `200%` relative improvement. The paired family-stratified difference is `0.2415` bits/acquisition with 95% interval `[0.1858, 0.3019]`, satisfying T3.

## Negative result

T4 fails. On high-mode/NA plus sector-dropout cases, support gating removes all wrong releases relative to the no-support adaptive method, but coverage falls by 32 percentage points—more than twice the allowed 15 points. The method therefore demonstrates a safe selective receiver and a relative improvement over a conservative global certificate, not a solved high-throughput receiver.

## Contribution boundary

The project contributes a controlled systems combination: physical acquisition factors, active sampling, topology-specific sufficient gates, paired goodput evaluation, frozen protocols and replayable evidence. It does not claim that optical skyrmions, Stokes polarimetry, winding estimators or reject-option prediction are individually new.

## Next experiment

A new protocol should replace the binary support gate with an acquisition policy that explicitly values the expected gain in certifiable margin per photon/angle. The research target is to recover T4 utility without weakening T2 safety, followed by validation on measured Stokes fields with calibrated OTF and Mueller uncertainty.
