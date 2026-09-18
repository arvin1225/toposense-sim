# Findings

## Confirmatory understanding

The frozen confirmation reproduces the three exploratory regimes:

- finite polygon winding can be integer-valued and still describe the wrong ideal topology after NA truncation, projected leakage or sector loss;
- a global Lipschitz bound is safe but highly conservative; interval-specific bounds and active refinement recover correct releases at the same 32-location budget;
- support/zero-mode gates are essential for suppressing wrong releases, but their coverage cost may violate the registered T4 utility constraint.

On untouched seeds, the finite polygon estimator released the wrong ideal topology in `37.2%` of trials. The adaptive support-aware certificate made no wrong release in 500 trials; its one-sided 95% upper bound was `0.538%`. Its correct released information was `0.3622` bits/acquisition, three times the global certificate's `0.1207`.

This does not mean the receiver solves the full utility problem. T4 failed because support gating lost 32 percentage points of coverage on high-mode/NA and dropout cases. The result supports stringent selective safety and relative goodput over a conservative global bound, not high absolute throughput.

## Frozen implementation choices

- 12 initial samples, at most 20 deterministic risk-directed refinements;
- per-edge local interpolation bound capped by the registered global mode envelope;
- Fourier support residual `<0.24`, edge-mode fraction `<0.34`, transfer headroom `>0.42`, maximum gap `<0.56 rad`, at most four dropped attempts;
- a zero observed winding needs minimum projected radius `>0.50`;
- calibration residual remains inside every measurement uncertainty budget.

## Claim limits

No source or held-out synthetic result establishes performance on a measured optical receiver. The certified object remains projected boundary winding, not a full two-dimensional skyrmion degree.

## H2 exploratory update

Pure local value-of-information sampling was not sufficient: it improved the
compound-shift family but reduced pooled utility because measurements collapsed
around the current limiting edge. A deterministic alternation with global
support recovery reversed that regression. On exploratory seeds it added five
correct releases at the same 32-attempt budget, with zero wrong releases and a
positive paired bootstrap interval. The practical effect remained modest
(`+5.68%` goodput; `+1` percentage point coverage), below registered T7. The
mechanistic takeaway is that certificate-directed sensing needs an explicit
observability-preservation step, not only a sharper acquisition score.

## H2 confirmatory update

The direction of the small utility gain repeated on untouched seeds (six extra
correct releases; `+8.0%` goodput), but it did not meet the registered evidence
standard. One high-mode/NA false release invalidated zero-error T5, and the
paired interval touched zero. Thus the defensible finding is narrower: the
interleaved policy is a promising acquisition heuristic, while the present
support certificate is not strong enough for a new selective-safety claim under
high-mode truncation. The independent propagation audit rules out an FFT/direct
Fourier implementation discrepancy as the explanation.
