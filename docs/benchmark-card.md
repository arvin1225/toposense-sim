# Benchmark card

## Intended use

Controlled study of projected topology decoding, selective release and equal-budget active acquisition under synthetic finite-noise Stokes measurements.

## Out of scope

- full two-dimensional skyrmion-number reconstruction;
- laboratory receiver certification;
- communication BER or turbulence claim;
- target recognition, surveillance or human inference;
- state-of-the-art optical hardware comparison.

## Families

| Family | Composed factors |
|---|---|
| blur × crosstalk | finite OTF support, residual Stokes mixing/background |
| photon × bias | Poisson/read noise, calibration and projected carrier |
| high mode × NA | hidden angular content, low cutoff, near-pole projection |
| sector dropout | missing angular arc, phase modulation and jitter |
| compound | low photons, NA, crosstalk, calibration, jitter and hidden modes |

## Splits and cost

Exploration uses seeds `0–499`; confirmation uses `1000–1099` per family. Every deployable method is capped at 32 acquisition attempts. Missing measurements consume attempts. The dense oracle is diagnostic and excluded from method claims.

## Known limitations

- one-dimensional closed boundary loop only;
- periodic surrogate OTF rather than a measured pupil/PSF;
- heuristic but registered angular-error envelope;
- no temporal tracking, turbulence sequence or detector saturation;
- strong synthetic residual-carrier stressor;
- absolute adaptive coverage is only 15.6%;
- failed T4 utility constraint.

## Integrity

The protocol predates code/results. The committed manifest contains source, CSV and summary hashes. Validation checks the complete family/method matrix, sample budget, finite values, symbol balance, oracle correctness and exact deterministic replay.
