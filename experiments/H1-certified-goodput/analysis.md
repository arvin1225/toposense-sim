# Exploratory analysis before confirmation

| Iteration | Mechanism check | Outcome | Decision |
|---|---|---|---|
| E1 | initial composed receiver | polygon false release `0.005` | failure boundary too weak |
| E2 | registered residual-carrier/leakage range strengthened | polygon false release `0.380`; adaptive certificate `0.080` | useful stressor, unsafe gate |
| E3a | zero-mode projected-radius gate `0.40` | 2 adaptive wrong releases in 500 | falsified by radii `0.443`, `0.460` |
| E3b | zero-mode gate frozen at `0.50` | adaptive wrong releases `0/500`; Wilson upper `0.00538` | lock implementation |

Final exploratory goodput at equal maximum sample budget:

| Method | Coverage | False-release probability | Certified goodput |
|---|---:|---:|---:|
| unconditional polygon | 1.000 | 0.364 | 1.4767 |
| global certificate | 0.058 | 0.000 | 0.1347 |
| uniform support certificate | 0.122 | 0.000 | 0.2833 |
| adaptive support certificate | 0.156 | 0.000 | 0.3622 |
| adaptive local, no support gate | 0.294 | 0.072 | 0.5155 |

The adaptive/global goodput difference was `0.2275` bits/acquisition with family-stratified bootstrap interval `[0.1764, 0.2879]`. T4's coverage-loss condition failed (`0.325 > 0.15`) and remains frozen.

No seed at or above 1000 was inspected during these iterations.

## Frozen confirmatory outcome

| Gate | Frozen result | Decision |
|---|---|---|
| T1: unconditional false release ≥5% | `0.372` (`186/500`) | pass |
| T2: adaptive Wilson upper ≤1% | `0/500`; upper `0.00538` | pass |
| T3: ≥20% goodput gain + positive paired CI | `+200%`; difference `0.2415`, CI `[0.1858, 0.3019]` | pass |
| T4: halve false release with ≤15pp coverage loss | 100% reduction, `32pp` loss | fail |

The registered study succeeds because T2 and T3 pass. T4 remains a failed secondary utility gate and bounds the claim: support-aware erasure is safe in this synthetic study but still too conservative in the hardest observability families.
