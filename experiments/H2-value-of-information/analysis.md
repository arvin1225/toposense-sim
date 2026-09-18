# H2 analysis

## Exploratory result — amended policy, seeds 500–599

The interleaved support-recovery/VOI policy produced 93 correct releases and no
wrong release in 500 trials, versus 88 correct and no wrong release for the
frozen H1 adaptive policy. Coverage increased from `0.176` to `0.186`, and
certified goodput increased from `0.40866` to `0.43188` bits per trial-budget
unit (`+5.68%`).

The paired goodput difference was `0.02322`, with 95% stratified-bootstrap
interval `[0.00464, 0.04644]`. Therefore exploratory T5, T6 and T8 passed. T7
failed because the one-percentage-point coverage gain was below three points
and the relative goodput gain was below 10%. The independent direct Fourier-sum
audit agreed with FFT propagation to `1.78e-15` maximum complex error and
preserved every audited dense winding.

These are exploratory data. The amended implementation is frozen before seeds
2000–2099 are opened. T7 remains failed in exploration and its threshold is not
relaxed.

## Mechanistic interpretation

Pure VOI over-concentrated measurements at the current limiting edge. Alternating
with the H1 support-recovery ranking preserved global angular coverage while VOI
steps attacked certificate bottlenecks. The gain is statistically paired but
small in practical magnitude, so confirmation is necessary and a negative H2
outcome remains plausible.

## Confirmatory result — frozen seeds 2000–2099

The VOI policy produced 81 correct releases and one wrong release in 500 trials;
H1 adaptive produced 75 correct and one wrong release. Coverage was `0.164`
versus `0.152`, and certified goodput was `0.37615` versus `0.34829` (`+8.0%`).
The paired difference was `0.02786`, but its 95% bootstrap interval
`[0.00000, 0.05573]` touched zero.

- T5 failed because the registered zero-wrong-release requirement was violated,
  although the one-sided Wilson upper bound was `0.891%` and remained below 1%.
- T6 failed because the paired interval lower endpoint was not strictly positive.
- T7 failed because the utility gain remained below both practical-effect
  thresholds and T5 did not pass.
- T8 passed: every operational row respected the 32-attempt budget.
- T9 passed: maximum production/reference propagation error was `2.00e-15`
  with all winding labels identical.

The independent artifact validator passed hashes, current code hash, 3,000-row
pairing, method/family/seed completeness, budgets, finite metrics, oracle control,
summary counts and exact row replay. `registered_success` is therefore correctly
false despite a small descriptive utility gain.
