# Focused literature survey

The survey identifies the gap TopoSense-Sim addresses; it does not claim novelty from citation absence.

## Optical topology and measured Stokes fields

- Shen et al., *Particle-like topologies in light*, Nature Communications (2021), generate and measure structured-light Stokes/phase textures and compute topology from discretely sampled measurements. This motivates explicit finite-sampling audit rather than assuming a continuous field from a plotted texture: https://www.nature.com/articles/s41467-021-26171-5
- *Topological protection of optical skyrmions through complex media*, Light: Science & Applications (2024), reports measured Stokes fields and discusses when smoothing remains topology preserving. It motivates treating preprocessing and measurement transfer as part of the claim: https://www.nature.com/articles/s41377-024-01659-z
- *Construction of optical spatiotemporal skyrmions*, Light: Science & Applications (2025), states the normalized Stokes map and skyrmion-number integral explicitly. TopoSense deliberately certifies a simpler projected boundary winding instead of silently claiming the full 2D degree: https://www.nature.com/articles/s41377-025-02028-0
- *Perturbation-resilient integer arithmetic using optical skyrmions*, Nature Photonics (2025), demonstrates discrete topological arithmetic and motivates goodput-oriented receiver questions, but does not provide this artifact's selective finite-observation certificate: https://www.nature.com/articles/s41566-025-01779-x
- *Topological rejection of noise by quantum skyrmions*, Nature Communications (2025), studies digitized topology under a specific quantum noise model. Relevance: shows that robustness depends on the field and noise construction; it does not remove the need to audit finite, noisy classical Stokes measurements. https://www.nature.com/articles/s41467-025-58232-4
- *Skyrmions based on optical anisotropy for topological encoding*, Light: Science & Applications (27 May 2026), demonstrates liquid-crystal retarder arrays and gives a 60-degree sufficient robustness rule for an S2-valued field. TopoSense's projected complex boundary loop is a different object; the paper supplies context for explicit perturbation assumptions, not validation of TopoSense. https://www.nature.com/articles/s41377-026-02307-4

## Polarimetric noise and calibration

- Goudail, *Noise minimization and equalization for Stokes polarimeters in the presence of signal-dependent Poisson shot noise*, Optics Letters (2009), analyzes Stokes-polarimeter design under Poisson noise. TopoSense uses paired analyzer counts with explicit Poisson and additive read-noise simulation: https://opg.optica.org/ol/abstract.cfm?uri=ol-34-5-647
- *Precision analysis of arbitrary full-Stokes polarimeters in the presence of additive and Poisson noise* derives variance behavior under mixed noise, motivating heteroscedastic per-sample angular bounds: https://opg.optica.org/josaa/upcoming_pdf.cfm?id=359784

## Selective prediction

- Geifman and El-Yaniv, *SelectiveNet*, ICML 2019, formalize risk–coverage evaluation for prediction with a reject option: https://proceedings.mlr.press/v97/geifman19a.html
- Bates et al., *Distribution-Free, Risk-Controlling Prediction Sets* (2021), emphasize explicit finite-sample risk control. TopoSense does not claim distribution-free validity under its held-out physical shifts; it uses deterministic certificates plus empirical false-release intervals: https://arxiv.org/abs/2101.02703

## Adaptive measurement design

- *Adaptive Sensing beyond Non-Adaptive Information Limits: End-to-End Co-Design of Geometry, Policy, and Inference* (2026 preprint) demonstrates that adaptive policies can outperform fixed designs only when hardware, action, and inference assumptions are modeled jointly. Relevance: TopoSense therefore compares every policy at the same finite acquisition budget and treats its VOI failure as evidence about the local policy, not evidence against adaptive sensing in general. https://arxiv.org/abs/2604.25193

## Gap used here

The project measures the release/erasure trade-off for finite Stokes observations. H1/H2 use empirical support gates and local slope estimates. The separate [bounded-loop implementation](../docs/BOUND_CERTIFICATE.md) provides a sufficient condition under independently supplied derivative and simultaneous endpoint-error bounds. Its current analytic stress study does not establish those bounds for the photon-noise receiver or recover a full two-dimensional skyrmion degree.
