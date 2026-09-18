"""Independent direct Fourier-sum audit for the finite-NA transfer."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .field import OpticalField, synthesize_field
from .geometry import polygon_winding


@dataclass(frozen=True)
class PropagationAudit:
    seed: int
    family: str
    samples: int
    maximum_complex_error: float
    production_winding: int
    reference_winding: int
    winding_match: bool


def direct_periodic_transfer(values: np.ndarray, cutoff: float) -> np.ndarray:
    """Evaluate the filtered Fourier series without calling FFT routines."""

    signal = np.asarray(values, dtype=complex)
    if signal.ndim != 1 or len(signal) < 2:
        raise ValueError("values must be a one-dimensional periodic signal")
    n = len(signal)
    raw = np.arange(n)
    frequencies = np.where(raw <= (n - 1) // 2, raw, raw - n).astype(float)
    sample_index = np.arange(n, dtype=float)
    analysis = np.exp(-2j * np.pi * frequencies[:, None] * sample_index[None, :] / n) / n
    synthesis = np.exp(2j * np.pi * sample_index[:, None] * frequencies[None, :] / n)
    coefficients = analysis @ signal
    transfer = np.exp(-((np.abs(frequencies) / max(cutoff, 0.4)) ** 4))
    return synthesis @ (coefficients * transfer)


def audit_propagation(seed: int, family: str, samples: int = 96) -> PropagationAudit:
    field: OpticalField = synthesize_field(seed, family, dense_samples=samples)
    reference = np.column_stack(
        [direct_periodic_transfer(field.ideal_jones[:, axis], field.config.na_cutoff_mode) for axis in range(2)]
    )
    error = float(np.max(np.abs(reference - field.received_jones)))
    # Import locally to keep this module's independent numerical path obvious.
    from .field import jones_to_stokes

    stokes = jones_to_stokes(reference)
    if field.config.projected_bias:
        from .geometry import normalize_stokes

        stokes = normalize_stokes(
            stokes + np.array([field.config.projected_bias, -0.35 * field.config.projected_bias, 0.0])[None, :]
        )
    reference_winding = polygon_winding(stokes)[0]
    return PropagationAudit(
        seed=seed,
        family=family,
        samples=samples,
        maximum_complex_error=error,
        production_winding=field.received_dense_winding,
        reference_winding=reference_winding,
        winding_match=reference_winding == field.received_dense_winding,
    )
