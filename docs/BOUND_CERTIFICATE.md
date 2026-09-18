# A conditional bound for received-loop winding

`toposense_bounds.certify_winding` accepts complex measurements, their error discs, sample angles and an independently justified derivative bound. It has no access to a field object, simulator seed, ideal symbol or ground-truth label.

The H1/H2 receiver remains a separate empirical method. Its local slope estimates and support thresholds are not deterministic bounds on an unobserved interval. The new routine makes a narrower, conditional mathematical statement about the **received** complex loop.

## Assumptions

Let `f(theta)` be a continuous, periodic complex loop, parameterized by angle in radians. Require:

- `|f(s) - f(t)| <= L |s - t|` on each unwrapped sampling interval, including the closing interval;
- each observed endpoint `z_i` satisfies `|f(theta_i) - z_i| <= epsilon_i` simultaneously;
- the angles are known, distinct modulo `2 pi`, and cover one period.

If angle jitter is bounded by `delta_i`, its contribution may be included as `L delta_i` in the endpoint error. If simultaneous bounds hold with probability `1-alpha`, the resulting guarantee is conditional on that event. Per-sample 95% intervals alone do not provide a simultaneous 95% statement.

## Sufficient condition

For an interval of angular width `h`, write `p(t) = (1-t) z_i + t z_(i+1)`, `0 <= t <= 1`. Endpoint interpolation and the Lipschitz inequality give

```text
|f(theta_i + t h) - p(t)|
  <= (1-t) epsilon_i + t epsilon_(i+1) + 2 L h t (1-t)
  <= max(epsilon_i, epsilon_(i+1)) + L h / 2 = R_i.
```

Compute the exact minimum distance `d_i` from the observed line segment to the origin. If every `d_i > R_i`, the straight homotopy between the received curve and its sampled polygon avoids the origin on every interval. Their winding numbers are therefore equal. This uses the standard homotopy invariance of winding; no novelty claim is made for that theorem.

The implementation also rejects bounds inconsistent with observed endpoint separation. A positive margin certifies the received loop, not preservation of an ideal transmitted symbol through an optical transfer function.

## What cannot be inferred from samples

Sixteen uniform samples of `exp(17 i theta)` are identical to samples of `exp(i theta)`. Substituting `L=1` for the true bound `L=17` can therefore produce a false certificate. A unit test retains this counterexample. The routine cannot discover a hidden high-frequency mode from those samples; deriving or validating `L` is a separate measurement-model problem.

## Reproduction

```bash
python -m pip install -e .
python -m unittest discover -s tests -p test_bound_certificate.py -v
python scripts/run_bound_study.py
```

The exploratory study evaluates 5 analytic loop families, 40 paired seeds and 3 sampling budgets, giving 600 inputs and 1,200 method rows. The budgets share curves; these are not 600 independent physical trials. Noise is bounded by construction, and the derivative bound comes from the known analytic Fourier coefficients, not from fitted sample slopes.

The recorded run released 240/600 inputs with the bound and made 0 wrong releases. Unconditional polygon decoding made 173 wrong releases. Coverage was 40%; the near-origin, high-frequency and missing-sector families were entirely rejected. This is a check of the sufficient condition under its assumptions, not a comparison against the H1/H2 photonic sensor experiment or evidence of laboratory performance.

Outputs: [row-level cases](../artifacts/bounded-loop-study/trials.csv), [summary](../artifacts/bounded-loop-study/summary.json), [local timing](../artifacts/bounded-loop-study/timing.json).

## Relation to recent optics work

[Zhang et al. (2026)](https://www.nature.com/articles/s41377-026-02307-4) demonstrate anisotropy-based skyrmion encoding and give a 60-degree robustness criterion for an S2-valued field. That concerns a different object from the complex boundary winding here. It supports asking for explicit perturbation assumptions; it does not validate this receiver or establish novelty for abstention.
