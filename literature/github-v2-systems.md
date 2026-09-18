# GitHub systems consulted for V2 design

Accessed 2026-08-10. These repositories are architectural references; no source
code is copied into TopoSense-Sim.

## TorchOptics

- Repository: <https://github.com/matthewfilipovich/torchoptics>
- Relevant idea: differentiable, tensor-based scalar-wave propagation with
  explicit optical systems and field objects.
- Design response here: keep the lightweight periodic finite-NA model, but add
  a mathematically independent direct Fourier-sum audit. An optional future
  adapter can compare this reduced boundary model against a TorchOptics optical
  train without making GPU/PyTorch a requirement for the core benchmark.

## Active-learning design principle

The V2 acquisition policy follows a general value-of-information principle:
measure where the next observation is predicted to reduce the decision
certificate deficit, not merely where the geometric gap is largest. Its
scientific contribution is therefore evaluated against the frozen H1 heuristic
at identical acquisition budget, with support-gate and uncertainty ablations.

## Boundary of reuse

The repository is MIT licensed. External references guide interface and
validation choices only; TopoSense-Sim retains its own synthetic Jones/Stokes
model, receiver likelihood and topological certificate.

